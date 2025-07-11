# apps/workflows/models.py
from django.db import models
from django.contrib.auth.models import User
import json

class ModuleCategory(models.Model):
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='network')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Module Category"
        verbose_name_plural = "Module Categories"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.display_name or self.name
    
    @property
    def full_path(self):
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

class Module(models.Model):
    MODULE_TYPES = [
        ('ansible', 'Ansible Module'),
        ('parser', 'CLI Parser'),
        ('custom', 'Custom Module'),
        ('api', 'API Call'),
        ('script', 'Python Script'),
    ]
    
    PROVIDERS = [
        ('cisco.aci', 'Cisco ACI'),
        ('genie', 'Genie Parser'),
        ('ntc_templates', 'NTC Templates'),
        ('ttp', 'TTP Parser'),
        ('custom', 'Custom Provider'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=200, unique=True)
    alias = models.CharField(max_length=200)
    module_type = models.CharField(max_length=20, choices=MODULE_TYPES)
    category = models.ForeignKey(ModuleCategory, on_delete=models.CASCADE, related_name='modules')
    subcategory = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    provider = models.CharField(max_length=100, choices=PROVIDERS)
    
    # Connection Points
    inputs = models.JSONField(
        default=list,
        help_text="List of input parameters this module accepts"
    )
    outputs = models.JSONField(
        default=list,
        help_text="List of outputs this module provides"
    )
    
    # Module Configuration
    default_yaml = models.TextField(help_text="Default YAML configuration")
    example_usage = models.TextField(blank=True, help_text="Example usage documentation")
    tags = models.JSONField(default=list, help_text="Searchable tags")
    
    # Parser Specific Fields
    parser_schema = models.JSONField(
        null=True, blank=True,
        help_text="JSON schema for parser output validation"
    )
    parser_rules = models.JSONField(
        default=list,
        help_text="Parser validation and processing rules"
    )
    
    # Metadata
    version = models.CharField(max_length=20, default='1.0.0')
    documentation_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_deprecated = models.BooleanField(default=False)
    deprecated_message = models.TextField(blank=True)
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['module_type', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return self.alias or self.name
    
    @property
    def input_count(self):
        return len(self.inputs) if self.inputs else 0
    
    @property
    def output_count(self):
        return len(self.outputs) if self.outputs else 0

class Workflow(models.Model):
    WORKFLOW_TYPES = [
        ('automation', 'Network Automation'),
        ('monitoring', 'Monitoring'),
        ('compliance', 'Compliance Check'),
        ('template', 'Template'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('deprecated', 'Deprecated'),
        ('archived', 'Archived'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    workflow_type = models.CharField(max_length=20, choices=WORKFLOW_TYPES, default='automation')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Ownership & Permissions
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflows')
    shared_users = models.ManyToManyField(User, blank=True, related_name='shared_workflows')
    is_public = models.BooleanField(default=False)
    
    # Workflow Configuration
    variables = models.JSONField(
        default=dict,
        help_text="Global workflow variables"
    )
    tags = models.JSONField(default=list)
    
    # Execution Settings
    execution_timeout = models.PositiveIntegerField(default=3600, help_text="Timeout in seconds")
    max_retries = models.PositiveIntegerField(default=3)
    retry_delay = models.PositiveIntegerField(default=60, help_text="Retry delay in seconds")
    
    # Metadata
    version = models.CharField(max_length=20, default='1.0.0')
    is_template = models.BooleanField(default=False)
    template_category = models.CharField(max_length=100, blank=True)
    
    # Statistics
    execution_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    last_executed = models.DateTimeField(null=True, blank=True)
    average_execution_time = models.DurationField(null=True, blank=True)
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['workflow_type', 'is_public']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def node_count(self):
        return self.nodes.count()
    
    @property
    def edge_count(self):
        return self.edges.count()
    
    @property
    def success_rate(self):
        if self.execution_count == 0:
            return 0
        return (self.success_count / self.execution_count) * 100

class WorkflowNode(models.Model):
    workflow = models.ForeignKey(Workflow, related_name='nodes', on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    
    # ReactFlow Properties
    node_id = models.CharField(max_length=100)  # React Flow node ID
    position_x = models.FloatField()
    position_y = models.FloatField()
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    
    # Node Configuration
    display_name = models.CharField(max_length=200, blank=True)
    custom_yaml = models.TextField(blank=True, help_text="Override module's default YAML")
    custom_config = models.JSONField(default=dict, help_text="Node-specific configuration")
    custom_tags = models.JSONField(default=list, help_text="Node-specific tags")
    node_variables = models.JSONField(default=dict, help_text="Node-level variables")
    
    # Execution Configuration
    execution_order = models.PositiveIntegerField(null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    continue_on_error = models.BooleanField(default=False)
    timeout_override = models.PositiveIntegerField(null=True, blank=True)
    
    # Conditional Execution
    condition_expression = models.TextField(
        blank=True,
        help_text="Python expression for conditional execution"
    )
    depends_on = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['workflow', 'node_id']
        ordering = ['execution_order', 'created_at']
    
    def __str__(self):
        return f"{self.workflow.name} - {self.display_name or self.module.name}"
    
    def get_yaml(self):
        """Get effective YAML (custom or module default)"""
        return self.custom_yaml.strip() if self.custom_yaml.strip() else self.module.default_yaml
    
    def get_tags(self):
        """Get effective tags (custom or module default)"""
        return self.custom_tags if self.custom_tags else self.module.tags
    
    def get_display_name(self):
        """Get effective display name"""
        return self.display_name or self.module.alias or self.module.name

class WorkflowEdge(models.Model):
    EDGE_TYPES = [
        ('success', 'Success Path'),
        ('error', 'Error Path'),
        ('conditional', 'Conditional'),
        ('data', 'Data Flow'),
    ]
    
    workflow = models.ForeignKey(Workflow, related_name='edges', on_delete=models.CASCADE)
    
    # ReactFlow Properties
    edge_id = models.CharField(max_length=100)
    source_node_id = models.CharField(max_length=100)
    target_node_id = models.CharField(max_length=100)
    source_handle = models.CharField(max_length=50, blank=True)
    target_handle = models.CharField(max_length=50, blank=True)
    
    # Edge Configuration
    edge_type = models.CharField(max_length=20, choices=EDGE_TYPES, default='success')
    label = models.CharField(max_length=100, blank=True)
    condition = models.TextField(blank=True, help_text="Condition for edge traversal")
    
    # Visual Configuration
    is_animated = models.BooleanField(default=True)
    style_config = models.JSONField(default=dict, help_text="Edge styling configuration")
    
    # Data Mapping
    data_mapping = models.JSONField(
        default=dict,
        help_text="Maps output from source to input of target"
    )
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['workflow', 'edge_id']
    
    def __str__(self):
        return f"{self.workflow.name} - {self.source_node_id} → {self.target_node_id}"

class WorkflowExecution(models.Model):
    EXECUTION_STATUSES = [
        ('pending', 'Pending'),
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('timeout', 'Timeout'),
    ]
    
    workflow = models.ForeignKey(Workflow, related_name='executions', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=EXECUTION_STATUSES, default='pending')
    
    # Execution Metadata
    execution_id = models.CharField(max_length=100, unique=True)  # Celery task ID
    started_by = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    # Execution Configuration
    execution_variables = models.JSONField(default=dict, help_text="Runtime variables")
    execution_context = models.JSONField(default=dict, help_text="Execution environment context")
    
    # Results & Logs
    result_data = models.JSONField(default=dict, help_text="Execution results")
    error_message = models.TextField(blank=True)
    log_output = models.TextField(blank=True)
    debug_info = models.JSONField(default=dict)
    
    # Generated Artifacts
    generated_playbook = models.TextField(blank=True)
    generated_inventory = models.TextField(blank=True)
    output_files = models.JSONField(default=list, help_text="List of generated output files")
    
    # Statistics
    nodes_executed = models.PositiveIntegerField(default=0)
    nodes_successful = models.PositiveIntegerField(default=0)
    nodes_failed = models.PositiveIntegerField(default=0)
    nodes_skipped = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['workflow', 'status']),
            models.Index(fields=['started_by', 'started_at']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def success_rate(self):
        if self.nodes_executed == 0:
            return 0
        return (self.nodes_successful / self.nodes_executed) * 100

class NodeExecution(models.Model):
    workflow_execution = models.ForeignKey(WorkflowExecution, related_name='node_executions', on_delete=models.CASCADE)
    node = models.ForeignKey(WorkflowNode, on_delete=models.CASCADE)
    
    # Execution Info
    status = models.CharField(max_length=20, choices=WorkflowExecution.EXECUTION_STATUSES)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    # Results
    output_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    log_output = models.TextField(blank=True)
    
    # Execution Context
    input_variables = models.JSONField(default=dict)
    environment_variables = models.JSONField(default=dict)
    
    class Meta:
        unique_together = ['workflow_execution', 'node']
        ordering = ['started_at']
    
    def __str__(self):
        return f"{self.workflow_execution} - {self.node.get_display_name()}"