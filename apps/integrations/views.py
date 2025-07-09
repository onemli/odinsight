# =============================================================================
# apps/integrations/views.py - Integrations app views
# =============================================================================

from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from rest_framework import viewsets
from .models import Integration
from .serializers import IntegrationSerializer

class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer

class IntegrationListView(ListView):
    model = Integration
    template_name = 'integrations/integration_list.html'
    context_object_name = 'integrations'

class NetBoxIntegrationView(TemplateView):
    template_name = 'integrations/netbox.html'

class AnsibleIntegrationView(TemplateView):
    template_name = 'integrations/ansible.html'

class SyncView(TemplateView):
    template_name = 'integrations/sync.html'