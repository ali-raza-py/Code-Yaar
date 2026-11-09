"""Audience resolution and real-outcome delivery for admin email campaigns.

Publishing content and emailing it are separate actions on this platform: a
campaign only exists when a Super Admin explicitly composes and confirms it,
and its counters move only on genuine transport results. ``sent`` means the
SMTP backend accepted the message; render-only backends (console/dummy/file)
record ``render_only`` instead of pretending a copy left the server, matching
the honesty contract of :mod:`learning.services.email_service`.

Fan-out runs in a daemon thread after the send request's transaction commits
— the platform has no task queue, and an admin HTTP request must not hang on
hundreds of SMTP round-trips. Per-recipient rows are updated with short
autocommitted writes, so SQLite keeps locking only for microseconds at a time.
"""

from __future__ import annotations

import logging
import threading

from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.db import connections
from django.db.models import Count
from django.template.loader import render_to_string
from django.utils import timezone

from ..models import (
    CompetitionRegistration, EmailCampaign, EmailCampaignRecipient, UserProfile,
)
from . import email_composer as composer
from .email_service import _email_logo, _sanitize_error, transport_is_render_only

logger = logging.getLogger(__name__)

UNSUBSCRIBE_SALT = 'email-unsubscribe'

#: Category pill for the branded email header, by campaign template. The
#: template already tells the reader what kind of mail arrived, so the layout
#: repeats it in the header instead of inside the message body.
CAMPAIGN_EYEBROW = {
    'general': 'Announcement',
    'new_course': 'New course',
    'notice': 'Important notice',
    'platform_update': 'Platform update',
}

#: Marketing mail respects this preference; essential mail ignores it.
MARKETING_PREFERENCE = 'email_announcements'

#: Campaign audience → CompetitionRegistration status filter.
COMPETITION_AUDIENCE_STATUSES = {
    EmailCampaign.Audience.COMP_PARTICIPANTS: ['registered', 'approved', 'pending', 'waitlisted'],
    EmailCampaign.Audience.COMP_APPROVED: ['approved'],
    EmailCampaign.Audience.COMP_PENDING: ['pending', 'registered'],
    EmailCampaign.Audience.COMP_WAITLISTED: ['waitlisted'],
}


def unsubscribe_token(user) -> str:
    """Signed, tamper-evident token identifying one recipient's opt-out."""
    return dumps({'uid': user.pk}, salt=UNSUBSCRIBE_SALT)


def unsubscribe_url(user) -> str:
    return f'{settings.FRONTEND_URL}/api/email/unsubscribe/{unsubscribe_token(user)}/'


def unpack_unsubscribe_token(token: str):
    """Return the user for a valid token, or ``None`` when invalid/expired."""
    try:
        payload = loads(token, salt=UNSUBSCRIBE_SALT, max_age=None)
    except (BadSignature, SignatureExpired):
        return None
    from django.contrib.auth import get_user_model
    return get_user_model().objects.filter(pk=payload.get('uid')).first()


