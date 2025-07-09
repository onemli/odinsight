# =============================================================================
# apps/integrations/admin.py - Integrations app admin
# =============================================================================

from django.contrib import admin
from .models import Integration

@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'integration_type', 'is_active', 'last_sync', 'created_at']
    list_filter = ['integration_type', 'is_active', 'last_sync']
    search_fields = ['name']
    list_editable = ['is_active']
    ordering = ['integration_type', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'integration_type', 'is_active')
        }),
        ('Configuration', {
            'fields': ('config',),
            'classes': ('collapse',)
        }),
        ('Sync Information', {
            'fields': ('last_sync',),
            'classes': ('collapse',)
        }),
    )