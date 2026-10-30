"""Award achievement badges from verified learning progress."""

from django.db import transaction

from ..models import (
    Achievement,
    Chapter,
    Enrollment,
    LessonProgress,
    UserAchievement,
    UserProfile,
)
from .xp import award_xp


@transaction.atomic
def award_eligible_achievements(user, *, lesson=None):
    completed_lessons = LessonProgress.objects.filter(
        user=user, status__in=['completed', 'mastered'],
    ).count()
    completed_course_slugs = set(Enrollment.objects.filter(
        user=user, status='completed',
    ).values_list('course__slug', flat=True))
    profile, _ = UserProfile.objects.get_or_create(user=user)

    completed_chapter = False
    if lesson is not None:
        active_lessons = lesson.chapter.lessons.filter(is_active=True)
        total_lessons = active_lessons.count()
        completed_chapter = total_lessons > 0 and LessonProgress.objects.filter(
            user=user,
            lesson__in=active_lessons,
            status__in=['completed', 'mastered'],
        ).count() == total_lessons

    for achievement in Achievement.objects.filter(is_active=True):
        condition = achievement.condition_type
        if condition == 'lesson_complete':
            try:
                required = max(1, int(achievement.condition_value or 1))
            except ValueError:
                required = 1
            eligible = completed_lessons >= required
        elif condition == 'chapter_complete':
            eligible = completed_chapter
        elif condition == 'course_complete':
            eligible = not achievement.condition_value or achievement.condition_value in completed_course_slugs
        elif condition == 'streak_7':
            eligible = profile.streak_days >= 7
        else:
            eligible = False

        if not eligible:
            continue

        _, created = UserAchievement.objects.get_or_create(
            user=user, achievement=achievement,
        )
        if created and achievement.xp_bonus > 0:
            award_xp(
                user,
                achievement.xp_bonus,
                'achievement_bonus',
                obj=achievement,
                description=f'Achievement earned: {achievement.title}',
            )