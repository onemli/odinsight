# =============================================================================
# apps/api/v1/urls.py - API v1 URLs
# =============================================================================

from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    path('devices/', include('apps.devices.urls', namespace='devices_api')),
    path('workflows/', include('apps.workflows.urls', namespace='workflows_api')),
    path('network/', include('apps.network.urls', namespace='network_api')),
    path('backups/', include('apps.backups.urls', namespace='backups_api')),
    path('integrations/', include('apps.integrations.urls', namespace='integrations_api')),
    path('users/', include('apps.users.urls', namespace='users_api')),
]