"""Centralized branded email delivery for Code Yaar.

Every product email flows through one function,
:func:`send_notification_email`, which renders one of the ``emails/`` Django
templates (HTML plus a plain-text alternative), applies the recipient's
optional-email preferences (never for security mail), claims idempotent
delivery via :class:`~learning.models.NotificationEmailLog`, sends through the
configured ``MAILERS`` transport *after* the surrounding transaction commits,
and records the outcome.

Emails are courtesies layered on top of a business action: transport failures
are logged with a sanitized reason and recorded in the ledger instead of being
raised into the caller's flow, so an SMTP outage can never un-issue the
achievement, certificate or registration it reports on. Render-only backends
(console/dummy/filebased) are recorded honestly as ``render_only`` in the same
spirit as ``learning.services.auth.mail_transport_ready()``.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from ..models import NotificationEmailLog, UserProfile

logger = logging.getLogger(__name__)

# Backends that only render a message (to a terminal, nowhere, or a file).
# Their send() reports success because nothing raises, which is exactly how an
# email outage masquerades as a delivered link — so they are recorded as
# ``render_only`` instead of pretending to be delivery.
RENDER_ONLY_BACKENDS = frozenset({
    'django.core.mail.backends.console',
    'django.core.mail.backends.dummy',
    'django.core.mail.backends.filebased',
})

# Context every template receives beyond the per-event context. ``logo_url``
# points at the frontend's published white mark so it stays visible on the
# navy header band; the alt text carries the brand either way.
BASE_EMAIL_CONTEXT = {
    'brand_name': 'Code Yaar',
    'brand_tagline': 'Think. Build. Evolve.',
    'logo_url': settings.FRONTEND_URL + '/logo-dark.png',
    'preferences_url': settings.FRONTEND_URL + '/settings?tab=preferences',
    'dashboard_url': settings.FRONTEND_URL + '/dashboard',
    'current_year': timezone.now().year,
}

#: Optional-email categories → the ``notification_preferences`` keys that gate
#: them. Security mail deliberately has no entry: it is never optional.
EMAIL_PREFERENCE_BY_KIND = {
    'learning': 'email_learning',
    'competition': 'email_competitions',
    'achievement': 'email_achievements',
    'certificate': 'email_certificates',
    'announcement': 'email_announcements',
}

EMAIL_PREFERENCE_KEYS = tuple(EMAIL_PREFERENCE_BY_KIND.values())


def _sanitize_error(exc: Exception) -> str:
    """Short, secret-free transport reason for the ledger.

    Exception texts never contain credentials, but SMTP protocol errors can
    quote the sender or subject line, so only the exception class plus a
    bounded, flattened message are stored.
    """
    text = f'{type(exc).__name__}: {exc}'
    return text[:480].replace('\n', ' ').replace('\r', ' ')


def email_context(user=None, **extra) -> dict:
    """Merge per-event context over a fresh shared-brand context."""
    context = {
        'brand_name': 'Code Yaar',
        'brand_tagline': 'Think. Build. Evolve.',
        'logo_url': settings.FRONTEND_URL + '/logo-dark.png',
        'preferences_url': settings.FRONTEND_URL + '/settings?tab=preferences',
        'dashboard_url': settings.FRONTEND_URL + '/dashboard',
        'current_year': timezone.now().year,
    }
    if user is not None:
        context['first_name'] = (user.get_full_name() or '').strip() or user.username
    context.update(extra)
    return context


def render_email(template: str, context: dict) -> tuple[str, str]:
    """Return ``(html, text)`` for the named ``emails/<template>`` pair."""
    html = render_to_string(f'emails/{template}.html', context)
    text = render_to_string(f'emails/{template}.txt', context)
    return html, text


def _claim(user, email_key: str, defaults: dict) -> NotificationEmailLog | None:
    """Claim the delivery for ``email_key`` exactly once.

    Returns the existing claim when the event was already handled (sent,
    rendered or still queued), ``None`` when a fresh claim could not be created
    or a previous *failed* attempt is being retried by a new claim.
    """
    existing = NotificationEmailLog.objects.filter(email_key=email_key).first()
    if existing is not None:
        if existing.status in (
            NotificationEmailLog.Status.SENT,
            NotificationEmailLog.Status.RENDER_ONLY,
            NotificationEmailLog.Status.QUEUED,
        ):
            logger.debug('Email %s already claimed (%s); skipping', email_key, existing.status)
            return existing
        return None
    try:
        return NotificationEmailLog.objects.create(user=user, email_key=email_key, **defaults)
    except Exception:  # pragma: no cover - concurrent claim trips the unique key
        logger.warning('Email claim for %s already taken concurrently', email_key)
        return None


def _deliver_email(log, subject, text, html, now) -> None:
    """Transmit one claimed email and record the true outcome."""
    backend_name = settings.MAILERS.get('default', {}).get('BACKEND', '')
    try:
        message = _build_message(log, subject, text, html)
        accepted = int(message.send())
    except Exception as exc:
        NotificationEmailLog.objects.filter(pk=log.pk).update(
            status=NotificationEmailLog.Status.FAILED,
            error=_sanitize_error(exc),
            attempted_at=now,
        )
        logger.exception('Email "%s" (%s) could not be sent', subject, log.email_key)
        return

    if backend_name in RENDER_ONLY_BACKENDS or accepted == 0:
        NotificationEmailLog.objects.filter(pk=log.pk).update(
            status=NotificationEmailLog.Status.RENDER_ONLY,
            attempted_at=now,
        )
        logger.warning(
            'Email "%s" (%s) was rendered by %s and never left the server; '
            'set EMAIL_BACKEND to an SMTP backend to send real mail.',
            subject, log.email_key, backend_name,
        )
        return

    NotificationEmailLog.objects.filter(pk=log.pk).update(
        status=NotificationEmailLog.Status.SENT,
        sent_at=now,
        attempted_at=now,
        error='',
    )


def _build_message(log, subject, text, html):
    from django.core.mail import EmailMultiAlternatives

    message = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[log.user.email],
    )
    message.attach_alternative(html, 'text/html')
    return message


def send_notification_email(
    user,
    *,
    template: str,
    subject: str,
    context: dict | None = None,
    email_key: str,
    kind: str,
    security: bool = False,
    notification=None,
) -> NotificationEmailLog | None:
    """Render and deliver one branded email, honoring optional preferences.

    Parameters
    ----------
    user:
        Recipient — from the authenticated request or the object that owns
        the event, never from caller-provided identifiers.
    template:
        Name of the ``emails/<template>.html``/``.txt`` pair.
    subject:
        Rendered message subject (template copy describes the event).
    context:
        Per-event template context (heading, message, cta_url, cta_label, ...).
    email_key:
        Event-derived idempotency token; the same key is never sent twice.
    kind:
        Optional-email category; gated by the ``email_<kind>`` preference.
        Security mail passes ``security=True`` and bypasses preferences.
    notification:
        Optional in-app notification this email relates to (for the ledger).

    Returns the delivery log, or ``None`` when the mail was skipped
    (preference off, no address, duplicate event). Never raises: failures land
    in the ledger as ``failed`` rows with a sanitized reason, so the
    surrounding business action always completes.
    """
    if user is None or not getattr(user, 'email', ''):
        logger.warning('Skipping email "%s": recipient has no address', subject)
        return None
    if not email_key:
        logger.warning('Skipping email "%s": missing idempotent email key', subject)
        return None

    if security:
        kind = 'security'
    else:
        profile = UserProfile.objects.filter(user=user).only(
            'notification_preferences',
        ).first()
        pref_key = EMAIL_PREFERENCE_BY_KIND.get(kind, '')
        if pref_key and profile is not None and not profile.get_notification_preference(pref_key):
            logger.debug(
                'Email "%s" skipped: %s is disabled for %s', subject, pref_key, user.username,
            )
            return None

    claim_defaults = {
        'kind': kind,
        'category': template.split('/', 1)[-1],
        'subject': subject[:200],
        'notification': notification,
    }
    log = _claim(user, email_key, claim_defaults)
    if log is None:
        return None

    html, text = render_email(template, email_context(user=user, **(context or {})))
    now = timezone.now()
    if transaction.get_connection().in_atomic_block:
        # Never email from inside a transaction whose source rows may roll
        # back; the claimed ledger row itself commits with the event.
        transaction.on_commit(lambda: _deliver_email(log, subject, text, html, now))
    else:
        _deliver_email(log, subject, text, html, now)
    return log


def send_security_email(
    user,
    *,
    template: str,
    subject: str,
    context: dict | None = None,
    email_key: str,
    notification=None,
) -> NotificationEmailLog | None:
    """Security/transactional mail: always sent, never preference-gated."""
    return send_notification_email(
        user,
        template=template,
        subject=subject,
        context=context,
        email_key=email_key,
        kind='security',
        security=True,
        notification=notification,
    )
