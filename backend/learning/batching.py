"""Per-request batch loaders that collapse serializer N+1 queries.

The database now lives on hosted Supabase Postgres, so every extra
round trip costs tens of milliseconds instead of microseconds. A
course page that once ran hundreds of COUNT/EXISTS queries against
local SQLite became seconds-slow. These helpers answer the same
questions with a single grouped query per request, memoised in the
shared DRF serializer context dict (nested serializers receive
``context=self.context``, so the cache is shared across the render).

Semantics are kept byte-for-byte identical to the original per-object
queries; when no context is available (scripts, direct instantiation)
callers fall back to the model properties.
"""

from django.db.models import Count, Sum

from .models import (
    Chapter, Course, Enrollment, Exercise, Hint, Lesson, LessonProgress,
)


def _cached(context, key, builder):
    """Memoise ``builder()`` in the shared serializer context dict."""
    if context is None:
        return None
    if key not in context:
        context[key] = builder()
    return context[key]


def _build_course_stats():
    """{course_id: {chapters, lessons, exercises, xp, minutes, lessons_all}}

    ``lessons``/``exercises`` count only active content (mirrors the
    Course.lesson_count / exercise_count / total_xp properties);
    ``lessons_all`` is unfiltered (mirrors Enrollment.progress_percentage).
    """
    stats = {}

    def bucket(course_id):
        return stats.setdefault(
            course_id,
            {'chapters': 0, 'lessons': 0, 'exercises': 0,
             'lesson_xp': 0, 'exercise_xp': 0, 'minutes': 0, 'lessons_all': 0},
        )

    for row in (
        Chapter.objects.filter(is_active=True)
        .values('course_id').annotate(n=Count('id'))
    ):
        bucket(row['course_id'])['chapters'] = row['n']
    for row in (
        Lesson.objects.filter(chapter__is_active=True, is_active=True)
        .values('chapter__course_id')
        .annotate(n=Count('id'), xp=Sum('xp_reward'), minutes=Sum('duration_minutes'))
    ):
        b = bucket(row['chapter__course_id'])
        b['lessons'] = row['n']
        b['lesson_xp'] = row['xp'] or 0
        b['minutes'] = row['minutes'] or 0
    for row in (
        Lesson.objects.values('chapter__course_id').annotate(n=Count('id'))
    ):
        bucket(row['chapter__course_id'])['lessons_all'] = row['n']
    for row in (
        Exercise.objects.filter(
            lesson__chapter__is_active=True, lesson__is_active=True, is_active=True,
        )
        .values('lesson__chapter__course_id')
        .annotate(n=Count('id'), xp=Sum('xp_reward'))
    ):
        b = bucket(row['lesson__chapter__course_id'])
        b['exercises'] = row['n']
        b['exercise_xp'] = row['xp'] or 0
    for b in stats.values():
        b['xp'] = b['lesson_xp'] + b['exercise_xp']
    return stats


def course_stats(context):
    return _cached(context, '_batch_course_stats', _build_course_stats)


def _build_published_courses_by_track():
    """{track_id: [course_id, ...]} for learner-visible (published) courses."""
    grouped = {}
    order = Course.objects.filter(is_active=True, is_published=True).order_by(
        'order', 'title'
    ).values_list('track_id', 'id')
    for track_id, course_id in order:
        grouped.setdefault(track_id, []).append(course_id)
    return grouped


def published_courses_by_track(context):
    return _cached(context, '_batch_published_courses', _build_published_courses_by_track)


def _build_exercise_counts_by_lesson():
    rows = (
        Exercise.objects.filter(is_active=True)
        .values('lesson_id').annotate(n=Count('id'))
    )
    return {row['lesson_id']: row['n'] for row in rows}


def exercise_counts_by_lesson(context):
    return _cached(context, '_batch_exercise_counts', _build_exercise_counts_by_lesson)


def _build_hint_counts_by_exercise():
    rows = Hint.objects.values('exercise_id').annotate(n=Count('id'))
    return {row['exercise_id']: row['n'] for row in rows}


