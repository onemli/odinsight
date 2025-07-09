# =============================================================================
# apps/network/urls.py - Network app URLs
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'topology', views.NetworkTopologyViewSet)
router.register(r'routes', views.RoutingTableViewSet)

app_name = 'network'

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.NetworkOverviewView.as_view(), name='network_overview'),
    path('topology/', views.TopologyView.as_view(), name='topology'),
    path('routes/', views.RouteAnalysisView.as_view(), name='route_analysis'),
    path('path-analysis/', views.PathAnalysisView.as_view(), name='path_analysis'),
]