def resolve_audience(campaign) -> list:
    """Materialize the campaign audience as a list of active users with addresses.

    Resolution happens once at send time so recipient counts shown before
    confirmation and the actual fan-out can never drift apart.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    base = User.objects.filter(is_active=True).exclude(email='').distinct()

    audience = campaign.audience
    if audience == EmailCampaign.Audience.ALL:
        return list(base)
    if audience == EmailCampaign.Audience.STUDENTS:
        return list(base.filter(profile__role='student'))
    if audience == EmailCampaign.Audience.INSTRUCTORS:
        return list(base.filter(profile__role__in=['instructor', 'mentor']))
    if audience == EmailCampaign.Audience.ADMINS:
        return list(
            base.filter(is_staff=True) | base.filter(profile__role='admin')
        )
    if audience == EmailCampaign.Audience.SPECIFIC:
        # Hand-picked recipients of the "Send Official Email" composer.
        return list(base.filter(pk__in=campaign.selected_users.values_list('pk', flat=True)))
    if audience in COMPETITION_AUDIENCE_STATUSES:
        if not campaign.competition_id:
            return []
        registrations = CompetitionRegistration.objects.filter(
            competition_id=campaign.competition_id,
            registration_status__in=COMPETITION_AUDIENCE_STATUSES[audience],
        )
        return list(base.filter(competition_registrations__in=registrations))
    return []


def audience_count(campaign) -> int:
    return len(resolve_audience(campaign))


def planned_recipient_count(campaign) -> int:
    """Everyone a send would reach, external custom addresses included."""
    users = resolve_audience(campaign)
    if campaign.audience != EmailCampaign.Audience.SPECIFIC:
        return len(users)
    covered = {user.email.lower() for user in users}
    external = [
        address for address in (campaign.custom_emails or [])
        if address.lower() not in covered
    ]
    return len(users) + len(external)


def accepts_marketing(user) -> bool:
    """Whether this user may receive a non-essential campaign email."""
    profile = UserProfile.objects.filter(user=user).only('notification_preferences').first()
    if profile is None:
        return True
    return profile.get_notification_preference(MARKETING_PREFERENCE)


def campaign_context(campaign, user, extra=None) -> dict:
    """Template context for one recipient of this campaign."""
    body_lines = [line.strip() for line in (campaign.body or '').splitlines() if line.strip()]
    context = {
        'brand_name': 'Code Yaar',
        'brand_tagline': 'Think. Build. Evolve.',
        'logo_url': _email_logo()[0],
        'preferences_url': settings.FRONTEND_URL + '/settings?tab=preferences',
        'dashboard_url': settings.FRONTEND_URL + '/dashboard',
        'current_year': timezone.now().year,
        'subject': campaign.subject,
        'eyebrow': CAMPAIGN_EYEBROW.get(campaign.template or 'general', 'Announcement'),
        'recipient_email': user.email,
        'preheader': (campaign.heading or campaign.subject)[:140],
        'heading': campaign.heading or campaign.name,
        'paragraphs': body_lines,
        'footer_note': (
            'You are receiving this because you have a Code Yaar account. '
            'Unsubscribing stops campaign mail only — essential account, '
            'competition and security notifications are never affected.'
        ),
        'first_name': (user.get_full_name() or '').strip() or user.username,
        'cta_url': campaign.cta_url or '',
        'cta_label': campaign.cta_label or '',
        'banner_url': (
            settings.FRONTEND_URL + campaign.banner_image.url if campaign.banner_image else ''
        ),
        'unsubscribe_url': unsubscribe_url(user),
    }
    if extra:
        context.update(extra)
    return context


def render_campaign_email(campaign, user) -> tuple[str, str]:
    template = campaign.template or 'general'
    html = render_to_string(f'emails/campaign_{template}.html', campaign_context(campaign, user))
    text = render_to_string(f'emails/campaign_{template}.txt', campaign_context(campaign, user))
    return html, text


def recipient_identity(recipient) -> tuple[str, str]:
    """``(display name, student id)`` for one recipient row.

    The student ID is the account username: it is what the platform already
    calls a learner by, and external addresses simply have no ID to show.
    """
    if recipient.user_id and recipient.user is not None:
        user = recipient.user
        name = (user.get_full_name() or '').strip() or user.username
        return name, user.username
    local = recipient.email.partition('@')[0]
    return local.replace('.', ' ').replace('_', ' ').title(), ''


def is_composed(campaign) -> bool:
    """True when the admin wrote a free-form rich-text email in the composer."""
    return bool(campaign.body_html)


def composed_variables(campaign, name: str, email: str, student_id: str) -> dict:
    """Personalization dictionary for one recipient of a composed email."""
    return composer.recipient_variables(name=name, email=email, student_id=student_id)


def composed_subject(campaign, variables: dict) -> str:
    return composer.personalize(campaign.subject, variables)


def render_composed_email(campaign, *, name: str, email: str, student_id: str,
                          has_account: bool = True, user=None) -> tuple[str, str]:
    """Render one personalized copy of a composer email.

    Every ``{{variable}}`` is substituted separately for this recipient, and
    the values are HTML-escaped into the already-sanitized body, so recipient
    data can neither collide nor inject markup. The shared branded layout
    wraps the result; unsubscribe links only go to people who have a Code
    Yaar account to unsubscribe with.
    """
    variables = composed_variables(campaign, name, email, student_id)
    subject = composed_subject(campaign, variables)
    heading = composer.personalize(campaign.heading or campaign.name, variables)
    if campaign.body_html:
        html_body = composer.personalize_html(campaign.body_html, variables)
        derived_text = composer.personalize(
            composer.plain_text_from_html(campaign.body_html), variables,
        )
    else:
        # Specific-recipient mail drafted in the legacy plain-text box.
        paragraphs = [line.strip() for line in (campaign.body or '').splitlines() if line.strip()]
        from html import escape as _escape
        html_body = ''.join(f'<p>{_escape(composer.personalize(paragraph, variables))}</p>' for paragraph in paragraphs)
        derived_text = '\n\n'.join(composer.personalize(paragraph, variables) for paragraph in paragraphs)
    text_body = composer.personalize(campaign.plain_text_alternative, variables) if campaign.plain_text_alternative else derived_text
    context = {
        'brand_name': 'Code Yaar',
        'brand_tagline': 'Think. Build. Evolve.',
        'logo_url': _email_logo()[0],
        'preferences_url': settings.FRONTEND_URL + '/settings?tab=preferences',
        'dashboard_url': settings.FRONTEND_URL + '/dashboard',
        'current_year': timezone.now().year,
        'subject': subject,
        'eyebrow': 'Official email' if has_account else 'Announcement',
        'recipient_email': email,
        'preheader': (heading or subject)[:140],
        'heading': heading,
        'custom_html': html_body,
        'custom_text': text_body,
        'first_name': name,
        'cta_url': composer.personalize(campaign.cta_url or '', variables),
        'cta_label': composer.personalize(campaign.cta_label or '', variables),
        'footer_note': (
            'You are receiving this because the Code Yaar team is writing to '
            'you directly. Unsubscribing stops campaign mail only — essential '
            'account, competition and security notifications are never affected.'
            if has_account else
            'You are receiving this because the Code Yaar team is writing to you directly.'
        ),
    }
    if has_account:
        context['unsubscribe_url'] = (
            unsubscribe_url(user) if user is not None
            else settings.FRONTEND_URL + '/settings?tab=preferences'
        )
    html = render_to_string('emails/campaign_custom.html', context)
    text = render_to_string('emails/campaign_custom.txt', context)
    return html, text


def render_email_for(campaign, recipient) -> tuple[str, str]:
    """Render the exact copy one recipient row will receive."""
    if is_composed(campaign) or recipient.user_id is None:
        name, student_id = recipient_identity(recipient)
        return render_composed_email(
            campaign, name=name, email=recipient.email, student_id=student_id,
            has_account=recipient.user_id is not None, user=recipient.user,
        )
    return render_campaign_email(campaign, recipient.user)


def subject_for(campaign, recipient) -> str:
    """Subject line for one recipient (personalized for composed mail)."""
    if is_composed(campaign) or recipient.user_id is None:
        name, student_id = recipient_identity(recipient)
        return composed_subject(campaign, composed_variables(campaign, name, recipient.email, student_id))
    return campaign.subject


def send_single(recipient: EmailCampaignRecipient, campaign) -> EmailCampaignRecipient:
    """Deliver one campaign email and record the honest outcome on the row.

    Composed ("Send Official Email") mail is rendered and titled per
    recipient, so personalization can never bleed between copies. Each
    message goes to exactly one address — the shared recipient list is never
    exposed — with the campaign CC attached; the BCC list rides on the first
    message of the dispatch only, so blind recipients get one copy each.
    """
    now = timezone.now()
    try:
        subject = subject_for(campaign, recipient)
        html, text = render_email_for(campaign, recipient)
        message = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient.email],
        )
        if getattr(settings, 'REPLY_TO_EMAIL', ''):
            message.reply_to = [settings.REPLY_TO_EMAIL]
        if campaign.cc_emails:
            message.cc = list(campaign.cc_emails)
        bcc = [] if getattr(campaign, '_bcc_sent', False) else list(campaign.bcc_emails or [])
        if bcc:
            message.bcc = bcc
            campaign._bcc_sent = True
        message.attach_alternative(html, 'text/html')
        _, logo_attachment = _email_logo()
        if logo_attachment is not None:
            message.attach(logo_attachment)
        accepted = int(message.send(fail_silently=False))
    except Exception as exc:  # noqa: BLE001 - per-recipient failure must not abort fan-out
        recipient.status = EmailCampaignRecipient.Status.FAILED
        recipient.error = _sanitize_error(exc)
        recipient.sent_at = None
        recipient.save(update_fields=['status', 'error', 'sent_at'])
        logger.warning('Campaign %s failed for recipient %s: %s', campaign.pk, recipient.pk, recipient.error)
        return recipient

    if transport_is_render_only() or accepted == 0:
        recipient.status = EmailCampaignRecipient.Status.RENDER_ONLY
    elif accepted:
        recipient.status = EmailCampaignRecipient.Status.SENT
        recipient.sent_at = now
    else:
        recipient.status = EmailCampaignRecipient.Status.FAILED
        recipient.error = 'Transport accepted zero recipients'
    recipient.save(update_fields=['status', 'error', 'sent_at'])
    return recipient


def prepare_recipients(campaign) -> int:
    """Create per-recipient rows, skipping opted-out users up front.

    Returns the number of recipients eligible for delivery. Skips are recorded
    so the history explains every member of the selected audience. External
    custom addresses (composer mail to people without accounts) get rows with
    a null user and are never preference-gated — there is no profile to gate.
    """
    users = resolve_audience(campaign)
    eligible = 0
    total = 0
    covered: set[str] = set()
    for user in users:
        covered.add(user.email.lower())
        skip = not campaign.essential and not accepts_marketing(user)
        recipient = EmailCampaignRecipient.objects.create(
            campaign=campaign,
            user=user,
            email=user.email,
            status=(
                EmailCampaignRecipient.Status.PENDING
                if not skip else EmailCampaignRecipient.Status.SKIPPED
            ),
        )
        if skip:
            recipient.error = 'Marketing preference off / unsubscribed'
            recipient.save(update_fields=['error'])
        else:
            eligible += 1
        total += 1
    if campaign.audience == EmailCampaign.Audience.SPECIFIC:
        for address in campaign.custom_emails or []:
            if address.lower() in covered:
                continue
            covered.add(address.lower())
            EmailCampaignRecipient.objects.create(
                campaign=campaign, user=None, email=address,
                status=EmailCampaignRecipient.Status.PENDING,
            )
            eligible += 1
            total += 1
    campaign.recipient_count = total
    campaign.skipped_count = total - eligible
    campaign.save(update_fields=['recipient_count', 'skipped_count'])
    return eligible


def finalize_campaign(campaign) -> None:
    """Roll counters up and set the campaign status from real outcomes."""
    counts = {
        row['status']: row['n']
        for row in EmailCampaignRecipient.objects.filter(campaign=campaign)
        .values('status').annotate(n=Count('id'))
    }
    sent = counts.get(EmailCampaignRecipient.Status.SENT, 0)
    rendered = counts.get(EmailCampaignRecipient.Status.RENDER_ONLY, 0)
    failed = counts.get(EmailCampaignRecipient.Status.FAILED, 0)
    campaign.sent_count = sent + rendered
    campaign.failed_count = failed
    campaign.status = (
        EmailCampaign.Status.FAILED if (failed and not sent and not rendered)
        else EmailCampaign.Status.PARTIAL if (failed and (sent or rendered))
        else EmailCampaign.Status.SENT
    )
    campaign.sent_at = timezone.now()
    campaign.save(update_fields=['sent_count', 'failed_count', 'status', 'sent_at'])


def dispatch_campaign(campaign, *, sync: bool = False) -> None:
    """Fan one campaign out to its audience.

    ``sync=True`` runs the loop inline (tests and small sends); production
    sends run it in a daemon thread so the admin request returns immediately.
    """
    def _run():
        try:
            campaign.status = EmailCampaign.Status.SENDING
            campaign.save(update_fields=['status'])
            if not EmailCampaignRecipient.objects.filter(campaign=campaign).exists():
                prepare_recipients(campaign)
            pending = EmailCampaignRecipient.objects.filter(
                campaign=campaign,
                status=EmailCampaignRecipient.Status.PENDING,
            ).select_related('user')
            for recipient in pending:
                send_single(recipient, campaign)
            finalize_campaign(campaign)
        except Exception:  # noqa: BLE001 - thread must never die silently
            logger.exception('Campaign %s dispatch crashed', campaign.pk)
            EmailCampaign.objects.filter(pk=campaign.pk).update(
                status=EmailCampaign.Status.FAILED,
            )
        finally:
            # Only the worker thread owns a thread-local connection to clean
            # up; closing connections in a synchronous (inline) dispatch would
            # destroy the caller's transaction — the admin request or test.
            if not sync:
                connections.close_all()

    if sync:
        _run()
        return
    thread = threading.Thread(target=_run, daemon=True, name=f'campaign-{campaign.pk}')
    thread.start()


def send_test_email(campaign_data: dict, to_user, to_email: str = '') -> dict:
    """Render one campaign-shaped draft and send it to exactly one address.

    Composed drafts go through the same personalized render path the real
    fan-out uses, with the requesting admin's own identity substituted for
    the variables — so the test copy shows exactly what a student would
    receive. Returns the honest transport outcome so the composer's "Send
    test" button can tell delivered-from-SMTP apart from console-rendered.
    """

    class _Preview:
        def __init__(self, data):
            self.subject = data.get('subject', 'Code Yaar test email')
            self.heading = data.get('heading', '')
            self.name = data.get('name', 'Test')
            self.body = data.get('body', '')
            self.body_html = data.get('body_html', '')
            self.plain_text_alternative = data.get('plain_text', '')
            self.template = data.get('template', 'general')
            self.cta_label = data.get('cta_label', '')
            self.cta_url = data.get('cta_url', '')
            self.cc_emails = []
            self.bcc_emails = []
            self.banner_image = None

    campaign = _Preview(campaign_data)
    address = composer.normalize_email(to_email) or (to_user.email if to_user else '')
    if not composer.validate_email(address):
        return {'ok': False, 'status': 'failed', 'error': 'Test address is not a valid email address'}
    if campaign.body_html:
        html, text = render_composed_email(
            campaign, name=composer.display_name(to_user), email=address,
            student_id=to_user.username if to_user else '', has_account=False,
        )
        subject = composed_subject(campaign, composed_variables(
            campaign, composer.display_name(to_user), address,
            to_user.username if to_user else '',
        ))
    else:
        html, text = render_campaign_email(campaign, to_user)
        subject = campaign.subject
    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[address],
        )
        if getattr(settings, 'REPLY_TO_EMAIL', ''):
            message.reply_to = [settings.REPLY_TO_EMAIL]
        message.attach_alternative(html, 'text/html')
        _, logo_attachment = _email_logo()
        if logo_attachment is not None:
            message.attach(logo_attachment)
        accepted = int(message.send(fail_silently=False))
    except Exception as exc:  # noqa: BLE001 - surface the reason to the admin
        return {'ok': False, 'status': 'failed', 'error': _sanitize_error(exc)}
    if transport_is_render_only() or accepted == 0:
        return {'ok': True, 'status': 'render_only', 'error': ''}
    return {'ok': True, 'status': 'sent', 'error': ''}
