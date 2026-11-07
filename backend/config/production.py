"""Production settings for a conventional CPython host."""

import os
from pathlib import Path
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

from .settings import *  # noqa: F403


def _required(name: str) -> str:
    value = os.environ.get(name, '').strip()
    if not value:
        raise ImproperlyConfigured(f'{name} must be configured for production.')
    return value


def _csv(name: str) -> list[str]:
    values = [value.strip() for value in _required(name).split(',') if value.strip()]
    if not values:
        raise ImproperlyConfigured(f'{name} must contain at least one value.')
    return values


def _validate_https_origin(name: str, origin: str) -> None:
    parsed = urlsplit(origin)
    if (
        parsed.scheme != 'https'
        or not parsed.netloc
        or parsed.path not in ('', '/')
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise ImproperlyConfigured(f'{name} must contain HTTPS origins without paths.')


DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '').strip() or _required('SECRET_KEY')
if len(SECRET_KEY) < 50 or SECRET_KEY.startswith('django-insecure-'):
    raise ImproperlyConfigured('SECRET_KEY must be a strong, non-development value.')

ALLOWED_HOSTS = _csv(
    'DJANGO_ALLOWED_HOSTS' if os.environ.get('DJANGO_ALLOWED_HOSTS') else 'ALLOWED_HOSTS',
)
if '*' in ALLOWED_HOSTS or any('/' in host or '://' in host for host in ALLOWED_HOSTS):
    raise ImproperlyConfigured('ALLOWED_HOSTS must contain hostnames, not wildcards or URLs.')

SITE_URL = _required('SITE_URL').rstrip('/')
FRONTEND_URL = _required('FRONTEND_URL').rstrip('/')
for setting_name, url in (('SITE_URL', SITE_URL), ('FRONTEND_URL', FRONTEND_URL)):
    _validate_https_origin(setting_name, url)

CORS_ALLOWED_ORIGINS = _csv(
    'CORS_ALLOWED_ORIGINS' if os.environ.get('CORS_ALLOWED_ORIGINS') else 'ALLOWED_ORIGINS',
)
for origin in CORS_ALLOWED_ORIGINS:
    _validate_https_origin('CORS_ALLOWED_ORIGINS', origin)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = _csv('CSRF_TRUSTED_ORIGINS')
for origin in CSRF_TRUSTED_ORIGINS:
    _validate_https_origin('CSRF_TRUSTED_ORIGINS', origin)
if FRONTEND_URL not in CORS_ALLOWED_ORIGINS or FRONTEND_URL not in CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured(
        'FRONTEND_URL must be present in CORS_ALLOWED_ORIGINS and CSRF_TRUSTED_ORIGINS.',
    )

if DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':  # noqa: F405
    raise ImproperlyConfigured('Production requires the existing PostgreSQL database.')
database = DATABASES['default']  # noqa: F405
if not database.get('HOST') or not database.get('NAME') or not database.get('USER') or not database.get('PASSWORD'):
    raise ImproperlyConfigured('Complete PostgreSQL connection settings are required.')
if database['HOST'].lower() in {'localhost', '127.0.0.1', '::1'}:
    raise ImproperlyConfigured('Production must connect to the existing remote PostgreSQL database.')
try:
    database['CONN_MAX_AGE'] = int(os.environ.get('DB_CONN_MAX_AGE', '60'))
except ValueError:
    raise ImproperlyConfigured('DB_CONN_MAX_AGE must be an integer.') from None
if not 0 <= database['CONN_MAX_AGE'] <= 600:
    raise ImproperlyConfigured('DB_CONN_MAX_AGE must be between 0 and 600 seconds.')
database['CONN_HEALTH_CHECKS'] = True
sslmode = os.environ.get('DB_SSLMODE', 'require').lower()
if sslmode not in {'require', 'verify-ca', 'verify-full'}:
    raise ImproperlyConfigured('Production PostgreSQL connections must use TLS.')
database.setdefault('OPTIONS', {})['sslmode'] = sslmode
database['OPTIONS']['connect_timeout'] = 5

EMAIL_BACKEND_PATH = _required('EMAIL_BACKEND')
if not EMAIL_BACKEND_PATH.endswith('smtp.EmailBackend'):
    raise ImproperlyConfigured('Production email must use the configured SMTP backend.')
email_options = MAILERS['default'].get('OPTIONS')  # noqa: F405
if not email_options or not all(
    email_options.get(key) for key in ('host', 'username', 'password')
):
    raise ImproperlyConfigured('SMTP host, username, and password are required.')
if email_options.get('use_ssl') and email_options.get('use_tls'):
    raise ImproperlyConfigured('Configure only one of EMAIL_USE_SSL and EMAIL_USE_TLS.')
DEFAULT_FROM_EMAIL = _required('DEFAULT_FROM_EMAIL')
AUTH_REQUIRE_EMAIL_VERIFICATION = True

SANDBOX_BACKEND = 'remote'
SANDBOX_RUNNER_URL = os.environ.get(
    'SANDBOX_RUNNER_URL', 'http://127.0.0.1:8765',
).strip()
SANDBOX_RUNNER_TOKEN = _required('SANDBOX_RUNNER_TOKEN')
if len(SANDBOX_RUNNER_TOKEN) < 32:
    raise ImproperlyConfigured('SANDBOX_RUNNER_TOKEN must contain at least 32 characters.')
runner_url = urlsplit(SANDBOX_RUNNER_URL)
if (
    runner_url.scheme != 'http'
    or runner_url.hostname != '127.0.0.1'
    or runner_url.username
    or runner_url.password
    or runner_url.path not in ('', '/')
    or runner_url.query
    or runner_url.fragment
):
    raise ImproperlyConfigured('SANDBOX_RUNNER_URL must use HTTP on 127.0.0.1.')
try:
    runner_port = runner_url.port
except ValueError:
    raise ImproperlyConfigured('SANDBOX_RUNNER_URL has an invalid port.') from None
if runner_port is None or not 1 <= runner_port <= 65535:
    raise ImproperlyConfigured('SANDBOX_RUNNER_URL must include a valid port.')
SANDBOX_TIMEOUT_SECONDS = 10.0
SANDBOX_MAX_OUTPUT_BYTES = 100_000

STATIC_URL = '/static/'
STATIC_ROOT = Path(os.environ.get('STATIC_ROOT', str(BASE_DIR / 'staticfiles')))  # noqa: F405
MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('MEDIA_ROOT', '/srv/codeyaar/media'))

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'
AUTH_REFRESH_COOKIE_SECURE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'production': {
            'format': '{asctime} {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'production',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO').upper(),
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
