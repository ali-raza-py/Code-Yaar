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

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction
from django.db.models import F
from django.db.models.functions import Greatest

from ..models import UserProfile, XPTransaction

logger = logging.getLogger(__name__)


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

    content_type = ContentType.objects.get_for_model(obj) if obj is not None else None
    object_id = obj.pk if obj is not None else None

    already = XPTransaction.objects.filter(
        user=user, action=action,
        content_type=content_type, object_id=object_id,
    ).exists()
    if already and action in XPTransaction.UNIQUE_AWARD_ACTIONS:
        return None

    try:
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

    xp_tx = XPTransaction.objects.create(
        user=user,
        amount=-amount,
        action=action,
        description=description,
        content_type=content_type,
        object_id=object_id,
    )
    UserProfile.objects.filter(user=user).update(
        xp_points=Greatest(F('xp_points') - amount, 0),
    )
    return xp_tx
