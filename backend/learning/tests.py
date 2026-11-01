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
"""

from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status

from .models import (
    UserProfile, CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Enrollment, LessonProgress, ExerciseAttempt, XPTransaction,
    Achievement, UserAchievement,
    PracticalClass, PracticalSubject, Practical, PracticalProgress,
    PracticalBookmark,
)
from .services.language_adapter import (
    get_adapter, get_supported_languages, PythonAdapter, JavaScriptAdapter,
)
from .services.sandbox import (
    DevelopmentSandbox, validate_submission, SandboxConfig,
)
from .services.xp import award_xp, deduct_xp


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
        self.school_class = PracticalClass.objects.create(
            slug='class-9', title='Class 9', description='Foundation practicals'
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
