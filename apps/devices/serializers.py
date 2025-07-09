# =============================================================================
# apps/devices/serializers.py - Devices app serializers
# =============================================================================

from rest_framework import serializers
from .models import Device, DeviceGroup, DeviceType

class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = '__all__'

class DeviceSerializer(serializers.ModelSerializer):
    device_type_name = serializers.CharField(source='device_type.name', read_only=True)
    
    class Meta:
        model = Device
        fields = '__all__'

class DeviceGroupSerializer(serializers.ModelSerializer):
    device_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DeviceGroup
        fields = '__all__'
    
    def get_device_count(self, obj):
        return obj.devices.count()