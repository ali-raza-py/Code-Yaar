from django.http import HttpResponse, JsonResponse
from django.utils.html import escape
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from .models import MaintenanceSettings


class MaintenanceModeMiddleware:
    """Block platform requests while preserving access for Django superusers."""

    AUTHENTICATION_PREFIX = '/api/auth/'
    EXEMPT_PREFIXES = (
        '/api/health/',
        '/api/platform/status/',
        '/api/admin/settings/',
        '/static/',
        '/media/',
        '/admin/login/',
    )

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authentication = JWTAuthentication()

    def __call__(self, request):
        if self._is_exempt(request):
            return self.get_response(request)

        # The cached snapshot keeps the per-request cost at zero database
        # round trips; admin toggles invalidate it on save, so a flip is
        # seen no later than the next request after the cache entry expires.
        snapshot = MaintenanceSettings.snapshot()
        if not snapshot['is_enabled']:
            return self.get_response(request)

        user = self._authenticated_user(request)
        if user is not None and user.is_superuser:
            return self.get_response(request)

        return self._maintenance_response(request, snapshot)

    def _is_exempt(self, request):
        path = request.path
        return (
            request.method == 'OPTIONS'
            or path.startswith(self.AUTHENTICATION_PREFIX)
            or path.startswith(self.EXEMPT_PREFIXES)
        )

    def _authenticated_user(self, request):
        if getattr(request, 'user', None) and request.user.is_authenticated:
            return request.user

        authorization = request.META.get('HTTP_AUTHORIZATION', '')
        if not authorization:
            return None

        try:
            authenticated = self.jwt_authentication.authenticate(request)
        except AuthenticationFailed:
            return None
        return authenticated[0] if authenticated else None

    def _maintenance_response(self, request, snapshot):
        message = snapshot['message'] or (
            'We are making improvements and will be back shortly.'
        )
        estimated_return_time = snapshot['estimated_return_time']
        payload = {
            'detail': message,
            'code': 'maintenance_mode',
            'maintenance_mode': True,
            'estimated_return_time': (
                estimated_return_time.isoformat() if estimated_return_time else None
            ),
        }
        if request.path.startswith('/api/'):
            response = JsonResponse(payload, status=503)
        else:
            response = HttpResponse(
                '<!doctype html><title>Maintenance</title>'
                f'<main><h1>We&rsquo;ll be back soon</h1><p>{escape(message)}</p></main>',
                status=503,
            )
        response['Retry-After'] = '300'
        return response


# ─── Cache-Control + server-side response caching ──────────────────────────

import re
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


# URL path regexes whose successful anonymous GET responses may be cached by
# browsers and CDNs. All other API responses are kept private.
PUBLIC_CACHE_PATTERNS = [
    re.compile(r'^/api/courses(?:/|$)'),
    re.compile(r'^/api/courses/[^/]+/?$'),
    re.compile(r'^/api/courses/[^/]+/chapters(?:/|$)'),
    re.compile(r'^/api/courses/[^/]+/chapters/[^/]+/?$'),
    re.compile(r'^/api/courses/[^/]+/lessons(?:/|$)'),
    re.compile(r'^/api/lessons/\d+/?$'),
    re.compile(r'^/api/tracks(?:/|$)'),
    re.compile(r'^/api/tracks/[^/]+/?$'),
    re.compile(r'^/api/leaderboard/?$'),
    re.compile(r'^/api/announcements(?:/|$)'),
    re.compile(r'^/api/announcements/[^/]+/?$'),
    re.compile(r'^/api/platform-updates(?:/|$)'),
    re.compile(r'^/api/platform-updates/[^/]+/?$'),
    re.compile(r'^/api/practical-classes(?:/|$)'),
    re.compile(r'^/api/practical-classes/[^/]+/?$'),
    re.compile(r'^/api/practical-subjects(?:/|$)'),
    re.compile(r'^/api/practicals(?:/|$)'),
    re.compile(r'^/api/practicals/[^/]+/?$'),
]

