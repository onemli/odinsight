# apps/workflows/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import (
    ModuleCategory, Module, Workflow, WorkflowNode, 
    WorkflowEdge, WorkflowExecution, NodeExecution
)

@admin.register(ModuleCategory)
class ModuleCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'parent', 'module_count', 'sort_order', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'display_name', 'description']
    ordering = ['sort_order', 'name']
    list_editable = ['sort_order', 'is_active']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'display_name', 'description', 'icon')
        }),
        ('Hierarchy', {
            'fields': ('parent', 'sort_order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def module_count(self, obj):
        return obj.modules.filter(is_active=True).count()
    module_count.short_description = 'Active Modules'

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'alias', 'module_type', 'category', 'provider', 
        'input_count', 'output_count', 'version', 'is_active'
    ]
    list_filter = [
        'module_type', 'provider', 'category', 'is_active', 
        'is_deprecated', 'created_at'
    ]
    search_fields = ['name', 'alias', 'description', 'tags']
    ordering = ['category', 'name']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at', 'input_count', 'output_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'alias', 'module_type', 'category', 'subcategory',
                'description', 'provider', 'version'
            )
        }),
        ('Connection Points', {
            'fields': ('inputs', 'outputs'),
            'description': 'JSON arrays defining input and output parameters'
        }),
        ('Configuration', {
            'fields': ('default_yaml', 'example_usage', 'tags'),
            'classes': ('collapse',)
        }),
        ('Parser Settings', {
            'fields': ('parser_schema', 'parser_rules'),
            'classes': ('collapse',),
            'description': 'Only applicable for parser-type modules'
        }),
        ('Metadata', {
            'fields': (
                'documentation_url', 'is_active', 'is_deprecated', 
                'deprecated_message', 'created_by'
            )
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'input_count', 'output_count'),
            'classes': ('collapse',)
        })
    )
    
    def input_count(self, obj):
        return obj.input_count
    input_count.short_description = 'Inputs'
    
    def output_count(self, obj):
        return obj.output_count
    output_count.short_description = 'Outputs'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class WorkflowNodeInline(admin.TabularInline):
    model = WorkflowNode
    extra = 0
    fields = [
        'node_id', 'module', 'display_name', 'position_x', 'position_y', 
        'execution_order', 'is_enabled'
    ]
    readonly_fields = ['node_id', 'position_x', 'position_y']

class WorkflowEdgeInline(admin.TabularInline):
    model = WorkflowEdge
    extra = 0
    fields = [
        'edge_id', 'source_node_id', 'target_node_id', 
        'edge_type', 'label', 'is_animated'
    ]
    readonly_fields = ['edge_id', 'source_node_id', 'target_node_id']

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'workflow_type', 'status', 'owner', 
        'node_count', 'edge_count', 'execution_count', 
        'success_rate_display', 'last_executed', 'updated_at'
    ]
    list_filter = [
        'workflow_type', 'status', 'is_public', 'is_template', 
        'created_at', 'last_executed'
    ]
    search_fields = ['name', 'description', 'tags', 'owner__username']
    ordering = ['-updated_at']
    list_editable = ['status']
    readonly_fields = [
        'created_at', 'updated_at', 'node_count', 'edge_count',
        'execution_count', 'success_count', 'success_rate_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'description', 'workflow_type', 'status',
                'version', 'tags'
            )
        }),
        ('Ownership & Sharing', {
            'fields': ('owner', 'shared_users', 'is_public')
        }),
        ('Template Settings', {
            'fields': ('is_template', 'template_category'),
            'classes': ('collapse',)
        }),
        ('Execution Settings', {
            'fields': (
                'execution_timeout', 'max_retries', 'retry_delay',
                'variables'
            ),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': (
                'node_count', 'edge_count', 'execution_count', 
                'success_count', 'success_rate_display', 'last_executed',
                'average_execution_time'
            ),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [WorkflowNodeInline, WorkflowEdgeInline]
    
    def node_count(self, obj):
        return obj.node_count
    node_count.short_description = 'Nodes'
    
    def edge_count(self, obj):
        return obj.edge_count
    edge_count.short_description = 'Edges'
    
    def success_rate_display(self, obj):
        rate = obj.success_rate
        if rate >= 90:
            color = 'green'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    success_rate_display.short_description = 'Success Rate'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner').prefetch_related(
            'nodes', 'edges', 'executions'
        )

