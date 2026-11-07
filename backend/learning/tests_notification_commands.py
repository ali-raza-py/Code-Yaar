"""Tests for the send_reminders and send_digest management commands.

These commands run outside the request cycle, so their tests call them through
``call_command``. Email is checked through the locmem outbox and the
:class:`~learning.models.NotificationEmailLog` ledger, exactly as production
code observes it.
"""

from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from .models import (
    Competition,
    CompetitionRegistration,
    NotificationEmailLog,
    UserNotification,
    UserProfile,
)

NOW = timezone.now()


def make_competition(**overrides):
    """A published, free, individual competition opening now-ish."""
    organizer = overrides.pop('organizer', None) or User.objects.create_user(
        f"organizer-{overrides.get('slug', 'comp')}",
        'organizer@example.com', 'Organizer-2026!',
    )
    defaults = {
        'organizer': organizer,
        'title': overrides.get('title', 'Code Sprint'),
        'slug': overrides.get('slug', 'code-sprint'),
        'short_description': 'A sprint.',
        'description': 'Describe the sprint here.',
        'category': 'Hackathon',
        'registration_start': NOW - timedelta(days=3),
        'registration_deadline': NOW + timedelta(hours=48),
        'competition_start': NOW + timedelta(days=5),
        'competition_end': NOW + timedelta(days=7),
        'submission_deadline': NOW + timedelta(days=8),
        'is_published': True,
    }
    defaults.update(overrides)
    return Competition.objects.create(**defaults)


def make_learner(username):
    user = User.objects.create_user(username, f'{username}@example.com', 'Learner-2026!')
    UserProfile.objects.create(user=user, email_verified=True)
    return user


def run_reminders(now=NOW):
    call_command('send_reminders', '--now', now.isoformat(), stdout=StringIO())


def run_digest(frequency='daily', now=NOW):
    call_command(
        'send_digest', '--frequency', frequency,
        '--now', now.isoformat(),
        stdout=StringIO(),
    )


def dedupe(kind, competition, user):
    return f'reminder:{kind}:{competition.pk}:{user.pk}'


