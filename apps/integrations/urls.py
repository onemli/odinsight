# =============================================================================
# apps/integrations/urls.py - Integrations app URLs
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'integrations', views.IntegrationViewSet)

app_name = 'integrations'

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.IntegrationListView.as_view(), name='integration_list'),
    path('netbox/', views.NetBoxIntegrationView.as_view(), name='netbox_integration'),
    path('ansible/', views.AnsibleIntegrationView.as_view(), name='ansible_integration'),
    path('sync/', views.SyncView.as_view(), name='sync'),
]