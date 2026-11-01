"""Centralized, integrity-safe XP awarding.

Every XP balance change on the platform flows through :func:`award_xp` so
that:

- XP is computed on the server, never trusted from the client.
- Each logical award produces exactly one ``XPTransaction`` — enforced both
  by ``transaction.atomic()`` and by a database-level unique constraint on
  (user, action, content reference) for award actions. Concurrent duplicate
  requests therefore cannot double-award.
- The cached ``UserProfile.xp_points`` balance is updated with an atomic
  ``F()`` expression inside the same transaction, keeping the ledger and the
  balance synchronized.
"""

import logging
from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction
from django.db.models import F
from django.db.models.functions import Greatest
from django.utils import timezone

from ..models import UserProfile, XPTransaction

logger = logging.getLogger(__name__)
XP_PER_LEVEL = 500


def _update_profile_progress(profile, *, record_activity=False):
    profile.refresh_from_db(fields=['xp_points', 'level', 'streak_days', 'last_active_at'])
    level = max(1, profile.xp_points // XP_PER_LEVEL + 1)
    updates = {'level': level}

    if record_activity:
        now = timezone.now()
        today = timezone.localdate(now)
        previous_day = timezone.localtime(profile.last_active_at).date() if profile.last_active_at else None
        if previous_day != today:
            profile.streak_days = profile.streak_days + 1 if previous_day == today - timedelta(days=1) else 1
            profile.last_active_at = now
            updates.update(streak_days=profile.streak_days, last_active_at=now)
            # A personal-best streak is the only honest "record": notify once,
            # when the current run exceeds every previous one.
            if profile.streak_days > profile.longest_streak:
                profile.longest_streak = profile.streak_days
                updates['longest_streak'] = profile.longest_streak
                from .notifications import create_notification
                from ..models import UserNotification
                create_notification(
                    profile.user,
                    type=UserNotification.Type.STREAK_RECORD,
                    title=f'{profile.streak_days}-day streak!',
                    body='You are learning every day — keep the run alive.',
                    link='/achievements',
                )

    if profile.level != level or len(updates) > 1:
        UserProfile.objects.filter(pk=profile.pk).update(**updates)


@transaction.atomic
def award_xp(user, amount: int, action: str, *, obj=None,
             description: str = '') -> XPTransaction | None:
    """Create one XP transaction and apply it to the balance, exactly once.

    Returns the created (immutable) transaction, or ``None`` when an
    identical award already exists — the caller then reports 0 XP awarded
    rather than silently double-counting.

    ``obj`` is the content item being awarded for (a Lesson, Exercise,
    Chapter, or Course). For award-class actions the database's unique
    constraint makes the guard safe against races: if two concurrent
    requests both pass the pre-check, the loser's INSERT is rejected.
    """
    if amount <= 0:
        return None

    UserProfile.objects.get_or_create(user=user)
    profile = UserProfile.objects.select_for_update().get(user=user)
    content_type = ContentType.objects.get_for_model(obj) if obj is not None else None
    object_id = obj.pk if obj is not None else None

    already = XPTransaction.objects.filter(
        user=user, action=action,
        content_type=content_type, object_id=object_id,
    ).exists()
    if already and action in XPTransaction.UNIQUE_AWARD_ACTIONS:
        return None

    try:
        # Isolate a conflicting insert in a savepoint so the surrounding
        # transaction remains usable after PostgreSQL rejects a duplicate.
        with transaction.atomic():
            xp_tx = XPTransaction.objects.create(
                user=user,
                amount=amount,
                action=action,
                description=description,
                content_type=content_type,
                object_id=object_id,
            )
    except IntegrityError:
        # Lost a race against an identical concurrent award — the winner has
        # already recorded (and applied) the transaction. Never award twice.
        logger.info(
            'Suppressed duplicate XP award: user=%s action=%s ref=%s:%s',
            getattr(user, 'pk', user), action,
            getattr(content_type, 'model', None), object_id,
        )
        return None

    UserProfile.objects.filter(user=user).update(xp_points=F('xp_points') + amount)
    _update_profile_progress(profile, record_activity=True)
    return xp_tx


@transaction.atomic
def deduct_xp(user, amount: int, action: str, *, obj=None,
              description: str = '') -> XPTransaction | None:
    """Record a (possibly negative) XP deduction, e.g. a hint penalty.

    ``amount`` is a positive magnitude; the transaction stores it as a
    negative number and the cached balance is floored at zero.
    """
    if amount <= 0:
        return None

    content_type = ContentType.objects.get_for_model(obj) if obj is not None else None
    object_id = obj.pk if obj is not None else None

    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile = UserProfile.objects.select_for_update().get(pk=profile.pk)
    is_unique_deduction = action == 'hint_used' and content_type is not None and object_id is not None
    if (action in XPTransaction.UNIQUE_AWARD_ACTIONS or is_unique_deduction) and XPTransaction.objects.filter(
        user=user, action=action, content_type=content_type, object_id=object_id,
    ).exists():
        return None

    actual_deduction = min(amount, profile.xp_points)
    if actual_deduction <= 0:
        return None

    try:
        with transaction.atomic():
            xp_tx = XPTransaction.objects.create(
                user=user,
                amount=-actual_deduction,
                action=action,
                description=description,
                content_type=content_type,
                object_id=object_id,
            )
    except IntegrityError:
        logger.info(
            'Suppressed duplicate XP deduction: user=%s action=%s ref=%s:%s',
            getattr(user, 'pk', user), action,
            getattr(content_type, 'model', None), object_id,
        )
        return None

    UserProfile.objects.filter(user=user).update(
        xp_points=Greatest(F('xp_points') - actual_deduction, 0),
    )
    _update_profile_progress(profile)
    return xp_tx
