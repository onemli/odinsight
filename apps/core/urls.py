# =============================================================================
# apps/core/urls.py - Core app URLs
# =============================================================================

# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('workflow-builder2/', views.workflow_builder, name='workflow_builder'),
    path('devices/', views.device_management, name='device_management'),
    path('ansible/', views.ansible_integration, name='ansible_integration'),]