@admin.register(WorkflowNode)
class WorkflowNodeAdmin(admin.ModelAdmin):
    list_display = [
        'workflow', 'node_id', 'module', 'display_name', 
        'position_x', 'position_y', 'execution_order', 'is_enabled'
    ]
    list_filter = ['workflow', 'module__category', 'is_enabled', 'continue_on_error']
    search_fields = ['workflow__name', 'module__name', 'display_name', 'node_id']
    ordering = ['workflow', 'execution_order']
    list_editable = ['execution_order', 'is_enabled']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('workflow', 'module', 'node_id', 'display_name')
        }),
        ('Position & Layout', {
            'fields': ('position_x', 'position_y', 'width', 'height')
        }),
        ('Configuration', {
            'fields': ('custom_yaml', 'custom_config', 'custom_tags', 'node_variables'),
            'classes': ('collapse',)
        }),
        ('Execution Settings', {
            'fields': (
                'execution_order', 'is_enabled', 'continue_on_error',
                'timeout_override', 'condition_expression', 'depends_on'
            )
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(WorkflowEdge)
class WorkflowEdgeAdmin(admin.ModelAdmin):
    list_display = [
        'workflow', 'edge_id', 'source_node_id', 'target_node_id',
        'edge_type', 'label', 'is_animated'
    ]
    list_filter = ['workflow', 'edge_type', 'is_animated']
    search_fields = ['workflow__name', 'edge_id', 'label']
    ordering = ['workflow', 'created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('workflow', 'edge_id', 'edge_type', 'label')
        }),
        ('Connection', {
            'fields': (
                'source_node_id', 'target_node_id',
                'source_handle', 'target_handle'
            )
        }),
        ('Configuration', {
            'fields': ('condition', 'data_mapping', 'style_config'),
            'classes': ('collapse',)
        }),
        ('Visual', {
            'fields': ('is_animated',)
        })
    )

class NodeExecutionInline(admin.TabularInline):
    model = NodeExecution
    extra = 0
    readonly_fields = [
        'node', 'status', 'started_at', 'completed_at', 
        'duration', 'output_data_preview'
    ]
    
    def output_data_preview(self, obj):
        if obj.output_data:
            preview = str(obj.output_data)[:100]
            if len(str(obj.output_data)) > 100:
                preview += "..."
            return preview
        return "-"
    output_data_preview.short_description = 'Output Preview'

