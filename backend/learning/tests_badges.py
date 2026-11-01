"""Tests for the badge system, notifications, avatar, preferences & public profile.

These cover the work introduced by the "Badge System, Profile & Achievement
Upgrade" plan:

- ``seed_badges`` is idempotent (no duplicate slugs) and materializes the whole
  registry.
- The award engine grants every registered condition type from *real* activity
  rows, never double-awards, and only writes a notification for a real unlock.
- Progress toward locked badges is derived from the same rows, never stored.
- The avatar endpoint accepts genuine images and rejects non-images and
  oversize payloads; removal resets to the initials default.
- Notification preference toggles persist server-side and reject bad values.
- The public profile honors the owner's privacy flags and never leaks email.
- An account-deletion request is recorded, not executed, and needs auth.
"""

import io

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from . import badge_registry
from .models import (
    Achievement, CareerTrack, Challenge, ChallengeSubmission, Chapter, Course,
    Enrollment, Exercise, ExerciseAttempt, Lesson, LessonProgress,
    UserAchievement, UserNotification, UserProfile,
)
from .services.achievements import award_eligible_achievements, measure_progress


def make_learner(username='badge-learner'):
    user = User.objects.create_user(
        username=username, email=f'{username}@example.com', password='pw12345',
    )
    UserProfile.objects.get_or_create(user=user)
    return user


def make_course(slug='py-101'):
    track = CareerTrack.objects.create(slug=f'{slug}-track', title='T', description='d')
    course = Course.objects.create(
        slug=slug, title='Course', description='', track=track,
        language='python', is_published=True,
    )
    chapter = Chapter.objects.create(course=course, title='Ch', slug=f'{slug}-ch', order=1)
    lesson = Lesson.objects.create(chapter=chapter, title='L', slug=f'{slug}-l', order=1)
    exercise = Exercise.objects.create(
        lesson=lesson, title='Ex', slug=f'{slug}-ex', exercise_type='code',
        instructions='hi', starter_code='#\n', solution_code='print(1)',
        language='python', xp_reward=10,
    )
    return {'track': track, 'course': course, 'chapter': chapter,
            'lesson': lesson, 'exercise': exercise}


def make_achievement(slug, **overrides):
    fields = dict(
        title=slug.replace('-', ' ').capitalize(), description='desc',
        icon='star', category='special', difficulty='beginner', xp_bonus=0,
        condition_type='first_activity', condition_value='', how_to_earn='do it',
        is_active=True,
    )
    fields.update(overrides)
    return Achievement.objects.create(slug=slug, **fields)


# ─── Registry & seeding ───────────────────────────────────────────────────────

class BadgeRegistrySeedTest(TestCase):
    def test_seed_is_idempotent(self):
        call_command('seed_badges')
        first_count = Achievement.objects.count()
        self.assertEqual(first_count, len(badge_registry.BADGES))
        # Re-running must not create duplicates.
        call_command('seed_badges')
        self.assertEqual(Achievement.objects.count(), first_count)
        slugs = list(Achievement.objects.values_list('slug', flat=True))
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_every_registry_badge_has_required_fields(self):
        for badge in badge_registry.BADGES:
            self.assertIn(badge['difficulty'], {'beginner', 'intermediate', 'advanced'})
            self.assertTrue(badge['how_to_earn'])
            self.assertTrue(badge['slug'])


# ─── Award engine ─────────────────────────────────────────────────────────────

