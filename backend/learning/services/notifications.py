"""In-app notifications and their companion emails — one responsible service.

Notifications are only ever created here, in response to a server-verified
event, so no code path can announce something that did not really happen.
Every notification type maps to exactly one in-app preference key *and* one
optional-email category; the two are governed independently, so a learner can
mute the in-app feed for competitions yet still receive their confirmation
email — or receive nothing at all.

``create_notification()`` keeps the original in-app-only contract used by the
XP/achievement services. ``notify()`` is the full entry point: it writes the
in-app row (idempotently when a ``dedupe_key`` is supplied) and schedules the
branded email through the centralized email service — after the caller's
database transaction commits, and only once per event even if the same code
path runs repeatedly.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.utils import timezone

from ..models import UserProfile, UserNotification
from . import email_service

logger = logging.getLogger(__name__)

Type = UserNotification.Type
Category = UserNotification.Category

# Notification type → governing graph. ``in_app_pref`` names the account-level
# in-app toggle that can suppress the row (``None`` means the notification is
# always created). ``email_template``/``email_kind`` name the optional email,
# which is additionally gated by the ``email_<kind>`` preference; ``security``
# email kinds are sent regardless of any preference.
_TYPE_GRAPH = {
    # ── Legacy types ──────────────────────────────────────────────────────
    Type.BADGE_UNLOCK: {
        'category': Category.LEARNING, 'in_app_pref': 'achievements',
        'email_template': 'achievement_unlocked', 'email_kind': 'achievement',
    },
    Type.STREAK_RECORD: {
        'category': Category.LEARNING, 'in_app_pref': 'streak_reminders',
        'email_template': None, 'email_kind': None,
    },
    Type.TRACK_COMPLETE: {
        'category': Category.LEARNING, 'in_app_pref': 'learning_reminders',
        'email_template': 'course_completed', 'email_kind': 'learning',
    },
    Type.XP_MILESTONE: {
        'category': Category.LEARNING, 'in_app_pref': 'achievements',
        'email_template': None, 'email_kind': None,
    },
    # ── Account & security ────────────────────────────────────────────────
    Type.WELCOME: {
        'category': Category.ACCOUNT, 'in_app_pref': None,
        'email_template': 'welcome', 'email_kind': 'announcement',
    },
    Type.EMAIL_VERIFIED: {
        'category': Category.ACCOUNT, 'in_app_pref': None,
        'email_template': None, 'email_kind': None,
    },
    Type.PASSWORD_CHANGED: {
        'category': Category.ACCOUNT, 'in_app_pref': None,
        'email_template': 'password_changed', 'email_kind': 'security',
        'security': True,
    },
    Type.ACCOUNT_SECURITY: {
        'category': Category.ACCOUNT, 'in_app_pref': None,
        'email_template': None, 'email_kind': 'security',
        'security': True,
    },
    # ── Learning & practice ───────────────────────────────────────────────
    Type.COURSE_ENROLLED: {
        'category': Category.LEARNING, 'in_app_pref': 'learning_reminders',
        'email_template': 'course_enrolled', 'email_kind': 'learning',
    },
    Type.COURSE_COMPLETED: {
        'category': Category.LEARNING, 'in_app_pref': 'learning_reminders',
        'email_template': 'course_completed', 'email_kind': 'learning',
    },
    Type.STREAK_MILESTONE: {
        'category': Category.LEARNING, 'in_app_pref': 'streak_reminders',
        'email_template': None, 'email_kind': None,
    },
    Type.CHALLENGE_SOLVED: {
        'category': Category.LEARNING, 'in_app_pref': 'learning_reminders',
        'email_template': None, 'email_kind': None,
    },
    # ── Competitions ──────────────────────────────────────────────────────
    Type.COMPETITION_REGISTERED: {
        'category': Category.COMPETITION, 'in_app_pref': 'competitions',
        'email_template': 'competition_registered', 'email_kind': 'competition',
    },
    Type.COMPETITION_APPROVED: {
        'category': Category.COMPETITION, 'in_app_pref': 'competitions',
        'email_template': 'competition_approved', 'email_kind': 'competition',
    },
    Type.COMPETITION_REJECTED: {
        'category': Category.COMPETITION, 'in_app_pref': 'competitions',
        'email_template': 'competition_registration_rejected', 'email_kind': 'competition',
    },
    Type.COMPETITION_WAITLISTED: {
        'category': Category.COMPETITION, 'in_app_pref': 'competitions',
        'email_template': 'competition_waitlisted', 'email_kind': 'competition',
    },
    Type.COMPETITION_REMINDER: {
        'category': Category.COMPETITION, 'in_app_pref': 'competitions',
        'email_template': 'competition_reminder', 'email_kind': 'competition',
    },
    Type.TEAM_INVITATION: {
        'category': Category.COMPETITION, 'in_app_pref': 'competitions',
        'email_template': 'team_invitation', 'email_kind': 'competition',
    },
    Type.COMP_SUBMISSION_RECEIVED: {
        'category': Category.COMPETITION, 'in_app_pref': 'competitions',
        'email_template': 'competition_submission', 'email_kind': 'competition',
    },
    Type.COMP_SUBMISSION_REVIEWED: {
        'category': Category.COMPETITION, 'in_app_pref': 'competitions',
        'email_template': 'competition_submission', 'email_kind': 'competition',
    },
    Type.COMP_RESULTS_PUBLISHED: {
        'category': Category.COMPETITION, 'in_app_pref': 'competitions',
        'email_template': 'competition_result', 'email_kind': 'competition',
    },
    # ── Credentials & platform ────────────────────────────────────────────
    Type.CERTIFICATE_ISSUED: {
        'category': Category.LEARNING, 'in_app_pref': 'achievements',
        'email_template': 'certificate_issued', 'email_kind': 'certificate',
    },
    Type.ANNOUNCEMENT: {
        'category': Category.ANNOUNCEMENT, 'in_app_pref': 'announcements',
        'email_template': None, 'email_kind': 'announcement',
    },
}

_DEFAULT_GRAPH = {
    'category': Category.LEARNING,
    'in_app_pref': None,
    'email_template': None,
    'email_kind': None,
    'security': False,
}


def graph_for(type_value) -> dict:
    """Resolve the type graph, tolerating unknown types (fail-soft)."""
    entry = _TYPE_GRAPH.get(type_value)
    if entry is None:
        return dict(_DEFAULT_GRAPH)
    return {**_DEFAULT_GRAPH, **entry}


def categories_for(types: list[str]) -> list[str]:
    return sorted({graph_for(t)['category'] for t in types})


def format_event_dt(value) -> str:
    """Human presentation for deadlines in emails and notification bodies.

    The platform runs on ``USE_TZ = True`` with ``TIME_ZONE = UTC`` (there is
    no per-user timezone model yet), so dates are shown in UTC with an explicit
    suffix. Every date is explicitly labelled to prevent misreading local time.
    """
    if value is None:
        return ''
    localized = timezone.localtime(value)
    return f"{localized.strftime('%d %b %Y, %I:%M %p')} UTC"


def _write_notification(
    user, *, type_value, title, body='', link='', dedupe_key=None,
    related_object_type='', related_object_id='',
) -> UserNotification | None:
    """Insert the in-app row, honoring in-app preference and idempotency."""
    graph = graph_for(type_value)
    profile = UserProfile.objects.filter(user=user).only('notification_preferences').first()
    if (
        graph['in_app_pref']
        and profile is not None
        and not profile.get_notification_preference(graph['in_app_pref'])
    ):
        return None

    if dedupe_key:
        existing = UserNotification.objects.filter(dedupe_key=dedupe_key).first()
        if existing is not None:
            return existing
        return UserNotification.objects.create(
            user=user,
            type=type_value,
            category=graph['category'],
            title=title[:200],
            body=body,
            link=link[:300],
            related_object_type=related_object_type[:50],
            related_object_id=related_object_id[:64],
            dedupe_key=dedupe_key[:150],
        )
    return UserNotification.objects.create(
        user=user,
        type=type_value,
        category=graph['category'],
        title=title[:200],
        body=body,
        link=link[:300],
        related_object_type=related_object_type[:50],
        related_object_id=related_object_id[:64],
    )


def create_notification(user, *, type, title, body='', link='', dedupe_key=None,
                        related_object_type='', related_object_id=''):
    """Create one in-app notification unless the learner muted its category.

    Backward-compatible core of the service: sponsors the award/XP flows.
    Returns the ``UserNotification`` or ``None`` when muted. Never raises:
    a notification is a courtesy, not part of the award's integrity, so a
    failure here must not roll back the underlying achievement transaction.
    """
    try:
        return _write_notification(
            user, type_value=type, title=title, body=body, link=link,
            dedupe_key=dedupe_key,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
        )
    except Exception:  # noqa: BLE001 - notifications never break business flows
        logger.exception('Failed to create notification of type %s', type)
        return None


def notify(
    user,
    *,
    type,
    title,
    body='',
    link='',
    dedupe_key=None,
    related_object_type='',
    related_object_id='',
    email_subject=None,
    email_context=None,
    email_key=None,
    send_email=True,
) -> UserNotification | None:
    """Full-event entry point: in-app notification plus optional email.

    The email is scheduled only after the surrounding transaction commits
    (inside ``email_service``), is skipped when the learner's ``email_<kind>``
    preference is off, and is never sent twice for the same ``email_key`` —
    the ledger claim lives inside the same commit as the event rows.
    """
    notification = None
    try:
        notification = _write_notification(
            user, type_value=type, title=title, body=body, link=link,
            dedupe_key=dedupe_key,
            related_object_type=related_object_type,
            related_object_id=related_object_id,
        )
    except Exception:  # noqa: BLE001 - notifications never break business flows
        logger.exception('Failed to create notification of type %s', type)
        return None

    graph = graph_for(type)
    template = graph.get('email_template')
    if notification is None or email_key is None or not send_email or not template:
        return notification

    try:
        # An event that carries an in-app link hands its email the same call to
        # action: the branded button then always exists and always opens the
        # screen the notification points at, even when the caller only supplied
        # a heading and a body. Explicit email_context values win.
        context = dict(email_context or {'message': body, 'heading': title})
        if link and not context.get('cta_url'):
            context['cta_url'] = settings.FRONTEND_URL + link
        email_service.send_notification_email(
            user,
            template=template,
            subject=(email_subject or title)[:200],
            context=context,
            email_key=email_key,
            kind=graph['email_kind'],
            security=graph.get('security', False),
            notification=notification,
        )
    except Exception:  # noqa: BLE001 - the event already happened; mail can fail
        logger.exception('Failed to schedule email for notification %s', notification.id)
    return notification
