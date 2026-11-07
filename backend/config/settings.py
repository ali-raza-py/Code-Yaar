"""
Django settings for config project.
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
# Fall back to an insecure dev key when the variable is unset *or* empty, so a
# blank SECRET_KEY= line in .env does not crash cookie/session signing.
SECRET_KEY = os.getenv('SECRET_KEY') or 'django-insecure-dev-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    # Enables refresh-token rotation/revocation (OutstandingToken/BlacklistedToken).
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    *(['debug_toolbar'] if DEBUG else []),
    # Local
    'learning',
    'certificates',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    *(['debug_toolbar.middleware.DebugToolbarMiddleware'] if DEBUG else []),
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'learning.middleware.MaintenanceModeMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# The toolbar is intentionally available only while Django DEBUG is enabled.
# Keep the allowlist configurable for local containers and remote development.
if DEBUG:
    INTERNAL_IPS = [
        address.strip()
        for address in os.getenv('INTERNAL_IPS', '127.0.0.1,::1').split(',')
        if address.strip()
    ]

# Reverse-proxy awareness (set behind nginx/traefik in production so
# is_secure() honours the client-facing scheme).
if os.getenv('USE_X_FORWARDED_PROTO') == 'True':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ROOT_URLCONF = 'config.urls'

# Auth backends — allow signing in with email or username

AUTHENTICATION_BACKENDS = [
    'learning.authentication.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database resolution order:
#   1. DATABASE_URL                 - full PostgreSQL connection string, parsed
#                                     with dj-database-url.
#   2. DB_ENGINE=postgres + DB_*    - discrete PostgreSQL settings.
#   3. DB_ENGINE=sqlite             - explicit local-development override.
#   4. sqlite file fallback         - keeps an unconfigured checkout usable.
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

_database_url = os.getenv('DATABASE_URL', '').strip()
# Older local examples used a [YOUR-PASSWORD] marker. Retain support for it
# while keeping the real password out of source code and allowing characters
# such as @, /, and : in DB_PASSWORD.
if '[YOUR-PASSWORD]' in _database_url:
    from urllib.parse import quote

    _database_url = _database_url.replace(
        '[YOUR-PASSWORD]', quote(os.getenv('DB_PASSWORD', ''), safe='')
    )
_db_engine = os.getenv('DB_ENGINE', '').strip().lower()

if _database_url and _db_engine == 'sqlite':
    raise RuntimeError(
        'DATABASE_URL is configured for PostgreSQL, but DB_ENGINE=sqlite. '
        'Remove DB_ENGINE=sqlite or remove DATABASE_URL intentionally.'
    )

if _database_url:
    import dj_database_url

    if _database_url.startswith('sqlite'):
        raise RuntimeError(
            'DATABASE_URL must be a PostgreSQL URL. Use DB_ENGINE=sqlite '
            'for an explicit local SQLite configuration.'
        )

    DATABASES = {
        'default': dj_database_url.parse(
            _database_url,
            conn_max_age=int(os.getenv('DB_CONN_MAX_AGE', '600')),
            conn_health_checks=True,
        )
    }
    DATABASES['default'].setdefault('ENGINE', 'django.db.backends.postgresql')
    _opts = DATABASES['default'].setdefault('OPTIONS', {})
    _opts['sslmode'] = os.getenv('DB_SSLMODE', 'require')
elif _db_engine == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    _db_host = os.getenv('DB_HOST', 'localhost')
    # Hosted Postgres (Supabase and similar) reject non-TLS connections and
    # require sslmode; a local server does not. Default to 'require' for any
    # remote host, '' (server preference) for localhost so local dev still works.
    _default_sslmode = '' if _db_host in ('', 'localhost', '127.0.0.1', '::1') else 'require'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'code_yaar'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': _db_host,
            'PORT': os.getenv('DB_PORT', '5432'),
            # Reuse connections across requests; harmless for SQLite path.
            # Reconnecting to hosted Postgres costs a full TCP+TLS handshake,
            # so keep pooled connections alive for ten minutes by default.
            'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '600')),
            'OPTIONS': {
                'sslmode': os.getenv('DB_SSLMODE', _default_sslmode),
            },
        }
    }

if DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
    # Pool-safety for hosted Postgres: validate a reused connection before it
    # is handed to a request, and cap how long one lives so a pooler-side kill
    # can never strand a stale server-side connection.
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True
    DATABASES['default']['CONN_MAX_AGE'] = int(os.getenv('DB_CONN_MAX_AGE', '600'))


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'
# Where `manage.py collectstatic` gathers files for production serving.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (generated certificate PDFs, uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Public base URL used to build certificate verification links embedded in QR
# codes. Must be set to the real site origin in production (.env SITE_URL).
SITE_URL = os.getenv('SITE_URL', 'http://localhost:3000').rstrip('/')

# Certificate issuance defaults (per-course values override these in the DB).
CERTIFICATE_DEFAULT_PASSING_SCORE = float(os.getenv('CERT_PASSING_SCORE', '70'))

# Origins used to build links inside transactional emails. `FRONTEND_URL`
# must point at the Next.js app; verification/reset links are frontend routes
# that exchange their token for an API call.
FRONTEND_URL = os.getenv('FRONTEND_URL', SITE_URL).rstrip('/')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000').rstrip('/')

# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration
# Django 6 configures transports through `MAILERS`; the legacy EMAIL_* settings
# are rejected when MAILERS exists, so transport options live under OPTIONS.
# The console backend is the safe default (nothing leaves the machine); set
# EMAIL_BACKEND to smtp.EmailBackend plus the EMAIL_HOST* values to deliver real
# mail. For Gmail: EMAIL_HOST=smtp.gmail.com, EMAIL_PORT=587, EMAIL_USE_TLS=True
# and EMAIL_HOST_PASSWORD set to a 16-character App Password (not the account
# password - Google no longer accepts those for SMTP).


def _env_flag(name, default=False):
    """Read a boolean env var; `True`, `1`, `yes` and `on` all mean true."""
    return os.getenv(name, str(default)).strip().lower() in {
        '1',
        'true',
        'yes',
        'on',
    }


EMAIL_BACKEND_PATH = os.getenv(
    'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend'
)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Code Yaar <no-reply@codeyaar.dev>')
# Reply-to for admin-composed campaign mail only; empty means mail replies go
# back to the sender address itself. The composer never lets a caller override
# the From identity — this is the only knob, and it lives here server-side.
REPLY_TO_EMAIL = os.getenv('REPLY_TO_EMAIL', '').strip()

MAILERS = {
    'default': {
        'BACKEND': EMAIL_BACKEND_PATH,
    },
}

# SMTP options are only passed to the SMTP backend: other backends (console,
# file, locmem) reject unknown options.
if EMAIL_BACKEND_PATH.endswith('smtp.EmailBackend'):
    MAILERS['default']['OPTIONS'] = {
        'host': os.getenv('EMAIL_HOST', 'localhost').strip(),
        'port': int(os.getenv('EMAIL_PORT') or 25),
        'username': os.getenv('EMAIL_HOST_USER', '').strip(),
        # Google shows App Passwords in four groups of four characters. The
        # spaces are presentation only and make the SMTP login fail when sent
        # verbatim, so they are stripped here instead of relying on the user.
        'password': os.getenv('EMAIL_HOST_PASSWORD', '').replace(' ', ''),
        'use_tls': _env_flag('EMAIL_USE_TLS'),
        'use_ssl': _env_flag('EMAIL_USE_SSL'),
        'timeout': int(os.getenv('EMAIL_TIMEOUT') or 10),
    }

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration
# `localhost` and `127.0.0.1` are two different origins, and Next.js answers on
# both. Allowing only one of them makes every request from the other fail as an
# opaque "Failed to fetch" in the browser, so both are allowed in development.
DEV_FRONTEND_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'ALLOWED_ORIGINS',
        ','.join(DEV_FRONTEND_ORIGINS if DEBUG else DEV_FRONTEND_ORIGINS[:1]),
    ).split(',')
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True

# CSRF: trust the site origin (used by admin/API sessions) in addition to
# any comma-separated origins provided via env.
_csrf_origins = [SITE_URL, *os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')]
if DEBUG:
    _csrf_origins += DEV_FRONTEND_ORIGINS
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_origins if origin.strip()]

# Hardening applied whenever DEBUG is off — never weaken these in prod.
if not DEBUG:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = os.getenv('USE_X_FORWARDED_PROTO') == 'True'
    CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ─── Authentication: JWT access + HttpOnly refresh cookie ───
#
# Access tokens are short-lived and only ever held in frontend memory.
# Refresh tokens live in an HttpOnly cookie so they are never readable by
# JavaScript, are rotated on every refresh, and are blacklisted on rotation,
# logout, password change, and password reset.

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=int(os.getenv('JWT_ACCESS_TOKEN_MINUTES') or 15)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=int(os.getenv('JWT_REFRESH_TOKEN_DAYS') or 7)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'UPDATE_LAST_LOGIN': False,
}

# Refresh cookie. SameSite=Lax is sufficient for the same-site frontend/API
# pair and is re-validated by a CSRF double-submit check on every cookie-based
# endpoint (`/auth/token/refresh/`, `/auth/logout/`).
AUTH_REFRESH_COOKIE_NAME = os.getenv('AUTH_REFRESH_COOKIE_NAME', 'cy_refresh')
AUTH_REFRESH_COOKIE_PATH = os.getenv('AUTH_REFRESH_COOKIE_PATH', '/')
AUTH_REFRESH_COOKIE_DOMAIN = os.getenv('AUTH_REFRESH_COOKIE_DOMAIN') or None
AUTH_REFRESH_COOKIE_SAMESITE = os.getenv('AUTH_REFRESH_COOKIE_SAMESITE', 'Lax')
AUTH_REFRESH_COOKIE_SECURE = os.getenv(
    'AUTH_REFRESH_COOKIE_SECURE', 'False' if DEBUG else 'True'
) == 'True'

# Email verification / password reset token lifetimes.
AUTH_EMAIL_VERIFICATION_TTL_HOURS = int(
    os.getenv('AUTH_EMAIL_VERIFICATION_TTL_HOURS') or 24
)
AUTH_PASSWORD_RESET_TTL_MINUTES = int(
    os.getenv('AUTH_PASSWORD_RESET_TTL_MINUTES') or 60
)
# When True, unverified accounts cannot sign in, and endpoints guarded by
# `IsEmailVerified` reject them. Left unset it follows the mail transport: a
# platform that demands verification it cannot deliver would lock every new
# account out, so the gate arms itself only once SMTP has a password. Set
# AUTH_REQUIRE_EMAIL_VERIFICATION=True/False to force the policy either way.
_verification_flag = os.getenv('AUTH_REQUIRE_EMAIL_VERIFICATION', '').strip().lower()
if _verification_flag:
    AUTH_REQUIRE_EMAIL_VERIFICATION = _verification_flag in {'1', 'true', 'yes', 'on'}
else:
    AUTH_REQUIRE_EMAIL_VERIFICATION = bool(
        EMAIL_BACKEND_PATH.endswith('smtp.EmailBackend')
        and os.getenv('EMAIL_HOST_PASSWORD', '').strip()
    )

# Django REST Framework
REST_FRAMEWORK = {
    # The `format` query parameter is reserved by the download endpoints
    # (certificates/badges use `?format=pdf|png|svg`) to pick a file type, so it
    # must NOT double as DRF's content-negotiation override — otherwise DRF tries
    # to find a renderer named "pdf", fails, and returns 404 before the view
    # runs. Representation is negotiated purely via the Accept header instead.
    'URL_FORMAT_OVERRIDE': None,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'learning.pagination.FlexiblePagination',
    'PAGE_SIZE': 100,
    # Scoped throttles guard credential endpoints against brute force and
    # email-bombing. Views opt in through `throttle_scope`.
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'auth_login': os.getenv('THROTTLE_AUTH_LOGIN', '10/min'),
        'auth_register': os.getenv('THROTTLE_AUTH_REGISTER', '10/hour'),
        'auth_verify_email': os.getenv('THROTTLE_AUTH_VERIFY_EMAIL', '20/min'),
        'auth_resend_verification': os.getenv(
            'THROTTLE_AUTH_RESEND_VERIFICATION', '5/hour'
        ),
        'auth_password_reset': os.getenv('THROTTLE_AUTH_PASSWORD_RESET', '5/hour'),
        'auth_password_reset_confirm': os.getenv(
            'THROTTLE_AUTH_PASSWORD_RESET_CONFIRM', '10/hour'
        ),
        'auth_change_password': os.getenv(
            'THROTTLE_AUTH_CHANGE_PASSWORD', '10/hour'
        ),
        'auth_refresh': os.getenv('THROTTLE_AUTH_REFRESH', '120/min'),
        'avatar_upload': os.getenv('THROTTLE_AVATAR_UPLOAD', '10/min'),
        'portfolio_media_upload': os.getenv('THROTTLE_PORTFOLIO_MEDIA_UPLOAD', '20/min'),
        # Admin composer sends (send / test / resend) per administrator.
        'email_campaign_send': os.getenv('THROTTLE_EMAIL_CAMPAIGN_SEND', '60/hour'),
    },
}


