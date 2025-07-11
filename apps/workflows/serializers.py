from rest_framework import serializers
from .models import (
    ModuleCategory, Module, Workflow, WorkflowNode, 
    WorkflowEdge, WorkflowExecution, NodeExecution
)

class ModuleCategorySerializer(serializers.ModelSerializer):
    module_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ModuleCategory
        fields = ['id', 'name', 'display_name', 'description', 'icon', 
                 'parent', 'sort_order', 'is_active', 'module_count']
    
    def get_module_count(self, obj):
        return obj.modules.filter(is_active=True).count()

class ModuleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    input_count = serializers.ReadOnlyField()
    output_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Module
        fields = [
            'id', 'name', 'alias', 'module_type', 'category', 'category_name',
            'subcategory', 'description', 'provider', 'inputs', 'outputs',
            'default_yaml', 'example_usage', 'tags', 'parser_schema',
            'parser_rules', 'version', 'is_active', 'input_count', 'output_count'
        ]

class WorkflowNodeSerializer(serializers.ModelSerializer):
    module_data = ModuleSerializer(source='module', read_only=True)
    effective_yaml = serializers.SerializerMethodField()
    effective_tags = serializers.SerializerMethodField()
    effective_display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowNode
        fields = [
            'id', 'node_id', 'position_x', 'position_y', 'width', 'height',
            'display_name', 'custom_yaml', 'custom_config', 'custom_tags',
            'node_variables', 'execution_order', 'is_enabled', 'continue_on_error',
            'condition_expression', 'module', 'module_data', 'effective_yaml',
            'effective_tags', 'effective_display_name'
        ]
    
    def get_effective_yaml(self, obj):
        return obj.get_yaml()
    
    def get_effective_tags(self, obj):
        return obj.get_tags()
    
    def get_effective_display_name(self, obj):
        return obj.get_display_name()

class WorkflowEdgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowEdge
        fields = [
            'id', 'edge_id', 'source_node_id', 'target_node_id',
            'source_handle', 'target_handle', 'edge_type', 'label',
            'condition', 'is_animated', 'style_config', 'data_mapping'
        ]

class WorkflowSerializer(serializers.ModelSerializer):
    nodes = WorkflowNodeSerializer(many=True, read_only=True)
    edges = WorkflowEdgeSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    node_count = serializers.ReadOnlyField()
    edge_count = serializers.ReadOnlyField()
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'description', 'workflow_type', 'status',
            'owner', 'owner_username', 'is_public', 'variables', 'tags',
            'execution_timeout', 'max_retries', 'version', 'is_template',
            'execution_count', 'success_count', 'last_executed',
            'created_at', 'updated_at', 'nodes', 'edges',
            'node_count', 'edge_count', 'success_rate'
        ]

class WorkflowExecutionSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    started_by_username = serializers.CharField(source='started_by.username', read_only=True)
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'execution_id', 'workflow', 'workflow_name', 'status',
            'started_by', 'started_by_username', 'started_at', 'completed_at',
            'duration', 'execution_variables', 'result_data', 'error_message',
            'nodes_executed', 'nodes_successful', 'nodes_failed', 'nodes_skipped',
            'success_rate'
        ]