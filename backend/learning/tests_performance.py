"""
Query-count regression guards for the hottest read endpoints.

Each test seeds a realistic catalogue into the isolated test database, then
counts the *actual* SQL statements Django issues for one request. The counts
are printed so a before/after comparison can be read straight off the test
output, and asserted so an N+1 regression fails CI instead of slowly rotting
production.

Why query counts rather than wall-clock time: on a developer machine timing
noise is larger than the effect of most ORM fixes, while the statement count
is deterministic and scales 1:1 with the data size for an N+1 pattern.

Run only this module:
    python manage.py test learning.tests_performance -v 2
"""

import time

from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from .models import (
    CareerTrack, Course, Chapter, Lesson, Exercise, Enrollment,
    LessonProgress, ExerciseAttempt, UserProfile,
)

# Dataset shape. Large enough that per-row queries dominate, small enough to
# seed in a couple of seconds.
TRACKS = 5
COURSES_PER_TRACK = 4          # 20 courses = exactly one DRF page (PAGE_SIZE)
CHAPTERS_PER_COURSE = 3
LESSONS_PER_CHAPTER = 4
EXERCISES_PER_LESSON = 2
LEARNERS = 60                  # > leaderboard default limit of 50


def seed_catalogue():
    """Create tracks → courses → chapters → lessons → exercises in bulk."""
    tracks = CareerTrack.objects.bulk_create([
        CareerTrack(
            slug=f'track-{t}', title=f'Track {t}', description='d',
            is_active=True, is_published=True, order=t,
        )
        for t in range(TRACKS)
    ])
    courses = Course.objects.bulk_create([
        Course(
            slug=f'course-{t}-{c}', title=f'Course {t}.{c}', description='d',
            track=track, order=c, is_active=True, is_published=True,
        )
        for t, track in enumerate(tracks)
        for c in range(COURSES_PER_TRACK)
    ])
    chapters = Chapter.objects.bulk_create([
        Chapter(course=course, title=f'Ch {k}', slug=f'ch-{k}', order=k)
        for course in courses
        for k in range(CHAPTERS_PER_COURSE)
    ])
    lessons = Lesson.objects.bulk_create([
        Lesson(
            chapter=chapter, title=f'L {k}', slug=f'l-{k}', order=k,
            duration_minutes=15, xp_reward=50,
        )
        for chapter in chapters
        for k in range(LESSONS_PER_CHAPTER)
    ])
    Exercise.objects.bulk_create([
        Exercise(
            lesson=lesson, title=f'E {k}', slug=f'e-{k}', order=k,
            instructions='i', xp_reward=100,
        )
        for lesson in lessons
        for k in range(EXERCISES_PER_LESSON)
    ])
    return tracks, courses, lessons


def seed_learners(courses, lessons):
    """Learners with profiles, enrollments, lesson progress and attempts so the
    leaderboard and per-user progress fields have real rows to aggregate."""
    users = User.objects.bulk_create([
        User(username=f'learner{i}', email=f'learner{i}@example.com')
        for i in range(LEARNERS)
    ])
    UserProfile.objects.bulk_create([
        UserProfile(user=user, xp_points=(i * 37) % 5000, level=1 + i % 7)
        for i, user in enumerate(users)
    ])
    enrollments = []
    for i, user in enumerate(users):
        for course in courses[i % len(courses):][:3]:
            enrollments.append(Enrollment(
                user=user, course=course,
                status='completed' if (i + course.order) % 3 == 0 else 'active',
            ))
    Enrollment.objects.bulk_create(enrollments)

    progress, attempts = [], []
    exercises = list(Exercise.objects.order_by('id')[:200])
    for i, user in enumerate(users):
        for lesson in lessons[i % 50:i % 50 + 6]:
            progress.append(LessonProgress(user=user, lesson=lesson, status='completed'))
        for exercise in exercises[i % 40:i % 40 + 5]:
            attempts.append(ExerciseAttempt(
                user=user, exercise=exercise, status='correct',
                attempt_number=1,
            ))
    LessonProgress.objects.bulk_create(progress)
    ExerciseAttempt.objects.bulk_create(attempts)
    return users


def _measure(client, url):
    """Return (query_count, elapsed_ms, response) for a single GET."""
    with CaptureQueriesContext(connection) as ctx:
        started = time.perf_counter()
        response = client.get(url)
        elapsed_ms = (time.perf_counter() - started) * 1000
    return len(ctx.captured_queries), elapsed_ms, response


