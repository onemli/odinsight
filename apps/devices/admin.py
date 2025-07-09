# =============================================================================
# apps/devices/admin.py - Devices app admin
# =============================================================================

from django.contrib import admin
from .models import Device, DeviceGroup, DeviceType

@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'model', 'device_family', 'created_at']
    list_filter = ['vendor', 'device_family']
    search_fields = ['name', 'vendor', 'model']
    ordering = ['vendor', 'model']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'device_type', 'status', 'location', 'created_at']
    list_filter = ['status', 'device_type__vendor', 'location']
    search_fields = ['name', 'ip_address', 'description']
    list_editable = ['status']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'ip_address', 'device_type', 'status')
        }),
        ('Location & Description', {
            'fields': ('location', 'description')
        }),
        ('Network Settings', {
            'fields': ('management_port',)
        }),
    )

@admin.register(DeviceGroup)
class DeviceGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_device_count', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['devices']
    ordering = ['name']
    
    def get_device_count(self, obj):
        return obj.devices.count()
    get_device_count.short_description = 'Device Count'