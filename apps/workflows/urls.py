# =============================================================================
# apps/workflows/urls.py - Workflows app URLs
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'workflows', views.WorkflowViewSet)
router.register(r'executions', views.WorkflowExecutionViewSet)

app_name = 'workflows'

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.WorkflowListView.as_view(), name='workflow_list'),
    path('<uuid:pk>/', views.WorkflowDetailView.as_view(), name='workflow_detail'),
    path('<uuid:pk>/builder/', views.WorkflowBuilderView.as_view(), name='workflow_builder'),
    path('<uuid:pk>/execute/', views.WorkflowExecuteView.as_view(), name='workflow_execute'),
]
