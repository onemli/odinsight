# =============================================================================
# apps/devices/urls.py - Devices app URLs
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'devices', views.DeviceViewSet)
router.register(r'device-groups', views.DeviceGroupViewSet)
router.register(r'device-types', views.DeviceTypeViewSet)

app_name = 'devices'

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.DeviceListView.as_view(), name='device_list'),
    path('<uuid:pk>/', views.DeviceDetailView.as_view(), name='device_detail'),
    path('groups/', views.DeviceGroupListView.as_view(), name='device_group_list'),
]