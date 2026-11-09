"""Tests for the admin "Send Official Email" composer.

Covers the guarantees the feature exists to provide: individual and
multi-recipient sends to specific students, external custom addresses for
people without accounts, per-recipient personalization, recipient validation
and deduplication, HTML sanitization, authorization, honest failure tracking,
resend of failed copies only, and history filtering.
"""

from __future__ import annotations

from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from .models import EmailCampaign, EmailCampaignRecipient, UserProfile
from .services import email_campaigns
from .services import email_composer as composer
from .services.auth import get_profile

User = get_user_model()

PASSWORD = 'Strong-Pass-9!'


class ComposerBase(TestCase):
    def setUp(self):
        # Plain client inside TestCase transactions: queued sends never fire
        # their on_commit dispatch here — tests call dispatch(sync=True)
        # themselves, exactly like the campaign suite in tests_publishing.
        self.client = APIClient()
        self.student1 = User.objects.create_user(
            username='ali123', password=PASSWORD, email='ali@example.com',
            first_name='Ali', last_name='Raza',
        )
        self.student2 = User.objects.create_user(
            username='sara77', password=PASSWORD, email='sara@example.com',
            first_name='Sara', last_name='Khan',
        )
        for student in (self.student1, self.student2):
            profile = get_profile(student)
            profile.role = 'student'
            profile.save(update_fields=['role'])
        self.instructor = User.objects.create_user(
            username='teach01', password=PASSWORD, email='teach@example.com',
            first_name='Tech', last_name='Er',
        )
        profile = get_profile(self.instructor)
        profile.role = 'instructor'
        profile.save(update_fields=['role'])
        self.student_outsider = User.objects.create_user(
            username='nosy', password=PASSWORD, email='nosy@example.com',
        )
        self.super_admin = User.objects.create_superuser(
            username='root-admin', password=PASSWORD, email='root@example.com',
        )
        mail.outbox.clear()

    def login(self, user):
        self.client.force_login(user)

    def composer_payload(self, **overrides):
        payload = {
            'name': 'Direct notice mail',
            'subject': 'Important Update for {{student_name}}',
            'heading': 'Account notice',
            'body': '',
            'body_html': (
                '<p>Dear {{student_name}}, your Code Yaar ID is {{student_id}} '
                'and today is {{current_date}}. — {{organization_name}}</p>'
            ),
            'audience': 'specific',
            'selected_users': [self.student1.pk],
            'custom_emails': [],
        }
        payload.update(overrides)
        return payload

    def create_draft(self, **overrides):
        response = self.client.post(
            '/api/admin/email-campaigns/', self.composer_payload(**overrides), format='json',
        )
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def send_and_dispatch(self, campaign_id):
        response = self.client.post(
            f'/api/admin/email-campaigns/{campaign_id}/send/', {'confirm': True}, format='json',
        )
        self.assertEqual(response.status_code, 202, response.data)
        campaign = EmailCampaign.objects.get(pk=campaign_id)
        email_campaigns.dispatch_campaign(campaign, sync=True)
        return EmailCampaign.objects.get(pk=campaign_id)


