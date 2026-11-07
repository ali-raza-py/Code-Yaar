"""Event-driven email automation helpers for Code Yaar Email Studio.

Automation rules are configured by administrators. When a business event
occurs, ``trigger_automation`` looks up the enabled rule for that trigger
and, when one exists with a template, renders and sends the configured
email. Disabled rules or missing templates are silent no-ops so existing
behaviour is preserved when no rule is configured.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.utils import timezone

from ..models import EmailAutomationRule, UserProfile
from . import email_composer as composer
from .email_service import (
    send_notification_email,
    send_security_email,
)

logger = logging.getLogger(__name__)

_SECURITY_TRIGGERS = {
    'email_verification_requested',
    'password_reset_requested',
    'password_changed',
    'security_notification',
}


def is_enabled(trigger: str) -> bool:
    rule = EmailAutomationRule.objects.filter(trigger=trigger).first()
    return bool(rule and rule.enabled)


def trigger_automation(trigger, user, *, email_key, context=None, kind=None):
    if user is None or not getattr(user, 'email', ''):
        return None
    if not email_key:
        return None

    rule = EmailAutomationRule.objects.filter(trigger=trigger).first()
    if rule is None or not rule.enabled:
        return None
    template = rule.template
    if template is None:
        return None

    variables = composer.recipient_variables(
        name=composer.display_name(user),
        email=user.email,
        student_id=getattr(user, 'username', '') or '',
    )
    subject = (rule.subject_override or template.subject or '').strip()
    subject = composer.personalize(subject, variables) if subject else template.name
    heading = composer.personalize(template.heading or template.name, variables)
    body_html = composer.personalize_html(template.body_html or '', variables)
    cta_url = composer.personalize(template.cta_url or '', variables)
    cta_label = composer.personalize(template.cta_label or '', variables)

    ctx = {
        'subject': subject,
        'eyebrow': template.category,
        'heading': heading,
        'custom_html': body_html,
        'cta_url': cta_url,
        'cta_label': cta_label,
        'preheader': (heading or subject)[:140],
    }
    if context:
        ctx.update(context)

    rule.last_run_at = timezone.now()
    try:
        if trigger in _SECURITY_TRIGGERS:
            log = send_security_email(
                user,
                template='campaign_custom',
                subject=subject,
                context=ctx,
                email_key=email_key,
            )
        else:
            log = send_notification_email(
                user,
                template='campaign_custom',
                subject=subject,
                context=ctx,
                email_key=email_key,
                kind=kind or 'announcement',
            )
        if log is not None:
            rule.success_count = (rule.success_count or 0) + 1
        else:
            rule.failure_count = (rule.failure_count or 0) + 1
        rule.save(update_fields=['last_run_at', 'success_count', 'failure_count', 'updated_at'])
        return log
    except Exception as exc:
        logger.exception('Automation %s failed: %s', trigger, exc)
        rule.failure_count = (rule.failure_count or 0) + 1
        rule.save(update_fields=['last_run_at', 'failure_count', 'updated_at'])
        return None