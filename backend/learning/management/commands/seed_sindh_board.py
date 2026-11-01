"""
Seed command for the Sindh Board textbook courses — idempotent upsert.

Usage:
    python manage.py seed_sindh_board
    python manage.py seed_sindh_board --course sindh-board-class-x-cpp

What it does:
    - Creates/refreshes the "Sindh Board" career track
    - Publishes Class X (C++) from the verified textbook curriculum
    - Creates Class XI and Class XII as drafts with no lessons, because their
      content has not been verified against their textbooks yet. The platform
      does not publish board syllabus it has not read.

Every chapter, lesson and exercise carries the printed page reference it was
taken from. `SourceReference.clean()` refuses to save "official" content that
is not marked verified, so this command cannot accidentally publish invented
syllabus.

Content is never deleted: anything dropped from the curriculum is deactivated
so existing learner progress rows keep pointing at real content.
"""

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from learning.curriculum import CURRICULA
from learning.models import (
    CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
)

REFERENCE_FIELDS = (
    'source_type', 'verification_status', 'textbook_board', 'textbook_class',
    'textbook_unit', 'textbook_topic', 'textbook_pages',
)

COURSE_FIELDS = (
    'title', 'subtitle', 'description', 'difficulty', 'language',
    'instructor', 'prerequisites', 'learning_objectives', 'is_free',
    'is_published', 'order',
)
CHAPTER_FIELDS = ('title', 'description', 'order', 'xp_reward')
LESSON_FIELDS = (
    'title', 'content_type', 'learning_objective', 'content_body',
    'order', 'duration_minutes', 'xp_reward',
)
EXERCISE_FIELDS = (
    'title', 'exercise_type', 'instructions', 'context', 'constraints',
    'expected_behavior', 'explain', 'difficulty', 'language',
    'starter_code', 'solution_code', 'choices', 'expected_output',
    'test_cases', 'hidden_tests', 'xp_reward', 'max_attempts',
    'is_final_assessment', 'order',
)


def _assign(instance, fields, spec):
    for name in fields:
        if name in spec:
            setattr(instance, name, spec[name])


def _apply_reference(instance, spec):
    """Write the textbook citation, enforce the guard, then persist."""
    reference = spec.get('reference')
    if reference:
        _assign(instance, REFERENCE_FIELDS, reference)
    else:
        # Nothing in a board course may go out without a citation.
        raise CommandError(
            f'{instance.__class__.__name__} "{instance.slug}" has no '
            f'"reference" — textbook-derived content must cite its pages.'
        )
    try:
        instance.full_clean()
    except ValidationError as exc:
        raise CommandError(
            f'{instance.__class__.__name__} "{instance.slug}" is invalid: {exc}'
        ) from exc
    # Save last: full_clean() only validates in memory, so this is the single
    # point that persists the assigned content, activity flag and citation.
    instance.save()


def _upsert_exercise(lesson, spec):
    exercise, _ = Exercise.objects.get_or_create(
        lesson=lesson, slug=spec['slug'],
        defaults={f: spec[f] for f in EXERCISE_FIELDS if f in spec},
    )
    _assign(exercise, EXERCISE_FIELDS, spec)
    exercise.is_active = True
    _apply_reference(exercise, spec)

    # Hints carry no learner data — safe to rebuild from the spec.
    exercise.hints.all().delete()
    for i, content in enumerate(spec.get('hints', []), start=1):
        Hint.objects.create(
            exercise=exercise, content=content, order=i,
            reveals_solution=content.startswith('Solution:'),
            xp_penalty=0 if i < 3 else 10,
        )
    return exercise


def _upsert_lesson(chapter, spec):
    lesson, _ = Lesson.objects.get_or_create(
        chapter=chapter, slug=spec['slug'],
        defaults={'content_type': 'text', 'title': spec['title']},
    )
    _assign(lesson, LESSON_FIELDS, spec)
    lesson.is_active = True
    _apply_reference(lesson, spec)

    spec_slugs = {e['slug'] for e in spec.get('exercises', [])}
    for espec in spec.get('exercises', []):
        _upsert_exercise(lesson, espec)
    lesson.exercises.exclude(slug__in=spec_slugs).update(is_active=False)
    return lesson


def _upsert_chapter(course, spec):
    chapter, _ = Chapter.objects.get_or_create(
        course=course, slug=spec['slug'],
        defaults={'title': spec['title']},
    )
    _assign(chapter, CHAPTER_FIELDS, spec)
    chapter.is_active = True
    _apply_reference(chapter, spec)

    spec_slugs = {l['slug'] for l in spec['lessons']}
    for lspec in spec['lessons']:
        _upsert_lesson(chapter, lspec)
    chapter.lessons.exclude(slug__in=spec_slugs).update(is_active=False)
    return chapter


def _upsert_course(track, spec):
    course, _ = Course.objects.get_or_create(
        slug=spec['slug'],
        defaults={'title': spec['title'], 'description': '', 'track': track},
    )
    _assign(course, COURSE_FIELDS, spec)
    course.track = track
    course.is_active = True
    course.save()

    chapters = spec.get('chapters', [])
    spec_slugs = {c['slug'] for c in chapters}
    for cspec in chapters:
        _upsert_chapter(course, cspec)
    course.chapters.exclude(slug__in=spec_slugs).update(is_active=False)
    return course


class Command(BaseCommand):
    help = 'Seed/refresh the Sindh Board textbook courses (idempotent upsert)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--course', default='',
            help='Only seed the course with this slug (default: all curricula)',
        )

    def handle(self, *args, **options):
        only = options['course']
        seeded = 0

        for curriculum in CURRICULA:
            track_spec = curriculum.TRACK
            track_fields = ('title', 'description', 'category', 'difficulty',
                            'estimated_hours', 'order', 'is_published')
            track, _ = CareerTrack.objects.get_or_create(
                slug=track_spec['slug'],
                defaults={
                    f: track_spec[f]
                    for f in track_fields
                    if f in track_spec
                },
            )
            _assign(track, track_fields, track_spec)
            track.is_active = True
            track.save()

            for spec in curriculum.COURSES:
                if only and spec['slug'] != only:
                    continue
                course = _upsert_course(track, spec)
                self.stdout.write(self.style.SUCCESS(
                    f'  {course.title}: '
                    f'{course.chapters.filter(is_active=True).count()} chapters, '
                    f'{course.lesson_count} lessons, {course.exercise_count} exercises '
                    f'({"published" if course.is_published else "DRAFT"})'
                ))
                seeded += 1

        if only and seeded == 0:
            raise CommandError(f'No curriculum defines the course slug "{only}".')

        self.stdout.write(self.style.SUCCESS(
            f'Sindh Board curricula seeded ({seeded} course(s)).'
        ))
