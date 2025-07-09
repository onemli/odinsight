# =============================================================================
# apps/workflows/views.py - Workflows app views
# =============================================================================

from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Workflow, WorkflowExecution
from .serializers import WorkflowSerializer, WorkflowExecutionSerializer

class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer

class WorkflowExecutionViewSet(viewsets.ModelViewSet):
    queryset = WorkflowExecution.objects.all()
    serializer_class = WorkflowExecutionSerializer

class WorkflowListView(ListView):
    model = Workflow
    template_name = 'workflows/workflow_list.html'
    context_object_name = 'workflows'

class WorkflowDetailView(DetailView):
    model = Workflow
    template_name = 'workflows/workflow_detail.html'
    context_object_name = 'workflow'

class WorkflowBuilderView(DetailView):
    model = Workflow
    template_name = 'workflows/workflow_builder.html'
    context_object_name = 'workflow'

class WorkflowExecuteView(DetailView):
    model = Workflow
    template_name = 'workflows/workflow_execute.html'
    context_object_name = 'workflow'
