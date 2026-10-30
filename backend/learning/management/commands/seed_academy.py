"""Seed all five Code Yaar Academy courses from the academy content package.

Usage:
    python manage.py seed_academy

Fully idempotent: safe to re-run after editing the content modules. Every
Track / Course / Chapter / Lesson / Exercise is matched by slug and UPDATED
in place, so existing learner progress and attempts stay attached to the same
rows. Content that disappeared from the spec is deactivated (never deleted).

Structure materialised per course:
    CareerTrack ← Course ← Chapter (module) ← Lesson ← Exercise
    The COURSE['assessment'] exercises live in a dedicated
    "Final Assessment" chapter/lesson and are flagged is_final_assessment,
    which the certificate eligibility service grades against.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from learning.models import CareerTrack, Chapter, Course, Exercise, Lesson

from learning.management.commands.academy import (
    cpp_course, dsa_course, git_course, python_course, web_course,
)

COURSES = [
    python_course.COURSE,
    cpp_course.COURSE,
    web_course.COURSE,
    git_course.COURSE,
    dsa_course.COURSE,
]

# Course language -> Exercise.language (Exercise choices differ slightly).
EXERCISE_LANGUAGE = {
    'python': 'python',
    'cpp': 'cpp',
    'javascript': 'javascript',
    'other': 'none',
    'java': 'java',
}

DEMO_EMAIL = 'demo@codeyaar.dev'
DEMO_PASSWORD = 'demo123'

# Course difficulty -> sensible default Exercise difficulty choice.
EXERCISE_DIFFICULTY = {'beginner': 'easy', 'intermediate': 'medium', 'advanced': 'hard'}

COURSE_FIELDS = (
    'title', 'subtitle', 'description', 'difficulty', 'language',
    'prerequisites', 'learning_objectives', 'is_free', 'is_published',
    'is_active', 'order',
    'certification_enabled', 'certification_passing_score',
    'require_all_lessons', 'require_final_assessment',
)
CHAPTER_FIELDS = ('title', 'description', 'order', 'is_active')
LESSON_FIELDS = (
    'title', 'learning_objective', 'content_body', 'content_type',
    'order', 'duration_minutes', 'xp_reward', 'is_active',
)
EXERCISE_FIELDS = (
    'title', 'exercise_type', 'instructions', 'context', 'constraints',
    'expected_behavior', 'explain', 'difficulty', 'language',
    'starter_code', 'solution_code', 'choices', 'expected_output',
    'test_cases', 'xp_reward', 'is_final_assessment', 'order', 'is_active',
)


class Command(BaseCommand):
    help = 'Seed/refresh the five Academy courses from the academy package.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.created = {'course': 0, 'chapter': 0, 'lesson': 0, 'exercise': 0}
        self.updated = {'course': 0, 'chapter': 0, 'lesson': 0, 'exercise': 0}

        for index, spec in enumerate(COURSES):
            self.seed_course(spec, index)

        self.ensure_demo_user()

        self.stdout.write(self.style.SUCCESS(
            'Academy seed complete: %d courses, %d chapters, %d lessons, '
            '%d exercises (created %d, updated %d).' % (
                len(COURSES),
                self.created['chapter'] + self.updated['chapter'],
                self.created['lesson'] + self.updated['lesson'],
                self.created['exercise'] + self.updated['exercise'],
                sum(self.created.values()), sum(self.updated.values()),
            )
        ))

    # ── Track & course ──

    def seed_course(self, spec, index):
        track_spec = spec['track']
        track, created = CareerTrack.objects.get_or_create(
            slug=track_spec['slug'],
            defaults={
                'title': track_spec['title'],
                'description': track_spec['description'],
                'difficulty': spec.get('difficulty', 'beginner'),
                'order': index,
            },
        )
        if not created:
            track.title = track_spec['title']
            track.description = track_spec['description']
            track.is_active = True
            track.save(update_fields=['title', 'description', 'is_active'])

        cert = spec.get('certification', {})
        fields = {
            'title': spec['title'],
            'subtitle': spec.get('subtitle', ''),
            'description': spec['description'],
            'difficulty': spec.get('difficulty', 'beginner'),
            'language': spec.get('language', 'python'),
            'prerequisites': spec.get('prerequisites', 'None'),
            'learning_objectives': spec.get('objectives', []),
            'is_free': spec.get('is_free', True),
            'is_published': True,
            'is_active': True,
            'order': index,
            'certification_enabled': cert.get('enabled', True),
            'certification_passing_score': cert.get('passing_score', 70),
            'require_all_lessons': cert.get('require_all_lessons', True),
            'require_final_assessment': cert.get('require_final_assessment', True),
        }
        # Look up by slug alone — the course may already exist under a
        # different track; re-point it instead of colliding on the unique slug.
        course = Course.objects.filter(slug=spec['slug']).first()
        created = course is None
        if created:
            course = Course.objects.create(slug=spec['slug'], track=track, **fields)
            self.created['course'] += 1
        else:
            if course.track_id != track.id:
                course.track = track
            for key, value in fields.items():
                setattr(course, key, value)
            course.save()
            self.updated['course'] += 1

        seen_chapters = set()
        for order, module in enumerate(spec['modules'], start=1):
            chapter = self.seed_chapter(course, module, order)
            seen_chapters.add(chapter.slug)
            self.seed_lessons(chapter, module.get('lessons', []))

        # Dedicated final-assessment chapter (only when the course has one).
        assessment = spec.get('assessment', [])
        if assessment:
            chapter = self.seed_chapter(course, {
                'slug': 'final-assessment',
                'title': 'Final Assessment',
                'description': (
                    'The graded end-of-course assessment. Pass it to unlock '
                    'your verifiable certificate.'
                ),
            }, order=len(spec['modules']) + 1)
            seen_chapters.add(chapter.slug)
            lesson = self.upsert(chapter.lessons, {'slug': 'final-assessment'}, {
                'title': 'Final Assessment',
                'learning_objective': 'Prove mastery of the course objectives.',
                'content_body': (
                    '# Final Assessment\n\nAnswer every question. Each item '
                    'counts equally toward your assessment score; the server '
                    'grades every submission. Retakes are allowed.\n'
                ),
                'content_type': 'text',
                'order': 1,
                'duration_minutes': 15,
                'xp_reward': 0,
                'is_active': True,
            }, LESSON_FIELDS, 'lesson')
            for order, ex in enumerate(assessment, start=1):
                self.seed_exercise(lesson, ex, order, final=True)

        # Deactivate chapters that vanished from the spec (never delete).
        # Their lessons and exercises are retired with them so grading and
        # certification only ever see current content.
        stale = course.chapters.exclude(slug__in=seen_chapters).filter(is_active=True)
        stale_count = stale.count()
        if stale_count:
            Lesson.objects.filter(chapter__in=stale, is_active=True).update(is_active=False)
            Exercise.objects.filter(lesson__chapter__in=stale, is_active=True).update(is_active=False)
            stale.update(is_active=False)
            self.stdout.write(self.style.WARNING(
                f'Deactivated {stale_count} chapter(s) no longer in the {course.slug} spec.'
            ))

        # Sweep: retire any lesson/exercise still active under an inactive
        # chapter (e.g. left behind by an older seeder).
        Lesson.objects.filter(
            chapter__course=course, chapter__is_active=False, is_active=True
        ).update(is_active=False)
        Exercise.objects.filter(
            lesson__chapter__course=course, lesson__chapter__is_active=False, is_active=True
        ).update(is_active=False)

    def seed_chapter(self, course, module, order):
        return self.upsert(course.chapters, {'slug': module['slug']}, {
            'title': module['title'],
            'description': module.get('description', ''),
            'order': order,
            'is_active': True,
        }, CHAPTER_FIELDS, 'chapter')

    def seed_lessons(self, chapter, lessons):
        seen = set()
        for order, lesson_spec in enumerate(lessons, start=1):
            lesson = self.upsert(chapter.lessons, {'slug': lesson_spec['slug']}, {
                'title': lesson_spec['title'],
                'learning_objective': lesson_spec.get('objective', ''),
                'content_body': lesson_spec.get('body', ''),
                'content_type': lesson_spec.get('content_type', 'text'),
                'order': order,
                'duration_minutes': lesson_spec.get('duration', 10),
                'xp_reward': lesson_spec.get('xp', 50),
                'is_active': True,
            }, LESSON_FIELDS, 'lesson')
            seen.add(lesson.slug)
            exercises = lesson_spec.get('exercises', [])
            for ex_order, ex in enumerate(exercises, start=1):
                self.seed_exercise(lesson, ex, ex_order, final=False)
        stale = chapter.lessons.exclude(slug__in=seen).filter(is_active=True)
        if stale.exists():
            stale.update(is_active=False)

    def seed_exercise(self, lesson, ex, order, *, final):
        course_language = lesson.chapter.course.language
        values = {
            'title': ex['title'],
            'exercise_type': ex['exercise_type'],
            'instructions': ex['instructions'],
            'context': ex.get('context', ''),
            'constraints': ex.get('constraints', ''),
            'expected_behavior': ex.get('expected_behavior', ''),
            'explain': ex.get('explain', ''),
            'difficulty': ex.get(
                'difficulty',
                EXERCISE_DIFFICULTY.get(lesson.chapter.course.difficulty, 'easy'),
            ),
            'language': ex.get('language', EXERCISE_LANGUAGE.get(course_language, 'python')),
            'starter_code': ex.get('starter_code', ''),
            'solution_code': ex.get('solution_code', ''),
            'choices': ex.get('choices', []),
            'expected_output': ex.get('expected_output', ''),
            'test_cases': ex.get('test_cases', []),
            'xp_reward': ex.get('xp_reward', 100),
            'is_final_assessment': final,
            'order': order,
            'is_active': True,
        }
        self.upsert(lesson.exercises, {'slug': ex['slug']}, values, EXERCISE_FIELDS, 'exercise')

    # ── Shared idempotent upsert ──

    def upsert(self, manager, key, values, update_fields, kind):
        obj, created = manager.get_or_create(**key, defaults=values)
        if created:
            self.created[kind] += 1
        else:
            for field in update_fields:
                if field in values:
                    setattr(obj, field, values[field])
            obj.save(update_fields=list(update_fields) + ['updated_at'])
            self.updated[kind] += 1
        return obj

    # ── Demo learner for manual verification ──

    def ensure_demo_user(self):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='demo',
            defaults={'email': DEMO_EMAIL, 'first_name': 'Demo', 'last_name': 'Learner'},
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'Created demo learner {DEMO_EMAIL} / {DEMO_PASSWORD}'
            ))
