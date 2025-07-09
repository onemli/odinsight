# =============================================================================
# apps/core/views.py - Core app views
# =============================================================================

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse

class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'ben_odinsight'})
