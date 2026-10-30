"""Authentication services.

Everything that is not request plumbing lives here: role resolution, audit
trail writes, single-use email verification / password reset tokens, refresh
token revocation, and the refresh cookie helpers.

Security rules enforced in this module:
- Raw verification/reset tokens are never persisted — only SHA-256 hashes.
- Issuing a new token invalidates every outstanding unused token for the user.
- Consuming a token marks it used inside a transaction, so replays fail.
- Audit records never contain passwords, hashes, or tokens.
"""

import ipaddress
import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage, mailers
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from ..models import (
    AuthenticationAuditLog,
    EmailVerificationToken,
    PasswordResetToken,
    UserProfile,
    hash_auth_token,
)

logger = logging.getLogger(__name__)

STUDENT_GROUP = 'Students'
INSTRUCTOR_GROUP = 'Instructors'
ADMIN_GROUP = 'Administrators'


# ─── Roles and profiles ─────────────────────────────────────────────────────


def get_profile(user) -> UserProfile:
    """Return the user's profile, creating it when absent."""
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def user_role(user) -> str:
    """Resolve the effective role from staff flags, groups, then profile.

    Staff/superuser and the Administrators group always win over the profile
    field so a stale profile row can never downgrade an administrator.
    """
    if not getattr(user, 'is_authenticated', False):
        return 'anonymous'
    if user.is_superuser or user.is_staff:
        return 'administrator'

    group_names = set(user.groups.values_list('name', flat=True))
    if ADMIN_GROUP in group_names:
        return 'administrator'
    if INSTRUCTOR_GROUP in group_names:
        return 'instructor'

    profile = getattr(user, 'profile', None)
    if profile is not None:
        if profile.role == 'admin':
            return 'administrator'
        if profile.role == 'mentor':
            return 'instructor'
    return 'student'


def assign_default_role(user):
    """Give a newly registered account the student role — nothing more."""
    profile = get_profile(user)
    if profile.role != 'student':
        profile.role = 'student'
        profile.save(update_fields=['role'])
    group = _group(STUDENT_GROUP)
    if group is not None:
        user.groups.add(group)


def _group(name):
    from django.contrib.auth.models import Group

    return Group.objects.filter(name=name).first()


# Baseline permissions per role. The API still enforces ownership and
# object-level rules itself; these groups keep Django permission checks and
# the admin consistent with the platform roles.
STUDENT_PERMISSIONS = {
    'careertrack': ('view',),
    'course': ('view',),
    'chapter': ('view',),
    'lesson': ('view',),
    'exercise': ('view',),
    'hint': ('view',),
    'resource': ('view',),
    'project': ('view',),
    'projectmilestone': ('view',),
    'challenge': ('view',),
    'achievement': ('view',),
    'certification': ('view',),
}

INSTRUCTOR_PERMISSIONS = {
    **STUDENT_PERMISSIONS,
    'course': ('view', 'add', 'change'),
    'chapter': ('view', 'add', 'change'),
    'lesson': ('view', 'add', 'change'),
    'exercise': ('view', 'add', 'change'),
    'hint': ('view', 'add', 'change'),
    'resource': ('view', 'add', 'change'),
    'project': ('view', 'add', 'change'),
    'projectmilestone': ('view', 'add', 'change'),
    'challenge': ('view', 'add', 'change'),
    'achievement': ('view', 'add', 'change'),
}


def _codenames(mapping):
    return [
        f'{action}_{model_name}'
        for model_name, actions in mapping.items()
        for action in actions
    ]


def sync_role_groups(sender=None, **kwargs):
    """Create the role groups and add their baseline permissions.

    Idempotent and additive: hooked into `post_migrate` so a fresh database
    ends up with the three roles, and re-running never removes permissions an
    operator granted by hand. Safe to call from a shell or deploy script.
    """
    from django.contrib.auth.models import Group, Permission

    for group_name, codenames in (
        (STUDENT_GROUP, _codenames(STUDENT_PERMISSIONS)),
        (INSTRUCTOR_GROUP, _codenames(INSTRUCTOR_PERMISSIONS)),
    ):
        group, _ = Group.objects.get_or_create(name=group_name)
        group.permissions.add(
            *Permission.objects.filter(
                content_type__app_label='learning', codename__in=codenames
            )
        )

    admins, _ = Group.objects.get_or_create(name=ADMIN_GROUP)
    admins.permissions.add(
        *Permission.objects.filter(
            content_type__app_label__in=('learning', 'certificates')
        )
    )


# ─── Audit trail ────────────────────────────────────────────────────────────


