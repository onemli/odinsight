# =============================================================================
# apps/workflows/models.py - Workflows app models
# =============================================================================

from django.db import models
from apps.core.models import BaseModel
from apps.devices.models import Device, DeviceGroup

class Workflow(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    workflow_data = models.JSONField(default=dict)  # JointJS+ data
    version = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'workflows'

class WorkflowExecution(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(default=dict)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.workflow.name} - {self.status}"
    
    class Meta:
        db_table = 'workflow_executions'