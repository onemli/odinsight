# =============================================================================
# apps/network/views.py - Network app views
# =============================================================================

from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import viewsets
from .models import NetworkTopology, RoutingTable
from .serializers import NetworkTopologySerializer, RoutingTableSerializer

class NetworkTopologyViewSet(viewsets.ModelViewSet):
    queryset = NetworkTopology.objects.all()
    serializer_class = NetworkTopologySerializer

class RoutingTableViewSet(viewsets.ModelViewSet):
    queryset = RoutingTable.objects.all()
    serializer_class = RoutingTableSerializer

class NetworkOverviewView(TemplateView):
    template_name = 'network/overview.html'

class TopologyView(TemplateView):
    template_name = 'network/topology.html'

class RouteAnalysisView(TemplateView):
    template_name = 'network/route_analysis.html'

class PathAnalysisView(TemplateView):
    template_name = 'network/path_analysis.html'