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


def transport_is_render_only() -> bool:
    """True when the configured mail transport only renders the message.

    ``settings.MAILERS`` stores the *full* dotted path to the backend class
    (``'django.core.mail.backends.console.EmailBackend'``) while
    ``RENDER_ONLY_BACKENDS`` lists backend *modules*, so comparing the raw
    setting against it never matched and a console-backend server recorded its
    printed copies as ``sent`` — the very outage-hiding this module exists to
    prevent. The class segment is dropped before the comparison.
    """
    backend = settings.MAILERS.get('default', {}).get('BACKEND', '')
    module = backend.rsplit('.', 1)[0] if '.' in backend else backend
    return module in RENDER_ONLY_BACKENDS


# The header brand mark is embedded in every message as an inline CID
# attachment rather than linked from FRONTEND_URL: mail clients block remote
# images by default, and in development the site host is a localhost port no
# provider can reach — either way a linked logo collapsed to a broken-image
# icon. Reading the packaged PNG lets the mark travel inside the email itself.
EMAIL_LOGO_CID = 'codeyaar-logo'
EMAIL_LOGO_PATH = settings.BASE_DIR / 'branding' / 'logo-dark.png'


def _email_logo():
    """Return ``(src, attachment)`` for the header brand mark.

    ``src`` is what the template places in the ``<img>`` and ``attachment`` is
    the MIME part to embed (``None`` when the asset cannot be read). If the PNG
    is missing the remote ``FRONTEND_URL`` URL is used instead, so a
    misconfigured deployment still renders the alt-text brand rather than
    raising in the middle of delivery.
    """
    try:
        data = EMAIL_LOGO_PATH.read_bytes()
    except OSError:
        return settings.FRONTEND_URL + '/logo-dark.png', None
    from email.mime.image import MIMEImage

    image = MIMEImage(data, _subtype='png')
    image.add_header('Content-ID', f'<{EMAIL_LOGO_CID}>')
    image.add_header(
        'Content-Disposition', 'inline', filename=EMAIL_LOGO_PATH.name,
    )
    return f'cid:{EMAIL_LOGO_CID}', image


# Context every template receives beyond the per-event context. ``logo_url``
# resolves to the inline brand mark (see ``_email_logo``) so it stays visible on
# the navy header band even when the client blocks remote images; the alt text
# carries the brand either way.
BASE_EMAIL_CONTEXT = {
    'brand_name': 'Code Yaar',
    'brand_tagline': 'Think. Build. Evolve.',
    'logo_url': f'cid:{EMAIL_LOGO_CID}',
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

#: Category pill shown in the branded header band of every email. Keyed by the
#: same ``kind`` values the preference map uses, so the label always matches
#: the box the message actually came from.
EYEBROW_BY_KIND = {
    'security': 'Account security',
    'learning': 'Learning',
    'competition': 'Competitions',
    'achievement': 'Achievements',
    'certificate': 'Credentials',
    'announcement': 'Announcements',
}


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
        'logo_url': _email_logo()[0],
        'preferences_url': settings.FRONTEND_URL + '/settings?tab=preferences',
        'dashboard_url': settings.FRONTEND_URL + '/dashboard',
        'current_year': timezone.now().year,
    }
    if user is not None:
        context['first_name'] = (user.get_full_name() or '').strip() or user.username
        context['recipient_email'] = user.email
    context.update(extra)
    return context


def render_email(template: str, context: dict) -> tuple[str, str]:
    """Return ``(html, text)`` for the named ``emails/<template>`` pair."""
    html = render_to_string(f'emails/{template}.html', context)
    text = render_to_string(f'emails/{template}.txt', context)
    return html, text


def _claim(user, email_key: str, defaults: dict) -> NotificationEmailLog | None:
    """Claim the delivery for ``email_key`` exactly once.

    A sent, rendered, or queued row means another call already owns the event,
    so it returns ``None`` and the caller does not deliver again. A failed row
    is atomically moved back to ``queued`` and reused, making transport failures
    retryable without weakening the unique idempotency key.
    """
    existing = NotificationEmailLog.objects.filter(email_key=email_key).first()
    if existing is not None:
        if existing.status != NotificationEmailLog.Status.FAILED:
            logger.debug('Email %s already claimed (%s); skipping', email_key, existing.status)
            return None

        retry_defaults = {
            **defaults,
            'user': user,
            'status': NotificationEmailLog.Status.QUEUED,
            'error': '',
            'attempted_at': None,
            'sent_at': None,
        }
        claimed = NotificationEmailLog.objects.filter(
            pk=existing.pk,
            status=NotificationEmailLog.Status.FAILED,
        ).update(**retry_defaults)
        if not claimed:
            logger.debug('Email retry for %s was claimed concurrently', email_key)
            return None
        existing.refresh_from_db()
        return existing
    try:
        return NotificationEmailLog.objects.create(user=user, email_key=email_key, **defaults)
    except Exception:  # pragma: no cover - concurrent claim trips the unique key
        logger.warning('Email claim for %s already taken concurrently', email_key)
        return None


def _deliver_email(log, subject, text, html, now) -> None:
    """Transmit one claimed email and record the true outcome.

    Both the ledger row and the in-memory ``log`` are updated: callers that
    delivered synchronously (``send_verification_email`` and friends) answer
    from ``log.status``, and a row that still read ``queued`` would turn a
    message the transport accepted into a false "we could not send it".
    """
    try:
        message = _build_message(log, subject, text, html)
        accepted = int(message.send())
    except Exception as exc:
        reason = _sanitize_error(exc)
        NotificationEmailLog.objects.filter(pk=log.pk).update(
            status=NotificationEmailLog.Status.FAILED,
            error=reason,
            attempted_at=now,
        )
        log.status = NotificationEmailLog.Status.FAILED
        log.error = reason
        log.attempted_at = now
        logger.exception('Email "%s" (%s) could not be sent', subject, log.email_key)
        return

    if transport_is_render_only() or accepted == 0:
        NotificationEmailLog.objects.filter(pk=log.pk).update(
            status=NotificationEmailLog.Status.RENDER_ONLY,
            attempted_at=now,
        )
        log.status = NotificationEmailLog.Status.RENDER_ONLY
        log.attempted_at = now
        logger.warning(
            'Email "%s" (%s) was rendered by %s and never left the server; '
            'set EMAIL_BACKEND to an SMTP backend to send real mail.',
            subject, log.email_key,
            settings.MAILERS.get('default', {}).get('BACKEND', ''),
        )
        return

    NotificationEmailLog.objects.filter(pk=log.pk).update(
        status=NotificationEmailLog.Status.SENT,
        sent_at=now,
        attempted_at=now,
        error='',
    )
    log.status = NotificationEmailLog.Status.SENT
    log.sent_at = now
    log.attempted_at = now
    log.error = ''


def _build_message(log, subject, text, html):
    from django.core.mail import EmailMultiAlternatives

    message = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[log.user.email],
    )
    message.attach_alternative(html, 'text/html')
    # Embed the brand mark inline so the header logo renders without the client
    # fetching anything (``_email_logo`` falls back to a remote URL, in which
    # case there is nothing to attach).
    _, logo_attachment = _email_logo()
    if logo_attachment is not None:
        message.attach(logo_attachment)
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

    # The layout always wants a subject line and a category pill; an event that
    # names its own eyebrow (or subject) simply overrides the derived value.
    render_context = {'subject': subject, 'eyebrow': EYEBROW_BY_KIND.get(kind, '')}
    render_context.update(context or {})
    html, text = render_email(template, email_context(user=user, **render_context))
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
