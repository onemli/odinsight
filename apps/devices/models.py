# =============================================================================
# apps/devices/models.py - Devices app models
# =============================================================================

from django.db import models
from apps.core.models import BaseModel, SoftDeleteMixin

class DeviceType(BaseModel):
    name = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    device_family = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.vendor} {self.model}"
    
    class Meta:
        db_table = 'device_types'
        unique_together = ['vendor', 'model']

class Device(BaseModel, SoftDeleteMixin):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
        ('error', 'Error'),
    ]
    
    name = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField()
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    management_port = models.PositiveIntegerField(default=22)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'devices'
        unique_together = ['name', 'ip_address']

class DeviceGroup(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    devices = models.ManyToManyField(Device, blank=True, related_name='groups')
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'device_groups'