class EndpointQueryBudgetTest(TestCase):
    """Counts SQL statements for the three heaviest public endpoints.

    The budgets below are the post-optimisation ceilings; a failure means a
    serializer or view reintroduced a per-row query.
    """

    # Maximum SQL statements allowed per request. Each is documented in the
    # corresponding test so a future change can be judged against it.
    BUDGET_COURSES_ANON = 4
    BUDGET_COURSES_AUTH = 6
    BUDGET_TRACK_DETAIL_ANON = 4
    BUDGET_TRACK_DETAIL_AUTH = 7
    BUDGET_LEADERBOARD = 4

    @classmethod
    def setUpTestData(cls):
        cls.tracks, cls.courses, cls.lessons = seed_catalogue()
        cls.users = seed_learners(cls.courses, cls.lessons)
        cls.learner = cls.users[0]

    def setUp(self):
        self.client = APIClient()

    def _report(self, label, queries, elapsed_ms, response):
        self.assertEqual(response.status_code, 200, response.content[:300])
        print(f'\n[perf] {label}: {queries} SQL queries, {elapsed_ms:.1f} ms')

    # ── GET /api/courses/ ──

    def test_course_list_anonymous(self):
        queries, ms, response = _measure(self.client, '/api/courses/')
        self._report('GET /api/courses/ (anonymous)', queries, ms, response)
        self.assertEqual(len(response.data['results']), COURSES_PER_TRACK * TRACKS)
        # Sanity: aggregates are real, not zeroed by the optimisation.
        first = response.data['results'][0]
        self.assertEqual(first['chapter_count'], CHAPTERS_PER_COURSE)
        self.assertEqual(first['lesson_count'], CHAPTERS_PER_COURSE * LESSONS_PER_CHAPTER)
        self.assertEqual(
            first['exercise_count'],
            CHAPTERS_PER_COURSE * LESSONS_PER_CHAPTER * EXERCISES_PER_LESSON,
        )
        self.assertEqual(first['total_xp'], 12 * 50 + 24 * 100)
        self.assertEqual(first['estimated_hours'], 3)  # 12 lessons × 15 min
        self.assertLessEqual(queries, self.BUDGET_COURSES_ANON)

    def test_course_list_authenticated(self):
        self.client.force_authenticate(user=self.learner)
        queries, ms, response = _measure(self.client, '/api/courses/')
        self._report('GET /api/courses/ (authenticated)', queries, ms, response)
        enrolled = [c for c in response.data['results'] if c['enrolled']]
        self.assertEqual(len(enrolled), 3)
        self.assertTrue(any(c['progress_percentage'] > 0 for c in enrolled))
        self.assertLessEqual(queries, self.BUDGET_COURSES_AUTH)

    # ── GET /api/tracks/<slug>/ ──

    def test_track_detail_anonymous(self):
        queries, ms, response = _measure(self.client, '/api/tracks/track-0/')
        self._report('GET /api/tracks/track-0/ (anonymous)', queries, ms, response)
        self.assertEqual(response.data['course_count'], COURSES_PER_TRACK)
        self.assertEqual(len(response.data['courses']), COURSES_PER_TRACK)
        self.assertEqual(
            response.data['total_xp'], COURSES_PER_TRACK * (12 * 50 + 24 * 100)
        )
        self.assertLessEqual(queries, self.BUDGET_TRACK_DETAIL_ANON)

    def test_track_detail_authenticated(self):
        self.client.force_authenticate(user=self.learner)
        queries, ms, response = _measure(self.client, '/api/tracks/track-0/')
        self._report('GET /api/tracks/track-0/ (authenticated)', queries, ms, response)
        self.assertEqual(response.data['enrolled_course_count'], 3)
        self.assertIsNotNone(response.data['continue_url_slug'])
        self.assertLessEqual(queries, self.BUDGET_TRACK_DETAIL_AUTH)

    # ── GET /api/leaderboard/ ──

    def test_leaderboard(self):
        queries, ms, response = _measure(self.client, '/api/leaderboard/')
        self._report('GET /api/leaderboard/ (limit=50)', queries, ms, response)
        self.assertEqual(response.data['total'], LEARNERS)
        self.assertEqual(len(response.data['entries']), 50)
        entries = response.data['entries']
        # Ranked by XP descending, ranks contiguous from 1.
        self.assertEqual([e['rank'] for e in entries], list(range(1, 51)))
        xp = [e['xp_points'] for e in entries]
        self.assertEqual(xp, sorted(xp, reverse=True))
        # Aggregates match a direct per-user recount.
        top = entries[0]
        self.assertEqual(
            top['courses_completed'],
            Enrollment.objects.filter(user_id=top['user_id'], status='completed').count(),
        )
        self.assertEqual(
            top['challenges_solved'],
            ExerciseAttempt.objects.filter(user_id=top['user_id'], status='correct')
            .values('exercise').distinct().count(),
        )
        self.assertLessEqual(queries, self.BUDGET_LEADERBOARD)