class ComposerDraftTests(ComposerBase):
    """Draft validation: recipients, addresses, variables, sanitization."""

    def setUp(self):
        super().setUp()
        self.login(self.super_admin)

    def test_specific_audience_requires_recipients(self):
        response = self.client.post('/api/admin/email-campaigns/', self.composer_payload(
            selected_users=[], custom_emails=[],
        ), format='json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_custom_email_is_rejected(self):
        response = self.client.post('/api/admin/email-campaigns/', self.composer_payload(
            selected_users=[], custom_emails=['not-an-email@@x'],
        ), format='json')
        self.assertEqual(response.status_code, 400)

    def test_duplicate_custom_emails_collapse_and_normalize(self):
        data = self.create_draft(
            selected_users=[],
            custom_emails=['Foo@Example.com', 'foo@example.com', 'other@example.org'],
        )
        self.assertEqual(
            sorted(data['custom_emails']), ['foo@example.com', 'other@example.org'],
        )

    def test_empty_body_is_refused(self):
        response = self.client.post('/api/admin/email-campaigns/', self.composer_payload(
            body_html='',
        ), format='json')
        self.assertEqual(response.status_code, 400)

    def test_unknown_variable_is_refused(self):
        response = self.client.post('/api/admin/email-campaigns/', self.composer_payload(
            subject='Hi {{principal_name}}',
        ), format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('principal_name', str(response.data))

    def test_body_html_is_sanitized_on_save(self):
        data = self.create_draft(
            body_html=(
                '<script>alert(1)</script>'
                '<p onclick="steal()">Hello <b>world</b></p>'
                '<a href="javascript:alert(2)">bad</a>'
                '<a href="https://codeyaar.dev">good</a>'
            ),
        )
        stored = data['body_html']
        self.assertNotIn('<script>', stored)
        self.assertNotIn('onclick', stored)
        self.assertNotIn('javascript:', stored)
        self.assertIn('<b>world</b>', stored)
        self.assertIn('https://codeyaar.dev', stored)

    def test_external_recipients_only_draft(self):
        data = self.create_draft(selected_users=[], custom_emails=['outside@example.com'])
        self.assertEqual(data['audience'], 'specific')


class ComposerSearchTests(ComposerBase):
    """Student lookup by name, email and student ID."""

    def setUp(self):
        super().setUp()
        self.login(self.super_admin)

    def search(self, term):
        response = self.client.get(f'/api/admin/email-campaigns/students-search/?q={term}')
        self.assertEqual(response.status_code, 200)
        return [row['email'] for row in response.data['results']]

    def test_search_by_name(self):
        self.assertIn('sara@example.com', self.search('Sara'))

    def test_search_by_email(self):
        self.assertIn('ali@example.com', self.search('ali@exam'))

    def test_search_by_student_id(self):
        # The username is the student ID the composer personalizes with.
        self.assertIn('sara@example.com', self.search('sara77'))

    def test_students_only(self):
        emails = self.search('01')  # teach01 is an instructor, not a student
        self.assertNotIn('teach@example.com', emails)

    def test_blank_query_returns_nothing(self):
        self.assertEqual(self.search(''), [])


class ComposerValidationEndpointTests(ComposerBase):

    def setUp(self):
        super().setUp()
        self.login(self.super_admin)

    def test_recipient_verification_resolves_names_and_flags_duplicates(self):
        response = self.client.post('/api/admin/email-campaigns/validate-recipients/', {
            'user_ids': [self.student1.pk],
            'emails': ['ali@example.com', 'brand-new@example.com', 'bad@@x'],
        }, format='json')
        self.assertEqual(response.status_code, 200)
        rows = response.data['recipients']
        self.assertEqual(len(rows), 2)  # the address matching student1 dedupes away
        self.assertEqual(response.data['invalid'], ['bad@@x'])
        self.assertEqual(response.data['duplicates_removed'], ['ali@example.com'])
        names = {row['email']: row['name'] for row in rows}
        self.assertEqual(names['ali@example.com'], 'Ali Raza')

    def test_sender_identity_is_read_only_server_config(self):
        with override_settings(DEFAULT_FROM_EMAIL='Code Yaar <no-reply@codeyaar.dev>'):
            response = self.client.get('/api/admin/email-campaigns/sender-identity/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['sender_email'], 'no-reply@codeyaar.dev')
        self.assertEqual(response.data['sender_name'], 'Code Yaar')


class ComposerSendTests(ComposerBase):
    """Delivery, personalization isolation, and duplicate-send protection."""

    def setUp(self):
        super().setUp()
        self.login(self.super_admin)

    def test_single_student_gets_the_only_copy(self):
        data = self.create_draft()
        self.send_and_dispatch(data['id'])
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ['ali@example.com'])
        self.assertIn('Important Update for Ali Raza', message.subject)
        html = message.alternatives[0][0]
        self.assertIn('Dear Ali Raza', html)
        self.assertIn('ID is ali123', html)
        self.assertIn(timezone.localdate().strftime('%B'), html)
        self.assertIn('Code Yaar', html)

    def test_multiple_recipients_are_mailed_individually(self):
        data = self.create_draft(selected_users=[self.student1.pk, self.student2.pk])
        campaign = self.send_and_dispatch(data['id'])
        self.assertEqual(len(mail.outbox), 2)
        for message in mail.outbox:
            # Private recipient lists: no other address leaks into headers.
            self.assertEqual(len(message.to), 1)
            self.assertNotIn(self.student2.email, message.to if message.to[0] != self.student2.email else ['x'])
            self.assertEqual(message.cc, [])
            self.assertEqual(message.bcc, [])
        recipients = {m.to[0] for m in mail.outbox}
        self.assertEqual(recipients, {'ali@example.com', 'sara@example.com'})
        sara_copy = next(m for m in mail.outbox if m.to[0] == 'sara@example.com')
        self.assertIn('Sara Khan', sara_copy.subject)
        self.assertIn('sara77', sara_copy.alternatives[0][0])
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, EmailCampaign.Status.SENT)
        self.assertEqual(campaign.recipient_count, 2)
        self.assertEqual(campaign.sent_count, 2)

    def test_external_custom_address_without_account_is_mailed(self):
        data = self.create_draft(selected_users=[], custom_emails=['outside@example.com'])
        campaign = self.send_and_dispatch(data['id'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['outside@example.com'])
        row = EmailCampaignRecipient.objects.get(campaign=campaign)
        self.assertIsNone(row.user_id)
        self.assertEqual(row.status, EmailCampaignRecipient.Status.SENT)
        # No signed unsubscribe link for people who have no account.
        self.assertNotIn('api/email/unsubscribe', mail.outbox[0].alternatives[0][0])

    def test_mixed_students_and_external_recipients(self):
        data = self.create_draft(
            selected_users=[self.student1.pk],
            custom_emails=['outside@example.com', 'ali@example.com'],  # dup of student1
        )
        campaign = self.send_and_dispatch(data['id'])
        # Exactly one copy per address: the duplicate custom entry is skipped.
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(campaign.recipient_count, 2)

    def test_plain_text_alternative_is_personalized(self):
        data = self.create_draft(plain_text_alternative='Hello {{student_name}}!')
        self.send_and_dispatch(data['id'])
        # The alternative is the email's own text content, wrapped in the
        # standard plain-text branding layout like every other campaign mail.
        self.assertIn('Hello Ali Raza!', mail.outbox[0].body)
        self.assertNotIn('Sara', mail.outbox[0].body)

    def test_cc_on_every_copy_bcc_once(self):
        data = self.create_draft(
            selected_users=[self.student1.pk, self.student2.pk],
            cc_emails=['boss@example.com'],
            bcc_emails=['archive@example.com'],
        )
        self.send_and_dispatch(data['id'])
        self.assertEqual(len(mail.outbox), 2)
        for message in mail.outbox:
            self.assertEqual(message.cc, ['boss@example.com'])
        bcc_copies = [m for m in mail.outbox if m.bcc]
        self.assertEqual(len(bcc_copies), 1)
        self.assertEqual(bcc_copies[0].bcc, ['archive@example.com'])

    def test_send_requires_confirmation(self):
        data = self.create_draft()
        response = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/send/', {}, format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    def test_second_send_is_refused_so_no_double_mailing(self):
        data = self.create_draft()
        self.send_and_dispatch(data['id'])
        again = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/send/', {'confirm': True}, format='json',
        )
        self.assertEqual(again.status_code, 409)
        self.assertEqual(len(mail.outbox), 1)

    def test_zero_recipient_selection_cannot_send(self):
        # An active selection that has since lost every account must not mail.
        data = self.create_draft(selected_users=[self.student1.pk])
        self.student1.is_active = False
        self.student1.save(update_fields=['is_active'])
        response = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/send/', {'confirm': True}, format='json',
        )
        self.assertEqual(response.status_code, 400)


