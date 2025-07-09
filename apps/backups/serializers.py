# =============================================================================
# apps/backups/serializers.py - Backups app serializers
# =============================================================================

from rest_framework import serializers
from .models import BackupJob, BackupFile

class BackupJobSerializer(serializers.ModelSerializer):
    device_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BackupJob
        fields = '__all__'
    
    def get_device_count(self, obj):
        return obj.devices.count()

class BackupFileSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = BackupFile
        fields = '__all__'