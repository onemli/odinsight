# =============================================================================
# apps/workflows/serializers.py - Workflows app serializers
# =============================================================================

from rest_framework import serializers
from .models import Workflow, WorkflowExecution

class WorkflowSerializer(serializers.ModelSerializer):
    execution_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workflow
        fields = '__all__'
    
    def get_execution_count(self, obj):
        return obj.executions.count()

class WorkflowExecutionSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    
    class Meta:
        model = WorkflowExecution
        fields = '__all__'