def hint_counts_by_exercise(context):
    return _cached(context, '_batch_hint_counts', _build_hint_counts_by_exercise)


def _build_final_assessment_chapters():
    return set(
        Exercise.objects.filter(
            is_final_assessment=True, is_active=True, lesson__is_active=True,
        ).values_list('lesson__chapter_id', flat=True)
    )


def final_assessment_chapter_ids(context):
    return _cached(context, '_batch_final_assessment', _build_final_assessment_chapters)


def _request_user(context):
    request = context.get('request') if context is not None else None
    user = getattr(request, 'user', None)
    return user if getattr(user, 'is_authenticated', False) else None


def lesson_progress_map(context):
    """{lesson_id: status} for the requester. One query per request."""
    user = _request_user(context)
    if user is None:
        return {}

    def build():
        rows = LessonProgress.objects.filter(user=user).values_list('lesson_id', 'status')
        latest = {}
        for lesson_id, status in rows:
            # Prefer the strongest state seen for a lesson.
            if status in ('completed', 'mastered') or lesson_id not in latest:
                latest[lesson_id] = status
        return latest

    return _cached(context, f'_batch_progress_{user.pk}', build)


def completed_lessons_by_course(context, statuses=('completed', 'mastered')):
    """{course_id: completed lesson count} for the requester (active lessons)."""
    user = _request_user(context)
    if user is None:
        return {}

    def build():
        rows = (
            LessonProgress.objects
            .filter(user=user, lesson__is_active=True, status__in=statuses)
            .values('lesson__chapter__course_id').annotate(n=Count('id'))
        )
        return {row['lesson__chapter__course_id']: row['n'] for row in rows}

    key = f'_batch_completed_by_course_{user.pk}_{"-".join(sorted(statuses))}'
    return _cached(context, key, build)


def completed_by_course_any(context, statuses=('completed', 'mastered')):
    """{course_id: count} with no active-content filtering, matching
    CourseDetailSerializer's original progress queries verbatim."""
    user = _request_user(context)
    if user is None:
        return {}

    def build():
        rows = (
            LessonProgress.objects
            .filter(user=user, status__in=statuses)
            .values('lesson__chapter__course_id').annotate(n=Count('id'))
        )
        return {row['lesson__chapter__course_id']: row['n'] for row in rows}

    key = f'_batch_any_completed_{user.pk}_{{}}'.format('-'.join(sorted(statuses)))
    return _cached(context, key, build)


def enrollment_completed_by_course(context):
    """{course_id: completed count} exactly as Enrollment.progress_percentage
    computes it (status='completed', no active-content filters)."""
    user = _request_user(context)
    if user is None:
        return {}

    def build():
        rows = (
            LessonProgress.objects
            .filter(user=user, status='completed')
            .values('lesson__chapter__course_id').annotate(n=Count('id'))
        )
        return {row['lesson__chapter__course_id']: row['n'] for row in rows}

    return _cached(context, f'_batch_enroll_completed_{user.pk}', build)


def enrollment_map(context):
    """{course_id: Enrollment} for the requester. One query per request."""
    user = _request_user(context)
    if user is None:
        return {}

    def build():
        return {
            e.course_id: e
            for e in Enrollment.objects.filter(user=user).select_related(
                'course', 'last_lesson'
            )
        }

    return _cached(context, f'_batch_enrollments_{user.pk}', build)


def course_total_xp(context, course_id, fallback=None):
    stats = course_stats(context)
    if stats is None:
        return fallback
    entry = stats.get(course_id)
    return entry['xp'] if entry else 0


def course_estimated_hours(context, course, fallback_value=None):
    """Mirror Course.estimated_hours: manual override wins, else derived."""
    if course.manual_estimated_hours:
        return course.manual_estimated_hours
    stats = course_stats(context)
    if stats is None:
        return fallback_value
    entry = stats.get(course.id)
    minutes = entry['minutes'] if entry else 0
    return max(1, round(minutes / 60))
