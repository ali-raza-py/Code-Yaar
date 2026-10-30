from django.contrib.auth import get_user_model
from learning.models import AuthenticationAuditLog, EmailVerificationToken
from learning.services.auth import get_profile

User = get_user_model()

print('=== USERS ===')
for u in User.objects.all().order_by('id'):
    p = get_profile(u)
    print(
        f'id={u.id} username={u.username!r} email={u.email!r} '
        f'is_active={u.is_active} verified={p.email_verified} '
        f'verified_at={p.email_verified_at} has_usable_pw={u.has_usable_password()}'
    )

print()
print('=== TOKENS for btwaliraza110@gmail.com ===')
target = User.objects.filter(email__iexact='btwaliraza110@gmail.com').first()
print('resolved user:', target)
if target:
    for t in EmailVerificationToken.objects.filter(user=target).order_by('-id')[:8]:
        print(
            f'id={t.id} created={t.created_at} expires={t.expires_at} '
            f'used_at={t.used_at} expired_now={t.is_expired} '
            f'hash_prefix={t.token_hash[:8]}'
        )

print()
print('=== AUDIT (last 20 verification events) ===')
events = [
    AuthenticationAuditLog.Event.EMAIL_VERIFICATION_SENT,
    AuthenticationAuditLog.Event.EMAIL_VERIFICATION_FAILED,
    AuthenticationAuditLog.Event.EMAIL_VERIFIED,
]
for row in (
    AuthenticationAuditLog.objects.filter(event__in=events).order_by('-id')[:20]
):
    print(
        f'{row.created_at} {row.event} user_id={row.user_id} '
        f'ident={row.identifier!r} meta={row.metadata} ip={row.ip_address}'
    )

print()
print('=== RECENT LOGIN_FAILED ===')
for row in (
    AuthenticationAuditLog.objects.filter(
        event=AuthenticationAuditLog.Event.LOGIN_FAILED
    ).order_by('-id')[:8]
):
    print(f'{row.created_at} ident={row.identifier!r} meta={row.metadata}')

print()
print('=== THROTTLE CACHE ===')
from django.core.cache import cache
print('cache backend:', cache.__class__.__module__)
from django.conf import settings
print('CACHES:', settings.CACHES)
print('rates:', settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'].get('auth_resend_verification'))
print('gate AUTH_REQUIRE_EMAIL_VERIFICATION:', settings.AUTH_REQUIRE_EMAIL_VERIFICATION)
print('MAILERS backend:', settings.MAILERS['default']['BACKEND'])
print('smtp password set:', bool(settings.MAILERS['default'].get('OPTIONS', {}).get('password')))
print('FRONTEND_URL:', settings.FRONTEND_URL)