class ComposerPreviewTestTests(ComposerBase):

    def setUp(self):
        super().setUp()
        self.login(self.super_admin)

    def test_preview_personalizes_for_a_chosen_student(self):
        data = self.create_draft(selected_users=[self.student1.pk, self.student2.pk])
        response = self.client.get(
            f'/api/admin/email-campaigns/{data["id"]}/preview/?as_user={self.student2.pk}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Important Update for Sara Khan', response.data['subject'])
        self.assertIn('Sara Khan', response.data['html'])
        self.assertIn('sara77', response.data['html'])

    def test_preview_defaults_to_the_requesting_admin(self):
        data = self.create_draft()
        response = self.client.get(f'/api/admin/email-campaigns/{data["id"]}/preview/')
        self.assertIn('root-admin', response.data['html'])

    def test_test_email_goes_only_to_the_admin(self):
        data = self.create_draft()
        response = self.client.post(f'/api/admin/email-campaigns/{data["id"]}/test/', {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['ok'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['root@example.com'])
        self.assertIn('[TEST]', mail.outbox[0].subject)

    def test_test_email_can_target_an_explicit_address(self):
        data = self.create_draft()
        response = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/test/',
            {'to': 'spotcheck@example.com'}, format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mail.outbox[0].to, ['spotcheck@example.com'])

    def test_invalid_test_address_is_refused(self):
        data = self.create_draft()
        response = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/test/',
            {'to': 'nope@@'}, format='json',
        )
        self.assertEqual(response.status_code, 400)


