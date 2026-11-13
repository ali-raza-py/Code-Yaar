from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views.static import serve
from django.conf.urls.static import static
import logging

if settings.DEBUG:
    import debug_toolbar

logger = logging.getLogger(__name__)


def health_check(request):
    """Liveness probe. Returns only a coarse status — no versions, secrets,
    DB credentials, or counts are exposed."""
    return JsonResponse({'status': 'ok'})


def readiness_check(request):
    """Read-only readiness probe that confirms the configured database responds."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except DatabaseError:
        logger.exception('Readiness database check failed.')
        return JsonResponse({'status': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok', 'database': 'ok'})


def root_view(request):
    """Root endpoint. Lightweight JSON status page — no secrets or internals."""
    return JsonResponse({
        'service': 'Code Yaar API',
        'status': 'operational',
        'message': 'Backend is running.',
    })


urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/health/ready/', readiness_check, name='readiness-check'),
    path('api/auth/', include('learning.auth_urls')),
    path('api/', include('learning.api_urls')),
    path('api/', include('certificates.urls')),
]

if settings.DEBUG:
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
        *urlpatterns,
    ]
