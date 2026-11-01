"""Authentication API test suite.

Covers registration, login, session refresh/rotation, logout, email
verification, password reset/change, profile updates, privilege-escalation
protection, RBAC groups, throttling, and token storage rules.

Every assertion here is backed by a real request against the API — no mocks
of the authentication layer.
"""

import re
import sys
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import (
    AuthenticationAuditLog, CareerTrack, Course, EmailVerificationToken,
    Enrollment, PasswordResetToken, UserProfile, hash_auth_token,
)
from .services.auth import (
    ADMIN_GROUP, INSTRUCTOR_GROUP, STUDENT_GROUP, mail_transport_ready, user_role,
)

PASSWORD = 'Learn-Python-2026!'
NEW_PASSWORD = 'Ship-Better-Code-2027!'
REFRESH_COOKIE = settings.AUTH_REFRESH_COOKIE_NAME
VERIFY_PATH = '/verify-email'
RESET_PATH = '/reset-password'


def extract_token(message, path):
    """Pull the raw single-use token out of an outgoing email link."""
    match = re.search(rf'{re.escape(path)}\?token=([A-Za-z0-9_\-]+)', message.body)
    return match.group(1) if match else None


# The verification gate follows the mail transport in `settings.py`, so a
# developer's real `.env` (SMTP + App Password) would arm it inside the test run
# and change what registration and login return. Tests therefore pin the policy
# explicitly; `EnforcedVerificationTests` opts back in to exercise the gate.
@override_settings(AUTH_REQUIRE_EMAIL_VERIFICATION=False)
class AuthAPITestCase(TestCase):
    """Shared client helpers for the authentication endpoints."""

    maxDiff = None

    def setUp(self):
        # Throttle counters live in the cache; isolate every test.
        cache.clear()
        self.client = APIClient()

    # ── request helpers ────────────────────────────────────────────────────

    def register(self, **overrides):
        payload = {
            'full_name': 'Test Learner',
            'username': 'tlearner',
            'email': 'tlearner@example.com',
            'password': PASSWORD,
            'confirm_password': PASSWORD,
        }
        payload.update(overrides)
        return self.client.post('/api/auth/register/', payload, format='json')

    def sign_in(self, identifier, password=PASSWORD):
        return self.client.post(
            '/api/auth/login/',
            {'identifier': identifier, 'password': password},
            format='json',
        )

    def use_access(self, access):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def me(self, **kwargs):
        return self.client.get('/api/auth/me/', **kwargs)

    def patch_me(self, data):
        return self.client.patch('/api/auth/me/', data, format='json')

    def csrf_token(self):
        response = self.client.get('/api/auth/csrf/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['csrfToken']

    def refresh(self, csrf=None):
        csrf = self.csrf_token() if csrf is None else csrf
        return self.client.post(
            '/api/auth/token/refresh/', {}, format='json', HTTP_X_CSRFTOKEN=csrf
        )

    def logout(self, csrf=None):
        csrf = self.csrf_token() if csrf is None else csrf
        return self.client.post(
            '/api/auth/logout/', {}, format='json', HTTP_X_CSRFTOKEN=csrf
        )

    @staticmethod
    def cookie_value(response, name=REFRESH_COOKIE):
        return response.cookies[name].value

    def signed_in(self):
        """Register the default learner and return the register response."""
        response = self.register()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        return response


# ─── Registration ───────────────────────────────────────────────────────────


class RegistrationTests(AuthAPITestCase):
    def test_registration_creates_a_student_account(self):
        response = self.signed_in()

        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.data['token_type'], 'Bearer')
        self.assertEqual(response.data['user']['username'], 'tlearner')
        self.assertEqual(response.data['user']['role'], 'student')
        self.assertTrue(response.data['verification_email_sent'])

        cookie = response.cookies[REFRESH_COOKIE]
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['samesite'], 'Lax')

        user = User.objects.get(username='tlearner')
        self.assertTrue(user.check_password(PASSWORD))
        self.assertNotEqual(user.password, PASSWORD)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.profile.role, 'student')
        self.assertTrue(user.groups.filter(name=STUDENT_GROUP).exists())

    def test_email_is_normalised_to_lowercase(self):
        response = self.register(email='Test.Learner@Example.COM')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            User.objects.get(username='tlearner').email, 'test.learner@example.com'
        )

    def test_duplicate_username_is_rejected_case_insensitively(self):
        self.signed_in()
        response = self.register(username='TLearner', email='other@example.com')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        self.signed_in()
        response = self.register(username='seconduser', email='TLEARNER@example.com')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_invalid_email_is_rejected(self):
        response = self.register(email='not-an-email')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_weak_password_is_rejected(self):
        response = self.register(password='12345678', confirm_password='12345678')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertFalse(User.objects.filter(username='tlearner').exists())

    def test_password_mismatch_is_rejected(self):
        response = self.register(confirm_password=NEW_PASSWORD)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

    def test_full_name_is_required(self):
        response = self.register(
            full_name='', first_name='', last_name='', username='noname'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('full_name', response.data)

    def test_registration_cannot_grant_privileges(self):
        response = self.register(
            role='admin', is_staff=True, is_superuser=True, email_verified=True
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username='tlearner')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.profile.role, 'student')
        self.assertFalse(user.profile.email_verified)
        self.assertFalse(user.groups.filter(name=ADMIN_GROUP).exists())
        self.assertEqual(response.data['user']['role'], 'student')

    def test_registration_audits_the_event(self):
        self.signed_in()
        self.assertTrue(
            AuthenticationAuditLog.objects.filter(event='register').exists()
        )

    def test_registration_emails_a_hashed_single_use_token(self):
        self.signed_in()

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ['tlearner@example.com'])
        self.assertIn(VERIFY_PATH, message.body)

        raw_token = extract_token(message, VERIFY_PATH)
        self.assertTrue(raw_token)

        record = EmailVerificationToken.objects.get()
        self.assertEqual(record.token_hash, hash_auth_token(raw_token))
        self.assertNotEqual(record.token_hash, raw_token)
        self.assertTrue(record.is_usable)
        self.assertLessEqual(
            record.expires_at,
            timezone.now() + timedelta(
                hours=settings.AUTH_EMAIL_VERIFICATION_TTL_HOURS + 1
            ),
        )