class ComposerAuthorizationTests(ComposerBase):
    """Only authorized administrators can touch the composer at all."""

    def test_student_is_forbidden(self):
        self.login(self.student_outsider)
        for path in (
            '/api/admin/email-campaigns/',
            '/api/admin/email-campaigns/students-search/?q=ali',
            '/api/admin/email-campaigns/sender-identity/',
        ):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 403, path)
        response = self.client.post('/api/admin/email-campaigns/', self.composer_payload(), format='json')
        self.assertEqual(response.status_code, 403)

    def test_instructor_is_forbidden(self):
        self.login(self.instructor)
        self.assertEqual(
            self.client.get('/api/admin/email-campaigns/').status_code, 403,
        )

    def test_anonymous_is_unauthenticated(self):
        response = self.client.get('/api/admin/email-campaigns/')
        self.assertIn(response.status_code, (401, 403))


class ComposerFailureTests(ComposerBase):
    """Transport failures are recorded honestly and only failures resend."""

    def setUp(self):
        super().setUp()
        self.login(self.super_admin)

    def test_delivery_failure_marks_failed_not_sent(self):
        data = self.create_draft(
            selected_users=[self.student1.pk, self.student2.pk],
        )
        real_send = mail.EmailMessage.send

        def flaky(self_message, *args, **kwargs):
            if self_message.to == ['ali@example.com']:
                raise OSError('SMTP 550 mailbox unavailable')
            return real_send(self_message, *args, **kwargs)

        with mock.patch.object(mail.EmailMessage, 'send', flaky):
            campaign = self.send_and_dispatch(data['id'])

        campaign.refresh_from_db()
        self.assertEqual(campaign.status, EmailCampaign.Status.PARTIAL)
        self.assertEqual(campaign.failed_count, 1)
        self.assertEqual(campaign.sent_count, 1)
        failed_row = EmailCampaignRecipient.objects.get(
            campaign=campaign, email='ali@example.com',
        )
        self.assertEqual(failed_row.status, EmailCampaignRecipient.Status.FAILED)
        self.assertIn('550', failed_row.error)
        # The failure reason is sanitized to a bounded single line.
        self.assertNotIn('\n', failed_row.error)

    def test_resend_failed_retries_only_failures(self):
        data = self.create_draft(
            selected_users=[self.student1.pk, self.student2.pk],
        )

        real_send = mail.EmailMessage.send
        attempts = {'ali': 0}

        def flaky(self_message, *args, **kwargs):
            if self_message.to == ['ali@example.com'] and attempts['ali'] == 0:
                attempts['ali'] += 1
                raise OSError('SMTP connection reset')
            return real_send(self_message, *args, **kwargs)

        with mock.patch.object(mail.EmailMessage, 'send', flaky):
            campaign = self.send_and_dispatch(data['id'])
        self.assertEqual(campaign.failed_count, 1)
        self.assertEqual(len(mail.outbox), 1)

        response = self.client.post(
            f'/api/admin/email-campaigns/{campaign.pk}/resend-failed/',
            {'confirm': True}, format='json',
        )
        self.assertEqual(response.status_code, 202)
        email_campaigns.dispatch_campaign(
            EmailCampaign.objects.get(pk=campaign.pk), sync=True,
        )
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, EmailCampaign.Status.SENT)
        self.assertEqual(campaign.failed_count, 0)
        # Two original copies (one failed) plus exactly one retry of the failure.
        self.assertEqual(len(mail.outbox), 2)
        ali_rows = EmailCampaignRecipient.objects.filter(
            campaign=campaign, email='ali@example.com',
        )
        self.assertEqual(ali_rows.count(), 1)
        self.assertEqual(ali_rows.get().status, EmailCampaignRecipient.Status.SENT)

    def test_resend_needs_confirmation_and_a_finished_campaign(self):
        data = self.create_draft()
        missing_confirm = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/resend-failed/', {}, format='json',
        )
        self.assertEqual(missing_confirm.status_code, 400)
        not_finished = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/resend-failed/',
            {'confirm': True}, format='json',
        )
        self.assertEqual(not_finished.status_code, 409)


