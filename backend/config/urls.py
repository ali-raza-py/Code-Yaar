from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    """Liveness probe. Returns only a coarse status — no versions, secrets,
    DB credentials, or counts are exposed."""
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/', include('learning.api_urls')),
    path('api/', include('certificates.urls')),
]