@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):
    list_display = [
        'workflow', 'execution_id_short', 'status', 'started_by',
        'started_at', 'duration', 'nodes_executed', 'success_rate_display'
    ]
    list_filter = [
        'status', 'started_at', 'workflow', 'started_by'
    ]
    search_fields = [
        'workflow__name', 'execution_id', 'started_by__username'
    ]
    ordering = ['-started_at']
    readonly_fields = [
        'execution_id', 'started_at', 'completed_at', 'duration',
        'success_rate_display', 'execution_summary_display'
    ]
    
    fieldsets = (
        ('Basic Info', {
            'fields': (
                'workflow', 'execution_id', 'status', 'started_by'
            )
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration')
        }),
        ('Configuration', {
            'fields': ('execution_variables', 'execution_context'),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': (
                'result_data', 'error_message', 'log_output',
                'execution_summary_display'
            ),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': (
                'nodes_executed', 'nodes_successful', 'nodes_failed',
                'nodes_skipped', 'success_rate_display'
            )
        }),
        ('Generated Files', {
            'fields': ('generated_playbook', 'generated_inventory', 'output_files'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [NodeExecutionInline]
    
    def execution_id_short(self, obj):
        return obj.execution_id[:8] + "..." if len(obj.execution_id) > 8 else obj.execution_id
    execution_id_short.short_description = 'Execution ID'
    
    def success_rate_display(self, obj):
        rate = obj.success_rate
        if rate >= 90:
            color = 'green'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, rate
        )
    success_rate_display.short_description = 'Success Rate'
    
    def execution_summary_display(self, obj):
        summary = {
            'total_nodes': obj.nodes_executed,
            'successful': obj.nodes_successful,
            'failed': obj.nodes_failed,
            'skipped': obj.nodes_skipped,
            'success_rate': f"{obj.success_rate:.1f}%"
        }
        return format_html(
            '<pre>{}</pre>',
            json.dumps(summary, indent=2)
        )
    execution_summary_display.short_description = 'Summary'

@admin.register(NodeExecution)
class NodeExecutionAdmin(admin.ModelAdmin):
    list_display = [
        'workflow_execution', 'node_name', 'status',
        'started_at', 'duration', 'output_preview'
    ]
    list_filter = [
        'status', 'started_at', 'workflow_execution__workflow'
    ]
    search_fields = [
        'workflow_execution__workflow__name',
        'node__display_name', 'node__module__name'
    ]
    ordering = ['-started_at']
    readonly_fields = [
        'workflow_execution', 'node', 'started_at', 'completed_at', 'duration'
    ]
    
    def node_name(self, obj):
        return obj.node.get_display_name()
    node_name.short_description = 'Node'
    
    def output_preview(self, obj):
        if obj.output_data:
            preview = str(obj.output_data)[:50]
            if len(str(obj.output_data)) > 50:
                preview += "..."
            return preview
        return "-"
    output_preview.short_description = 'Output Preview'

# Custom Admin Site Configuration
admin.site.site_header = "OdinSight Workflow Administration"
admin.site.site_title = "OdinSight Admin"
admin.site.index_title = "Welcome to OdinSight Workflow Administration"

# Admin Actions
def make_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
make_active.short_description = "Mark selected items as active"

def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
make_inactive.short_description = "Mark selected items as inactive"

def duplicate_workflow(modeladmin, request, queryset):
    for workflow in queryset:
        # Create duplicate workflow
        new_workflow = Workflow.objects.create(
            name=f"{workflow.name} (Copy)",
            description=workflow.description,
            workflow_type=workflow.workflow_type,
            owner=request.user,
            variables=workflow.variables,
            tags=workflow.tags,
            execution_timeout=workflow.execution_timeout,
            max_retries=workflow.max_retries,
            retry_delay=workflow.retry_delay
        )
        
        # Copy nodes
        for node in workflow.nodes.all():
            WorkflowNode.objects.create(
                workflow=new_workflow,
                module=node.module,
                node_id=node.node_id,
                position_x=node.position_x,
                position_y=node.position_y,
                display_name=node.display_name,
                custom_yaml=node.custom_yaml,
                custom_config=node.custom_config,
                custom_tags=node.custom_tags,
                node_variables=node.node_variables,
                execution_order=node.execution_order,
                is_enabled=node.is_enabled,
                continue_on_error=node.continue_on_error,
                timeout_override=node.timeout_override,
                condition_expression=node.condition_expression
            )
        
        # Copy edges
        for edge in workflow.edges.all():
            WorkflowEdge.objects.create(
                workflow=new_workflow,
                edge_id=edge.edge_id,
                source_node_id=edge.source_node_id,
                target_node_id=edge.target_node_id,
                source_handle=edge.source_handle,
                target_handle=edge.target_handle,
                edge_type=edge.edge_type,
                label=edge.label,
                condition=edge.condition,
                is_animated=edge.is_animated,
                style_config=edge.style_config,
                data_mapping=edge.data_mapping
            )

duplicate_workflow.short_description = "Duplicate selected workflows"

# Add actions to admin classes
ModuleAdmin.actions = [make_active, make_inactive]
ModuleCategoryAdmin.actions = [make_active, make_inactive]
WorkflowAdmin.actions = [duplicate_workflow]