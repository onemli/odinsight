# =============================================================================
# config/urls.py - Main URL configuration
# =============================================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.api.v1.urls')),
    path('api/v2/', include('apps.api.v2.urls')),
    path('devices/', include('apps.devices.urls')),
    path('workflows/', include('apps.workflows.urls')),
    path('network/', include('apps.network.urls')),
    path('backups/', include('apps.backups.urls')),
    path('integrations/', include('apps.integrations.urls')),
    path('users/', include('apps.users.urls')),
    path('', include('apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns