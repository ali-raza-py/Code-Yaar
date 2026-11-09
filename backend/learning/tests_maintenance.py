import json

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from .models import MaintenanceSettings


class MaintenanceModeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username='student', password='password'
        )
        self.administrator = User.objects.create_user(
            username='administrator', password='password', is_staff=True
        )
        self.super_admin = User.objects.create_superuser(
            username='super-admin', password='password', email='super@example.com'
        )
        # Written through save() rather than queryset.update(): the
        # middleware reads a short-lived cached snapshot that the model's
        # save() invalidates, and update() would bypass that.
        settings = MaintenanceSettings.get_solo()
        settings.is_enabled = True
        settings.maintenance_message = 'Scheduled maintenance.'
        settings.save()

    def tearDown(self):
        cache.delete(MaintenanceSettings.CACHE_KEY)
        super().tearDown()

    def test_anonymous_api_request_returns_structured_503(self):
        response = self.client.get('/api/courses/')

        self.assertEqual(response.status_code, 503)
        payload = json.loads(response.content)
        self.assertEqual(payload['code'], 'maintenance_mode')
        self.assertTrue(payload['maintenance_mode'])

    def test_regular_users_and_administrators_are_blocked(self):
        for user in (self.student, self.administrator):
            with self.subTest(user=user.username):
                self.client.login(username=user.username, password='password')
                response = self.client.get('/api/courses/')
                self.assertEqual(response.status_code, 503)
                self.client.logout()

    def test_super_admin_can_use_api_during_maintenance(self):
        self.client.login(username='super-admin', password='password')

        response = self.client.get('/api/courses/')

        self.assertNotEqual(response.status_code, 503)

    def test_super_admin_can_use_django_admin_during_maintenance(self):
        self.client.login(username='super-admin', password='password')

        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, 200)

    def test_regular_staff_cannot_view_maintenance_settings_in_django_admin(self):
        settings = MaintenanceSettings.get_solo()
        settings.is_enabled = False
        settings.save()
        self.client.login(username='administrator', password='password')

        response = self.client.get('/admin/learning/maintenancesettings/')

        self.assertEqual(response.status_code, 403)

    def test_status_endpoint_remains_available(self):
        response = self.client.get('/api/platform/status/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['maintenance_mode'])
        self.assertEqual(response.data['estimated_return_time'], '')

    def test_only_super_admin_can_change_maintenance(self):
        self.client.login(username='administrator', password='password')
        response = self.client.patch(
            '/api/admin/settings/',
            {'maintenance_mode': False},
            format='json',
        )
        self.assertEqual(response.status_code, 403)

        self.client.login(username='super-admin', password='password')
        response = self.client.patch(
            '/api/admin/settings/',
            {'maintenance_mode': False},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['maintenance_mode'])

        self.client.logout()
        response = self.client.get('/api/courses/')
        self.assertNotEqual(response.status_code, 503)

    def test_maintenance_settings_are_a_singleton(self):
        MaintenanceSettings(is_enabled=False).save()
        self.assertEqual(MaintenanceSettings.objects.count(), 1)
        self.assertEqual(MaintenanceSettings.objects.get().pk, 1)
