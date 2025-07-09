# =============================================================================
# apps/workflows/admin.py - Workflows app admin
# =============================================================================

from django.contrib import admin
from .models import Workflow, WorkflowExecution

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'version', 'get_execution_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active', 'version')
        }),
        ('Workflow Data', {
            'fields': ('workflow_data',),
            'classes': ('collapse',)
        }),
    )
    
    def get_execution_count(self, obj):
        return obj.executions.count()
    get_execution_count.short_description = 'Executions'

@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'status', 'started_at', 'completed_at', 'created_at']
    list_filter = ['status', 'started_at', 'created_at']
    search_fields = ['workflow__name']
    readonly_fields = ['started_at', 'completed_at', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('workflow', 'status')
        }),
        ('Execution Details', {
            'fields': ('started_at', 'completed_at', 'error_message')
        }),
        ('Result Data', {
            'fields': ('result',),
            'classes': ('collapse',)
        }),
    )
