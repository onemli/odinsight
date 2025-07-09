# =============================================================================
# apps/backups/models.py - Backups app models
# =============================================================================

from django.db import models
from apps.core.models import BaseModel
from apps.devices.models import Device

class BackupJob(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    devices = models.ManyToManyField(Device, related_name='backup_jobs')
    schedule = models.CharField(max_length=100, blank=True)  # Cron expression
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'backup_jobs'

class BackupFile(BaseModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='backup_files')
    backup_job = models.ForeignKey(BackupJob, on_delete=models.CASCADE, related_name='backup_files')
    file_path = models.CharField(max_length=500)
    file_size = models.PositiveBigIntegerField(default=0)
    checksum = models.CharField(max_length=64, blank=True)
    backup_type = models.CharField(max_length=50, default='config')
    
    def __str__(self):
        return f"{self.device.name} - {self.created_at}"
    
    class Meta:
        db_table = 'backup_files'