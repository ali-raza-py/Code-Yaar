"""Administrative analytics for the dashboard command centre (spec section 2).

Every number here comes from real rows, because an administrator makes staffing and
curriculum decisions from this screen, and an invented figure is worse than no figure.

Two rules hold throughout. *Aggregation happens in the database*: each series is one
grouped query, because the flat admin serializers counted lessons and enrolments per
row - the N+1 pattern the specification forbids. *Nothing is reported that the data
cannot support*: the spec asks for a quiz performance chart and cards for Hackathon
Leads and Campus Ambassadors, but there is no quiz model (question types live inside
``Exercise``) and no leadership model, so those come back as explicitly unavailable
with a reason instead of a zero that reads as "no leaders" rather than "not tracked".
"""

import csv
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Count, Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import (
    CareerTrack, Competition, CompetitionRegistration, Course, Enrollment,
    ExerciseAttempt, LearningActivity, Lesson, LessonProgress, UserCertification, UserProfile,
)
from .permissions import HasAdminCapability
from .services.admin_access import ANALYTICS_EXPORT, ANALYTICS_VIEW
from .services.auth import user_role

#: How far back "over time" charts reach when the caller supplies no range.
DEFAULT_WINDOW_DAYS = 90

#: Largest cohort matrix returned; a wider retention grid is unreadable and slow.
MAX_RETENTION_MONTHS = 6

BUCKETS = {'day': TruncDate, 'week': TruncWeek, 'month': TruncMonth}

#: Days per bucket, used to walk the axis so quiet periods show as zero instead of
#: vanishing - a chart whose x-axis omits quiet weeks makes a plateau look like a gap.
BUCKET_DAYS = {'day': 1, 'week': 7, 'month': 30}

#: Surfaces the specification asks for that no model can back yet, and why.
UNAVAILABLE = [
    {
        'id': 'quiz_performance',
        'label': 'Quiz performance',
        'reason': 'The quiz / question-bank system is not built yet; question types live '
                  'inside Exercise and are reported under exercise submissions.',
        'phase': 'Priority 2',
    },
    {
        'id': 'leadership_appointments',
        'label': 'Leadership appointments',
        'reason': 'No leadership appointment model exists, so there is no real data to chart.',
        'phase': 'Priority 3',
    },
    {
        'id': 'activity_reports',
        'label': 'Leader activity reports',
        'reason': 'Reporting belongs to the leadership module and does not exist yet.',
        'phase': 'Priority 3',
    },
]


def _resolve_range(request):
    """Return ``(since, until, bucket)`` from ``?from`` / ``?to`` / ``?bucket``."""
    params = request.query_params
    bucket = (params.get('bucket') or 'week').lower()
    if bucket not in BUCKETS:
        bucket = 'week'
    until = parse_date(params.get('to') or '') or timezone.localdate()
    since = parse_date(params.get('from') or '') or (until - timedelta(days=DEFAULT_WINDOW_DAYS))
    if since > until:
        since, until = until, since
    return since, until, bucket


def _series(qs, field, *, since, until, bucket):
    """Group one queryset into ``[{period, value}]`` with contiguous periods filled in."""
    rows = (
        qs.filter(**{f'{field}__date__gte': since}, **{f'{field}__date__lte': until})
        .annotate(period=BUCKETS[bucket](field))
        .values('period')
        .annotate(total=Count('id'))
        .order_by('period')
    )
    found = {}
    for row in rows:
        period = row['period']
        key = period.date() if hasattr(period, 'date') else period
        if key is not None:
            found[key] = row['total']

    stepped = []
    cursor = since
    while cursor <= until:
        stepped.append({'period': cursor.isoformat(), 'value': found.pop(cursor, 0)})
        if bucket == 'month':
            cursor = (cursor.replace(day=1) + timedelta(days=32)).replace(day=1)
        else:
            cursor = cursor + timedelta(days=BUCKET_DAYS[bucket])
    # Anything the database bucketed outside the stepped sequence (a truncation
    # boundary that drifted a day) is still reported rather than dropped.
    stepped.extend({'period': key.isoformat(), 'value': total} for key, total in found.items())
    stepped.sort(key=lambda row: row['period'])
    return stepped