def client_ip(request):
    """Best-effort client IP for the audit trail (never trusted for auth)."""
    if request is None:
        return None
    raw = request.META.get('REMOTE_ADDR')
    if not raw:
        return None
    try:
        return str(ipaddress.ip_address(raw))
    except ValueError:
        return None


def audit(event, *, request=None, user=None, identifier='', metadata=None):
    """Record an authentication event.

    Audit writes must never break the authentication flow, so failures are
    logged and swallowed. Only coarse, non-secret metadata is stored.
    """
    try:
        AuthenticationAuditLog.objects.create(
            user=user,
            event=event,
            identifier=(identifier or '')[:254],
            ip_address=client_ip(request),
            user_agent=(request.META.get('HTTP_USER_AGENT', '') if request else '')[:255],
            metadata=metadata or {},
        )
    except Exception:  # pragma: no cover - defensive
        logger.exception('Failed to write authentication audit event %s', event)


# ─── Email verification / password reset tokens ─────────────────────────────


def _issue_token(model, user, lifetime: timedelta) -> str:
    raw_token = secrets.token_urlsafe(32)
    now = timezone.now()
    with transaction.atomic():
        # A fresh request invalidates every older unused token.
        model.objects.filter(user=user, used_at__isnull=True).update(used_at=now)
        model.objects.create(
            user=user,
            token_hash=hash_auth_token(raw_token),
            expires_at=now + lifetime,
        )
    return raw_token


def _consume_token(model, raw_token):
    """Look up and atomically consume a token.

    Returns ``(status, token_obj)`` where status is one of
    ``ok``, ``invalid``, ``expired``, or ``used``.
    """
    if not raw_token:
        return 'invalid', None
    try:
        token = model.objects.select_related('user').get(
            token_hash=hash_auth_token(raw_token)
        )
    except model.DoesNotExist:
        return 'invalid', None

    if token.used_at is not None:
        return 'used', token
    if token.is_expired:
        return 'expired', token

    updated = model.objects.filter(pk=token.pk, used_at__isnull=True).update(
        used_at=timezone.now()
    )
    if not updated:
        return 'used', token
    token.refresh_from_db(fields=['used_at'])
    return 'ok', token


def issue_email_verification(user, request=None):
    """Create and email a verification token. Returns True when sent."""
    lifetime = timedelta(hours=settings.AUTH_EMAIL_VERIFICATION_TTL_HOURS)
    raw_token = _issue_token(EmailVerificationToken, user, lifetime)
    sent = send_verification_email(user, raw_token)
    audit(
        AuthenticationAuditLog.Event.EMAIL_VERIFICATION_SENT,
        request=request,
        user=user,
        identifier=user.email,
        metadata={'delivered': sent},
    )
    return sent


def verify_email(raw_token, request=None):
    """Consume a verification token and mark the profile verified."""
    status, token = _consume_token(EmailVerificationToken, raw_token)
    if status != 'ok':
        audit(
            AuthenticationAuditLog.Event.EMAIL_VERIFICATION_FAILED,
            request=request,
            user=getattr(token, 'user', None),
            metadata={'reason': status},
        )
        return status, getattr(token, 'user', None)

    user = token.user
    profile = get_profile(user)
    profile.email_verified = True
    profile.email_verified_at = timezone.now()
    profile.save(update_fields=['email_verified', 'email_verified_at'])
    audit(
        AuthenticationAuditLog.Event.EMAIL_VERIFIED,
        request=request,
        user=user,
        identifier=user.email,
    )
    return 'ok', user


def issue_password_reset(user, request=None):
    """Create and email a password reset token. Returns True when sent."""
    lifetime = timedelta(minutes=settings.AUTH_PASSWORD_RESET_TTL_MINUTES)
    raw_token = _issue_token(PasswordResetToken, user, lifetime)
    sent = send_password_reset_email(user, raw_token)
    audit(
        AuthenticationAuditLog.Event.PASSWORD_RESET_REQUESTED,
        request=request,
        user=user,
        identifier=user.email,
        metadata={'delivered': sent},
    )
    return sent


def reset_password(raw_token, new_password, request=None):
    """Consume a reset token, set the new password, and revoke sessions."""
    status, token = _consume_token(PasswordResetToken, raw_token)
    if status != 'ok':
        return status, getattr(token, 'user', None)

    user = token.user
    user.set_password(new_password)
    user.save(update_fields=['password'])
    revoke_refresh_tokens(user)
    audit(
        AuthenticationAuditLog.Event.PASSWORD_RESET_COMPLETED,
        request=request,
        user=user,
        identifier=user.email,
    )
    return 'ok', user


# ─── Session / refresh token handling ───────────────────────────────────────


def revoke_refresh_tokens(user):
    """Blacklist every outstanding refresh token for the user."""
    outstanding = OutstandingToken.objects.filter(user=user)
    for token in outstanding.iterator():
        BlacklistedToken.objects.get_or_create(token=token)