# Browser + CDN TTLs (seconds) per policy group.
PUBLIC_TTL_SECONDS = {
    'courses': 600,       # course list / detail / chapters / lessons
    'tracks': 900,        # tracks change rarely
    'leaderboard': 45,    # leaderboard snapshot
    'announcements': 120, # public announcements
    'updates': 900,       # platform changelog
    'practicals': 600,    # school practicals
    'default': 300,
}


def _public_policy_for_path(path: str) -> str:
    for pattern in PUBLIC_CACHE_PATTERNS:
        if pattern.search(path):
            if '/leaderboard' in path:
                return 'leaderboard'
            if '/tracks' in path:
                return 'tracks'
            if '/announcements' in path:
                return 'announcements'
            if '/platform-updates' in path:
                return 'updates'
            if 'practical' in path:
                return 'practicals'
            return 'courses'
    return 'default'


class PublicCacheControlMiddleware(MiddlewareMixin):
    """
    Stamp Cache-Control on outgoing responses based on path and auth state.

    Rules:
      - Public GET + 2xx + matching pattern  -> public, max-age=<ttl>
      - Public GET + 2xx + non-matching    -> private, no-cache
      - Any authenticated request          -> private, no-cache
      - Any write method                   -> private, no-cache
      - Error responses (4xx/5xx)          -> no-cache
    """
    async_mode = False

    def process_response(self, request, response):
        if not request.path.startswith('/api/'):
            return response
        if response.has_header('Cache-Control'):
            return response

        is_public_get = (
            request.method == 'GET'
            and response.status_code == 200
            and not (getattr(request, 'user', None) and request.user.is_authenticated)
        )

        if is_public_get:
            policy = _public_policy_for_path(request.path)
            ttl = PUBLIC_TTL_SECONDS.get(policy, PUBLIC_TTL_SECONDS['default'])
            response['Cache-Control'] = f'public, max-age={ttl}'
            if settings.DEBUG:
                response['Cache-Control'] += ', must-revalidate'
        else:
            response['Cache-Control'] = 'private, no-cache'

        return response


class ResponseCacheMiddleware(MiddlewareMixin):
    """
    Server-side response caching for expensive public read endpoints.

    Caches the rendered response body in Django's cache framework keyed by
    path + query string. Only anonymous GET 200 responses are stored.
    Authenticated requests bypass the cache entirely — personal data must not
    live in a shared cache.
    """
    async_mode = False

    def __init__(self, get_response):
        super().__init__(get_response)
        from django.core.cache import caches
        self.cache = caches['default']

    def _cache_key(self, request):
        query = request.META.get('QUERY_STRING', '')
        return f'cy:response:{request.path}?{query}'

    def process_request(self, request):
        if not request.path.startswith('/api/'):
            return None
        if request.method != 'GET':
            return None
        if getattr(request, 'user', None) and request.user.is_authenticated:
            return None

        key = self._cache_key(request)
        cached = self.cache.get(key)
        if cached is not None:
            status, headers, body = cached
            from django.http import HttpResponse
            response = HttpResponse(
                body, status=status,
                content_type=headers.get('Content-Type', 'application/json'),
            )
            for name, value in headers.items():
                if name.lower() not in ('content-type', 'content-length'):
                    response[name] = value
            return response
        return None

    def process_response(self, request, response):
        if not request.path.startswith('/api/'):
            return response
        if request.method != 'GET':
            return response
        if getattr(request, 'user', None) and request.user.is_authenticated:
            return response
        if response.status_code != 200:
            return response

        cc = response.get('Cache-Control', '')
        if 'public' not in cc:
            return response

        key = self._cache_key(request)
        ttl = PUBLIC_TTL_SECONDS.get(_public_policy_for_path(request.path), PUBLIC_TTL_SECONDS['default'])
        self.cache.set(
            key,
            (response.status_code, dict(response.items()), response.content),
            ttl,
        )
        return response
