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
        if getattr(request.user, 'is_authenticated', False):
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
