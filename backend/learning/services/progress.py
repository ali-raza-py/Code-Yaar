"""Helpers for recording meaningful, server-authoritative learning activity."""

from datetime import timedelta

from django.utils import timezone

from ..models import LearningActivity, UserProfile

MEANINGFUL_ACTIVITY_TYPES = (
    'lesson_completed',
    'practical_completed',
    'quiz_attempted',
    'course_completed',
)


def record_learning_activity(
    user,
    activity_type,
    title,
    *,
    course=None,
    lesson=None,
    practical=None,
    exercise=None,
    status='completed',
):
    """Record at most one equivalent event per learner and local calendar day."""
    activity_date = timezone.localdate()
    object_id = (
        getattr(lesson, 'pk', None) or getattr(practical, 'pk', None)
        or getattr(exercise, 'pk', None) or getattr(course, 'pk', None) or 0
    )
    dedupe_key = f'{user.pk}:{activity_type}:{object_id}:{activity_date.isoformat()}'
    activity, created = LearningActivity.objects.get_or_create(
        dedupe_key=dedupe_key,
        defaults={
            'user': user,
            'activity_type': activity_type,
            'title': title,
            'status': status,
            'course': course,
            'lesson': lesson,
            'practical': practical,
            'exercise': exercise,
            'activity_date': activity_date,
        },
    )
    if created:
        UserProfile.objects.filter(user=user).update(last_active_at=timezone.now())
    return activity, created


def streak_summary(user):
    """Return current/longest streaks based on distinct local activity dates."""
    dates = set(
        LearningActivity.objects.filter(
            user=user,
            activity_type__in=MEANINGFUL_ACTIVITY_TYPES,
        )
        .values_list('activity_date', flat=True)
    )
    if not dates:
        return {'current': 0, 'longest': 0, 'active_dates': []}

    ordered = sorted(dates)
    longest = current_run = 1
    for previous, current in zip(ordered, ordered[1:]):
        if (current - previous).days == 1:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 1

    today = timezone.localdate()
    cursor = today if today in dates else today - timedelta(days=1)
    current = 0
    while cursor in dates:
        current += 1
        cursor -= timedelta(days=1)
    return {
        'current': current,
        'longest': longest,
        'active_dates': [date.isoformat() for date in ordered[-90:]],
    }