# ─── send_reminders ───────────────────────────────────────────────────────────


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class RegistrationClosingSoonTests(TestCase):
    def setUp(self):
        mail.outbox.clear()

    def make_world(self, hours_left=48):
        competition = make_competition(
            registration_deadline=NOW + timedelta(hours=hours_left),
            competition_start=NOW + timedelta(days=20),
        )
        learner = make_learner('closing-learner')
        return competition, learner

    def test_notifies_unregistered_verified_learners(self):
        competition, learner = self.make_world()
        run_reminders()
        self.assertTrue(
            UserNotification.objects.filter(
                user=learner,
                type='competition_reminder',
                dedupe_key=dedupe('registration-close', competition, learner),
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_replay_sends_one_email_for_one_event(self):
        competition, learner = self.make_world()
        run_reminders()
        run_reminders()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            UserNotification.objects.filter(user=learner).count(), 1,
        )

    def test_respects_in_app_mute(self):
        competition, learner = self.make_world()
        learner.profile.notification_preferences = {'competitions': False}
        learner.profile.save(update_fields=['notification_preferences'])
        run_reminders()
        self.assertFalse(UserNotification.objects.filter(user=learner).exists())
        # Email preference still on: an opted-out in-app feed must not silence
        # opt-in competition email, so the reminder mail still goes out.
        self.assertEqual(len(mail.outbox), 1)

    def test_respects_email_mute(self):
        competition, learner = self.make_world()
        learner.profile.notification_preferences = {'email_competitions': False}
        learner.profile.save(update_fields=['notification_preferences'])
        run_reminders()
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(
            UserNotification.objects.filter(user=learner).exists()
        )

    def test_outside_window_is_silent(self):
        competition, learner = self.make_world(hours_left=70)
        run_reminders()
        self.assertFalse(UserNotification.objects.filter(user=learner).exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_past_deadline_is_silent(self):
        competition, learner = self.make_world(hours_left=-2)
        run_reminders()
        self.assertFalse(UserNotification.objects.filter(user=learner).exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_unpublished_or_archived_are_silent(self):
        learner = make_learner('closing-learner')
        for kwargs in ({'is_published': False}, {'is_archived': True}):
            competition = make_competition(**kwargs)
            run_reminders()
            self.assertFalse(
                UserNotification.objects.filter(
                    dedupe_key=dedupe('registration-close', competition, learner),
                ).exists()
            )

    def test_unverified_learners_get_no_registration_blast(self):
        learner = make_learner('closing-learner')
        learner.profile.email_verified = False
        learner.profile.save(update_fields=['email_verified'])
        competition = make_competition()
        run_reminders()
        self.assertFalse(
            UserNotification.objects.exists()
            and UserNotification.objects.filter(user=learner).exists()
        )


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class StartSoonTests(TestCase):
    def setUp(self):
        mail.outbox.clear()

    def make_world(self, hours_to_start=24, **overrides):
        competition = make_competition(
            competition_start=NOW + timedelta(hours=hours_to_start),
            registration_deadline=NOW + timedelta(days=2),
            registration_start=NOW - timedelta(days=10),
            **overrides,
        )
        learner = make_learner('starting-learner')
        CompetitionRegistration.objects.create(
            competition=competition, user=learner,
            registration_status='approved', rules_accepted_at=NOW,
        )
        return competition, learner

    def test_notifies_active_registrants(self):
        competition, learner = self.make_world()
        run_reminders()
        self.assertTrue(
            UserNotification.objects.filter(
                user=learner,
                dedupe_key=dedupe('start-soon', competition, learner),
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_skips_waitlisted_withdrawn_rejected_disqualified(self):
        learner_a = make_learner('starting-waitlist')
        learner_b = make_learner('starting-withdrawn')
        learner_c = make_learner('starting-rejected')
        learner_d = make_learner('starting-disq')
        competition = make_competition(
            competition_start=NOW + timedelta(hours=20),
            registration_deadline=NOW + timedelta(days=2),
            registration_start=NOW - timedelta(days=10),
        )
        for learner, status in (
            (learner_a, 'waitlisted'), (learner_b, 'withdrawn'),
            (learner_c, 'rejected'), (learner_d, 'disqualified'),
        ):
            CompetitionRegistration.objects.create(
                competition=competition, user=learner,
                registration_status=status, rules_accepted_at=NOW,
            )
        run_reminders()
        self.assertFalse(UserNotification.objects.filter(user__in=[learner_a, learner_b, learner_c, learner_d]).exists())

    def test_outside_window_is_silent(self):
        competition, learner = self.make_world(hours_to_start=30)
        run_reminders()
        self.assertFalse(UserNotification.objects.filter(user=learner).exists())


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SubmissionDeadlineTests(TestCase):
    def setUp(self):
        mail.outbox.clear()

    def make_world(self, hours_left=24, **overrides):
        competition = make_competition(
            competition_start=NOW - timedelta(days=1),
            submission_deadline=NOW + timedelta(hours=hours_left),
            competition_end=NOW + timedelta(days=5),
            registration_deadline=NOW - timedelta(hours=10),
            registration_start=NOW - timedelta(days=10),
            **overrides,
        )
        learner = make_learner('submitting-learner')
        CompetitionRegistration.objects.create(
            competition=competition, user=learner,
            registration_status='approved', rules_accepted_at=NOW,
        )
        return competition, learner

    def test_notifies_active_registrants(self):
        competition, learner = self.make_world()
        run_reminders()
        self.assertTrue(
            UserNotification.objects.filter(
                user=learner,
                dedupe_key=dedupe('submission-deadline', competition, learner),
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_soupn_notifies_before_competition_starts(self):
        competition, learner = self.make_world()
        CompetitionRegistration.objects.all().delete()
        CompetitionRegistration.objects.create(
            competition=competition, user=learner,
            registration_status='registered', rules_accepted_at=NOW,
        )
        early = make_competition(
            slug='early-contest',
            submission_deadline=NOW + timedelta(hours=10),
            competition_start=NOW + timedelta(days=3),
            competition_end=NOW + timedelta(days=9),
        )
        run_reminders()
        self.assertFalse(
            UserNotification.objects.filter(
                user=learner,
                dedupe_key=dedupe('submission-deadline', early, learner),
            ).exists()
        )


# ─── send_digest ──────────────────────────────────────────────────────────────


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class DigestTests(TestCase):
    def setUp(self):
        mail.outbox.clear()

    def enable_digest(self, user, frequency='daily'):
        user.profile.notification_preferences = {'email_digest': frequency}
        user.profile.save(update_fields=['notification_preferences'])

    def make_notification(self, user, **overrides):
        defaults = {
            'user': user,
            'type': 'challenge_solved',
            'title': 'Solved a challenge',
            'body': 'First solve!',
            'link': '/challenges',
        }
        defaults.update(overrides)
        return UserNotification.objects.create(**defaults)

    def test_daily_digest_sent_to_selected_users(self):
        learner = make_learner('digest-daily')
        self.enable_digest(learner, 'daily')
        self.make_notification(learner)
        run_digest('daily')
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertIn('daily digest', message.subject)
        self.assertIn('Solved a challenge', message.body)

    def test_digest_respects_frequency_choice(self):
        learner = make_learner('digest-weekly')
        self.enable_digest(learner, 'weekly')
        self.make_notification(learner)
        run_digest('daily')
        self.assertEqual(len(mail.outbox), 0)
        run_digest('weekly')
        self.assertEqual(len(mail.outbox), 1)

    def test_digest_is_idempotent_per_day(self):
        learner = make_learner('digest-once')
        self.enable_digest(learner, 'daily')
        self.make_notification(learner)
        run_digest('daily')
        run_digest('daily')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            NotificationEmailLog.objects.filter(
                user=learner,
                email_key__startswith='digest:daily',
            ).count(),
            1,
        )

    def test_digest_excludes_individually_emailed_notifications(self):
        learner = make_learner('digest-picky')
        self.enable_digest(learner, 'daily')
        emailed = self.make_notification(learner, type='certificate_issued')
        NotificationEmailLog.objects.create(
            user=learner,
            notification=emailed,
            email_key='cert:X',
            kind='certificate',
            subject='Your certificate',
            status=NotificationEmailLog.Status.SENT,
        )
        self.make_notification(learner, type='challenge_solved')
        run_digest('daily')
        self.assertEqual(len(mail.outbox), 1)
        self.assertNotIn('certificate', mail.outbox[0].body)
        self.assertIn('Solved a challenge', mail.outbox[0].body)

    def test_no_notifications_no_email(self):
        learner = make_learner('digest-quiet')
        self.enable_digest(learner, 'daily')
        run_digest('daily')
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(NotificationEmailLog.objects.exists())

    def test_default_digest_is_off(self):
        learner = make_learner('digest-default')
        self.make_notification(learner)
        run_digest('daily')
        self.assertEqual(len(mail.outbox), 0)
