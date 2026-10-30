"""Server-side course-completion evaluation.

Course completion is a fact derived from the learner's real, server-recorded
progress — never from a client assertion. This module turns an ``Enrollment``
to ``status='completed'`` (recording the timestamp and awarding the one-time
course-completion XP) only once every configured requirement is genuinely met.

Requirements evaluated (all gated by the course's own configuration):
- Every active lesson is completed (when ``require_all_lessons`` is set).
- The final-assessment exercises are passed at or above the configured
  ``certification_passing_score`` (when ``require_final_assessment`` is set).
"""

from django.db import transaction
from django.utils import timezone

from ..models import (
    Course, Enrollment, Exercise, Lesson, LessonProgress,
)


def _lessons_completed(user, course: Course):
    total = Lesson.objects.filter(
        chapter__course=course, chapter__is_active=True, is_active=True,
    ).count()
    done = LessonProgress.objects.filter(
        user=user,
        lesson__chapter__course=course,
        lesson__is_active=True,
        status__in=['completed', 'mastered'],
    ).count()
    return done, total


def _final_assessment_passed(user, course: Course) -> bool:
    """True when every final-assessment exercise has a server-graded pass."""
    items = Exercise.objects.filter(
        lesson__chapter__course=course,
        lesson__chapter__is_active=True,
        lesson__is_active=True,
        is_final_assessment=True,
        is_active=True,
    )
    total = items.count()
    if total == 0:
        # Nothing to grade against: do not fabricate completion.
        return False
    passed = items.filter(
        attempts__user=user, attempts__status='correct',
    ).distinct().count()
    return round((passed / total) * 100, 1) >= course.certification_passing_score


def is_course_complete(user, course: Course) -> bool:
    """Pure check: does the learner currently satisfy every course rule?"""
    if not Enrollment.objects.filter(user=user, course=course).exists():
        return False

    if course.require_all_lessons:
        done, total = _lessons_completed(user, course)
        if total == 0 or done < total:
            return False

    if course.require_final_assessment and not _final_assessment_passed(user, course):
        return False

    return True


@transaction.atomic
def evaluate_course_completion(user, course: Course):
    """Recompute and persist the enrollment's completion state.

    Idempotent and safe to call on every progress-changing event. Returns the
    (possibly unchanged) enrollment. No extra XP is granted here: every lesson
    and exercise already awarded its own server-guarded XP, so completion is
    the sum of genuinely-earned merit and is never re-counted.
    """
    enrollment = (
        Enrollment.objects.select_for_update()
        .filter(user=user, course=course)
        .first()
    )
    if enrollment is None:
        return None

    if enrollment.status != 'completed':
        if is_course_complete(user, course):
            enrollment.status = 'completed'
            enrollment.completed_at = timezone.now()
            enrollment.save(update_fields=['status', 'completed_at'])
    return enrollment
