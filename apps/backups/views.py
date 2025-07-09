# =============================================================================
# apps/backups/views.py - Backups app views
# =============================================================================

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from rest_framework import viewsets
from .models import BackupJob, BackupFile
from .serializers import BackupJobSerializer, BackupFileSerializer

class BackupJobViewSet(viewsets.ModelViewSet):
    queryset = BackupJob.objects.all()
    serializer_class = BackupJobSerializer

class BackupFileViewSet(viewsets.ModelViewSet):
    queryset = BackupFile.objects.all()
    serializer_class = BackupFileSerializer

class BackupListView(ListView):
    model = BackupFile
    template_name = 'backups/backup_list.html'
    context_object_name = 'backups'

class BackupJobListView(ListView):
    model = BackupJob
    template_name = 'backups/backup_job_list.html'
    context_object_name = 'backup_jobs'

class BackupJobDetailView(DetailView):
    model = BackupJob
    template_name = 'backups/backup_job_detail.html'
    context_object_name = 'backup_job'

class BackupFileListView(ListView):
    model = BackupFile
    template_name = 'backups/backup_file_list.html'
    context_object_name = 'backup_files'