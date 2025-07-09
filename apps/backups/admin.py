# =============================================================================
# apps/backups/admin.py - Backups app admin
# =============================================================================

from django.contrib import admin
from .models import BackupJob, BackupFile

@admin.register(BackupJob)
class BackupJobAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'get_device_count', 'last_run', 'next_run', 'created_at']
    list_filter = ['status', 'last_run', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['status']
    filter_horizontal = ['devices']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'status')
        }),
        ('Devices', {
            'fields': ('devices',)
        }),
        ('Schedule', {
            'fields': ('schedule', 'last_run', 'next_run')
        }),
    )
    
    def get_device_count(self, obj):
        return obj.devices.count()
    get_device_count.short_description = 'Device Count'

@admin.register(BackupFile)
class BackupFileAdmin(admin.ModelAdmin):
    list_display = ['device', 'backup_job', 'backup_type', 'file_size_mb', 'created_at']
    list_filter = ['backup_type', 'device', 'backup_job', 'created_at']
    search_fields = ['device__name', 'backup_job__name', 'file_path']
    readonly_fields = ['file_size', 'checksum', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('device', 'backup_job', 'backup_type')
        }),
        ('File Details', {
            'fields': ('file_path', 'file_size', 'checksum')
        }),
    )
    
    def file_size_mb(self, obj):
        return f"{obj.file_size / (1024*1024):.2f} MB"
    file_size_mb.short_description = 'File Size'