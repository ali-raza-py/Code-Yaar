import time

from django.conf import settings
from rest_framework.test import APIClient

from learning.models import AuthenticationAuditLog, EmailVerificationToken

print('BACKEND   :', settings.MAILERS['default']['BACKEND'])
print('PASSWORD  :', bool(settings.MAILERS['default'].get('OPTIONS', {}).get('password')))
print('GATE      :', settings.AUTH_REQUIRE_EMAIL_VERIFICATION)
print()

client = APIClient()
# ALLOWED_HOSTS only trusts the real hosts, and the API client defaults to
# `testserver`; point it at a host this project already allows.
client.defaults['HTTP_HOST'] = 'localhost'
client.defaults['HTTP_ORIGIN'] = 'http://localhost:3000'
started = time.monotonic()
response = client.post(
    '/api/auth/resend-verification/',
    {'email': 'btwaliraza110@gmail.com'},
    format='json',
)
elapsed = time.monotonic() - started

print('HTTP', response.status_code, 'in', round(elapsed, 2), 's')
try:
    print('BODY', response.json())
except Exception:
    print('BODY (raw)', response.content[:300])

print()
newest = EmailVerificationToken.objects.order_by('-id').first()
print('NEWEST TOKEN:', newest.id, newest.created_at, 'used_at=', newest.used_at)
row = AuthenticationAuditLog.objects.order_by('-id').first()
print('NEWEST AUDIT:', row.id, row.created_at, row.event, row.identifier, row.metadata)
