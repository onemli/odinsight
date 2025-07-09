# =============================================================================
# apps/integrations/serializers.py - Integrations app serializers
# =============================================================================

from rest_framework import serializers
from .models import Integration

class IntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integration
        fields = '__all__'