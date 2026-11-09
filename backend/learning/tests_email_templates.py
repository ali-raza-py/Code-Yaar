"""Tests for the Email Templates Library.

Covers the guarantees the feature is meant to provide and *nothing else*:
creating/saving/retrieving templates, editing, duplicating, deleting,
favoriting, search + category filtering, the seeded starter collection,
variable + sanitization handling on save, the branded preview render, the
Super Admin permission boundary, and — the integration contract — that using
a template populates a composed email without mutating the saved template.

These tests deliberately do *not* touch the campaign send pipeline beyond
reading; templates never send mail, and this suite asserts that.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from rest_framework.test import APIClient

from .models import EmailTemplate, UserProfile
from .services.auth import get_profile
from .default_email_templates import DEFAULT_EMAIL_TEMPLATES

User = get_user_model()
PASSWORD = 'Strong-Pass-9!'
BASE = '/api/admin/email-templates/'


class TemplateBase(TestCase):
    # Whether to wipe the migration-seeded starter templates before each test.
    # Most CRUD/filter tests want an empty library; the seed tests opt out.
    purge_seeded = True

    def setUp(self):
        self.client = APIClient()
        if self.purge_seeded:
            EmailTemplate.objects.all().delete()
        self.super_admin = User.objects.create_superuser(
            username='root-admin', password=PASSWORD, email='root@example.com',
        )
        self.regular_admin = User.objects.create_user(
            username='adm', password=PASSWORD, email='adm@example.com',
        )
        profile = get_profile(self.regular_admin)
        profile.role = 'administrator'
        profile.save(update_fields=['role'])
        self.student = User.objects.create_user(
            username='stu', password=PASSWORD, email='stu@example.com',
            first_name='Sam', last_name='Tutor',
        )
        sp = get_profile(self.student)
        sp.role = 'student'
        sp.save(update_fields=['role'])
        mail.outbox.clear()

    def login(self, user):
        self.client.force_login(user)

    def payload(self, **overrides):
        data = {
            'name': 'Notice template',
            'category': 'Important Announcements',
            'description': 'Used for platform-wide notices.',
            'subject': 'Heads up, {{student_name}}',
            'heading': 'An important update',
            'preview_text': 'Read this before your next lesson.',
            'body_html': '<p>Dear {{student_name}}, today is {{current_date}}. — {{organization_name}}</p>',
            'cta_label': 'Open Code Yaar',
            'cta_url': 'https://codeyaar.dev/dashboard',
            'footer_content': 'Sent to {{student_email}}.',
            'is_favorite': False,
        }
        data.update(overrides)
        return data

    def create(self, **overrides):
        response = self.client.post(BASE, self.payload(**overrides), format='json')
        self.assertEqual(response.status_code, 201, response.data)
        return response.data


class TemplateCrudTests(TemplateBase):
    def setUp(self):
        super().setUp()
        self.login(self.super_admin)

    def test_create_persists_all_fields(self):
        data = self.create()
        template = EmailTemplate.objects.get(pk=data['id'])
        self.assertEqual(template.name, 'Notice template')
        self.assertEqual(template.category, 'Important Announcements')
        self.assertEqual(template.created_by, self.super_admin)
        self.assertIn('{{student_name}}', template.body_html)

    def test_plain_text_derived_from_body_when_absent(self):
        data = self.create()
        template = EmailTemplate.objects.get(pk=data['id'])
        self.assertIn('Dear {{student_name}}', template.plain_text)

    def test_body_is_sanitized_on_save(self):
        data = self.create(
            body_html='<p onclick="x()">Hi <script>alert(1)</script>{{student_name}}</p>',
        )
        template = EmailTemplate.objects.get(pk=data['id'])
        self.assertNotIn('<script>', template.body_html)
        self.assertNotIn('onclick', template.body_html)
        self.assertIn('{{student_name}}', template.body_html)

    def test_unknown_variable_is_rejected(self):
        response = self.client.post(BASE, self.payload(subject='Hi {{principal_name}}'), format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('principal_name', str(response.data))

    def test_update_changes_the_template(self):
        data = self.create()
        response = self.client.patch(
            f'{BASE}{data["id"]}/', {'subject': 'Updated subject'}, format='json',
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(EmailTemplate.objects.get(pk=data['id']).subject, 'Updated subject')

    def test_duplicate_creates_independent_copy(self):
        data = self.create()
        response = self.client.post(f'{BASE}{data["id"]}/duplicate/', {}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        clone = EmailTemplate.objects.get(pk=response.data['id'])
        self.assertTrue(clone.name.startswith('Copy of '))
        self.assertEqual(clone.subject, EmailTemplate.objects.get(pk=data['id']).subject)
        self.assertFalse(clone.is_favorite)
        # Editing the clone must not touch the original.
        clone.subject = 'clone only'
        clone.save()
        self.assertNotEqual(
            EmailTemplate.objects.get(pk=data['id']).subject, 'clone only',
        )

    def test_delete_removes_the_template(self):
        data = self.create()
        response = self.client.delete(f'{BASE}{data["id"]}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(EmailTemplate.objects.filter(pk=data['id']).exists())

    def test_favorite_toggle_persists(self):
        data = self.create()
        self.client.patch(f'{BASE}{data["id"]}/', {'is_favorite': True}, format='json')
        self.assertTrue(EmailTemplate.objects.get(pk=data['id']).is_favorite)


class TemplateListFilterTests(TemplateBase):
    def setUp(self):
        super().setUp()
        self.login(self.super_admin)
        self.create(name='Alpha', category='Welcome & Onboarding')
        self.create(name='Beta', category='Password Reset', is_favorite=True)
        self.create(name='Gamma', category='Welcome & Onboarding')

    def test_search_by_name(self):
        response = self.client.get(f'{BASE}?search=Alpha')
        names = [row['name'] for row in response.data['results']]
        self.assertEqual(names, ['Alpha'])

    def test_filter_by_category(self):
        response = self.client.get(f'{BASE}?category=Welcome%20%26%20Onboarding')
        self.assertEqual({row['name'] for row in response.data['results']}, {'Alpha', 'Gamma'})

    def test_filter_favorites(self):
        response = self.client.get(f'{BASE}?category=favorites')
        self.assertEqual([row['name'] for row in response.data['results']], ['Beta'])

    def test_categories_include_presets_and_used(self):
        self.create(name='Custom one', category='Very Custom')
        response = self.client.get(f'{BASE}categories/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome & Onboarding', response.data['categories'])
        self.assertIn('Very Custom', response.data['categories'])


class TemplateSeedTests(TemplateBase):
    """The migration-installed starter collection is present and complete."""

    purge_seeded = False

    def test_default_templates_are_seeded(self):
        names = set(EmailTemplate.objects.values_list('name', flat=True))
        for spec in DEFAULT_EMAIL_TEMPLATES:
            self.assertIn(spec['name'], names)

    def test_every_seed_has_professional_content(self):
        for template in EmailTemplate.objects.all():
            self.assertTrue(template.subject.strip(), template.name)
            self.assertTrue(template.body_html.strip(), template.name)
            self.assertNotIn('lorem', template.body_html.lower(), template.name)


class TemplatePreviewTests(TemplateBase):
    def setUp(self):
        super().setUp()
        self.login(self.super_admin)

    def test_preview_renders_branded_and_personalizes_for_viewer(self):
        data = self.create(subject='Hi {{student_name}}')
        response = self.client.get(f'{BASE}{data["id"]}/preview/')
        self.assertEqual(response.status_code, 200, response.data)
        # The admin's own identity fills the tokens in the preview.
        self.assertIn('root', response.data['subject'].lower())
        self.assertIn('Code Yaar', response.data['html'])

    def test_preview_does_not_send_mail(self):
        data = self.create()
        self.client.get(f'{BASE}{data["id"]}/preview/')
        self.assertEqual(len(mail.outbox), 0)


class TemplatePermissionTests(TemplateBase):
    def test_regular_admin_is_forbidden(self):
        self.login(self.regular_admin)
        self.assertEqual(self.client.get(BASE).status_code, 403)
        self.assertEqual(
            self.client.post(BASE, self.payload(), format='json').status_code, 403,
        )

    def test_student_is_forbidden(self):
        self.login(self.student)
        self.assertEqual(self.client.get(BASE).status_code, 403)

    def test_anonymous_is_unauthenticated(self):
        self.assertIn(self.client.get(BASE).status_code, (401, 403))


class TemplateComposerIntegrationTests(TemplateBase):
    """The core contract: applying a template fills a draft, not the template."""

    def setUp(self):
        super().setUp()
        self.login(self.super_admin)

    def test_using_template_populates_composer_without_mutating_template(self):
        from .models import EmailCampaign

        data = self.create(
            subject='Enrollment confirmed for {{student_name}}',
            heading='You are enrolled',
            cta_label='Go to my course',
            cta_url='https://codeyaar.dev/dashboard',
        )
        template = EmailTemplate.objects.get(pk=data['id'])
        original_subject = template.subject
        original_body = template.body_html

        # Simulate the composer applying the template: copy content into a draft.
        draft = EmailCampaign.objects.create(
            name=template.name,
            subject=template.subject,
            heading=template.heading,
            body='',
            body_html=template.body_html,
            plain_text_alternative=template.plain_text,
            cta_label=template.cta_label,
            cta_url=template.cta_url,
            audience=EmailCampaign.Audience.SPECIFIC,
            created_by=self.super_admin,
        )
        # Editing the composed draft must never change the saved template.
        draft.subject = 'Edited during composition'
        draft.save(update_fields=['subject'])

        template.refresh_from_db()
        self.assertEqual(template.subject, original_subject)
        self.assertEqual(template.body_html, original_body)
        self.assertEqual(draft.subject, 'Edited during composition')
        # Variables survive the copy: still unrendered in both places.
        self.assertIn('{{student_name}}', template.body_html)