def _retention(since, until):
    """Cohort retention by month of registration, inside the requested window.

    A cohort is the students who registered in a given month; a cell is how many of them
    were active in the Nth month after that. Counts are distinct users, so a learner who
    did six things in a month is still one learner.
    """
    rows = (
        LearningActivity.objects.filter(
            occurred_at__date__gte=since, occurred_at__date__lte=until,
            user__date_joined__isnull=False,
        )
        .annotate(cohort=TruncMonth('user__date_joined'), active=TruncMonth('occurred_at'))
        .values('cohort', 'active')
        .annotate(learners=Count('user', distinct=True))
        .order_by('cohort', 'active')
    )
    cohorts = {}
    for row in rows:
        cohort, active = row['cohort'], row['active']
        if cohort is None or active is None:
            continue
        offset = (active.year - cohort.year) * 12 + (active.month - cohort.month)
        if not 0 <= offset <= MAX_RETENTION_MONTHS:
            continue
        key = cohort.date().isoformat()[:7]
        cell = cohorts.setdefault(key, {'cohort': key, 'months': {}})
        cell['months'][f'month_{offset}'] = row['learners']

    sizes = {}
    for row in (
        UserProfile.objects.filter(role='student', user__is_active=True)
        .annotate(month=TruncMonth('user__date_joined'))
        .values('month').annotate(count=Count('id')).order_by('month')
    ):
        if row['month'] is not None:
            sizes[row['month'].date().isoformat()[:7]] = row['count']
    for key, cell in cohorts.items():
        cell['cohort_size'] = sizes.get(key, 0)
    return [cohorts[key] for key in sorted(cohorts)[-12:]]


