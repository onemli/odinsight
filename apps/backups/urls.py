
# =============================================================================
# apps/backups/urls.py - Backups app URLs
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'backup-jobs', views.BackupJobViewSet)
router.register(r'backup-files', views.BackupFileViewSet)

app_name = 'backups'

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.BackupListView.as_view(), name='backup_list'),
    path('jobs/', views.BackupJobListView.as_view(), name='backup_job_list'),
    path('jobs/<uuid:pk>/', views.BackupJobDetailView.as_view(), name='backup_job_detail'),
    path('files/', views.BackupFileListView.as_view(), name='backup_file_list'),
]