def set_refresh_cookie(response, raw_token):
    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=raw_token,
        max_age=int(
            settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        ),
        httponly=True,
        secure=settings.AUTH_REFRESH_COOKIE_SECURE,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
        domain=settings.AUTH_REFRESH_COOKIE_DOMAIN,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
    )
    return response


def clear_refresh_cookie(response):
    response.delete_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        domain=settings.AUTH_REFRESH_COOKIE_DOMAIN,
        path=settings.AUTH_REFRESH_COOKIE_PATH,
        samesite=settings.AUTH_REFRESH_COOKIE_SAMESITE,
    )
    return response


def refresh_token_from_request(request):
    return request.COOKIES.get(settings.AUTH_REFRESH_COOKIE_NAME) or None


def find_user_by_identifier(identifier):
    """Resolve a username or email to a user without revealing existence."""
    User = get_user_model()
    identifier = (identifier or '').strip()
    if not identifier:
        return None
    if '@' in identifier:
        return User.objects.filter(email__iexact=identifier).first()
    return User.objects.filter(username__iexact=identifier).first()


# ─── Email delivery ─────────────────────────────────────────────────────────


# Backends that only render a message (to stdout, to a file, or nowhere). Their
# `send_messages()` reports success because nothing raised, which is exactly how
# an email outage masquerades as a delivered link: the UI says "on its way" and
# the message sits in a terminal. They are therefore reported as NOT delivered.
RENDER_ONLY_BACKENDS = frozenset({
    'django.core.mail.backends.console',
    'django.core.mail.backends.dummy',
    'django.core.mail.backends.filebased',
})


def mail_transport_ready():
    """True when auth email can actually leave this server right now.

    This describes the configured transport, never the account being asked
    about, so it is safe to hand to anonymous callers: every request gets the
    same answer, and no address, name or credential is involved. Without it the
    resend endpoint — which is deliberately vague about accounts — could only
    report success, and a server whose mail is disabled would look healthy to
    the sign-in screen that cannot authenticate and therefore cannot be told
    about a specific delivery failure.
    """
    backend = mailers.default
    backend_name = type(backend).__module__
    if backend_name in RENDER_ONLY_BACKENDS:
        return False
    if backend_name == 'django.core.mail.backends.smtp':
        # SMTP without a login is always refused, and nothing raises until the
        # message is opened, so the credentials are checked up front.
        return bool(
            getattr(backend, 'username', '') and getattr(backend, 'password', '')
        )
    return True


def _send_email(subject, body, recipient):
    if not recipient:
        logger.warning('Skipping auth email "%s": no recipient address', subject)
        return False
    backend = mailers.default
    backend_name = type(backend).__module__
    try:
        message = EmailMessage(
            subject, body, settings.DEFAULT_FROM_EMAIL, [recipient]
        )
        # `mailers.default` honours the MAILERS setting (console in dev, SMTP
        # in production, locmem under test).
        accepted = backend.send_messages([message])
    except Exception:  # pragma: no cover - depends on the configured backend
        logger.exception('Failed to send authentication email "%s"', subject)
        return False
    if backend_name in RENDER_ONLY_BACKENDS:
        logger.warning(
            'Authentication email "%s" was rendered by %s and never left the '
            'server; set EMAIL_BACKEND to django.core.mail.backends.smtp.'
            'EmailBackend to send real mail.',
            subject,
            backend_name,
        )
        return False
    return bool(accepted)


def send_verification_email(user, raw_token):
    link = f"{settings.FRONTEND_URL}/verify-email?token={raw_token}"
    hours = settings.AUTH_EMAIL_VERIFICATION_TTL_HOURS
    return _send_email(
        'Verify your Code Yaar email address',
        (
            f'Hi {user.get_full_name().strip() or user.username},\n\n'
            'Confirm your email address to finish setting up your Code Yaar '
            f'account. This link expires in {hours} hours and can be used once.\n\n'
            f'{link}\n\n'
            'If you did not create a Code Yaar account, you can ignore this email.'
        ),
        user.email,
    )


def send_password_reset_email(user, raw_token):
    link = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
    minutes = settings.AUTH_PASSWORD_RESET_TTL_MINUTES
    return _send_email(
        'Reset your Code Yaar password',
        (
            f'Hi {user.get_full_name().strip() or user.username},\n\n'
            'A password reset was requested for your Code Yaar account. This '
            f'link expires in {minutes} minutes and can be used once.\n\n'
            f'{link}\n\n'
            'If you did not request a password reset, no action is needed — '
            'your password has not changed.'
        ),
        user.email,
    )
