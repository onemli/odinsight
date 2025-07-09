# =============================================================================
# apps/integrations/models.py - Integrations app models
# =============================================================================

from django.db import models
from apps.core.models import BaseModel

class Integration(BaseModel):
    INTEGRATION_TYPES = [
        ('netbox', 'NetBox'),
        ('ansible', 'Ansible Tower'),
        ('monitoring', 'Monitoring System'),
    ]
    
    name = models.CharField(max_length=200)
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPES)
    config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.integration_type})"
    
    class Meta:
        db_table = 'integrations'