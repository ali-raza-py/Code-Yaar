"""
Backend tests for the learning platform (spec §45).

Tests cover:
- User registration and authentication
- Course enrollment
- Lesson progress tracking
- Exercise submission (code, MCQ, output prediction)
- Duplicate submission handling
- XP awarding and penalties
- Permission checks
- Course/chapter completion flow
- Hint system
- Language adapter
- Sandbox service
- Real subprocess sandbox (Python executed, C++ compiled and run)
- Textbook source references and the official-content verification guard
"""

from datetime import timedelta
from unittest import skipUnless

from django.test import TestCase, Client, override_settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from .models import (
    UserProfile, CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Enrollment, LessonProgress, ExerciseAttempt, XPTransaction,
    Achievement, UserAchievement,
    PracticalClass, PracticalSubject, Practical, PracticalProgress,
    PracticalBookmark, LearningActivity,
)
from .services.language_adapter import (
    get_adapter, get_supported_languages, PythonAdapter, JavaScriptAdapter,
)
from .services.sandbox import (
    DevelopmentSandbox, SubprocessSandbox, validate_submission, SandboxConfig,
)
from .services.xp import award_xp, deduct_xp
from .services.progress import record_learning_activity


# ─── Model Tests ─────────────────────────────────────────────────────────────

class CourseModelTest(TestCase):
    def setUp(self):
        self.track = CareerTrack.objects.create(
            slug='python', title='Python', description='Python track',
        )
        self.course = Course.objects.create(
            slug='python-101', title='Python 101', description='Intro',
            track=self.track, difficulty='beginner', language='python',
            is_published=True,
        )
        self.chapter = Chapter.objects.create(
            course=self.course, title='Basics', slug='basics', order=1,
        )
        self.lesson = Lesson.objects.create(
            chapter=self.chapter, title='Hello', slug='hello',
            content_type='text', order=1, xp_reward=50,
        )

    def test_course_str(self):
        self.assertEqual(str(self.course), 'Python 101')

    def test_chapter_str(self):
        self.assertEqual(str(self.chapter), 'Python 101 > Basics')

    def test_lesson_str(self):
        self.assertIn('Hello', str(self.lesson))

    def test_chapter_count(self):
        self.assertEqual(self.course.chapter_count, 1)

    def test_lesson_count(self):
        self.assertEqual(self.course.lesson_count, 1)


class ExerciseModelTest(TestCase):
    def setUp(self):
        self.track = CareerTrack.objects.create(slug='py', title='Py', description='Py')
        self.course = Course.objects.create(
            slug='c1', title='C1', description='', track=self.track,
            language='python', is_published=True,
        )
        self.chapter = Chapter.objects.create(
            course=self.course, title='Ch1', slug='ch1', order=1,
        )
        self.lesson = Lesson.objects.create(
            chapter=self.chapter, title='L1', slug='l1', order=1,
        )
        self.exercise = Exercise.objects.create(
            lesson=self.lesson, title='Ex1', slug='ex1',
            exercise_type='code', instructions='Write hello world',
            starter_code='# code\n', solution_code='print("hello")',
            language='python', xp_reward=100,
        )

    def test_exercise_str(self):
        self.assertIn('Ex1', str(self.exercise))

    def test_exercise_type(self):
        self.assertEqual(self.exercise.exercise_type, 'code')


class PracticalsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='practical-reader', password='pass123')
        UserProfile.objects.create(user=self.user)
        self.school_class, _ = PracticalClass.objects.get_or_create(
            slug='class-9',
            defaults={
                'title': 'Class 9',
                'description': 'Foundation practicals',
                'board': 'stb',
            },
        )
        self.subject = PracticalSubject.objects.create(
            practical_class=self.school_class, slug='science', title='Science'
        )
        self.practical = Practical.objects.create(
            practical_class=self.school_class,
            subject=self.subject,
            slug='separation-of-mixtures',
            title='Separation of Mixtures',
            practical_number=1,
            aim='Study separation methods.',
            is_published=True,
        )

    def test_published_practical_catalog_and_detail(self):
        classes = self.client.get('/api/practical-classes/')
        self.assertEqual(classes.status_code, status.HTTP_200_OK)
        self.assertEqual(classes.data['count'], 4)
        self.assertEqual(classes.data['results'][0]['board'], 'stb')
        self.assertEqual(classes.data['results'][0]['subject_count'], 1)

        subjects = self.client.get('/api/practical-subjects/?class=class-9')
        self.assertEqual(subjects.status_code, status.HTTP_200_OK)
        self.assertEqual(subjects.data['results'][0]['practical_count'], 1)

        practicals = self.client.get('/api/practicals/?class=class-9&subject=science')
        self.assertEqual(practicals.status_code, status.HTTP_200_OK)
        self.assertEqual(practicals.data['results'][0]['title'], 'Separation of Mixtures')

        detail = self.client.get('/api/practicals/separation-of-mixtures/')
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data['aim'], 'Study separation methods.')

    def test_unpublished_practical_is_hidden(self):
        self.practical.is_published = False
        self.practical.save(update_fields=['is_published'])
        response = self.client.get('/api/practicals/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_completion_and_bookmark_require_authentication(self):
        complete = self.client.post(f'/api/practicals/{self.practical.slug}/complete/')
        self.assertEqual(complete.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user)
        complete = self.client.post(f'/api/practicals/{self.practical.slug}/complete/')
        self.assertEqual(complete.status_code, status.HTTP_200_OK)
        self.assertTrue(PracticalProgress.objects.filter(
            user=self.user, practical=self.practical, completed_at__isnull=False
        ).exists())

        bookmark = self.client.post(f'/api/practicals/{self.practical.slug}/bookmark/')
        self.assertEqual(bookmark.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PracticalBookmark.objects.filter(
            user=self.user, practical=self.practical
        ).exists())

        self.client.delete(f'/api/practicals/{self.practical.slug}/bookmark/')
        self.assertFalse(PracticalBookmark.objects.filter(
            user=self.user, practical=self.practical
        ).exists())

    def test_management_endpoints_are_admin_only(self):
        response = self.client.post('/api/admin/practical-classes/', {
            'title': 'Student Attempt',
            'slug': 'student-attempt',
            'board': 'stb',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        admin = User.objects.create_user(username='content-admin', password='pass123')
        UserProfile.objects.create(user=admin, role='admin')
        self.client.force_authenticate(user=admin)

        response = self.client.patch(
            f'/api/admin/practical-classes/{self.school_class.id}/',
            {'is_published': False},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_published'])

        response = self.client.post('/api/admin/practical-subjects/', {
            'practical_class': self.school_class.id,
            'title': 'Physics',
            'slug': 'physics',
            'description': 'STB Physics',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        subject = PracticalSubject.objects.get(slug='physics')

        response = self.client.post('/api/admin/practicals/', {
            'practical_class': self.school_class.id,
            'subject': subject.id,
            'slug': 'admin-created-practical',
            'title': 'Admin-created practical',
            'practical_number': 2,
            'is_published': False,
            'diagrams': [],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        practical = Practical.objects.get(slug='admin-created-practical')
        self.assertFalse(practical.is_published)

        response = self.client.patch(
            f'/api/admin/practicals/{practical.id}/',
            {'is_published': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_published'])

        response = self.client.delete(f'/api/admin/practicals/{practical.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ProgressDashboardAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='progress-reader', password='pass123')
        UserProfile.objects.create(user=self.user)
        track = CareerTrack.objects.create(
            slug='progress-track', title='Progress Track', description='Track'
        )
        self.course = Course.objects.create(
            slug='progress-course', title='Progress Course', description='Course',
            track=track, language='python', is_published=True,
        )
        chapter = Chapter.objects.create(
            course=self.course, title='Module', slug='module', order=1,
        )
        self.lesson = Lesson.objects.create(
            chapter=chapter, title='Lesson', slug='lesson', order=1,
        )

    def test_new_student_has_zero_progress(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/progress/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['overview']['overall_percentage'], 0)
        self.assertEqual(response.data['overview']['lessons_completed'], 0)
        self.assertEqual(response.data['overview']['current_streak'], 0)

    def test_course_and_lesson_progress_are_server_derived(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        LessonProgress.objects.create(
            user=self.user, lesson=self.lesson, status='completed',
        )
        LearningActivity.objects.create(
            user=self.user, activity_type='lesson_completed',
            title='Completed Lesson', course=self.course, lesson=self.lesson,
            activity_date=timezone.localdate(),
            dedupe_key=f'{self.user.pk}:lesson_completed:{self.lesson.pk}:test',
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/progress/')
        self.assertEqual(response.data['overview']['overall_percentage'], 100)
        self.assertEqual(response.data['courses'][0]['completed_lessons'], 1)
        self.assertEqual(response.data['courses'][0]['remaining_lessons'], 0)
        self.assertEqual(len(response.data['activities']), 1)

    def test_progress_endpoint_is_private(self):
        response = self.client.get('/api/progress/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_streak_uses_distinct_local_activity_days(self):
        today = timezone.localdate()
        for offset in range(3):
            activity_date = today - timedelta(days=offset)
            LearningActivity.objects.create(
                user=self.user, activity_type='lesson_completed',
                title='Lesson', course=self.course, lesson=self.lesson,
                activity_date=activity_date,
                dedupe_key=f'{self.user.pk}:lesson:{offset}',
            )
        first, created = record_learning_activity(
            self.user, 'lesson_completed', 'Lesson',
            course=self.course, lesson=self.lesson,
        )
        second, duplicate = record_learning_activity(
            self.user, 'lesson_completed', 'Lesson',
            course=self.course, lesson=self.lesson,
        )
        self.assertTrue(created)
        self.assertFalse(duplicate)
        self.assertEqual(first.pk, second.pk)
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/progress/')
        self.assertEqual(response.data['overview']['current_streak'], 3)
        self.assertEqual(response.data['overview']['longest_streak'], 3)


# ─── Enrollment Tests ────────────────────────────────────────────────────────

# Exercises and enrollment run behind the verified-email gate in production;
# these suites test the flows themselves (the gate has dedicated coverage in
# tests_auth.py), so they run with the requirement lifted — same convention
# as tests_auth.AuthAPITestCase.
@override_settings(AUTH_REQUIRE_EMAIL_VERIFICATION=False)
class EnrollmentAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        UserProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

        self.track = CareerTrack.objects.create(slug='py', title='Py', description='Py')
        self.course = Course.objects.create(
            slug='python-101', title='Python 101', description='Intro',
            track=self.track, language='python', is_published=True, is_active=True,
        )

    def test_enroll_in_course(self):
        response = self.client.post(f'/api/courses/{self.course.slug}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(user=self.user, course=self.course).exists())

    def test_duplicate_enrollment(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        response = self.client.post(f'/api/courses/{self.course.slug}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Enrollment.objects.filter(user=self.user, course=self.course).count(), 1)

    def test_unauthenticated_enrollment_fails(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f'/api/courses/{self.course.slug}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_enrollment_progress(self):
        enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        chapter = Chapter.objects.create(course=self.course, title='Ch1', slug='ch1', order=1)
        l1 = Lesson.objects.create(chapter=chapter, title='L1', slug='l1', order=1)
        l2 = Lesson.objects.create(chapter=chapter, title='L2', slug='l2', order=2)
        LessonProgress.objects.create(user=self.user, lesson=l1, status='completed')
        self.assertEqual(enrollment.progress_percentage, 50)


# ─── Lesson Completion Tests ─────────────────────────────────────────────────

class LessonCompletionAPITest(TestCase):
    """
    `POST /api/lessons/<pk>/complete/` resolves the lesson by `pk`, while the
    course-scoped reading URL resolves it by `slug`. Both lookups go through
    `LessonViewSet.get_object`, so both need coverage.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='reader', password='pass123')
        UserProfile.objects.create(user=self.user, xp_points=0)
        self.client.force_authenticate(user=self.user)

        self.track = CareerTrack.objects.create(slug='py', title='Py', description='Py')
        self.course = Course.objects.create(
            slug='py-101', title='Py 101', description='', track=self.track,
            language='python', is_published=True, is_active=True,
        )
        self.chapter = Chapter.objects.create(
            course=self.course, title='Ch1', slug='ch1', order=1,
        )
        self.lesson = Lesson.objects.create(
            chapter=self.chapter, title='Reading', slug='reading', order=1,
            xp_reward=50,
        )

    def test_complete_exercise_free_lesson_by_pk(self):
        response = self.client.post(f'/api/lessons/{self.lesson.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
        self.assertEqual(response.data['xp_awarded'], 50)
        self.assertEqual(response.data['exercises_remaining'], 0)

    def test_completion_records_progress_and_enrollment(self):
        self.client.post(f'/api/lessons/{self.lesson.id}/complete/')

        progress = LessonProgress.objects.get(user=self.user, lesson=self.lesson)
        self.assertEqual(progress.status, 'completed')
        self.assertIsNotNone(progress.completed_at)

        enrollment = Enrollment.objects.get(user=self.user, course=self.course)
        self.assertEqual(enrollment.last_lesson, self.lesson)

    def test_completing_twice_awards_xp_once(self):
        first = self.client.post(f'/api/lessons/{self.lesson.id}/complete/')
        second = self.client.post(f'/api/lessons/{self.lesson.id}/complete/')
        self.assertEqual(first.data['xp_awarded'], 50)
        self.assertEqual(second.data['xp_awarded'], 0)
        self.assertEqual(
            XPTransaction.objects.filter(user=self.user, action='lesson_complete').count(), 1
        )
        self.assertEqual(UserProfile.objects.get(user=self.user).xp_points, 50)

    def test_first_lesson_badge_and_bonus_are_awarded_once(self):
        badge = Achievement.objects.create(
            slug='first-lesson-test', title='First Steps',
            description='Complete one lesson.', icon='trophy', category='course',
            xp_bonus=25, condition_type='lesson_complete', condition_value='1',
        )

        first = self.client.post(f'/api/lessons/{self.lesson.id}/complete/')
        second = self.client.post(f'/api/lessons/{self.lesson.id}/complete/')

        self.assertEqual(first.data['xp_awarded'], 50)
        self.assertEqual(second.data['xp_awarded'], 0)
        earned = UserAchievement.objects.get(user=self.user, achievement=badge)
        self.assertTrue(earned.credential_id.startswith('CY-BDG-'))
        self.assertTrue(earned.public_id)
        self.assertEqual(
            XPTransaction.objects.filter(
                user=self.user, action='achievement_bonus', object_id=badge.id,
            ).count(),
            1,
        )
        self.assertEqual(UserProfile.objects.get(user=self.user).xp_points, 75)

    def test_lesson_with_unsolved_exercises_stays_in_progress(self):
        Exercise.objects.create(
            lesson=self.lesson, title='Ex1', slug='ex1', exercise_type='code',
            instructions='Print hi', starter_code='', solution_code='print("hi")',
            language='python', xp_reward=100,
        )
        response = self.client.post(f'/api/lessons/{self.lesson.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertEqual(response.data['exercises_remaining'], 1)
        self.assertEqual(response.data['xp_awarded'], 0)

    def test_slug_based_lesson_retrieve_still_works(self):
        response = self.client.get(
            f'/api/courses/{self.course.slug}/lessons/{self.lesson.slug}/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['slug'], self.lesson.slug)

    def test_completion_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f'/api/lessons/{self.lesson.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ExerciseActionPermissionTest(TestCase):
    """
    `/exercises/<pk>/run/` and `/submit/` are registered with explicit
    `as_view` mappings, so their auth requirements come from
    `ExerciseViewSet.action_permissions` rather than the `@action` decorator.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='runner', password='pass123')
        UserProfile.objects.create(user=self.user)

        self.track = CareerTrack.objects.create(slug='py', title='Py', description='Py')
        self.course = Course.objects.create(
            slug='py-101', title='Py 101', description='', track=self.track,
            language='python', is_published=True, is_active=True,
        )
        self.chapter = Chapter.objects.create(
            course=self.course, title='Ch1', slug='ch1', order=1,
        )
        self.lesson = Lesson.objects.create(
            chapter=self.chapter, title='L1', slug='l1', order=1,
        )
        self.exercise = Exercise.objects.create(
            lesson=self.lesson, title='Ex1', slug='ex1', exercise_type='code',
            instructions='Print hi', starter_code='', solution_code='print("hi")',
            language='python', xp_reward=100,
        )

    def test_run_requires_authentication(self):
        response = self.client.post(
            f'/api/exercises/{self.exercise.id}/run/',
            {'code': 'print(1)'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_submit_requires_authentication(self):
        response = self.client.post(
            f'/api/exercises/{self.exercise.id}/submit/',
            {'code': 'print("hi")'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_hint_stays_public(self):
        response = self.client.get(f'/api/exercises/{self.exercise.id}/hint/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# ─── Exercise Submission Tests ───────────────────────────────────────────────

@override_settings(AUTH_REQUIRE_EMAIL_VERIFICATION=False)
class ExerciseSubmissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='learner', password='pass123')
        UserProfile.objects.create(user=self.user, xp_points=0)
        self.client.force_authenticate(user=self.user)

        self.track = CareerTrack.objects.create(slug='py', title='Py', description='Py')
        self.course = Course.objects.create(
            slug='c1', title='C1', description='', track=self.track,
            language='python', is_published=True, is_active=True,
        )
        Enrollment.objects.create(user=self.user, course=self.course)
        self.chapter = Chapter.objects.create(course=self.course, title='Ch1', slug='ch1', order=1)
        self.lesson = Lesson.objects.create(chapter=self.chapter, title='L1', slug='l1', order=1, xp_reward=50)
        self.exercise = Exercise.objects.create(
            lesson=self.lesson, title='MCQ Test', slug='mcq-test',
            exercise_type='multiple_choice', instructions='Pick one',
            choices=[
                {'id': 'a', 'text': 'Wrong', 'is_correct': False},
                {'id': 'b', 'text': 'Right', 'is_correct': True},
                {'id': 'c', 'text': 'Wrong', 'is_correct': False},
            ],
            xp_reward=100,
        )

    def test_correct_mcq_submission(self):
        response = self.client.post(
            f'/api/exercises/{self.exercise.id}/submit/',
            {'selected_answer': 'b', 'time_spent_seconds': 30},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'correct')
        self.assertGreater(response.data['xp_earned'], 0)

    def test_incorrect_mcq_submission(self):
        response = self.client.post(
            f'/api/exercises/{self.exercise.id}/submit/',
            {'selected_answer': 'a', 'time_spent_seconds': 30},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'incorrect')
        self.assertEqual(response.data['xp_earned'], 0)

    def test_xp_awarded_on_correct(self):
        self.client.post(
            f'/api/exercises/{self.exercise.id}/submit/',
            {'selected_answer': 'b', 'time_spent_seconds': 10},
            format='json',
        )
        profile = UserProfile.objects.get(user=self.user)
        self.assertGreater(profile.xp_points, 0)

    def test_xp_transaction_created(self):
        self.client.post(
            f'/api/exercises/{self.exercise.id}/submit/',
            {'selected_answer': 'b', 'time_spent_seconds': 10},
            format='json',
        )
        self.assertTrue(
            XPTransaction.objects.filter(user=self.user, action='exercise_complete').exists()
        )

    def test_attempt_recorded(self):
        self.client.post(
            f'/api/exercises/{self.exercise.id}/submit/',
            {'selected_answer': 'b', 'time_spent_seconds': 10},
            format='json',
        )
        self.assertEqual(ExerciseAttempt.objects.filter(user=self.user, exercise=self.exercise).count(), 1)

    def test_multiple_attempts_tracked(self):
        self.client.post(
            f'/api/exercises/{self.exercise.id}/submit/',
            {'selected_answer': 'a', 'time_spent_seconds': 10},
            format='json',
        )
        self.client.post(
            f'/api/exercises/{self.exercise.id}/submit/',
            {'selected_answer': 'b', 'time_spent_seconds': 20},
            format='json',
        )
        attempts = ExerciseAttempt.objects.filter(user=self.user, exercise=self.exercise)
        self.assertEqual(attempts.count(), 2)


# ─── Hint System Tests ───────────────────────────────────────────────────────

class HintSystemTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='hintuser', password='pass123')
        UserProfile.objects.create(user=self.user, xp_points=500)
        self.client.force_authenticate(user=self.user)

        self.track = CareerTrack.objects.create(slug='py', title='Py', description='Py')
        self.course = Course.objects.create(
            slug='c1', title='C1', description='', track=self.track,
            language='python', is_published=True, is_active=True,
        )
        self.chapter = Chapter.objects.create(course=self.course, title='Ch1', slug='ch1', order=1)
        self.lesson = Lesson.objects.create(chapter=self.chapter, title='L1', slug='l1', order=1)
        self.exercise = Exercise.objects.create(
            lesson=self.lesson, title='HintEx', slug='hint-ex',
            exercise_type='code', instructions='Do something',
            xp_reward=100,
        )
        Hint.objects.create(exercise=self.exercise, content='Hint 1', order=1, xp_penalty=10)
        Hint.objects.create(exercise=self.exercise, content='Hint 2', order=2, xp_penalty=20)
        Hint.objects.create(
            exercise=self.exercise, content='Solution', order=3,
            reveals_solution=True, xp_penalty=50,
        )

    def test_repeated_hint_request_deducts_xp_only_once(self):
        first = self.client.get(f'/api/exercises/{self.exercise.id}/hint/')
        second = self.client.get(f'/api/exercises/{self.exercise.id}/hint/')

        self.assertEqual(first.data['xp_penalty'], 10)
        self.assertEqual(second.data['xp_penalty'], 10)
        self.assertEqual(UserProfile.objects.get(user=self.user).xp_points, 490)
        self.assertEqual(XPTransaction.objects.filter(user=self.user, action='hint_used').count(), 1)

    def test_get_hint(self):
        response = self.client.get(f'/api/exercises/{self.exercise.id}/hint/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('hint', response.data)

    def test_hint_deducts_xp(self):
        initial_xp = UserProfile.objects.get(user=self.user).xp_points
        self.client.get(f'/api/exercises/{self.exercise.id}/hint/')
        updated_xp = UserProfile.objects.get(user=self.user).xp_points
        self.assertLess(updated_xp, initial_xp)

    def test_repeated_hint_request_deducts_xp_only_once(self):
        first = self.client.get(f'/api/exercises/{self.exercise.id}/hint/')
        second = self.client.get(f'/api/exercises/{self.exercise.id}/hint/')

        self.assertEqual(first.data['xp_penalty'], 10)
        self.assertEqual(second.data['xp_penalty'], 10)
        self.assertEqual(UserProfile.objects.get(user=self.user).xp_points, 490)
        self.assertEqual(XPTransaction.objects.filter(user=self.user, action='hint_used').count(), 1)


class XPServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='xpuser', password='pass123')
        self.track = CareerTrack.objects.create(slug='xp', title='XP', description='XP')
        self.course = Course.objects.create(
            slug='xp-course', title='XP Course', description='', track=self.track,
        )
        self.chapter = Chapter.objects.create(course=self.course, title='Chapter', slug='chapter')
        self.lesson = Lesson.objects.create(
            chapter=self.chapter, title='Lesson', slug='lesson', xp_reward=650,
        )

    def test_award_xp_updates_balance_level_and_is_idempotent(self):
        first = award_xp(self.user, 650, 'lesson_complete', obj=self.lesson)
        duplicate = award_xp(self.user, 650, 'lesson_complete', obj=self.lesson)

        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(first.amount, 650)
        self.assertIsNone(duplicate)
        self.assertEqual(profile.xp_points, 650)
        self.assertEqual(profile.level, 2)

    def test_deduction_is_capped_at_balance_and_updates_level(self):
        award_xp(self.user, 650, 'lesson_complete', obj=self.lesson)
        transaction = deduct_xp(self.user, 900, 'hint_used', obj=self.lesson)

        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(transaction.amount, -650)
        self.assertEqual(profile.xp_points, 0)
        self.assertEqual(profile.level, 1)

    def test_same_hint_penalty_is_deducted_once(self):
        hint = Hint.objects.create(
            exercise=self.lesson.exercises.create(
                title='Exercise', slug='exercise', exercise_type='code',
                instructions='Solve it.', solution_code='pass',
            ),
            content='Hint', order=1, xp_penalty=10,
        )
        award_xp(self.user, 100, 'lesson_complete', obj=self.lesson)

        first = deduct_xp(self.user, 10, 'hint_used', obj=hint)
        duplicate = deduct_xp(self.user, 10, 'hint_used', obj=hint)

        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(first.amount, -10)
        self.assertIsNone(duplicate)
        self.assertEqual(profile.xp_points, 90)


class ProfileAchievementsAPITest(TestCase):
    def test_profile_returns_earned_and_locked_badges(self):
        user = User.objects.create_user(username='badges', password='pass123')
        UserProfile.objects.create(user=user)
        earned = Achievement.objects.create(
            slug='earned-test', title='First Steps', description='A completed milestone.',
            icon='trophy', category='course', condition_type='lesson_complete',
        )
        locked = Achievement.objects.create(
            slug='locked-test', title='Week Warrior', description='Learn for seven days.',
            icon='fire', category='streak', condition_type='streak_7',
        )
        UserAchievement.objects.create(user=user, achievement=earned)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/api/profile/stats/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        badges = {badge['id']: badge for badge in response.data['achievements']}
        self.assertTrue(badges[earned.id]['earned'])
        self.assertIsNotNone(badges[earned.id]['earned_at'])
        self.assertFalse(badges[locked.id]['earned'])
        self.assertIsNone(badges[locked.id]['earned_at'])


# ─── Language Adapter Tests ──────────────────────────────────────────────────

class LanguageAdapterTest(TestCase):
    def test_python_adapter_exists(self):
        adapter = get_adapter('python')
        self.assertIsInstance(adapter, PythonAdapter)
        self.assertEqual(adapter.language_code, 'python')

    def test_javascript_adapter_exists(self):
        adapter = get_adapter('javascript')
        self.assertIsInstance(adapter, JavaScriptAdapter)

    def test_unsupported_language_raises(self):
        with self.assertRaises(ValueError):
            get_adapter('ruby')

    def test_supported_languages(self):
        langs = get_supported_languages()
        self.assertIn('python', langs)
        self.assertIn('javascript', langs)
        self.assertIn('cpp', langs)

    def test_python_error_formatting(self):
        adapter = PythonAdapter()
        formatted = adapter.format_error('NameError: name x is not defined')
        self.assertIn('hasn\'t been defined', formatted)


# ─── Sandbox Service Tests ───────────────────────────────────────────────────

class SandboxServiceTest(TestCase):
    def test_development_sandbox_health(self):
        sandbox = DevelopmentSandbox()
        self.assertTrue(sandbox.health_check())

    def test_development_sandbox_execute(self):
        sandbox = DevelopmentSandbox()
        result = sandbox.execute('print("hello")', 'python')
        self.assertEqual(result.status, 'success')

    def test_empty_code_returns_error(self):
        sandbox = DevelopmentSandbox()
        result = sandbox.execute('', 'python')
        self.assertEqual(result.status, 'error')

    def test_validate_mcq_correct(self):
        track = CareerTrack.objects.create(slug='py', title='Py', description='Py')
        course = Course.objects.create(
            slug='c1', title='C1', description='', track=track, language='python',
        )
        chapter = Chapter.objects.create(course=course, title='Ch1', slug='ch1', order=1)
        lesson = Lesson.objects.create(chapter=chapter, title='L1', slug='l1', order=1)
        exercise = Exercise.objects.create(
            lesson=lesson, title='MCQ', slug='mcq',
            exercise_type='multiple_choice', instructions='Pick',
            choices=[
                {'id': 'a', 'text': 'Wrong', 'is_correct': False},
                {'id': 'b', 'text': 'Right', 'is_correct': True},
            ],
            xp_reward=100,
        )
        result = validate_submission(exercise, None, selected_answer='b')
        self.assertTrue(result.all_passed)
        self.assertEqual(result.xp_earned, 100)

    def test_validate_mcq_incorrect(self):
        track = CareerTrack.objects.create(slug='py2', title='Py2', description='Py')
        course = Course.objects.create(
            slug='c2', title='C2', description='', track=track, language='python',
        )
        chapter = Chapter.objects.create(course=course, title='Ch1', slug='ch1b', order=1)
        lesson = Lesson.objects.create(chapter=chapter, title='L1', slug='l1b', order=1)
        exercise = Exercise.objects.create(
            lesson=lesson, title='MCQ2', slug='mcq2',
            exercise_type='multiple_choice', instructions='Pick',
            choices=[
                {'id': 'a', 'text': 'Wrong', 'is_correct': False},
                {'id': 'b', 'text': 'Right', 'is_correct': True},
            ],
            xp_reward=100,
        )
        result = validate_submission(exercise, None, selected_answer='a')
        self.assertFalse(result.all_passed)
        self.assertEqual(result.xp_earned, 0)

    def _make_exercise(self, slug, **kwargs):
        track = CareerTrack.objects.create(slug=f't{slug}', title='T', description='T')
        course = Course.objects.create(
            slug=f'c{slug}', title='C', description='', track=track, language='python',
        )
        chapter = Chapter.objects.create(course=course, title='Ch', slug=f'ch{slug}', order=1)
        lesson = Lesson.objects.create(chapter=chapter, title='L', slug=f'l{slug}', order=1)
        defaults = dict(lesson=lesson, title='Ex', slug=slug, instructions='Do it')
        defaults.update(kwargs)
        return Exercise.objects.create(**defaults)

    def test_code_exercise_is_honest_pending_not_fake_pass(self):
        """Code exercises must never report a pass without a real evaluator."""
        exercise = self._make_exercise(
            'code1', exercise_type='code', language='python',
            starter_code='# start', test_cases=[], xp_reward=100,
        )
        result = validate_submission(exercise, 'print("done")')
        self.assertEqual(result.status, 'pending')
        self.assertFalse(result.all_passed)
        self.assertEqual(result.xp_earned, 0)

    def test_debugging_validated_against_solution(self):
        """Debugging/fill-blank are graded for real via solution comparison."""
        exercise = self._make_exercise(
            'dbg1', exercise_type='debugging', language='python',
            starter_code='print(nums[5])  # fix',
            solution_code='nums = [10, 20, 30, 40, 50]\nprint(nums[4])',
            xp_reward=100,
        )
        correct = validate_submission(exercise, 'nums = [10, 20, 30, 40, 50]\nprint(nums[4])  # fixed')
        self.assertEqual(correct.status, 'correct')
        self.assertEqual(correct.xp_earned, 100)

        wrong = validate_submission(exercise, 'nums = [10, 20, 30, 40, 50]\nprint(nums[3])')
        self.assertEqual(wrong.status, 'incorrect')
        self.assertEqual(wrong.xp_earned, 0)

    def test_output_prediction_status_flag(self):
        exercise = self._make_exercise(
            'op1', exercise_type='output_prediction', expected_output='0\n2\n4', xp_reward=75,
        )
        result = validate_submission(exercise, None, selected_answer='0\n2\n4')
        self.assertEqual(result.status, 'correct')
        self.assertEqual(result.xp_earned, 75)


# ─── Course API Tests ────────────────────────────────────────────────────────

class CourseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.track = CareerTrack.objects.create(slug='py', title='Python', description='Python track')
        self.course = Course.objects.create(
            slug='python-foundations', title='Python Foundations',
            description='Learn Python', track=self.track,
            difficulty='beginner', language='python',
            is_published=True, is_active=True,
        )
        self.chapter = Chapter.objects.create(
            course=self.course, title='Basics', slug='basics', order=1,
        )
        self.lesson = Lesson.objects.create(
            chapter=self.chapter, title='Hello', slug='hello', order=1,
            content_type='text', content_body='# Hello\nWorld',
        )

    def test_list_courses(self):
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_course(self):
        response = self.client.get(f'/api/courses/{self.course.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Foundations')

    def test_list_chapters(self):
        response = self.client.get(f'/api/courses/{self.course.slug}/chapters/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_lessons(self):
        response = self.client.get(f'/api/courses/{self.course.slug}/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_by_difficulty(self):
        response = self.client.get('/api/courses/?difficulty=beginner')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unpublished_course_hidden(self):
        Course.objects.create(
            slug='hidden', title='Hidden', description='', track=self.track,
            is_published=False, is_active=True,
        )
        response = self.client.get('/api/courses/')
        # List endpoints are globally paginated (PageNumberPagination).
        titles = [c['title'] for c in response.data['results']]
        self.assertNotIn('Hidden', titles)

    def test_retired_chapters_stay_out_of_the_course_map(self):
        """Re-seeding retires rows; they must never leak into the learner's map."""
        retired = Chapter.objects.create(
            course=self.course, title='Old Basics', slug='old-basics', order=1,
            is_active=False,
        )
        Lesson.objects.create(
            chapter=retired, title='Old lesson', slug='old-lesson', order=1,
        )

        response = self.client.get(f'/api/courses/{self.course.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = [c['slug'] for c in response.data['chapters']]
        self.assertEqual(slugs, ['basics'])
        self.assertEqual(response.data['lesson_count'], 1)

    def test_final_assessment_chapter_is_flagged(self):
        final = Chapter.objects.create(
            course=self.course, title='Final assessment', slug='final-assessment', order=2,
        )
        final_lesson = Lesson.objects.create(
            chapter=final, title='Course quiz', slug='course-quiz', order=1,
        )
        Exercise.objects.create(
            lesson=final_lesson, title='Quiz', slug='quiz',
            exercise_type='multiple_choice', instructions='Pick one',
            language='none', is_final_assessment=True,
        )

        response = self.client.get(f'/api/courses/{self.course.slug}/')
        chapters = response.data['chapters']
        # Final assessment is last and clearly marked for the sidebar.
        self.assertEqual(chapters[-1]['slug'], 'final-assessment')
        self.assertTrue(chapters[-1]['is_final_assessment'])
        self.assertFalse(chapters[0]['is_final_assessment'])


# ─── Auth API Tests ──────────────────────────────────────────────────────────

@override_settings(AUTH_REQUIRE_EMAIL_VERIFICATION=False)
class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Throttling is cache-backed; a fresh cache keeps counts per test.
        cache.clear()

    def test_register(self):
        response = self.client.post('/api/auth/register/', {
            'full_name': 'New User',
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Learn-Python-2026!',
            'confirm_password': 'Learn-Python-2026!',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    def test_login(self):
        User.objects.create_user(username='loginuser', password='Learn-Python-2026!')
        response = self.client.post('/api/auth/login/', {
            'username': 'loginuser',
            'password': 'Learn-Python-2026!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_invalid_login(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'nobody',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_auth(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ─── Security & Integrity Tests (Phase H) ───────────────────────────────────────

class AnswerLeakageTest(TestCase):
    """The content API must never hand learners the answers or grading data."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='curious', password='pass123')
        self.client.force_authenticate(user=self.user)
        self.track = CareerTrack.objects.create(slug='py', title='Py', description='Py')
        self.course = Course.objects.create(
            slug='c1', title='C1', description='', track=self.track,
            language='python', is_published=True, is_active=True,
        )
        self.chapter = Chapter.objects.create(course=self.course, title='Ch1', slug='ch1', order=1)
        self.lesson = Lesson.objects.create(chapter=self.chapter, title='L1', slug='l1', order=1)

    def _detail(self, exercise):
        response = self.client.get(f'/api/exercises/{exercise.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_mcq_detail_hides_correct_flags(self):
        exercise = Exercise.objects.create(
            lesson=self.lesson, title='MCQ', slug='mcq',
            exercise_type='multiple_choice', instructions='Pick',
            choices=[
                {'id': 'a', 'text': 'Wrong', 'is_correct': False},
                {'id': 'b', 'text': 'Right', 'is_correct': True},
            ],
            solution_code='b',
        )
        data = self._detail(exercise).data
        self.assertNotIn('solution_code', data)
        for choice in data['choices']:
            self.assertNotIn('is_correct', choice)
            self.assertIn('text', choice)

    def test_output_prediction_detail_hides_expected_answer(self):
        exercise = Exercise.objects.create(
            lesson=self.lesson, title='OP', slug='op',
            exercise_type='output_prediction', instructions='What prints?',
            expected_output='42',
        )
        data = self._detail(exercise).data
        self.assertEqual(data['expected_output'], '')

    def test_code_exercise_keeps_spec_output(self):
        exercise = Exercise.objects.create(
            lesson=self.lesson, title='Code', slug='code',
            exercise_type='code', instructions='Print 42',
            expected_output='42', solution_code='print(42)',
            test_cases=[{'input': '', 'expected_output': '42'}],
        )
        data = self._detail(exercise).data
        # Code exercises show the expected behaviour as part of the spec…
        self.assertEqual(data['expected_output'], '42')
        # …but never the solution or the grading tests.
        self.assertNotIn('solution_code', data)
        self.assertNotIn('test_cases', data)
        self.assertNotIn('hidden_tests', data)


class HonestGradingIntegrityTest(TestCase):
    """Ungradeable submissions are recorded honestly — never as fake passes."""

    def setUp(self):
        self.track = CareerTrack.objects.create(slug='py', title='Py', description='Py')
        self.course = Course.objects.create(
            slug='c1', title='C1', description='', track=self.track,
            language='python', is_published=True,
        )
        self.chapter = Chapter.objects.create(course=self.course, title='Ch1', slug='ch1', order=1)
        self.lesson = Lesson.objects.create(chapter=self.chapter, title='L1', slug='l1', order=1)

    def test_code_without_tests_or_solution_is_pending(self):
        exercise = Exercise.objects.create(
            lesson=self.lesson, title='Open', slug='open',
            exercise_type='code', instructions='Write anything',
        )
        result = validate_submission(exercise, 'print("whatever")')
        self.assertNotEqual(result.status, 'correct')
        self.assertFalse(result.all_passed)

    def test_fill_blank_wrong_answer_is_incorrect(self):
        exercise = Exercise.objects.create(
            lesson=self.lesson, title='FB', slug='fb',
            exercise_type='fill_blank', instructions='Complete',
            solution_code='git add',
        )
        wrong = validate_submission(exercise, 'git commit')
        self.assertEqual(wrong.status, 'incorrect')
        right = validate_submission(exercise, ' git  add ')
        self.assertEqual(right.status, 'correct')


class SeedAcademyIntegrityTest(TestCase):
    """The academy seeder must produce the five full courses, idempotently."""

    def test_seed_is_idempotent_and_complete(self):
        from django.core.management import call_command
        from .models import Lesson as LessonModel

        call_command('seed_academy', verbosity=0)
        first_exercises = Exercise.objects.count()
        first_lessons = LessonModel.objects.count()

        expected = {
            'python-foundations', 'cpp-fundamentals', 'web-foundations',
            'git-github-foundations', 'problem-solving-dsa',
        }
        slugs = set(Course.objects.filter(slug__in=expected).values_list('slug', flat=True))
        self.assertEqual(slugs, expected)

        for course in Course.objects.filter(slug__in=expected):
            finals = Exercise.objects.filter(
                lesson__chapter__course=course,
                lesson__chapter__is_active=True,
                lesson__is_active=True,
                is_final_assessment=True,
                is_active=True,
            )
            self.assertGreaterEqual(finals.count(), 5, course.slug)
            self.assertTrue(
                LessonModel.objects.filter(chapter__course=course, is_active=True).exists(),
                course.slug,
            )

        # Re-running must not duplicate anything.
        call_command('seed_academy', verbosity=0)
        self.assertEqual(Exercise.objects.count(), first_exercises)
        self.assertEqual(LessonModel.objects.count(), first_lessons)


class SeedProjectsTest(TestCase):
    """Real World Projects must exist with ordered, non-placeholder milestones."""

    def test_seed_creates_professional_projects_idempotently(self):
        from django.core.management import call_command
        from .models import Project

        call_command('seed_projects', verbosity=0)
        projects = Project.objects.filter(is_active=True)
        self.assertGreaterEqual(projects.count(), 3)

        for project in projects:
            self.assertIsNotNone(project.track, project.slug)
            self.assertGreaterEqual(project.milestones.count(), 5, project.slug)
            self.assertGreater(project.estimated_hours, 0, project.slug)
            self.assertTrue(project.technologies, project.slug)
            for milestone in project.milestones.all():
                self.assertTrue(milestone.description.strip(), milestone.title)

        before = {
            p.slug: (p.milestones.count(), p.title) for p in projects
        }
        call_command('seed_projects', verbosity=0)
        after = {
            p.slug: (p.milestones.count(), p.title)
            for p in Project.objects.filter(is_active=True)
        }
        self.assertEqual(before, after)


# ─── Real Subprocess Sandbox ───────────────────────────────────────────────
# These tests execute code for real. They exist to prove the platform never
# reports a result it did not actually compute.

class SubprocessSandboxPythonTest(TestCase):
    def setUp(self):
        self.sandbox = SubprocessSandbox(
            config=SandboxConfig(timeout_seconds=30.0, max_output_bytes=100_000),
        )

    def test_python_runs_and_produces_real_output(self):
        result = self.sandbox.execute('print(sum(range(1, 11)))', 'python')
        self.assertEqual(result.status, 'success')
        self.assertEqual(result.output.strip(), '55')

    def test_python_reads_stdin(self):
        result = self.sandbox.execute('print(input().upper())', 'python', stdin='hello\n')
        self.assertEqual(result.status, 'success')
        self.assertEqual(result.output.strip(), 'HELLO')

    def test_python_runtime_error_is_surfaced(self):
        result = self.sandbox.execute('print(1 / 0)', 'python')
        self.assertEqual(result.status, 'error')
        self.assertIn('ZeroDivisionError', result.error)

    def test_infinite_loop_times_out_instead_of_hanging(self):
        sandbox = SubprocessSandbox(
            config=SandboxConfig(timeout_seconds=3.0, max_output_bytes=1000),
        )
        result = sandbox.execute('while True: pass', 'python')
        self.assertEqual(result.status, 'timeout')


CPP_HELLO = (
    '#include <iostream>\n'
    'using namespace std;\n\n'
    'int main() {\n'
    '    cout << "Hello, World!";\n'
    '    return 0;\n'
    '}\n'
)

CPP_ADD = (
    '#include <iostream>\n'
    'using namespace std;\n\n'
    'int main() {\n'
    '    int a, b;\n'
    '    cin >> a >> b;\n'
    '    cout << a + b;\n'
    '    return 0;\n'
    '}\n'
)


@skipUnless(SubprocessSandbox().cpp_available, 'No C++ compiler on this host')
class SubprocessSandboxCppTest(TestCase):
    """C++ must genuinely compile and run, or the request must fail honestly."""

    def setUp(self):
        self.sandbox = SubprocessSandbox(
            config=SandboxConfig(timeout_seconds=60.0, max_output_bytes=100_000),
        )

    def test_advertises_cpp_only_when_a_compiler_exists(self):
        self.assertIn('cpp', self.sandbox.supported_languages())

    def test_compiles_and_runs(self):
        result = self.sandbox.execute(CPP_HELLO, 'cpp')
        self.assertEqual(result.status, 'success', result.error)
        self.assertEqual(result.output.strip(), 'Hello, World!')

    def test_reads_stdin_via_cin(self):
        result = self.sandbox.execute(CPP_ADD, 'cpp', stdin='15 27\n')
        self.assertEqual(result.status, 'success', result.error)
        self.assertEqual(result.output.strip(), '42')

    def test_grades_multiple_test_cases(self):
        results = self.sandbox.run_tests(CPP_ADD, 'cpp', [
            {'input': '2 3', 'expected_output': '5'},
            {'input': '10 20', 'expected_output': '30'},
            {'input': '1 1', 'expected_output': '99'},
        ])
        self.assertEqual([r.status for r in results], ['passed', 'passed', 'failed'])

    def test_compile_error_is_reported_not_swallowed(self):
        result = self.sandbox.execute('int main() { cout << "x"; }', 'cpp')
        self.assertEqual(result.status, 'error')
        self.assertIn('error', result.error.lower())

    def test_compile_error_does_not_leak_server_paths(self):
        result = self.sandbox.execute('int main() { cout << "x"; }', 'cpp')
        self.assertNotIn('Temp', result.error)
        self.assertNotIn('cy-sandbox-', result.error)

    def test_unsupported_language_is_refused(self):
        result = self.sandbox.execute(CPP_HELLO, 'javascript')
        self.assertEqual(result.status, 'error')
        self.assertIn('supports Python and C++', result.error)


# ─── Textbook source references (curriculum accuracy) ───────────────────

class TextbookSourceReferenceTest(TestCase):
    """
    Official board-textbook content may only be stored once it has been
    verified against the book, so un-reviewed material cannot be published as
    Sindh Board syllabus.
    """

    def setUp(self):
        self.track = CareerTrack.objects.create(
            slug='qa-textbook-board', title='Sindh Board', description='Board syllabus',
        )
        self.course = Course.objects.create(
            slug='class-x-cpp', title='Class X — C++', description='',
            track=self.track, language='cpp',
        )
        self.chapter = Chapter.objects.create(
            course=self.course, title='Input/Output Handling in C++',
            slug='unit-3', order=1,
        )
        self.lesson = Lesson.objects.create(
            chapter=self.chapter, title='Escape Sequences', slug='escape-sequences',
            order=1,
        )

    def _reference(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.lesson, key, value)
        return self.lesson

    def test_official_content_must_be_verified(self):
        lesson = self._reference(
            source_type='official', verification_status='', textbook_class='Class X',
        )
        with self.assertRaises(ValidationError) as ctx:
            lesson.full_clean()
        self.assertIn('verification_status', ctx.exception.message_dict)

    def test_official_verified_content_is_accepted(self):
        lesson = self._reference(
            source_type='official', verification_status='verified',
            textbook_class='Class X', textbook_unit='Unit 3',
            textbook_topic='3.3.4 Escape Sequences', textbook_pages='56',
        )
        lesson.full_clean()

    def test_supplementary_content_does_not_claim_verification(self):
        lesson = self._reference(
            source_type='supplementary', verification_status='', textbook_class='Class X',
        )
        lesson.full_clean()

    def test_textbook_content_must_name_its_class(self):
        lesson = self._reference(source_type='official', verification_status='verified')
        with self.assertRaises(ValidationError) as ctx:
            lesson.full_clean()
        self.assertIn('textbook_class', ctx.exception.message_dict)

    def test_reference_label_carries_the_printed_pages(self):
        lesson = self._reference(
            source_type='official', verification_status='verified',
            textbook_class='Class X', textbook_unit='Unit 3',
            textbook_topic='3.3.4 Escape Sequences', textbook_pages='56',
        )
        self.assertEqual(
            lesson.textbook_reference_label,
            'Unit 3 > 3.3.4 Escape Sequences (p. 56)',
        )

    def test_non_textbook_content_keeps_no_reference(self):
        general = CareerTrack.objects.create(
            slug='backend', title='Backend', description='Backend',
        )
        course = Course.objects.create(
            slug='python-basics', title='Python Basics', description='',
            track=general, language='python',
        )
        chapter = Chapter.objects.create(course=course, title='Ch', slug='ch', order=1)
        lesson = Lesson.objects.create(chapter=chapter, title='L', slug='l', order=1)
        self.assertFalse(lesson.has_textbook_reference)
        self.assertEqual(lesson.textbook_reference_label, '')

    def test_exercise_carries_its_own_page_reference(self):
        exercise = Exercise.objects.create(
            lesson=self.lesson, title='Unit 3 MCQ', slug='unit-3-mcq',
            exercise_type='multiple_choice', instructions='Pick',
            source_type='official', verification_status='verified',
            textbook_class='Class X', textbook_unit='Unit 3',
            textbook_topic='EXERCISE A', textbook_pages='67',
            choices=[{'id': 'a', 'text': 'A', 'is_correct': True}],
        )
        self.assertEqual(
            exercise.textbook_reference_label, 'Unit 3 > EXERCISE A (p. 67)'
        )

    def test_serialiser_exposes_reference_for_textbook_lesson(self):
        from .serializers import LessonDetailSerializer

        self._reference(
            source_type='official', verification_status='verified',
            textbook_class='Class X', textbook_unit='Unit 3',
            textbook_topic='3.3.4 Escape Sequences', textbook_pages='56',
        ).save()
        data = LessonDetailSerializer(self.lesson).data
        self.assertEqual(data['textbook_reference']['source_type'], 'official')
        self.assertEqual(data['textbook_reference']['pages'], '56')

    def test_serialiser_returns_no_reference_for_general_content(self):
        from .serializers import LessonDetailSerializer

        other_track = CareerTrack.objects.create(
            slug='data', title='Data', description='Data',
        )
        other_course = Course.objects.create(
            slug='ds', title='DS', description='', track=other_track, language='python',
        )
        other_chapter = Chapter.objects.create(
            course=other_course, title='Ch', slug='ch', order=1,
        )
        other_lesson = Lesson.objects.create(
            chapter=other_chapter, title='L', slug='l', order=1,
        )
        data = LessonDetailSerializer(other_lesson).data
        self.assertIsNone(data['textbook_reference'])


# ─── Class X end-to-end (real seeded curriculum through the real API) ────────

CLASS_X_SLUG = 'sindh-board-class-x-cpp'
UNIT_CHAPTER_SLUGS = [
    'unit-2-basics-of-programming-in-cpp',
    'unit-3-input-output-handling-in-cpp',
    'unit-4-control-structure',
    'unit-5-functions',
]


@override_settings(AUTH_REQUIRE_EMAIL_VERIFICATION=False)
class SindhBoardClassXEndToEndTest(TestCase):
    """
    Seed the real Class X textbook curriculum and walk it through the same
    HTTP endpoints the frontend calls. This proves the published course is
    navigable, that every chapter carries verified Sindh Board provenance, and
    that a textbook C++ exercise genuinely executes and awards XP — not a
    hand-built fixture, but the material a learner actually meets.
    """

    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command

        call_command('seed_sindh_board', verbosity=0)

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='x_learner', password='pass123')
        UserProfile.objects.create(user=self.user, xp_points=0)
        self.client.force_authenticate(user=self.user)

    def test_published_course_lists_all_four_programming_units(self):
        response = self.client.get(f'/api/courses/{CLASS_X_SLUG}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        chapters = response.data['chapters']
        self.assertEqual(len(chapters), 4)
        self.assertEqual([c['slug'] for c in chapters], UNIT_CHAPTER_SLUGS)
        # Every unit must carry real, verified textbook provenance.
        for chapter in chapters:
            ref = chapter['textbook_reference']
            self.assertIsNotNone(ref, chapter['slug'])
            self.assertEqual(ref['source_type'], 'official')
            self.assertEqual(ref['verification_status'], 'verified')
            self.assertTrue(ref['pages'])
            # No unit is an empty shell — each has lessons.
            self.assertGreaterEqual(len(chapter['lessons']), 4, chapter['slug'])

    def test_lesson_exposes_content_and_provenance(self):
        response = self.client.get(f'/api/courses/{CLASS_X_SLUG}/lessons/the-if-statement/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['content_body'].strip())
        ref = response.data['textbook_reference']
        self.assertEqual(ref['class'], 'Class X')
        self.assertEqual(ref['unit'], 'Unit 4')

    @skipUnless(SubprocessSandbox().cpp_available, 'No C++ compiler on this host')
    def test_textbook_cpp_exercise_executes_and_awards_xp(self):
        exercise = Exercise.objects.get(
            slug='pass-or-fail-program', lesson__chapter__course__slug=CLASS_X_SLUG,
        )
        self.assertEqual(exercise.exercise_type, 'code')
        self.assertEqual(exercise.language, 'cpp')

        response = self.client.post(
            f'/api/exercises/{exercise.id}/submit/',
            {'code': exercise.solution_code, 'time_spent_seconds': 60},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'correct', response.data.get('error'))
        self.assertGreater(response.data['xp_earned'], 0)
        self.assertTrue(
            XPTransaction.objects.filter(user=self.user, action='exercise_complete').exists()
        )
        # Submitting real work auto-enrolled the learner.
        self.assertTrue(
            Enrollment.objects.filter(user=self.user, course__slug=CLASS_X_SLUG).exists()
        )

    @skipUnless(SubprocessSandbox().cpp_available, 'No C++ compiler on this host')
    def test_wrong_cpp_program_is_not_marked_correct(self):
        exercise = Exercise.objects.get(
            slug='pass-or-fail-program', lesson__chapter__course__slug=CLASS_X_SLUG,
        )
        # Compiles and runs, but prints the wrong word — must fail the tests.
        wrong = (
            '#include <iostream>\n'
            'using namespace std;\n'
            'int main() {\n'
            '    int marks; cin >> marks;\n'
            '    cout << "Maybe";\n'
            '    return 0;\n'
            '}\n'
        )
        response = self.client.post(
            f'/api/exercises/{exercise.id}/submit/',
            {'code': wrong, 'time_spent_seconds': 30},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['status'], 'correct')
        self.assertEqual(response.data['xp_earned'], 0)

    def test_xii_remains_unpublished_shell(self):
        """Class XII stays infrastructure-only until its book is verified."""
        course = Course.objects.get(slug='sindh-board-class-xii-python')
        self.assertFalse(course.is_published)
        self.assertEqual(course.chapters.filter(is_active=True).count(), 0)
        # Class X and XI are the two fully built, published board courses.
        self.assertTrue(Course.objects.get(slug=CLASS_X_SLUG).is_published)
        self.assertTrue(
            Course.objects.get(slug='sindh-board-class-xi-python').is_published
        )


# ─── Class XI end-to-end (real seeded Python curriculum through the API) ──────

CLASS_XI_SLUG = 'sindh-board-class-xi-python'
XI_CHAPTER_SLUGS = [
    'xi-programming-with-python',
    'xi-ide-and-python-basics',
    'xi-io-and-operators',
    'xi-control-structures',
    'xi-libraries-and-debugging',
]


@override_settings(AUTH_REQUIRE_EMAIL_VERIFICATION=False)
class SindhBoardClassXIEndToEndTest(TestCase):
    """
    Seed the real Class XI Unit 3 Python curriculum and walk it through the
    same HTTP endpoints the frontend calls. This proves the published course
    is navigable, every chapter carries verified Sindh Board provenance, and a
    textbook Python exercise genuinely executes in the sandbox and awards XP.
    Unlike C++, Python needs no compiler check — the sandbox always runs it.
    """

    @classmethod
    def setUpTestData(cls):
        from django.core.management import call_command

        call_command('seed_sindh_board', verbosity=0)

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='xi_learner', password='pass123')
        UserProfile.objects.create(user=self.user, xp_points=0)
        self.client.force_authenticate(user=self.user)

    def test_published_course_lists_all_unit_three_chapters(self):
        response = self.client.get(f'/api/courses/{CLASS_XI_SLUG}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        chapters = response.data['chapters']
        self.assertEqual([c['slug'] for c in chapters], XI_CHAPTER_SLUGS)
        for chapter in chapters:
            ref = chapter['textbook_reference']
            self.assertIsNotNone(ref, chapter['slug'])
            self.assertEqual(ref['source_type'], 'official')
            self.assertEqual(ref['verification_status'], 'verified')
            self.assertTrue(ref['pages'])
            self.assertGreaterEqual(len(chapter['lessons']), 2, chapter['slug'])

    def test_lesson_exposes_content_and_provenance(self):
        response = self.client.get(
            f'/api/courses/{CLASS_XI_SLUG}/lessons/the-if-and-if-else-statements/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['content_body'].strip())
        ref = response.data['textbook_reference']
        self.assertEqual(ref['class'], 'Class XI')
        self.assertEqual(ref['unit'], 'Unit 3')

    def test_textbook_python_exercise_executes_and_awards_xp(self):
        exercise = Exercise.objects.get(
            slug='cnic-or-crc', lesson__chapter__course__slug=CLASS_XI_SLUG,
        )
        solution = (
            'age = int(input())\n'
            'if age >= 18:\n'
            '    print("Adult")\n'
            'else:\n'
            '    print("Minor")\n'
        )
        response = self.client.post(
            f'/api/exercises/{exercise.id}/submit/',
            {'code': solution, 'time_spent_seconds': 40},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'correct', response.data.get('error'))
        self.assertGreater(response.data['xp_earned'], 0)
        self.assertTrue(
            XPTransaction.objects.filter(user=self.user, action='exercise_complete').exists()
        )
        self.assertTrue(
            Enrollment.objects.filter(user=self.user, course__slug=CLASS_XI_SLUG).exists()
        )

    def test_wrong_python_program_is_not_marked_correct(self):
        exercise = Exercise.objects.get(
            slug='cnic-or-crc', lesson__chapter__course__slug=CLASS_XI_SLUG,
        )
        # Runs fine but prints the wrong word for the 11-year-old test case.
        wrong = (
            'age = int(input())\n'
            'print("Adult")\n'
        )
        response = self.client.post(
            f'/api/exercises/{exercise.id}/submit/',
            {'code': wrong, 'time_spent_seconds': 20},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['status'], 'correct')
        self.assertEqual(response.data['xp_earned'], 0)


# ─── Learning Tracks API Tests ────────────────────────────────────────────────

@override_settings(AUTH_REQUIRE_EMAIL_VERIFICATION=False)
class LearningTracksAPITest(TestCase):
    """Contract of the Tracks discovery layer (list/detail/enroll/protect)."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='learner', password='pass123')
        self.board = CareerTrack.objects.create(
            slug='qa-board', title='Sindh Board Computer Science',
            description='Board track', category='school_board',
            is_published=True, order=0,
        )
        self.programming = CareerTrack.objects.create(
            slug='qa-programming', title='Programming Fundamentals',
            description='Core track', category='programming',
            is_published=True, order=1,
            learning_objectives=['Write Python programs'],
        )
        self.hidden = CareerTrack.objects.create(
            slug='draft-track', title='Draft Track', description='No',
            category='other', is_published=False,
        )
        self.empty = CareerTrack.objects.create(
            slug='ai-empty', title='Artificial Intelligence',
            description='No courses yet', category='ai', is_published=True,
        )
        self.class_x = Course.objects.create(
            slug='class-x', title='Class X', description='C++ for board class X',
            track=self.board, academic_class='Class X', order=1,
            language='cpp', is_published=True,
        )
        self.class_xi = Course.objects.create(
            slug='class-xi', title='Class XI', description='Python for board class XI',
            track=self.board, academic_class='Class XI', order=2,
            language='python', is_published=True,
        )
        self.draft_course = Course.objects.create(
            slug='class-xii', title='Class XII', description='Draft shell',
            track=self.board, order=3, is_published=False,
        )
        self.python = Course.objects.create(
            slug='py-101', title='Python 101', description='Intro',
            track=self.programming, order=1, is_published=True,
        )
        chapter = Chapter.objects.create(course=self.python, title='B', slug='b', order=1)
        self.lesson = Lesson.objects.create(
            chapter=chapter, title='L', slug='l', order=1, xp_reward=50,
        )

    def _slugs(self, response):
        return [t['slug'] for t in response.data['results']]

    def test_list_only_published_tracks_with_openable_courses(self):
        response = self.client.get('/api/tracks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = self._slugs(response)
        self.assertIn('qa-board', slugs)
        self.assertIn('qa-programming', slugs)
        # Unpublished tracks and published-but-empty tracks never surface:
        # an empty shelf is not a browseable destination.
        self.assertNotIn('draft-track', slugs)
        self.assertNotIn('ai-empty', slugs)

    def test_category_filter_is_database_driven(self):
        response = self.client.get('/api/tracks/?category=school_board')
        self.assertEqual(self._slugs(response), ['qa-board'])

    def test_course_count_excludes_unpublished_courses(self):
        response = self.client.get('/api/tracks/')
        track = next(t for t in response.data['results'] if t['slug'] == 'qa-board')
        self.assertEqual(track['course_count'], 2)

    def test_detail_sequences_courses_and_exposes_metadata(self):
        response = self.client.get(f'/api/tracks/{self.board.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        courses = response.data['courses']
        self.assertEqual([c['slug'] for c in courses], ['class-x', 'class-xi'])
        self.assertEqual([c['academic_class'] for c in courses], ['Class X', 'Class XI'])
        self.assertEqual(courses[0]['language'], 'cpp')
        self.assertEqual(response.data['category'], 'school_board')

    def test_track_enroll_creates_one_enrollment_per_published_course(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/tracks/{self.board.slug}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Enrollment.objects.filter(user=self.user).count(), 2
        )
        self.assertFalse(
            Enrollment.objects.filter(user=self.user, course=self.draft_course).exists()
        )

    def test_track_enroll_is_idempotent_and_keeps_progress(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(f'/api/tracks/{self.board.slug}/enroll/')
        LessonProgress.objects.create(
            user=self.user, lesson=self.lesson, status='completed'
        )
        response = self.client.post(f'/api/tracks/{self.board.slug}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Enrollment.objects.filter(user=self.user).count(), 2)

    def test_enroll_requires_authentication(self):
        response = self.client.post(f'/api/tracks/{self.board.slug}/enroll/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_reports_learner_progress(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(f'/api/tracks/{self.programming.slug}/enroll/')
        LessonProgress.objects.create(
            user=self.user, lesson=self.lesson, status='completed'
        )
        response = self.client.get(f'/api/tracks/{self.programming.slug}/')
        self.assertEqual(response.data['enrolled_course_count'], 1)
        self.assertEqual(response.data['progress_percentage'], 100)
        self.assertEqual(response.data['continue_url_slug'], 'py-101')

    def test_anonymous_progress_fields_are_neutral(self):
        response = self.client.get(f'/api/tracks/{self.board.slug}/')
        self.assertEqual(response.data['enrolled_course_count'], 0)
        self.assertEqual(response.data['progress_percentage'], 0)

    def test_track_with_courses_cannot_be_deleted(self):
        from django.db.models.deletion import ProtectedError
        with self.assertRaises(ProtectedError):
            self.board.delete()
        # Courses (and their enrollment chains) survive untouched.
        self.assertEqual(self.board.courses.count(), 3)
