# =============================================================================
# apps/network/serializers.py - Network app serializers
# =============================================================================

from rest_framework import serializers
from .models import NetworkTopology, RoutingTable

class NetworkTopologySerializer(serializers.ModelSerializer):
    device_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NetworkTopology
        fields = '__all__'
    
    def get_device_count(self, obj):
        return obj.devices.count()

class RoutingTableSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = RoutingTable
        fields = '__all__'
