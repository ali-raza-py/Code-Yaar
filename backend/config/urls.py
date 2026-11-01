from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import JsonResponse
from django.views.static import serve


def health_check(request):
    """Liveness probe. Returns only a coarse status — no versions, secrets,
    DB credentials, or counts are exposed."""
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health-check'),
    path('api/auth/', include('learning.auth_urls')),
    path('api/', include('learning.api_urls')),
    path('api/', include('certificates.urls')),
]

# Serve admin uploads (track cover images) straight from MEDIA_ROOT in
# development; production front/server stacks are expected to put media
# behind a real file host instead.
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
