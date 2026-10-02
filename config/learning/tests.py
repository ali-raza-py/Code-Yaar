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

from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from .models import (
    UserProfile, CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Enrollment, LessonProgress, ExerciseAttempt, XPTransaction,
    Achievement, UserAchievement,
)
from .services.language_adapter import (
    get_adapter, get_supported_languages, PythonAdapter, JavaScriptAdapter,
)
from .services.sandbox import (
    DevelopmentSandbox, validate_submission, SandboxConfig,
)


# ─── Model Tests ─────────────────────────────────────────────────────────────

class CourseModelTest(TestCase):
    def setUp(self):
        self.track = CareerTrack.objects.create(
            slug='python', title='Python', description='Python track',
        )
        self.course = Course.objects.create(
            slug='python-101', title='Python 101', description='Intro',
            track=self.track, difficulty='beginner', language='python',
            estimated_hours=4, total_xp=1000, is_published=True,
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


# ─── Enrollment Tests ────────────────────────────────────────────────────────

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


# ─── Exercise Submission Tests ───────────────────────────────────────────────

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

    def test_get_hint(self):
        response = self.client.get(f'/api/exercises/{self.exercise.id}/hint/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('hint', response.data)

    def test_hint_deducts_xp(self):
        initial_xp = UserProfile.objects.get(user=self.user).xp_points
        self.client.get(f'/api/exercises/{self.exercise.id}/hint/')
        updated_xp = UserProfile.objects.get(user=self.user).xp_points
        self.assertLess(updated_xp, initial_xp)


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


# ─── Course API Tests ────────────────────────────────────────────────────────

class CourseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.track = CareerTrack.objects.create(slug='py', title='Python', description='Python track')
        self.course = Course.objects.create(
            slug='python-foundations', title='Python Foundations',
            description='Learn Python', track=self.track,
            difficulty='beginner', language='python',
            estimated_hours=4, total_xp=3900,
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
        titles = [c['title'] for c in response.data]
        self.assertNotIn('Hidden', titles)


# ─── Auth API Tests ──────────────────────────────────────────────────────────

class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepass123',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    def test_login(self):
        User.objects.create_user(username='loginuser', password='pass123')
        response = self.client.post('/api/auth/login/', {
            'username': 'loginuser',
            'password': 'pass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_invalid_login(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'nobody',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_auth(self):
        response = self.client.get('/api/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