# ─── Login ──────────────────────────────────────────────────────────────────


class LoginTests(AuthAPITestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='loginuser',
            email='loginuser@example.com',
            password=PASSWORD,
            first_name='Login',
            last_name='User',
        )

    def test_login_with_username(self):
        response = self.sign_in('loginuser')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'loginuser')
        self.assertIn(REFRESH_COOKIE, response.cookies)

    def test_login_with_email_is_case_insensitive(self):
        response = self.sign_in('LOGINUSER@EXAMPLE.COM')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_accepts_the_legacy_username_key(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'loginuser', 'password': PASSWORD},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_updates_last_login(self):
        self.assertIsNone(self.user.last_login)
        self.sign_in('loginuser')
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)

    def test_failed_login_uses_a_generic_message(self):
        known = self.sign_in('loginuser', password='Wrong-Password-9!')
        unknown = self.sign_in('ghost@example.com', password='Wrong-Password-9!')

        self.assertEqual(known.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(unknown.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(str(known.data['detail']), str(unknown.data['detail']))
        self.assertEqual(str(known.data['detail']), 'Invalid credentials.')
        self.assertTrue(
            AuthenticationAuditLog.objects.filter(event='login_failed').exists()
        )

    def test_inactive_account_cannot_sign_in(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
        response = self.sign_in('loginuser')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn(REFRESH_COOKIE, response.cookies)

    def test_login_creates_a_missing_profile(self):
        UserProfile.objects.filter(user=self.user).delete()
        response = self.sign_in('loginuser')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())


# ─── Current user / profile ─────────────────────────────────────────────────


class MeTests(AuthAPITestCase):
    def setUp(self):
        super().setUp()
        self.register_response = self.signed_in()
        self.use_access(self.register_response.data['access'])
        self.user = User.objects.get(username='tlearner')

    def test_requires_authentication(self):
        self.client.credentials()
        self.assertEqual(self.me().status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_nested_and_flat_profile_fields(self):
        response = self.me()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for key in (
            'user', 'profile', 'avatar', 'bio', 'role', 'email_verified',
            'institution', 'education_level', 'github_url', 'linkedin_url',
            'xp_points', 'streak_days', 'level', 'last_active_at',
        ):
            self.assertIn(key, response.data)
        self.assertEqual(response.data['user']['username'], 'tlearner')
        self.assertEqual(response.data['role'], 'student')
        self.assertFalse(response.data['email_verified'])

    def test_updates_editable_profile_fields(self):
        response = self.patch_me({
            'full_name': 'Ada Lovelace',
            'bio': 'Learning Python.',
            'institution': 'Code Yaar Academy',
            'education_level': 'undergraduate',
            'github_url': 'https://github.com/ada',
            'linkedin_url': 'https://www.linkedin.com/in/ada',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['user']['first_name'], 'Ada')
        self.assertEqual(response.data['user']['last_name'], 'Lovelace')
        self.assertEqual(response.data['bio'], 'Learning Python.')
        self.assertEqual(response.data['institution'], 'Code Yaar Academy')
        self.assertEqual(response.data['education_level'], 'undergraduate')
        self.assertEqual(response.data['github_url'], 'https://github.com/ada')

    def test_rejects_invalid_education_level(self):
        response = self.patch_me({'education_level': 'phd'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('education_level', response.data)

    def test_role_cannot_be_changed_via_profile_api(self):
        response = self.patch_me({'role': 'admin'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fields', response.data)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
        self.assertEqual(self.user.profile.role, 'student')
        self.assertTrue(
            AuthenticationAuditLog.objects.filter(
                event='privilege_escalation_blocked'
            ).exists()
        )

    def test_staff_flags_cannot_be_changed_via_profile_api(self):
        response = self.patch_me({'is_staff': True, 'is_superuser': True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(username='taken', password=PASSWORD)
        response = self.patch_me({'username': 'TAKEN'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_changing_email_resets_verification(self):
        UserProfile.objects.filter(user=self.user).update(
            email_verified=True, email_verified_at=timezone.now()
        )
        mail.outbox.clear()

        response = self.patch_me({'email': 'ada@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data['email_changed'])
        self.assertTrue(response.data['verification_email_sent'])
        self.assertEqual(len(mail.outbox), 1)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'ada@example.com')
        self.user.profile.refresh_from_db()
        self.assertFalse(self.user.profile.email_verified)
        self.assertIsNone(self.user.profile.email_verified_at)


# ─── Sessions: refresh + logout ─────────────────────────────────────────────


class SessionTests(AuthAPITestCase):
    def setUp(self):
        super().setUp()
        self.register_response = self.signed_in()
        self.raw_refresh = self.cookie_value(self.register_response)

    def test_refresh_requires_the_csrf_header(self):
        response = self.client.post('/api/auth/token/refresh/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_refresh_requires_the_cookie(self):
        # Drop the cookie issued at registration: nothing left to rotate.
        self.client.cookies.clear()
        response = self.refresh()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_rotates_the_cookie_and_never_leaks_it(self):
        response = self.refresh()
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)

        rotated = self.cookie_value(response)
        self.assertTrue(rotated)
        self.assertNotEqual(rotated, self.raw_refresh)

    def test_rotated_token_is_blacklisted(self):
        self.refresh()
        # Replay the pre-rotation token: rotation blacklists it.
        self.client.cookies[REFRESH_COOKIE] = self.raw_refresh
        response = self.refresh()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_requires_the_csrf_header(self):
        response = self.client.post('/api/auth/logout/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_revokes_the_refresh_token(self):
        response = self.logout()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(REFRESH_COOKIE, response.cookies)
        self.assertEqual(response.cookies[REFRESH_COOKIE].value, '')

        self.client.cookies[REFRESH_COOKIE] = self.raw_refresh
        response = self.refresh()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_csrf_endpoint_returns_the_cookie_value(self):
        response = self.client.get('/api/auth/csrf/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['csrfToken']
        self.assertTrue(token)
        self.assertEqual(token, response.cookies[settings.CSRF_COOKIE_NAME].value)


# ─── Email verification ─────────────────────────────────────────────────────


class EmailVerificationTests(AuthAPITestCase):
    def setUp(self):
        super().setUp()
        self.register_response = self.signed_in()
        self.raw_token = extract_token(mail.outbox[0], VERIFY_PATH)

    def verify(self, token):
        return self.client.post(
            '/api/auth/verify-email/', {'token': token}, format='json'
        )

    def test_verifies_a_valid_token(self):
        response = self.verify(self.raw_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data['user']['email_verified'])

        user = User.objects.get(username='tlearner')
        self.assertTrue(user.profile.email_verified)
        self.assertIsNotNone(user.profile.email_verified_at)
        self.assertTrue(
            AuthenticationAuditLog.objects.filter(event='email_verified').exists()
        )

    def test_token_cannot_be_reused(self):
        first = self.verify(self.raw_token)
        self.assertEqual(first.status_code, status.HTTP_200_OK, first.data)
        verified_at = User.objects.get(username='tlearner').profile.email_verified_at

        second = self.verify(self.raw_token)
        # The token is spent: the second call reports the current state instead of
        # verifying again, so a refresh or duplicate submit is not an error.
        self.assertEqual(second.status_code, status.HTTP_200_OK, second.data)
        self.assertEqual(second.data['code'], 'already_verified')
        self.assertEqual(
            User.objects.get(username='tlearner').profile.email_verified_at,
            verified_at,
        )
        self.assertEqual(
            AuthenticationAuditLog.objects.filter(event='email_verified').count(), 1
        )

    def test_expired_token_is_rejected(self):
        record = EmailVerificationToken.objects.get()
        record.expires_at = timezone.now() - timedelta(minutes=1)
        record.save(update_fields=['expires_at'])

        response = self.verify(self.raw_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'token_expired')
        self.assertFalse(User.objects.get(username='tlearner').profile.email_verified)

    def test_unknown_token_is_rejected(self):
        response = self.verify('definitely-not-a-real-token')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'token_invalid')

    def test_resend_for_signed_in_user_issues_a_new_token(self):
        self.use_access(self.register_response.data['access'])
        response = self.client.post(
            '/api/auth/resend-verification/', {}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)

        # The first token is invalidated when a new one is issued.
        stale = self.verify(self.raw_token)
        self.assertEqual(stale.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(stale.data['code'], 'token_used')

        fresh = extract_token(mail.outbox[1], VERIFY_PATH)
        self.assertNotEqual(fresh, self.raw_token)
        self.assertEqual(self.verify(fresh).status_code, status.HTTP_200_OK)

    def test_resend_for_unknown_address_is_generic_and_sends_nothing(self):
        self.client.credentials()
        response = self.client.post(
            '/api/auth/resend-verification/',
            {'email': 'ghost@example.com'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)


# ─── Password reset + change ────────────────────────────────────────────────


class PasswordResetTests(AuthAPITestCase):
    def setUp(self):
        super().setUp()
        self.register_response = self.signed_in()
        self.raw_refresh = self.cookie_value(self.register_response)
        mail.outbox.clear()

    def request_reset(self, email='tlearner@example.com'):
        return self.client.post(
            '/api/auth/password-reset/', {'email': email}, format='json'
        )

    def confirm_reset(self, token, password=NEW_PASSWORD):
        return self.client.post(
            '/api/auth/password-reset/confirm/',
            {
                'token': token,
                'password': password,
                'confirm_password': password,
            },
            format='json',
        )

    def test_request_is_generic_for_known_and_unknown_addresses(self):
        known = self.request_reset()
        unknown = self.request_reset('ghost@example.com')
        self.assertEqual(known.status_code, status.HTTP_200_OK)
        self.assertEqual(unknown.status_code, status.HTTP_200_OK)
        self.assertEqual(str(known.data['detail']), str(unknown.data['detail']))
        self.assertEqual(len(mail.outbox), 1)

    def test_request_emails_a_single_use_token(self):
        self.request_reset()
        self.assertEqual(len(mail.outbox), 1)
        raw_token = extract_token(mail.outbox[0], RESET_PATH)
        self.assertTrue(raw_token)

        record = PasswordResetToken.objects.get()
        self.assertEqual(record.token_hash, hash_auth_token(raw_token))
        self.assertNotEqual(record.token_hash, raw_token)
        self.assertTrue(record.is_usable)

    def test_confirmation_changes_the_password_and_revokes_sessions(self):
        self.request_reset()
        raw_token = extract_token(mail.outbox[0], RESET_PATH)

        response = self.confirm_reset(raw_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        user = User.objects.get(username='tlearner')
        self.assertTrue(user.check_password(NEW_PASSWORD))
        self.assertFalse(user.check_password(PASSWORD))
        self.assertTrue(
            AuthenticationAuditLog.objects.filter(
                event='password_reset_completed'
            ).exists()
        )

        # The pre-reset refresh token is blacklisted.
        self.client.cookies[REFRESH_COOKIE] = self.raw_refresh
        self.assertEqual(
            self.refresh().status_code, status.HTTP_401_UNAUTHORIZED
        )

        self.assertEqual(self.sign_in('tlearner', PASSWORD).status_code, 401)
        self.assertEqual(
            self.sign_in('tlearner', NEW_PASSWORD).status_code, 200
        )

    def test_token_cannot_be_reused(self):
        self.request_reset()
        raw_token = extract_token(mail.outbox[0], RESET_PATH)
        self.confirm_reset(raw_token)

        response = self.confirm_reset(raw_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'token_used')

    def test_expired_token_is_rejected(self):
        self.request_reset()
        raw_token = extract_token(mail.outbox[0], RESET_PATH)
        record = PasswordResetToken.objects.get()
        record.expires_at = timezone.now() - timedelta(minutes=1)
        record.save(update_fields=['expires_at'])

        response = self.confirm_reset(raw_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'token_expired')
        self.assertTrue(User.objects.get(username='tlearner').check_password(PASSWORD))

    def test_weak_new_password_is_rejected(self):
        self.request_reset()
        raw_token = extract_token(mail.outbox[0], RESET_PATH)

        response = self.confirm_reset(raw_token, password='12345678')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertTrue(User.objects.get(username='tlearner').check_password(PASSWORD))


class ChangePasswordTests(AuthAPITestCase):
    def setUp(self):
        super().setUp()
        self.register_response = self.signed_in()
        self.raw_refresh = self.cookie_value(self.register_response)
        self.use_access(self.register_response.data['access'])

    def change(self, current, new=NEW_PASSWORD, confirm=None):
        return self.client.post(
            '/api/auth/change-password/',
            {
                'current_password': current,
                'new_password': new,
                'confirm_password': new if confirm is None else confirm,
            },
            format='json',
        )

    def test_requires_the_current_password(self):
        response = self.change('Wrong-Password-9!')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('current_password', response.data)
        self.assertTrue(User.objects.get(username='tlearner').check_password(PASSWORD))

    def test_rejects_password_mismatch(self):
        response = self.change(PASSWORD, confirm=NEW_PASSWORD + 'x')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

    def test_changes_password_and_starts_a_new_session(self):
        response = self.change(PASSWORD)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn('access', response.data)
        self.assertTrue(response.data['expires_in'] > 0)

        user = User.objects.get(username='tlearner')
        self.assertTrue(user.check_password(NEW_PASSWORD))
        self.assertTrue(
            AuthenticationAuditLog.objects.filter(event='password_changed').exists()
        )

        # Old refresh token is revoked; the response carries a fresh one.
        self.client.cookies[REFRESH_COOKIE] = self.raw_refresh
        self.assertEqual(self.refresh().status_code, 401)


# ─── RBAC ───────────────────────────────────────────────────────────────────


class RBACTests(AuthAPITestCase):
    def setUp(self):
        super().setUp()
        track = CareerTrack.objects.create(
            slug='python', title='Python', description='Python track'
        )
        self.course = Course.objects.create(
            slug='python-101', title='Python 101', description='Intro',
            track=track, difficulty='beginner', language='python',
            is_published=True, is_active=True,
        )

    def test_role_groups_exist_with_baseline_permissions(self):
        self.assertTrue(Group.objects.filter(name=STUDENT_GROUP).exists())
        self.assertTrue(Group.objects.filter(name=INSTRUCTOR_GROUP).exists())
        self.assertTrue(Group.objects.filter(name=ADMIN_GROUP).exists())

        students = Group.objects.get(name=STUDENT_GROUP)
        self.assertTrue(students.permissions.filter(codename='view_course').exists())
        self.assertFalse(students.permissions.filter(codename='add_course').exists())

        instructors = Group.objects.get(name=INSTRUCTOR_GROUP)
        self.assertTrue(instructors.permissions.filter(codename='add_course').exists())

    def test_role_resolution_prefers_privileged_sources(self):
        student = User.objects.create_user(username='s1', password=PASSWORD)
        self.assertEqual(user_role(student), 'student')

        mentor = User.objects.create_user(username='m1', password=PASSWORD)
        UserProfile.objects.create(user=mentor, role='mentor')
        self.assertEqual(user_role(mentor), 'instructor')

        grouped = User.objects.create_user(username='i1', password=PASSWORD)
        grouped.groups.add(Group.objects.get(name=INSTRUCTOR_GROUP))
        self.assertEqual(user_role(grouped), 'instructor')

        staff = User.objects.create_user(
            username='a1', password=PASSWORD, is_staff=True
        )
        self.assertEqual(user_role(staff), 'administrator')

    def test_new_accounts_are_students_not_administrators(self):
        response = self.signed_in()
        self.assertEqual(response.data['user']['role'], 'student')

        user = User.objects.get(username='tlearner')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.has_perm('learning.add_course'))

    def test_unverified_students_are_blocked_when_verification_is_required(self):
        user = User.objects.create_user(
            username='unverified', email='unverified@example.com', password=PASSWORD
        )
        self.client.force_authenticate(user=user)

        with override_settings(AUTH_REQUIRE_EMAIL_VERIFICATION=True):
            response = self.client.post(f'/api/courses/{self.course.slug}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            Enrollment.objects.filter(user=user, course=self.course).exists()
        )

    def test_verified_students_can_enroll_when_verification_is_required(self):
        user = User.objects.create_user(
            username='verified', email='verified@example.com', password=PASSWORD
        )
        UserProfile.objects.create(user=user, email_verified=True)
        self.client.force_authenticate(user=user)

        with override_settings(AUTH_REQUIRE_EMAIL_VERIFICATION=True):
            response = self.client.post(f'/api/courses/{self.course.slug}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(
            Enrollment.objects.filter(user=user, course=self.course).exists()
        )

    def test_verification_gate_is_off_by_default(self):
        user = User.objects.create_user(
            username='defaultgate', email='gate@example.com', password=PASSWORD
        )
        self.client.force_authenticate(user=user)
        response = self.client.post(f'/api/courses/{self.course.slug}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# ─── Throttling ─────────────────────────────────────────────────────────────


class ThrottleTests(AuthAPITestCase):
    def test_login_is_rate_limited(self):
        from unittest import mock
        from rest_framework.throttling import SimpleRateThrottle

        User.objects.create_user(username='throttled', password=PASSWORD)

        # Freeze the throttle's clock: the 10/min window ages entries by wall
        # time, so on a loaded machine the eleven requests could straddle the
        # 60s duration and drop history early. A fixed timer makes the count
        # exact while still exercising the real cache-backed counter.
        frozen = {'now': 1_700_000_000.0}
        with mock.patch.object(
            SimpleRateThrottle, 'timer', classmethod(lambda cls: frozen['now'])
        ):
            statuses = []
            for _ in range(11):
                statuses.append(
                    self.sign_in('throttled', 'Wrong-Password-9!').status_code
                )

        self.assertEqual(statuses[:10], [status.HTTP_401_UNAUTHORIZED] * 10)
        self.assertEqual(statuses[10], status.HTTP_429_TOO_MANY_REQUESTS)

    def test_password_reset_is_rate_limited(self):
        statuses = []
        for _ in range(6):
            statuses.append(
                self.client.post(
                    '/api/auth/password-reset/',
                    {'email': 'ghost@example.com'},
                    format='json',
                ).status_code
            )

        self.assertEqual(statuses[:5], [status.HTTP_200_OK] * 5)
        self.assertEqual(statuses[5], status.HTTP_429_TOO_MANY_REQUESTS)


# ─── Storage hygiene ────────────────────────────────────────────────────────


class TokenHygieneTests(AuthAPITestCase):
    def test_no_plaintext_credentials_are_persisted(self):
        self.signed_in()
        raw_token = extract_token(mail.outbox[0], VERIFY_PATH)

        user = User.objects.get(username='tlearner')
        self.assertNotIn(PASSWORD, user.password)

        record = EmailVerificationToken.objects.get()
        self.assertNotIn(raw_token, record.token_hash)

        for event in AuthenticationAuditLog.objects.all():
            payload = ' '.join([
                event.identifier,
                str(event.metadata),
                event.user_agent,
            ])
            self.assertNotIn(PASSWORD, payload)
            self.assertNotIn(raw_token, payload)

    def test_access_token_is_required_for_me_endpoint(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)


# ─── Repeating a verification link ──────────────────────────────────────────


class VerificationIdempotencyTests(AuthAPITestCase):
    """A second submission of an already-consumed link must not look like a
    failure: refreshes and duplicate submits land on the success screen."""

    def setUp(self):
        super().setUp()
        self.signed_in()
        self.raw_token = extract_token(mail.outbox[0], VERIFY_PATH)

    def verify(self):
        return self.client.post(
            '/api/auth/verify-email/', {'token': self.raw_token}, format='json'
        )

    def test_repeating_a_verified_link_reports_already_verified(self):
        self.assertEqual(self.verify().status_code, status.HTTP_200_OK)

        again = self.verify()
        self.assertEqual(again.status_code, status.HTTP_200_OK, again.data)
        self.assertEqual(again.data['code'], 'already_verified')
        self.assertEqual(again.data['user']['email'], 'tlearner@example.com')

    def test_a_used_link_for_an_unverified_account_is_still_rejected(self):
        # Resending invalidates the older token without verifying anything, so
        # that token must keep answering "already used" rather than success.
        self.client.post(
            '/api/auth/resend-verification/',
            {'email': 'tlearner@example.com'},
            format='json',
        )

        response = self.verify()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'token_used')


# ─── Enforced verification: sign-in gate ────────────────────────────────────


@override_settings(AUTH_REQUIRE_EMAIL_VERIFICATION=True)
class EnforcedVerificationTests(AuthAPITestCase):
    """With the gate on, an unverified account gets no session and no sign-in."""

    def setUp(self):
        super().setUp()
        self.registration = self.register()
        self.raw_token = extract_token(mail.outbox[0], VERIFY_PATH)

    def test_registration_withholds_the_session(self):
        self.assertEqual(
            self.registration.status_code, status.HTTP_201_CREATED,
            self.registration.data,
        )
        self.assertNotIn('access', self.registration.data)
        self.assertNotIn(REFRESH_COOKIE, self.registration.cookies)
        self.assertTrue(self.registration.data['verification_email_sent'])

    def test_unverified_sign_in_is_refused_with_a_resend_hint(self):
        response = self.sign_in('tlearner@example.com')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)
        self.assertEqual(response.data['code'], 'email_not_verified')
        self.assertEqual(response.data['email'], 'tlearner@example.com')
        self.assertTrue(response.data['can_resend'])
        self.assertNotIn('access', response.data)
        self.assertNotIn(REFRESH_COOKIE, response.cookies)

    def test_a_wrong_password_still_looks_like_a_wrong_password(self):
        response = self.sign_in('tlearner@example.com', 'Not-The-Password-1!')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('code', response.data)

    def test_verifying_then_signing_in_succeeds(self):
        verified = self.client.post(
            '/api/auth/verify-email/', {'token': self.raw_token}, format='json'
        )
        self.assertEqual(verified.status_code, status.HTTP_200_OK, verified.data)

        response = self.sign_in('tlearner@example.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn('access', response.data)

    def test_staff_bypass_the_gate(self):
        User.objects.filter(username='tlearner').update(is_staff=True)

        response = self.sign_in('tlearner@example.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)


# ─── mail_check diagnostic ──────────────────────────────────────────────────


class MailCheckCommandTests(TestCase):
    """The diagnostic must describe the transport, never a fake success."""

    def run_check(self, *args):
        output = StringIO()
        call_command('mail_check', *args, stdout=output)
        return output.getvalue()

    def test_reports_the_transport_and_the_verification_gate(self):
        output = self.run_check()

        self.assertIn('Backend', output)
        self.assertIn(settings.MAILERS['default']['BACKEND'], output)
        self.assertIn('Verification required', output)

    @override_settings(
        MAILERS={
            'default': {
                'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
                'OPTIONS': {
                    'host': 'smtp.example.com',
                    'port': 587,
                    'username': 'sender@example.com',
                    'password': '',
                },
            },
        }
    )
    def test_refuses_to_send_without_an_smtp_password(self):
        with self.assertRaises(CommandError) as caught:
            self.run_check('someone@example.com')

        self.assertIn('password', str(caught.exception))
        self.assertEqual(len(mail.outbox), 0)


# ─── Delivery honesty ───────────────────────────────────────────────────────


@override_settings(
    MAILERS={
        'default': {
            'BACKEND': 'django.core.mail.backends.console.EmailBackend',
        },
    }
)
class RenderOnlyBackendTests(AuthAPITestCase):
    """A transport that only prints must never be reported as delivered.

    This is the failure that makes an email outage invisible: the console
    backend returns "1 message sent" because nothing raised, so a naive
    implementation records success while no mail ever leaves the machine.
    """

    def send(self, **kwargs):
        """Run a request with the console backend's stdout noise swallowed."""
        with patch.object(sys, 'stdout', new_callable=StringIO):
            return self.register(**kwargs)

    def test_registration_reports_that_no_mail_left_the_server(self):
        response = self.send()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertIs(response.data['verification_email_sent'], False)
        # The locmem outbox stays empty because nothing was captured: the
        # message went to a terminal, not to a mail server.
        self.assertEqual(len(mail.outbox), 0)

        event = AuthenticationAuditLog.objects.filter(
            event=AuthenticationAuditLog.Event.EMAIL_VERIFICATION_SENT
        ).latest('id')
        self.assertIs(event.metadata['delivered'], False)

    def test_resend_reports_the_delivery_failure_to_the_account_owner(self):
        signed = self.send()
        self.use_access(signed.data['access'])

        with patch.object(sys, 'stdout', new_callable=StringIO):
            response = self.client.post(
                '/api/auth/resend-verification/', {}, format='json'
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIs(response.data['verification_email_sent'], False)

    def test_anonymous_resend_admits_that_no_mail_can_leave(self):
        """The sign-in button resends anonymously.

        It can never be handed `verification_email_sent` — that would make the
        endpoint an account oracle — so without a transport-level answer it can
        only ever report success, which is how a console-backend server kept
        telling the screen "a link is on its way" while printing it locally.
        """
        self.signed_in()

        with patch.object(sys, 'stdout', new_callable=StringIO):
            response = self.client.post(
                '/api/auth/resend-verification/',
                {'email': 'tlearner@example.com'},
                format='json',
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIs(response.data['email_delivery_enabled'], False)
        self.assertNotIn('verification_email_sent', response.data)


class ResendDeliveryReportingTests(AuthAPITestCase):
    """Who is told what, without turning the endpoint into an oracle."""

    def test_the_account_owner_is_told_whether_the_mail_was_delivered(self):
        signed = self.signed_in()
        self.use_access(signed.data['access'])

        response = self.client.post(
            '/api/auth/resend-verification/', {}, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIs(response.data['verification_email_sent'], True)
        self.assertIs(response.data['email_delivery_enabled'], True)
        self.assertEqual(len(mail.outbox), 2)

    def test_anonymous_callers_never_receive_the_delivery_flag(self):
        self.signed_in()
        mail.outbox.clear()

        response = self.client.post(
            '/api/auth/resend-verification/',
            {'email': 'tlearner@example.com'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertNotIn('verification_email_sent', response.data)

        # An unknown address gets the byte-identical answer, so the response
        # cannot be used to probe which emails are registered.
        unknown = self.client.post(
            '/api/auth/resend-verification/',
            {'email': 'nobody-else@example.com'},
            format='json',
        )
        self.assertEqual(unknown.status_code, status.HTTP_200_OK)
        self.assertEqual(unknown.data, response.data)


class MailTransportReadinessTests(AuthAPITestCase):
    """`mail_transport_ready()` describes the deployment, never the account."""

    def test_render_only_transports_are_not_ready(self):
        for backend, options in (
            ('django.core.mail.backends.console.EmailBackend', {}),
            ('django.core.mail.backends.dummy.EmailBackend', {}),
            ('django.core.mail.backends.filebased.EmailBackend',
             {'file_path': 'test-rendered-emails'}),
        ):
            with self.subTest(backend=backend), override_settings(
                MAILERS={'default': {'BACKEND': backend, 'OPTIONS': options}}
            ):
                self.assertFalse(mail_transport_ready())

    def test_smtp_without_a_login_is_not_ready(self):
        with override_settings(MAILERS={'default': {
            'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'OPTIONS': {'host': 'localhost', 'port': 587},
        }}):
            self.assertFalse(mail_transport_ready())

    def test_smtp_with_a_login_is_ready(self):
        with override_settings(MAILERS={'default': {
            'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'OPTIONS': {'host': 'localhost', 'port': 587,
                        'username': 'sender@example.com', 'password': 'secret'},
        }}):
            self.assertTrue(mail_transport_ready())

    def test_the_test_transport_counts_as_ready(self):
        # locmem captures messages for assertions instead of printing them, so
        # the suite must not read its own sends as failures.
        self.assertTrue(mail_transport_ready())
