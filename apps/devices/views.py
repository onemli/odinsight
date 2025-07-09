# =============================================================================
# apps/devices/views.py - Devices app views
# =============================================================================

from django.shortcuts import render
from django.views.generic import ListView, DetailView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Device, DeviceGroup, DeviceType
from .serializers import DeviceSerializer, DeviceGroupSerializer, DeviceTypeSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

class DeviceGroupViewSet(viewsets.ModelViewSet):
    queryset = DeviceGroup.objects.all()
    serializer_class = DeviceGroupSerializer

class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer

class DeviceListView(ListView):
    model = Device
    template_name = 'devices/device_list.html'
    context_object_name = 'devices'

class DeviceDetailView(DetailView):
    model = Device
    template_name = 'devices/device_detail.html'
    context_object_name = 'device'

class DeviceGroupListView(ListView):
    model = DeviceGroup
    template_name = 'devices/device_group_list.html'
    context_object_name = 'device_groups'
