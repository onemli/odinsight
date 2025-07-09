# =============================================================================
# apps/network/models.py - Network app models
# =============================================================================

from django.db import models
from apps.core.models import BaseModel
from apps.devices.models import Device

class NetworkTopology(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    topology_data = models.JSONField(default=dict)
    devices = models.ManyToManyField(Device, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'network_topologies'

class RoutingTable(BaseModel):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='routing_tables')
    destination = models.CharField(max_length=100)
    next_hop = models.CharField(max_length=100)
    interface = models.CharField(max_length=100)
    metric = models.PositiveIntegerField(default=0)
    route_data = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.device.name} - {self.destination}"
    
    class Meta:
        db_table = 'routing_tables'