def _overview_payload(request):
    since, until, bucket = _resolve_range(request)

    students = UserProfile.objects.filter(role='student', user__is_active=True)
    active_profiles = UserProfile.objects.filter(
        user__is_active=True, last_active_at__isnull=False,
    ).exclude(role='admin')

    enrollments_all = Enrollment.objects.all()
    # One grouped aggregate per model instead of two COUNT round trips
    # each - the hosted database charges a visible round trip per query.
    enrollment_counts = enrollments_all.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='completed')),
    )
    total_enrollments = enrollment_counts['total']
    completed_enrollments = enrollment_counts['completed']
    attempt_counts = ExerciseAttempt.objects.aggregate(
        total=Count('id'),
        correct=Count('id', filter=Q(status='correct')),
    )
    total_attempts = attempt_counts['total']
    correct_attempts = attempt_counts['correct']

    top_courses = list(
        Course.objects.filter(is_published=True, is_active=True)
        .annotate(
            learners=Count('enrollments', distinct=True),
            finishers=Count('enrollments',
                            filter=Q(enrollments__status='completed'), distinct=True),
            lesson_count=Count('chapters__lessons', distinct=True),
        )
        .order_by('-learners', 'title')[:10]
        .values('id', 'title', 'slug', 'learners', 'finishers', 'lesson_count')
    )
    for course in top_courses:
        learners = course['learners']
        course['completion_rate'] = (
            round(course['finishers'] / learners * 100) if learners else 0
        )

    top_tracks = list(
        CareerTrack.objects.filter(is_published=True, is_active=True)
        .annotate(
            course_count=Count('courses', distinct=True),
            learners=Count('courses__enrollments', distinct=True),
        )
        .order_by('-learners', 'title')[:10]
        .values('id', 'title', 'slug', 'course_count', 'learners')
    )

    # Drop-off per lesson: of the course's enrolments, how many finished this
    # lesson. Split into two grouped queries joined in Python - the previous
    # single annotate chain joined BOTH enrollments and progress rows per
    # lesson, and the two-path join fan-out made it the slowest query on the
    # platform (measured ~1.9s). Semantics are unchanged: completions counts
    # progress rows with status='completed'; enrolled counts every enrollment
    # row for the lesson's course.
    enrollments_by_course = {
        row['course_id']: row['n']
        for row in Enrollment.objects.values('course_id').annotate(n=Count('id'))
    }
    # One projection query instead of ORM instances: fetching full Lesson
    # rows dragged every lesson's content_body (long text) across the wire
    # only to read three title fields in Python.
    dropoff = [
        {
            'lesson_id': row['id'],
            'lesson': row['title'],
            'course': row['chapter__course__title'],
            'chapter': row['chapter__title'],
            'enrolled': enrollments_by_course.get(row['chapter__course_id'], 0) or 0,
            'completions': row['completions'],
            'completion_rate': (
                round(row['completions'] / enrollments_by_course[row['chapter__course_id']] * 100)
                if enrollments_by_course.get(row['chapter__course_id']) else 0
            ),
        }
        for row in (
            Lesson.objects.filter(is_active=True, chapter__course__is_published=True)
            .annotate(
                completions=Count('progress_entries',
                                  filter=Q(progress_entries__status='completed'), distinct=True),
            )
            .order_by('chapter__course__title', 'chapter__order', 'order')[:80]
            .values('id', 'title', 'chapter__course_id',
                    'chapter__course__title', 'chapter__title', 'completions')
        )
    ]
    worst = sorted(dropoff, key=lambda row: (row['completion_rate'], -row['enrolled']))[:10]

    top_competitions = list(
        Competition.objects.filter(is_published=True)
        .annotate(
            total=Count('registrations', distinct=True),
            waiting=Count('registrations',
                          filter=Q(registrations__registration_status='pending'), distinct=True),
        )
        .order_by('-total', 'title')[:10]
        .values('id', 'title', 'slug', 'total', 'waiting')
    )

    # Both head-line student numbers describe the same rows, so one grouped
    # aggregate answers both — each extra query is a full network round trip.
    # The base queryset is already role='student', which subsumes the
    # active_profiles queryset's ~role='admin' exclusion.
    student_counts = students.aggregate(
        total=Count('id'),
        recently_active=Count(
            'id',
            filter=Q(
                last_active_at__isnull=False,
                last_active_at__date__gte=timezone.localdate() - timedelta(days=28),
            ),
        ),
    )
    student_total = student_counts['total']
    recently_active = student_counts['recently_active']

    # One grouped status count answers total, pending and the breakdown;
    # three COUNTs used to cost three round trips each page load.
    registration_by_status = {
        row['registration_status']: row['count']
        for row in (
            CompetitionRegistration.objects.values('registration_status')
            .annotate(count=Count('id')).order_by('-count')
        )
    }

    return {
        'range': {'from': since.isoformat(), 'to': until.isoformat(), 'bucket': bucket},
        'students': {
            'registrations': _series(students, 'user__date_joined',
                                     since=since, until=until, bucket=bucket),
            'active': _series(active_profiles, 'last_active_at',
                              since=since, until=until, bucket=bucket),
            'total_students': student_total,
            'engagement_rate': round(recently_active / student_total * 100, 1)
            if student_total else 0,
        },
        'education': {
            'enrollments': _series(enrollments_all, 'enrolled_at',
                                   since=since, until=until, bucket=bucket),
            'completions': _series(enrollments_all.filter(status='completed'), 'completed_at',
                                   since=since, until=until, bucket=bucket),
            'lesson_completions': _series(
                LessonProgress.objects.filter(status='completed'), 'completed_at',
                since=since, until=until, bucket=bucket),
            'exercise_submissions': _series(ExerciseAttempt.objects.all(), 'created_at',
                                            since=since, until=until, bucket=bucket),
            'activity': _series(LearningActivity.objects.all(), 'occurred_at',
                                since=since, until=until, bucket=bucket),
            'enrollment_completion_rate': (
                round(completed_enrollments / total_enrollments * 100, 1)
                if total_enrollments else 0
            ),
            'exercise_pass_rate': (
                round(correct_attempts / total_attempts * 100, 1) if total_attempts else 0
            ),
            'exercise_attempts': {'total': total_attempts, 'correct': correct_attempts},
            # Plain totals next to the series, so a card does not have to sum buckets
            # (and does not disagree with the chart when a bucket is outside the window).
            'total_enrollments': total_enrollments,
            'completed_enrollments': completed_enrollments,
            'total_lesson_completions': LessonProgress.objects.filter(
                status='completed').count(),
            'top_courses': top_courses,
            'top_tracks': top_tracks,
            'dropoff': {'lessons': dropoff, 'worst': worst},
            'retention': _retention(since, until),
        },
        'competitions': {
            'registrations': _series(CompetitionRegistration.objects.all(), 'registered_at',
                                     since=since, until=until, bucket=bucket),
            'total_registrations': sum(registration_by_status.values()),
            'pending_approval': registration_by_status.get('pending', 0),
            'by_status': [
                {'registration_status': status, 'count': count}
                for status, count in registration_by_status.items()
            ],
            'top_competitions': top_competitions,
        },
        'unavailable': UNAVAILABLE,
    }


@api_view(['GET'])
@permission_classes([HasAdminCapability])
def admin_analytics_overview(request):
    """Time-bounded platform analytics for the admin dashboard charts.

    The payload is the same truth the CSV export reads, but it costs ~20
    grouped queries; the admin convention of a short (15 s) cache - same
    as top-courses and recent-activity - collapses repeat chart refreshes
    without showing an administrator anything the database does not hold.
    """
    since, until, bucket = _resolve_range(request)
    cache_key = f'admin-analytics-overview-{since}-{until}-{bucket}'
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached)
    payload = _overview_payload(request)
    cache.set(cache_key, payload, 15)
    return Response(payload)