class AwardEngineTest(TestCase):
    def setUp(self):
        self.user = make_learner()
        self.profile = self.user.profile
        self.ctx = make_course()

    def _complete_lesson(self):
        return LessonProgress.objects.create(
            user=self.user, lesson=self.ctx['lesson'], status='completed',
        )

    def test_lesson_complete_awards_once(self):
        make_achievement('first-lesson', condition_type='lesson_complete', condition_value='1')
        self._complete_lesson()
        newly = award_eligible_achievements(self.user)
        self.assertTrue(any(a.achievement.slug == 'first-lesson' for a in newly))
        # Calling again must not duplicate.
        award_eligible_achievements(self.user)
        self.assertEqual(
            UserAchievement.objects.filter(user=self.user, achievement__slug='first-lesson').count(),
            1,
        )

    def test_no_award_without_activity(self):
        make_achievement('first-lesson', condition_type='lesson_complete', condition_value='1')
        newly = award_eligible_achievements(self.user)
        self.assertFalse(any(a.achievement.slug == 'first-lesson' for a in newly))
        self.assertFalse(UserAchievement.objects.filter(user=self.user).exists())

    def test_exercise_correct_count(self):
        make_achievement('first-commit', condition_type='exercise_correct_count', condition_value='1')
        ExerciseAttempt.objects.create(user=self.user, exercise=self.ctx['exercise'], status='correct')
        newly = award_eligible_achievements(self.user)
        self.assertTrue(any(a.achievement.slug == 'first-commit' for a in newly))

    def test_challenge_count_and_topic(self):
        make_achievement('challenge-initiate', condition_type='challenge_count', condition_value='1')
        make_achievement('dsa-explorer', condition_type='challenge_topic_count', condition_value='dsa:2')
        challenge = Challenge.objects.create(
            slug='two-sum', title='Two Sum', description='d', topic='DSA', difficulty='beginner',
        )
        ChallengeSubmission.objects.create(user=self.user, challenge=challenge, status='correct')
        newly = {a.achievement.slug for a in award_eligible_achievements(self.user)}
        self.assertIn('challenge-initiate', newly)
        self.assertNotIn('dsa-explorer', newly)  # only 1 of 2 required dsa solved

    def test_streak_n(self):
        make_achievement('streak-3', condition_type='streak_n', condition_value='3')
        self.profile.streak_days = 3
        self.profile.save(update_fields=['streak_days'])
        newly = {a.achievement.slug for a in award_eligible_achievements(self.user)}
        self.assertIn('streak-3', newly)

    def test_account_and_first_activity(self):
        make_achievement('community-member', condition_type='account')
        make_achievement('first-activity', condition_type='first_activity')
        # No activity yet: only the account badge is eligible.
        newly = {a.achievement.slug for a in award_eligible_achievements(self.user)}
        self.assertIn('community-member', newly)
        self.assertNotIn('first-activity', newly)
        # A lesson unlocks first-activity on the next pass.
        self._complete_lesson()
        newly2 = {a.achievement.slug for a in award_eligible_achievements(self.user)}
        self.assertIn('first-activity', newly2)

    def test_notification_created_on_unlock(self):
        make_achievement('first-lesson', condition_type='lesson_complete', condition_value='1')
        self._complete_lesson()
        award_eligible_achievements(self.user)
        notif = UserNotification.objects.filter(user=self.user, type='badge_unlock')
        self.assertTrue(notif.exists())
        self.assertIn('first-lesson', notif.first().link)

    def test_notification_muted_by_preference(self):
        self.profile.notification_preferences = {'achievements': False}
        self.profile.save(update_fields=['notification_preferences'])
        make_achievement('first-lesson', condition_type='lesson_complete', condition_value='1')
        self._complete_lesson()
        newly = award_eligible_achievements(self.user)
        self.assertTrue(any(a.achievement.slug == 'first-lesson' for a in newly))
        self.assertFalse(UserNotification.objects.filter(user=self.user).exists())

    def test_measure_progress_reflects_real_rows(self):
        achievement = make_achievement('knowledge-seeker', condition_type='lesson_complete', condition_value='25')
        for i in range(3):
            lesson = Lesson.objects.create(
                chapter=self.ctx['chapter'], title=f'L{i}', slug=f'extra-l{i}', order=i + 10,
            )
            LessonProgress.objects.create(user=self.user, lesson=lesson, status='completed')
        current, target = measure_progress(self.user, achievement)
        self.assertEqual((current, target), (3, 25))


# ─── Achievement API ──────────────────────────────────────────────────────────

class AchievementAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_learner('api-learner')
        make_achievement('first-lesson', condition_type='lesson_complete',
                         condition_value='1', difficulty='beginner')

    def test_list_includes_difficulty_and_progress(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get('/api/achievements/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        row = next(r for r in res.data['results'] if r['slug'] == 'first-lesson')
        self.assertEqual(row['difficulty'], 'beginner')
        self.assertEqual(row['difficulty_label'], 'Beginner')
        self.assertTrue(row['how_to_earn'])
        self.assertIn('progress', row)
        self.assertEqual(set(row['progress'].keys()), {'current', 'target', 'complete'})

    def test_progress_null_for_anonymous(self):
        res = self.client.get('/api/achievements/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        row = next(r for r in res.data['results'] if r['slug'] == 'first-lesson')
        self.assertIsNone(row['progress'])


# ─── Notification API ─────────────────────────────────────────────────────────

class NotificationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_learner('notif-learner')
        self.client.force_authenticate(user=self.user)
        UserNotification.objects.create(
            user=self.user, type='badge_unlock', title='Unlocked', body='b', link='/achievements',
        )

    def test_list_reports_unread_count(self):
        res = self.client.get('/api/notifications/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['unread_count'], 1)
        self.assertEqual(len(res.data['results']), 1)
        self.assertTrue(res.data['results'][0]['unread'])

    def test_mark_single_read(self):
        n = UserNotification.objects.get(user=self.user)
        res = self.client.post(f'/api/notifications/{n.id}/read/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        n.refresh_from_db()
        self.assertIsNotNone(n.read_at)

    def test_mark_all_read(self):
        UserNotification.objects.create(user=self.user, type='xp_milestone', title='xp')
        res = self.client.post('/api/notifications/read-all/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['marked_read'], 2)
        self.assertEqual(UserNotification.objects.filter(user=self.user, read_at__isnull=True).count(), 0)

    def test_requires_auth(self):
        self.client.force_authenticate(user=None)
        res = self.client.get('/api/notifications/')
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


# ─── Avatar upload ────────────────────────────────────────────────────────────

def _image_bytes(fmt, size=(64, 64)):
    buf = io.BytesIO()
    Image.new('RGB', size, (120, 30, 90)).save(buf, format=fmt)
    return buf.getvalue()


class AvatarAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_learner('avatar-learner')
        self.client.force_authenticate(user=self.user)

    def test_valid_upload(self):
        for fmt, name, mime in (('JPEG', 'a.jpg', 'image/jpeg'), ('PNG', 'a.png', 'image/png')):
            upload = SimpleUploadedFile(name, _image_bytes(fmt), content_type=mime)
            res = self.client.post('/api/profile/avatar/', {'file': upload}, format='multipart')
            self.assertEqual(res.status_code, status.HTTP_200_OK, res.content)
            self.assertTrue(res.data['avatar'])
            self.user.profile.refresh_from_db()
            self.assertTrue(self.user.profile.avatar)

    def test_non_image_rejected(self):
        upload = SimpleUploadedFile('evil.png', b'not actually an image', content_type='image/png')
        res = self.client.post('/api/profile/avatar/', {'file': upload}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_oversize_rejected(self):
        big = b'\x00' * (5 * 1024 * 1024 + 10)
        upload = SimpleUploadedFile('big.jpg', big, content_type='image/jpeg')
        res = self.client.post('/api/profile/avatar/', {'file': upload}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_resets(self):
        upload = SimpleUploadedFile('a.jpg', _image_bytes('JPEG'), content_type='image/jpeg')
        self.client.post('/api/profile/avatar/', {'file': upload}, format='multipart')
        res = self.client.delete('/api/profile/avatar/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['avatar'], '')
        self.user.profile.refresh_from_db()
        self.assertFalse(bool(self.user.profile.avatar))


# ─── Preferences ──────────────────────────────────────────────────────────────

class PreferencesAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_learner('pref-learner')
        self.client.force_authenticate(user=self.user)

    def test_persist_valid_toggle(self):
        res = self.client.patch('/api/profile/preferences/', {'achievements': False}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertFalse(self.user.profile.get_notification_preference('achievements'))

    def test_rejects_non_boolean(self):
        res = self.client.patch('/api/profile/preferences/', {'community': 'maybe'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


# ─── Public profile & privacy ─────────────────────────────────────────────────

class PublicProfileAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = make_learner('public-owner')
        self.profile = self.owner.profile
        self.achievement = make_achievement('first-lesson', condition_type='lesson_complete', condition_value='1')
        UserAchievement.objects.create(user=self.owner, achievement=self.achievement)

    def test_public_profile_has_no_email(self):
        res = self.client.get('/api/users/public-owner/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'public-owner')
        self.assertNotIn('email', res.data)
        self.assertEqual(len(res.data['badges']), 1)

    def test_show_badges_off_hides_badges(self):
        self.profile.show_badges = False
        self.profile.save(update_fields=['show_badges'])
        res = self.client.get('/api/users/public-owner/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['badges'], [])

    def test_private_profile_is_404(self):
        self.profile.is_profile_public = False
        self.profile.save(update_fields=['is_profile_public'])
        res = self.client.get('/api/users/public-owner/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_unknown_user_is_404(self):
        res = self.client.get('/api/users/does-not-exist/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


# ─── Account deletion request ─────────────────────────────────────────────────

class AccountDeletionRequestTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_learner('deleter')

    def test_requires_auth(self):
        res = self.client.post('/api/account/deletion-request/')
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_records_not_executes(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post('/api/account/deletion-request/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertIsNotNone(self.user.profile.deletion_requested_at)
        # The account itself is untouched — deletion stays an admin action.
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
