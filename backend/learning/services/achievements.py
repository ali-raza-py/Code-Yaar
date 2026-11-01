"""Award achievement badges from verified learning progress.

The single measure of truth for every condition type is
:func:`measure_progress`, which derives ``(current, target)`` purely from
server-recorded activity rows — lessons, exercise attempts, challenge
submissions, enrolments, and the streak on ``UserProfile``. A badge is only
ever granted when ``current >= target``; progress toward locked badges uses
the same function, so a learner can never see a claim the database does not
back. Duplicate awards are impossible at the database level via
``UserAchievement``'s unique (user, achievement) constraint.
"""

from django.db import transaction

from ..models import (
    Achievement,
    Challenge,
    ChallengeSubmission,
    Chapter,
    Enrollment,
    ExerciseAttempt,
    LessonProgress,
    UserAchievement,
    UserProfile,
)
from .notifications import create_notification
from .xp import award_xp


def _parse_target(value: str, default: int = 1) -> int:
    try:
        return max(1, int(value or default))
    except ValueError:
        return default


def _completed_lessons(user):
    return LessonProgress.objects.filter(
        user=user, status__in=['completed', 'mastered'],
    ).count()


def _completed_course_slugs(user):
    return set(Enrollment.objects.filter(
        user=user, status='completed',
    ).values_list('course__slug', flat=True))


def _exercises_passed(user):
    return ExerciseAttempt.objects.filter(
        user=user, status='correct',
    ).values('exercise').distinct().count()


def _challenges_solved(user, topic_prefix: str | None = None):
    solved = (
        ChallengeSubmission.objects
        .filter(user=user, status='correct')
        .values_list('challenge_id', flat=True)
        .distinct()
    )
    if topic_prefix is None:
        return Challenge.objects.filter(pk__in=solved).count()
    return Challenge.objects.filter(
        pk__in=solved, topic__icontains=topic_prefix,
    ).count()


def _project_course_completions(user):
    """Completed enrolments in tracks that actually offer projects."""
    return (
        Enrollment.objects
        .filter(user=user, status='completed', course__track__projects__isnull=False)
        .values('course').distinct().count()
    )


def _any_activity(user):
    return (
        _completed_lessons(user) > 0
        or _exercises_passed(user) > 0
        or _challenges_solved(user) > 0
    )


def _chapter_completed(user, lesson=None):
    """True when every active lesson of any one chapter is completed.

    When ``lesson`` is supplied, only its chapter is examined — the cheap
    path used on every lesson completion.
    """
    chapters = (
        [lesson.chapter] if lesson is not None
        else list(Chapter.objects.filter(is_active=True))
    )
    for chapter in chapters:
        active_lessons = chapter.lessons.filter(is_active=True)
        total = active_lessons.count()
        if total and LessonProgress.objects.filter(
            user=user, lesson__in=active_lessons,
            status__in=['completed', 'mastered'],
        ).count() == total:
            return True
    return False


def measure_progress(user, achievement) -> tuple[int, int]:
    """Return (current, target) for one badge from real rows. Never stored."""
    condition = achievement.condition_type
    value = achievement.condition_value or ''

    if condition == 'lesson_complete':
        return _completed_lessons(user), _parse_target(value)
    if condition == 'chapter_complete':
        return (1 if _chapter_completed(user) else 0), 1
    if condition in ('course_complete', 'project_course_complete'):
        if condition == 'course_complete' and value and not value.isdigit():
            # Course-slug pinned award: binary — done or not.
            return (1 if value in _completed_course_slugs(user) else 0), 1
        if condition == 'project_course_complete':
            return _project_course_completions(user), _parse_target(value, default=1)
        # Numeric target: count of completed courses (0 = any single course).
        target = _parse_target(value) if value.isdigit() else 1
        return len(_completed_course_slugs(user)), target
    if condition == 'exercise_correct_count':
        return _exercises_passed(user), _parse_target(value)
    if condition == 'challenge_count':
        return _challenges_solved(user), _parse_target(value)
    if condition == 'challenge_topic_count':
        topic, _, count = value.partition(':')
        return _challenges_solved(user, topic_prefix=topic), _parse_target(count or '1')
    if condition in ('streak_n', 'streak_7'):
        target = 7 if condition == 'streak_7' else _parse_target(value)
        profile = UserProfile.objects.filter(user=user).first()
        return (profile.streak_days if profile else 0), target
    if condition == 'first_activity':
        return (1 if _any_activity(user) else 0), 1
    if condition == 'account':
        return 1, 1
    return 0, 1


def _is_eligible(user, achievement, lesson=None) -> bool:
    condition = achievement.condition_type
    if condition == 'chapter_complete':
        return _chapter_completed(user, lesson=lesson)
    if achievement.slug == 'excellence-award':
        # Requires BOTH a 7-day streak and at least one completed course.
        profile = UserProfile.objects.filter(user=user).first()
        return bool(profile and profile.streak_days >= 7
                    and _completed_course_slugs(user))
    current, target = measure_progress(user, achievement)
    return current >= target


@transaction.atomic
def award_eligible_achievements(user, *, lesson=None) -> list[UserAchievement]:
    """Grant every badge the learner has genuinely earned; return new awards.

    Called from lesson/exercise/challenge completion paths. The returned list
    lets API responses announce newly unlocked badges without a second query
    round; existing awards are never re-created or re-notified.
    """
    newly_awarded: list[UserAchievement] = []
    already_earned = set(UserAchievement.objects.filter(
        user=user,
    ).values_list('achievement_id', flat=True))

    for achievement in Achievement.objects.filter(is_active=True):
        if achievement.pk in already_earned:
            continue
        if not _is_eligible(user, achievement, lesson=lesson):
            continue

        # get_or_create keeps a concurrent duplicate request from violating
        # the (user, achievement) unique constraint; only the winner notifies.
        created, was_new = UserAchievement.objects.get_or_create(
            user=user, achievement=achievement,
        )
        if not was_new:
            continue
        newly_awarded.append(created)
        if achievement.xp_bonus > 0:
            award_xp(
                user,
                achievement.xp_bonus,
                'achievement_bonus',
                obj=achievement,
                description=f'Achievement earned: {achievement.title}',
            )
        create_notification(
            user,
            type='badge_unlock',
            title=f'Badge unlocked: {achievement.title}',
            body=achievement.description,
            link=f'/achievements?badge={achievement.slug}',
        )
    return newly_awarded