# ``@api_view`` builds a view class behind the scenes; the permission instance the
# request is checked against is *that* class, so the capability has to be declared on
# ``.cls``. Setting it on the decorated function looks harmless and is not - the
# check would silently fall back to "any administrator", which would deny a Competition
# Manager their export while letting an instructor read every student record.
admin_analytics_overview.cls.required_admin_capability = ANALYTICS_VIEW


#: Each report is ``(heading, row-builder)`` over an existing queryset, so a CSV is the
#: same truth the dashboard shows rather than a second implementation of it.
CSV_REPORTS = {
    'registrations': (
        ['name', 'email', 'role', 'joined_at', 'active'],
        lambda: (
            {
                'name': ' '.join(p for p in (u.first_name, u.last_name) if p) or u.username,
                'email': u.email, 'role': user_role(u),
                'joined_at': u.date_joined.isoformat(),
                'active': 'yes' if u.is_active else 'no',
            }
            for u in User.objects.order_by('date_joined')
        ),
    ),
    'enrollments': (
        ['student', 'course', 'status', 'enrolled_at', 'completed_at'],
        lambda: (
            {
                'student': e.user.username, 'course': e.course.title,
                'status': e.status, 'enrolled_at': e.enrolled_at.isoformat(),
                'completed_at': e.completed_at.isoformat() if e.completed_at else '',
            }
            for e in Enrollment.objects.select_related('user', 'course').order_by('enrolled_at')
        ),
    ),
    'completions': (
        ['student', 'course', 'completed_at'],
        lambda: (
            {
                'student': e.user.username, 'course': e.course.title,
                'completed_at': e.completed_at.isoformat(),
            }
            for e in Enrollment.objects.filter(status='completed')
            .select_related('user', 'course').order_by('completed_at')
        ),
    ),
    'exercise_submissions': (
        ['student', 'course', 'lesson', 'exercise', 'status', 'submitted_at'],
        lambda: (
            {
                'student': a.user.username,
                'course': a.exercise.lesson.chapter.course.title,
                'lesson': a.exercise.lesson.title,
                'exercise': a.exercise.title, 'status': a.status,
                'submitted_at': a.created_at.isoformat(),
            }
            for a in ExerciseAttempt.objects.select_related(
                'user', 'exercise', 'exercise__lesson', 'exercise__lesson__chapter',
                'exercise__lesson__chapter__course',
            ).order_by('created_at')
        ),
    ),
    'certificates': (
        ['student', 'email', 'certification', 'credential_id', 'earned_at'],
        lambda: (
            {
                'student': c.user.username, 'email': c.user.email,
                'certification': c.certification.title, 'credential_id': c.credential_id,
                'earned_at': c.earned_at.isoformat(),
            }
            for c in UserCertification.objects.select_related(
                'user', 'certification',
            ).order_by('earned_at')
        ),
    ),
    'competition_registrations': (
        ['competition', 'student', 'status', 'registered_at'],
        lambda: (
            {
                'competition': r.competition.title, 'student': r.user.username,
                'status': r.registration_status,
                'registered_at': r.registered_at.isoformat(),
            }
            for r in CompetitionRegistration.objects.select_related(
                'competition', 'user',
            ).order_by('registered_at')
        ),
    ),
}


@api_view(['GET'])
@permission_classes([HasAdminCapability])
def admin_analytics_export(request):
    """Stream a report as CSV for offline analysis and institutional reporting.

    Only rows the caller's role may already see are exported; there is no separate
    narrower filter per report, because the underlying data is platform-wide and the
    export capability (``ANALYTICS_EXPORT``) is deliberately stronger than view.
    """
    report = (request.query_params.get('report') or '').strip()
    if report not in CSV_REPORTS:
        return Response({
            'detail': f'Unknown report "{report}".',
            'available': sorted(CSV_REPORTS),
        }, status=400)

    heading, rows = CSV_REPORTS[report]
    response = HttpResponse(content_type='text/csv')
    filename = f'codeyaar-{report}-{timezone.localdate().isoformat()}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(heading)
    for row in rows():
        writer.writerow([row.get(column, '') for column in heading])
    return response


admin_analytics_export.cls.required_admin_capability = ANALYTICS_EXPORT
