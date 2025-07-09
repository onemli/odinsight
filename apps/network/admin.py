# =============================================================================
# apps/network/admin.py - Network app admin
# =============================================================================

from django.contrib import admin
from .models import NetworkTopology, RoutingTable

@admin.register(NetworkTopology)
class NetworkTopologyAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_device_count', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['devices']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Devices', {
            'fields': ('devices',)
        }),
        ('Topology Data', {
            'fields': ('topology_data',),
            'classes': ('collapse',)
        }),
    )
    
    def get_device_count(self, obj):
        return obj.devices.count()
    get_device_count.short_description = 'Device Count'

@admin.register(RoutingTable)
class RoutingTableAdmin(admin.ModelAdmin):
    list_display = ['device', 'destination', 'next_hop', 'interface', 'metric', 'created_at']
    list_filter = ['device', 'interface', 'created_at']
    search_fields = ['device__name', 'destination', 'next_hop', 'interface']
    ordering = ['device', 'destination']
    
    fieldsets = (
        ('Route Information', {
            'fields': ('device', 'destination', 'next_hop', 'interface', 'metric')
        }),
        ('Additional Data', {
            'fields': ('route_data',),
            'classes': ('collapse',)
        }),
    )