class ComposerHistoryTests(ComposerBase):
    """Sent-email history: search, filters, and duplicate-as-draft."""

    def setUp(self):
        super().setUp()
        self.login(self.super_admin)

    def test_history_searches_by_recipient(self):
        data = self.create_draft(custom_emails=[])
        self.send_and_dispatch(data['id'])
        response = self.client.get('/api/admin/email-campaigns/?search=ali@example.com')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        missed = self.client.get('/api/admin/email-campaigns/?search=nobody@example.com')
        self.assertEqual(missed.data['count'], 0)

    def test_history_filters_by_status(self):
        sent = self.create_draft(name='Sent one')
        self.send_and_dispatch(sent['id'])
        self.create_draft(name='Draft two')
        drafts = self.client.get('/api/admin/email-campaigns/?status=draft')
        self.assertEqual(drafts.data['count'], 1)
        self.assertEqual(drafts.data['results'][0]['name'], 'Draft two')

    def test_history_filters_by_date(self):
        data = self.create_draft()
        today = timezone.localdate().isoformat()
        response = self.client.get(
            f'/api/admin/email-campaigns/?date_from={today}&date_to={today}'
        )
        self.assertEqual(response.data['count'], 1)
        past = self.client.get('/api/admin/email-campaigns/?date_to=2000-01-01')
        self.assertEqual(past.data['count'], 0)

    def test_recipient_rows_search_and_filter(self):
        data = self.create_draft(
            selected_users=[self.student1.pk, self.student2.pk],
        )
        self.send_and_dispatch(data['id'])
        response = self.client.get(
            f'/api/admin/email-campaigns/{data["id"]}/recipients/?search=sara'
        )
        self.assertEqual(len(response.data['results']), 1)
        failed = self.client.get(
            f'/api/admin/email-campaigns/{data["id"]}/recipients/?status=failed'
        )
        self.assertEqual(failed.status_code, 200, failed.data)
        self.assertEqual(len(failed.data['results']), 0)

    def test_duplicate_reopens_a_sent_email_as_a_new_draft(self):
        data = self.create_draft(
            selected_users=[self.student1.pk], custom_emails=['outside@example.com'],
        )
        self.send_and_dispatch(data['id'])
        response = self.client.post(f'/api/admin/email-campaigns/{data["id"]}/duplicate/')
        self.assertEqual(response.status_code, 201)
        clone = response.data
        self.assertNotEqual(clone['id'], data['id'])
        self.assertEqual(clone['status'], 'draft')
        self.assertEqual(clone['subject'], data['subject'])
        self.assertEqual(clone['selected_users'], [self.student1.pk])
        self.assertEqual(clone['custom_emails'], ['outside@example.com'])
        # The clone can be confirmed and sent independently.
        self.send_and_dispatch(clone['id'])

    def test_sending_is_recorded_in_the_audit_log(self):
        from .models import AuthenticationAuditLog
        data = self.create_draft()
        self.send_and_dispatch(data['id'])
        events = set(
            AuthenticationAuditLog.objects.filter(user=self.super_admin)
            .values_list('event', flat=True)
        )
        self.assertIn('email_campaign_draft_created', events)
        self.assertIn('email_campaign_queued', events)


class ComposerSanitizerUnitTests(TestCase):
    """Direct unit coverage of the sanitizer and personalization primitives."""

    def test_sanitize_drops_disallowed_structure(self):
        cleaned = composer.sanitize_html(
            '<div style="x">Ok <iframe src="https://evil.example"></iframe>'
            '<img src="https://ok.example/p.png" alt="p" onerror="bad()">'
            '<a href="mailto:x@y.z" target="_blank">mail</a></div>'
        )
        self.assertIn('<div>Ok ', cleaned)
        self.assertNotIn('iframe', cleaned)
        self.assertNotIn('onerror', cleaned)
        self.assertNotIn('style', cleaned)
        self.assertIn('mailto:x@y.z', cleaned)
        self.assertIn('<img src="https://ok.example/p.png" alt="p">', cleaned)

    def test_personalization_escapes_values_into_html(self):
        variables = composer.recipient_variables(
            name='<script>nuke</script>', email='x@example.com', student_id='x1',
        )
        out = composer.personalize_html('<p>Hi {{student_name}}</p>', variables)
        self.assertNotIn('<script>', out)
        self.assertIn('&lt;script&gt;', out)

    def test_plain_text_conversion(self):
        text = composer.plain_text_from_html(
            '<p>First</p><ul><li>One</li><li>Two</li></ul><p>See <a href="https://a.dev">the site</a></p>'
        )
        self.assertIn('First', text)
        self.assertIn('• One', text)
        self.assertIn('the site (<https://a.dev>)', text)

    def test_recipient_variables_shape(self):
        variables = composer.recipient_variables(name='Ab. Cd', email='a@b.c', student_id='pk-1')
        self.assertEqual(variables['student_name'], 'Ab. Cd')
        self.assertEqual(variables['student_email'], 'a@b.c')
        self.assertEqual(variables['student_id'], 'pk-1')
        self.assertEqual(variables['organization_name'], 'Code Yaar')
        self.assertIn(str(timezone.localdate().year), variables['current_date'])

    def test_unknown_variables_reporting(self):
        self.assertEqual(composer.unknown_variables('Hi {{student_name}}'), [])
        self.assertEqual(composer.unknown_variables('Hi {{bogus_thing}}'), ['bogus_thing'])
