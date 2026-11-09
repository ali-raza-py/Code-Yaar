"""Tests for the admin publishing system, hackathon registration, and email campaigns.

Covers the scenario matrix from the Admin Publishing System / Hackathon
Registration & Email Communication specification: enforced Draft→Published
workflows, the announcement-viewset routing fix, per-hackathon form builder,
server-side registration validation, admin application review, changelog
feeds, and the honest campaign-email pipeline.
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import (
    Announcement, Competition, CompetitionRegistration, EmailCampaign,
    EmailCampaignRecipient, PlatformUpdate, RegistrationFormField, UserProfile,
    seed_default_registration_fields,
)
from .services import email_campaigns
from .services.auth import get_profile


def make_competition(organizer, **overrides):
    now = timezone.now()
    defaults = {
        'organizer': organizer,
        'title': 'Karachi Code Sprint',
        'slug': 'karachi-code-sprint',
        'short_description': 'A 48-hour build sprint.',
        'description': 'Build something great in 48 hours.',
        'category': 'Programming',
        'registration_start': now - timedelta(days=1),
        'registration_deadline': now + timedelta(days=10),
        'competition_start': now + timedelta(days=12),
        'competition_end': now + timedelta(days=14),
        'submission_deadline': now + timedelta(days=14),
        'is_published': True,
    }
    defaults.update(overrides)
    return Competition.objects.create(**defaults)


class BaseAccounts(TestCase):
    def setUp(self):
        # Deliberately the plain client: a campaign's queued send dispatches on
        # commit, and flushing every request would let that worker thread race
        # this test transaction. Tests that must observe mail flush the callbacks
        # themselves, at the point where the decision is made.
        self.client = APIClient()
        self.student = User.objects.create_user(
            username='learner', password='password', email='learner@example.com'
        )
        get_profile(self.student)  # ensure the profile row exists before use
        # Registration endpoints guard on verified emails (the deployment sets
        # AUTH_REQUIRE_EMAIL_VERIFICATION), so the learner starts verified.
        UserProfile.objects.filter(user=self.student).update(
            email_verified=True, email_verified_at=timezone.now()
        )
        self.admin = User.objects.create_user(
            username='staff-admin', password='password',
            email='staff-admin@example.com', is_staff=True,
        )
        self.super_admin = User.objects.create_superuser(
            username='root-admin', password='password', email='root@example.com'
        )
        # Pin profile roles so audience resolution is deterministic: only the
        # student may land in the "students" campaign audience.
        for admin_user in (self.admin, self.super_admin):
            profile = get_profile(admin_user)
            profile.role = 'admin'
            profile.save(update_fields=['role'])
        mail.outbox.clear()

    def login(self, user):
        self.client.force_login(user)


# ─── §1/§4: Announcements — routing fix + enforced publishing ───────────────

class AnnouncementPublishingTests(BaseAccounts):

    def create_announcement(self, **overrides):
        payload = {
            'title': 'Maintenance window Sunday',
            'body': 'The platform will restart briefly at 02:00 UTC.',
            'short_description': 'Brief maintenance Sunday night.',
            'category': 'maintenance',
            'priority': 'important',
            'target_audience': 'all',
        }
        payload.update(overrides)
        response = self.client.post(
            '/api/admin/announcements/', payload, format='json'
        )
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def test_admin_announcement_endpoint_is_routed(self):
        # Root cause of the broken publishing control: this route 404ed.
        self.login(self.admin)
        response = self.client.get('/api/admin/announcements/')
        self.assertEqual(response.status_code, 200)

    def test_create_defaults_to_draft_and_is_not_public(self):
        self.login(self.admin)
        data = self.create_announcement()
        self.assertEqual(data['status'], 'draft')
        self.assertFalse(data['is_published'])
        public = self.client.get('/api/announcements/')
        self.assertEqual(public.data['count'], 0)

    def test_publish_requires_super_admin(self):
        self.login(self.admin)
        data = self.create_announcement()
        denied = self.client.post(f'/api/admin/announcements/{data["id"]}/publish/')
        self.assertEqual(denied.status_code, 403)

        self.login(self.super_admin)
        allowed = self.client.post(f'/api/admin/announcements/{data["id"]}/publish/')
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(allowed.data['status'], 'published')
        self.assertTrue(allowed.data['is_published'])
        self.assertIsNotNone(allowed.data['published_at'])

    def test_publish_only_never_sends_email(self):
        self.login(self.super_admin)
        data = self.create_announcement()
        self.client.post(f'/api/admin/announcements/{data["id"]}/publish/')
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(EmailCampaign.objects.count(), 0)

    def test_email_draft_stages_campaign_without_sending(self):
        self.login(self.super_admin)
        data = self.create_announcement()
        response = self.client.post(
            f'/api/admin/announcements/{data["id"]}/email-draft/'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'draft')
        self.assertEqual(len(mail.outbox), 0)

    def test_unpublish_removes_from_public_feed(self):
        self.login(self.super_admin)
        data = self.create_announcement()
        self.client.post(f'/api/admin/announcements/{data["id"]}/publish/')
        self.assertEqual(self.client.get('/api/announcements/').data['count'], 1)
        self.client.post(f'/api/admin/announcements/{data["id"]}/unpublish/')
        self.assertEqual(self.client.get('/api/announcements/').data['count'], 0)

    def test_audience_filtering(self):
        self.login(self.admin)
        everyone = self.create_announcement(title='Everyone sees me')
        students = self.create_announcement(
            title='Students only', target_audience='students'
        )
        self.login(self.super_admin)
        for item in (everyone, students):
            self.client.post(f'/api/admin/announcements/{item["id"]}/publish/')

        anonymous_slugs = {row['slug'] for row in self.client.get('/api/announcements/').data['results']}
        self.assertIn('everyone-sees-me', anonymous_slugs)
        self.assertNotIn('students-only', anonymous_slugs)

        self.client.force_login(self.student)
        student_slugs = {row['slug'] for row in self.client.get('/api/announcements/').data['results']}
        self.assertIn('students-only', student_slugs)

    def test_expired_announcements_are_hidden(self):
        self.login(self.super_admin)
        data = self.create_announcement(slug='about-to-expire')
        self.client.post(f'/api/admin/announcements/{data["id"]}/publish/')
        Announcement.objects.filter(pk=data['id']).update(
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        slugs = {row['slug'] for row in self.client.get('/api/announcements/').data['results']}
        self.assertNotIn('about-to-expire', slugs)

    def test_status_cannot_be_flipped_through_plain_writes(self):
        self.login(self.admin)
        data = self.create_announcement()
        response = self.client.patch(
            f'/api/admin/announcements/{data["id"]}/',
            {'status': 'published'}, format='json',
        )
        self.assertEqual(response.status_code, 200)
        response.data  # serializer ignores it either way — verify the database
        self.assertEqual(
            Announcement.objects.get(pk=data['id']).status,
            Announcement.Status.DRAFT,
        )


# ─── §2: Hackathon management + publishing workflow ─────────────────────────

class HackathonWorkflowTests(BaseAccounts):

    def test_admin_created_hackathon_starts_unpublished_with_default_form(self):
        self.login(self.admin)
        now = timezone.now()
        response = self.client.post('/api/admin/competitions/', {
            'title': 'Lahore AI Weekend',
            'slug': 'lahore-ai-weekend',
            'short_description': 'Build an AI demo in a weekend.',
            'description': 'Two days, one prototype.',
            'category': 'AI',
            'registration_start': (now - timedelta(days=1)).isoformat(),
            'registration_deadline': (now + timedelta(days=5)).isoformat(),
            'competition_start': (now + timedelta(days=6)).isoformat(),
            'competition_end': (now + timedelta(days=8)).isoformat(),
            'submission_deadline': (now + timedelta(days=8)).isoformat(),
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertFalse(response.data['is_published'])
        competition = Competition.objects.get(slug='lahore-ai-weekend')
        self.assertEqual(competition.form_fields.count(), 15)

    def test_draft_hackathon_is_not_public_and_publish_makes_it_live(self):
        competition = make_competition(self.admin, is_published=False)
        self.assertEqual(self.client.get('/api/competitions/').data['count'], 0)
        self.login(self.admin)
        response = self.client.post(f'/api/admin/competitions/{competition.pk}/publish/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/api/competitions/').data['count'], 1)

    def test_status_follows_dates(self):
        competition = make_competition(self.admin)
        self.assertEqual(competition.status, 'registration_open')
        competition.registration_start = timezone.now() + timedelta(days=2)
        self.assertEqual(competition.status, 'upcoming')
        competition.is_archived = True
        self.assertEqual(competition.status, 'archived')

    def test_archive_leaves_listings_and_republishing_restores_them(self):
        competition = make_competition(self.admin)
        self.login(self.admin)
        self.client.post(f'/api/admin/competitions/{competition.pk}/archive/')
        self.assertEqual(self.client.get('/api/competitions/').data['count'], 0)
        # Archiving also un-publishes, so bringing a hackathon back is a
        # deliberate two-step: un-archive, then publish again.
        self.client.post(f'/api/admin/competitions/{competition.pk}/unarchive/')
        competition.refresh_from_db()
        self.assertFalse(competition.is_archived)
        self.assertFalse(competition.is_published)
        self.assertEqual(self.client.get('/api/competitions/').data['count'], 0)
        self.client.post(f'/api/admin/competitions/{competition.pk}/publish/')
        self.assertEqual(self.client.get('/api/competitions/').data['count'], 1)

    def test_publishing_a_hackathon_sends_no_email(self):
        competition = make_competition(self.admin, is_published=False)
        self.login(self.admin)
        self.client.post(f'/api/admin/competitions/{competition.pk}/publish/')
        self.assertEqual(len(mail.outbox), 0)


# ─── §3: Registration form builder ───────────────────────────────────────────

class FormBuilderTests(BaseAccounts):

    def setUp(self):
        super().setUp()
        self.competition = make_competition(self.admin)
        seed_default_registration_fields(self.competition)
        self.login(self.admin)

    def test_default_seed_is_idempotent(self):
        # make_competition bypasses the admin API, so seeding happens here:
        # first run creates all fifteen questions, a re-run creates none.
        existing = self.competition.form_fields.count()
        self.assertEqual(existing, 15)
        self.assertEqual(len(seed_default_registration_fields(self.competition)), 0)

    def test_add_custom_field(self):
        response = self.client.post('/api/admin/registration-form-fields/', {
            'competition': self.competition.pk,
            'label': 'T-shirt size',
            'field_key': 'tshirt_size',
            'field_type': 'dropdown',
            'options': ['S', 'M', 'L'],
            'required': False,
            'order': 99,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)

    def test_choice_field_without_options_is_rejected(self):
        response = self.client.post('/api/admin/registration-form-fields/', {
            'competition': self.competition.pk,
            'label': 'Favorite language',
            'field_key': 'fav_language',
            'field_type': 'dropdown',
            'options': [],
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_reserved_field_key_is_rejected(self):
        response = self.client.post('/api/admin/registration-form-fields/', {
            'competition': self.competition.pk,
            'label': 'Rules',
            'field_key': 'rules_accepted',
            'field_type': 'short_text',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_edit_and_delete_field(self):
        field = RegistrationFormField.objects.create(
            competition=self.competition, label='Team name',
            field_key='team_nickname', field_type='short_text',
        )
        patch = self.client.patch(
            f'/api/admin/registration-form-fields/{field.pk}/',
            {'label': 'Preferred team name'}, format='json',
        )
        self.assertEqual(patch.status_code, 200)
        field.refresh_from_db()
        self.assertEqual(field.label, 'Preferred team name')
        self.assertEqual(
            self.client.delete(f'/api/admin/registration-form-fields/{field.pk}/').status_code,
            204,
        )

    def test_reorder_persists(self):
        fields = list(self.competition.form_fields.order_by('order')[:3])
        reversed_fields = list(reversed(fields))
        items = [
            {'id': field.pk, 'order': index + 1}
            for index, field in enumerate(reversed_fields)
        ]
        response = self.client.post(
            '/api/admin/registration-form-fields/reorder/', {'items': items}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        reordered = list(self.competition.form_fields.filter(
            pk__in=[f.pk for f in fields]).order_by('order'))
        self.assertEqual([f.pk for f in reordered], [f.pk for f in reversed_fields])
        self.assertLess(reordered[0].order, reordered[-1].order)

    def test_public_form_only_shows_active_fields(self):
        first = self.competition.form_fields.order_by('order').first()
        RegistrationFormField.objects.filter(pk=first.pk).update(is_active=False)
        response = self.client.get(f'/api/competitions/{self.competition.slug}/registration-form/')
        self.assertEqual(response.status_code, 200)
        keys = [row['field_key'] for row in response.data]
        self.assertNotIn(first.field_key, keys)
        self.assertIn('full_name', keys) if first.field_key != 'full_name' else self.assertIn('email_address', keys)


# ─── §3: Public registration + server-side validation ───────────────────────

class PublicRegistrationTests(BaseAccounts):

    def setUp(self):
        super().setUp()
        self.competition = make_competition(self.admin)
        seed_default_registration_fields(self.competition)
        self.client.force_login(self.student)

    def valid_answers(self):
        return {
            'full_name': 'Ali Raza',
            'email_address': 'ali@example.com',
            'username': 'aliraza',
            'institution': 'City Polytechnic',
            'education_level': 'Bachelor',
            'city': 'Karachi',
            'country': 'Pakistan',
            'programming_experience': 'Intermediate',
            'participation_type': 'Individual',
        }

    def register(self, answers, extra=None):
        payload = {'rules_accepted': True, 'registration_data': answers}
        payload.update(extra or {})
        return self.client.post(
            f'/api/competitions/{self.competition.slug}/register/', payload, format='json'
        )

    def test_valid_registration_gets_reference(self):
        response = self.register(self.valid_answers())
        self.assertEqual(response.status_code, 201, response.data)
        registration = CompetitionRegistration.objects.get(user=self.student)
        self.assertTrue(registration.reference)
        self.assertEqual(registration.registration_status, 'registered')

    def test_missing_required_answer_fails_with_field_errors(self):
        answers = self.valid_answers()
        del answers['full_name']
        response = self.register(answers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('full_name', response.data)

    def test_invalid_email_answer_is_rejected(self):
        answers = self.valid_answers()
        answers['email_address'] = 'not-an-email'
        response = self.register(answers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email_address', response.data)

    def test_dropdown_membership_is_enforced(self):
        answers = self.valid_answers()
        answers['education_level'] = 'Kindergarten'
        response = self.register(answers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('education_level', response.data)

    def test_duplicate_registration_is_rejected(self):
        self.assertEqual(self.register(self.valid_answers()).status_code, 201)
        second = self.register(self.valid_answers())
        self.assertEqual(second.status_code, 409)

    def test_registration_closes_at_the_deadline(self):
        Competition.objects.filter(pk=self.competition.pk).update(
            registration_deadline=timezone.now() - timedelta(hours=1)
        )
        response = self.register(self.valid_answers())
        self.assertEqual(response.status_code, 400)

    def test_participant_limit_blocks_overflow(self):
        Competition.objects.filter(pk=self.competition.pk).update(participant_limit=1)
        other = User.objects.create_user(
            username='early-bird', password='password', email='early@example.com'
        )
        CompetitionRegistration.objects.create(
            competition=self.competition, user=other,
            rules_accepted_at=timezone.now(),
        )
        response = self.register(self.valid_answers())
        self.assertEqual(response.status_code, 400)
        self.assertIn('full', str(response.data.get('detail', '')))

    def test_rules_must_be_accepted(self):
        Competition.objects.filter(pk=self.competition.pk).update(
            competition_rules=['No plagiarism.']
        )
        response = self.register(self.valid_answers(), {'rules_accepted': False})
        self.assertEqual(response.status_code, 400)


# ─── §3: Admin application review + decision emails + CSV ────────────────────

class ApplicationReviewTests(BaseAccounts):

    def setUp(self):
        super().setUp()
        self.competition = make_competition(self.admin)
        seed_default_registration_fields(self.competition)
        self.registration = CompetitionRegistration.objects.create(
            competition=self.competition, user=self.student,
            registration_data={'full_name': 'Ali Raza'},
            rules_accepted_at=timezone.now(),
        )
        self.login(self.admin)

    def decide(self, new_status):
        """Post a review decision, flushing the queued decision email.

        Notification mail is handed to ``transaction.on_commit()``, which never
        fires inside a TestCase's outer atomic block, so the callbacks are
        captured and run here to observe the real delivery.
        """
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(
                f'/api/admin/hackathon-registrations/{self.registration.pk}/update-status/',
                {'status': new_status}, format='json',
            )

    def test_approve_sends_essential_email_and_records_status(self):
        response = self.decide('approved')
        self.assertEqual(response.status_code, 200)
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.registration_status, 'approved')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('approved', mail.outbox[0].subject.lower())

    def test_waitlist_uses_waitlist_template(self):
        response = self.decide('waitlisted')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('waitlist', mail.outbox[0].subject.lower())

    def test_unknown_status_is_rejected(self):
        self.assertEqual(self.decide('promoted').status_code, 400)

    def test_stats_and_filters(self):
        stats = self.client.get(f'/api/admin/hackathon-registrations/stats/?competition={self.competition.pk}')
        self.assertEqual(stats.status_code, 200)
        self.assertEqual(stats.data['total'], 1)
        listed = self.client.get(f'/api/admin/hackathon-registrations/?competition={self.competition.pk}&status=registered')
        self.assertEqual(listed.data['count'], 1)

    def test_csv_export_contains_registration(self):
        response = self.client.get('/api/admin/hackathon-registrations/export_csv/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        body = b''.join(response.streaming_content).decode() if getattr(response, 'streaming', False) else response.content.decode()
        self.assertIn(self.registration.reference, body)
        self.assertIn('Ali Raza', body)


# ─── §5: Platform updates / changelog ────────────────────────────────────────

class PlatformUpdateTests(BaseAccounts):

    def create_update(self):
        response = self.client.post('/api/admin/platform-updates/', {
            'title': 'Sandbox upgrades',
            'slug': 'sandbox-upgrades',
            'category': 'feature',
            'summary': 'Faster runs and Python 3.13.',
            'content': 'We rebuilt the sandbox on a faster image.',
            'change_list': ['Python 3.13', '2× faster cold starts'],
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def test_draft_is_not_public_and_publish_makes_it_live(self):
        self.login(self.admin)
        data = self.create_update()
        self.assertEqual(data['status'], 'draft')
        self.assertEqual(self.client.get('/api/platform-updates/').data['count'], 0)
        denied = self.client.post(f'/api/admin/platform-updates/{data["id"]}/publish/')
        self.assertEqual(denied.status_code, 403)  # publishing is Super Admin only
        self.login(self.super_admin)
        self.client.post(f'/api/admin/platform-updates/{data["id"]}/publish/')
        feed = self.client.get('/api/platform-updates/')
        self.assertEqual(feed.data['count'], 1)
        self.assertEqual(feed.data['results'][0]['slug'], 'sandbox-upgrades')

    def test_category_filter_on_public_feed(self):
        self.login(self.super_admin)
        data = self.create_update()
        response = self.client.post(f'/api/admin/platform-updates/{data["id"]}/publish/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get('/api/platform-updates/?category=bug_fix').data['count'], 0)
        self.assertEqual(self.client.get('/api/platform-updates/?category=feature').data['count'], 1)

    def test_email_draft_stages_but_publish_never_emails(self):
        self.login(self.super_admin)
        data = self.create_update()
        self.client.post(f'/api/admin/platform-updates/{data["id"]}/publish/')
        self.assertEqual(len(mail.outbox), 0)
        draft = self.client.post(f'/api/admin/platform-updates/{data["id"]}/email-draft/')
        self.assertEqual(draft.status_code, 201)
        self.assertEqual(draft.data['status'], 'draft')
        self.assertEqual(len(mail.outbox), 0)


# ─── §6: Email campaigns — composer gates and honest tracking ────────────────

class EmailCampaignTests(BaseAccounts):

    def setUp(self):
        super().setUp()
        self.login(self.super_admin)

    def campaign_payload(self, **overrides):
        payload = {
            'name': 'November update mail',
            'subject': 'New this month on Code Yaar',
            'heading': 'New this month',
            'body': 'First paragraph.\nSecond paragraph.',
            'template': 'platform_update',
            'audience': 'students',
            'cta_label': 'See updates',
            # cta_url is a URLField, so relative app paths are refused.
            'cta_url': 'https://codeyaar.dev/updates',
        }
        payload.update(overrides)
        return payload

    def create_campaign(self, **overrides):
        response = self.client.post(
            '/api/admin/email-campaigns/', self.campaign_payload(**overrides), format='json'
        )
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def test_regular_admin_cannot_touch_campaigns(self):
        self.login(self.admin)
        response = self.client.get('/api/admin/email-campaigns/')
        self.assertEqual(response.status_code, 403)

    def test_send_without_confirmation_is_refused(self):
        data = self.create_campaign()
        response = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/send/', {}, format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_send_requires_draft_status_and_never_remails(self):
        data = self.create_campaign()
        queued = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/send/', {'confirm': True}, format='json'
        )
        self.assertEqual(queued.status_code, 202)
        self.assertEqual(queued.data['status'], 'queued')
        again = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/send/', {'confirm': True}, format='json'
        )
        self.assertEqual(again.status_code, 409)

    def test_zero_recipient_audience_is_refused(self):
        data = self.create_campaign(audience='instructors')
        response = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/send/', {'confirm': True}, format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_hackathon_audience_requires_competition(self):
        data = self.create_campaign(audience='comp_approved')
        response = self.client.post(
            f'/api/admin/email-campaigns/{data["id"]}/send/', {'confirm': True}, format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_audience_count_and_preview(self):
        data = self.create_campaign()
        counted = self.client.get(f'/api/admin/email-campaigns/{data["id"]}/audience-count/')
        self.assertEqual(counted.data['count'], 1)  # only the student has role=student
        preview = self.client.get(f'/api/admin/email-campaigns/{data["id"]}/preview/')
        self.assertIn('New this month', preview.data['html'])
        self.assertIn('First paragraph.', preview.data['text'])

    def test_dispatch_delivers_and_records_honest_outcomes(self):
        data = self.create_campaign()
        campaign = EmailCampaign.objects.get(pk=data['id'])
        email_campaigns.dispatch_campaign(campaign, sync=True)
        recipients = EmailCampaignRecipient.objects.filter(campaign=campaign)
        self.assertEqual(recipients.count(), 1)
        recipient = recipients.get()
        self.assertIn(recipient.status, (
            EmailCampaignRecipient.Status.SENT, EmailCampaignRecipient.Status.RENDER_ONLY,
        ))
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, EmailCampaign.Status.SENT)
        self.assertEqual(campaign.sent_count, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('unsubscribe', mail.outbox[0].alternatives[0][0].lower())

    def test_marketing_optout_recipients_are_skipped(self):
        profile = self.student.profile
        profile.notification_preferences = {'email_announcements': False}
        profile.save()
        data = self.create_campaign()
        campaign = EmailCampaign.objects.get(pk=data['id'])
        email_campaigns.dispatch_campaign(campaign, sync=True)
        recipient = EmailCampaignRecipient.objects.get(campaign=campaign)
        self.assertEqual(recipient.status, EmailCampaignRecipient.Status.SKIPPED)
        self.assertEqual(len(mail.outbox), 0)
        campaign.refresh_from_db()
        self.assertEqual(campaign.skipped_count, 1)

    def test_test_email_goes_only_to_the_admin(self):
        data = self.create_campaign()
        response = self.client.post(f'/api/admin/email-campaigns/{data["id"]}/test/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['root@example.com'])
        self.assertIn('[TEST]', mail.outbox[0].subject)


# ─── §7: Unsubscribe + email settings exposure rules ─────────────────────────

class UnsubscribeAndSettingsTests(BaseAccounts):

    def test_signed_unsubscribe_link_flips_preference(self):
        token = email_campaigns.unsubscribe_token(self.student)
        response = self.client.get(f'/api/email/unsubscribe/{token}/')
        self.assertEqual(response.status_code, 200)
        profile = self.student.profile
        profile.refresh_from_db()  # the view writes through its own instance
        self.assertFalse(
            profile.get_notification_preference(email_campaigns.MARKETING_PREFERENCE)
        )

    def test_tampered_token_is_refused(self):
        response = self.client.get('/api/email/unsubscribe/not-a-real-token/')
        self.assertEqual(response.status_code, 400)
        self.assertIn('unsubscribe', response.content.decode().lower())

    def test_email_settings_never_expose_the_password(self):
        self.login(self.admin)
        self.assertEqual(self.client.get('/api/admin/email/settings/').status_code, 403)
        self.login(self.super_admin)
        response = self.client.get('/api/admin/email/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('password', response.data)
        self.assertIn('password_configured', response.data)
        self.assertIn('backend', response.data)
