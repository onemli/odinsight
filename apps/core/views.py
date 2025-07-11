# core/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def index(request):
    """Dashboard homepage"""
    context = {
        'page_title': 'Dashboard',
        'active_devices': 12,
        'total_workflows': 8,
        'successful_executions': 156,
        'pending_tasks': 3,
    }
    return render(request, 'core/dashboard.html', context)

def workflow_builder(request):
    """Network Automation Workflow Builder"""
    context = {
        'page_title': 'Workflow Builder',
    }
    return render(request, 'core/workflow_builder.html', context)

@login_required  
def device_management(request):
    """Device Management Page"""
    context = {
        'page_title': 'Device Management',
    }
    return render(request, 'core/device_management.html', context)

@login_required
def ansible_integration(request):
    """Ansible Tower Integration"""
    context = {
        'page_title': 'Ansible Tower',
    }
    return render(request, 'core/ansible_integration.html', context)