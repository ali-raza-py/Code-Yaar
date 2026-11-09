"""Cloudflare Worker settings; production secrets are supplied by Worker bindings."""

import os
from urllib.parse import urlsplit

os.environ['DEBUG'] = 'False'
os.environ['PYTHON_DOTENV_DISABLED'] = '1'

from django.core.exceptions import ImproperlyConfigured
from workers import env

from .settings import *  # noqa: F403


def _required(name: str) -> str:
    value = getattr(env, name, None)
    if not isinstance(value, str) or not value.strip():
        raise ImproperlyConfigured(f'Cloudflare Worker value {name} is required.')
    return value.strip()


def _csv(name: str) -> list[str]:
    values = [value.strip() for value in _required(name).split(',') if value.strip()]
    if not values:
        raise ImproperlyConfigured(f'{name} must contain at least one value.')
    return values


def _flag(name: str) -> bool:
    value = _required(name).lower()
    if value not in {'true', 'false'}:
        raise ImproperlyConfigured(f'{name} must be "true" or "false".')
    return value == 'true'


def _hyperdrive_value(name: str) -> str:
    value = getattr(hyperdrive, name, None)
    if value is None or not str(value).strip():
        raise ImproperlyConfigured(f'Hyperdrive binding field {name} is required.')
    return str(value).strip()


DEBUG = False
SECRET_KEY = _required('DJANGO_SECRET_KEY')
if len(SECRET_KEY) < 50 or SECRET_KEY.startswith('django-insecure-'):
    raise ImproperlyConfigured('DJANGO_SECRET_KEY must be a strong, non-development value.')

ALLOWED_HOSTS = _csv('DJANGO_ALLOWED_HOSTS')
if '*' in ALLOWED_HOSTS or any('/' in host or '://' in host for host in ALLOWED_HOSTS):
    raise ImproperlyConfigured('DJANGO_ALLOWED_HOSTS must contain hostnames only.')

SITE_URL = _required('SITE_URL').rstrip('/')
FRONTEND_URL = _required('FRONTEND_URL').rstrip('/')
BACKEND_URL = _required('BACKEND_URL').rstrip('/')
CORS_ALLOWED_ORIGINS = _csv('CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = _csv('CSRF_TRUSTED_ORIGINS')
if FRONTEND_URL not in CORS_ALLOWED_ORIGINS or FRONTEND_URL not in CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured(
        'FRONTEND_URL must be present in CORS_ALLOWED_ORIGINS and CSRF_TRUSTED_ORIGINS.'
    )
CORS_ALLOW_CREDENTIALS = True

try:
    hyperdrive = env.HYPERDRIVE
except AttributeError:
    raise ImproperlyConfigured('The HYPERDRIVE binding is required.') from None

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _hyperdrive_value('database'),
        'USER': _hyperdrive_value('user'),
        'PASSWORD': _hyperdrive_value('password'),
        'HOST': _hyperdrive_value('host'),
        'PORT': _hyperdrive_value('port'),
        'CONN_MAX_AGE': 0,
        'CONN_HEALTH_CHECKS': False,
        'OPTIONS': {'sslmode': 'disable'},
    }
}

EMAIL_BACKEND_PATH = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = _required('DEFAULT_FROM_EMAIL')
email_use_tls = _flag('EMAIL_USE_TLS')
email_use_ssl = _flag('EMAIL_USE_SSL')
if email_use_tls == email_use_ssl:
    raise ImproperlyConfigured('Configure exactly one of EMAIL_USE_TLS or EMAIL_USE_SSL.')
MAILERS = {
    'default': {
        'BACKEND': EMAIL_BACKEND_PATH,
        'OPTIONS': {
            'host': _required('EMAIL_HOST'),
            'port': int(_required('EMAIL_PORT')),
            'username': _required('EMAIL_HOST_USER'),
            'password': _required('EMAIL_HOST_PASSWORD'),
            'use_tls': email_use_tls,
            'use_ssl': email_use_ssl,
            'timeout': 10,
        },
    },
}
AUTH_REQUIRE_EMAIL_VERIFICATION = True

SANDBOX_BACKEND = 'remote'
SANDBOX_RUNNER_URL = _required('SANDBOX_RUNNER_URL')
SANDBOX_RUNNER_TOKEN = _required('SANDBOX_RUNNER_TOKEN')
runner_url = urlsplit(SANDBOX_RUNNER_URL)
if (
    runner_url.scheme != 'https'
    or not runner_url.hostname
    or runner_url.username
    or runner_url.password
    or runner_url.path not in ('', '/')
    or runner_url.query
    or runner_url.fragment
):
    raise ImproperlyConfigured(
        'SANDBOX_RUNNER_URL must be a credential-free HTTPS origin without a path.'
    )
try:
    runner_port = runner_url.port
except ValueError:
    raise ImproperlyConfigured('SANDBOX_RUNNER_URL has an invalid port.') from None
if runner_port is not None and not 1 <= runner_port <= 65535:
    raise ImproperlyConfigured('SANDBOX_RUNNER_URL has an invalid port.')
if len(SANDBOX_RUNNER_TOKEN) < 32:
    raise ImproperlyConfigured('SANDBOX_RUNNER_TOKEN must contain at least 32 characters.')
SANDBOX_TIMEOUT_SECONDS = 10.0
SANDBOX_MAX_OUTPUT_BYTES = 100_000

R2_S3_ENDPOINT_URL = _required('R2_S3_ENDPOINT_URL')
if urlsplit(R2_S3_ENDPOINT_URL).scheme != 'https':
    raise ImproperlyConfigured('R2_S3_ENDPOINT_URL must use HTTPS.')
AWS_ACCESS_KEY_ID = _required('R2_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = _required('R2_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = _required('R2_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = R2_S3_ENDPOINT_URL
AWS_S3_REGION_NAME = 'auto'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = True
AWS_S3_FILE_OVERWRITE = False
STORAGES = {
    'default': {'BACKEND': 'storages.backends.s3.S3Storage'},
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}
CLOUD_STORAGE_ENABLED = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'
AUTH_REFRESH_COOKIE_SECURE = True
