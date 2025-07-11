from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg
from django.utils import timezone
from .models import (
    ModuleCategory, Module, Workflow, WorkflowNode, 
    WorkflowEdge, WorkflowExecution
)
from .serializers import (
    ModuleCategorySerializer, ModuleSerializer, WorkflowSerializer,
    WorkflowNodeSerializer, WorkflowEdgeSerializer, WorkflowExecutionSerializer
)
from .tasks import execute_workflow_task
import uuid
import yaml

# Django Template Views
@login_required
def workflow_builder(request):
    """Ana workflow builder sayfası"""
    context = {
        'page_title': 'Network Automation Workflow Builder',
        'user_workflows': Workflow.objects.filter(owner=request.user)[:10]
    }
    return render(request, 'workflows/builder.html', context)

@login_required
def workflow_list(request):
    """Kullanıcının workflow'larını listele"""
    workflows = Workflow.objects.filter(
        Q(owner=request.user) | Q(shared_users=request.user) | Q(is_public=True)
    ).distinct().order_by('-updated_at')
    
    context = {
        'workflows': workflows,
        'page_title': 'My Workflows'
    }
    return render(request, 'workflows/workflow-list.html', context)

# API ViewSets
class ModuleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ModuleCategory.objects.filter(is_active=True)
    serializer_class = ModuleCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def tree_structure(self, request):
        """Modül kategorilerini tree yapısında döndür"""
        categories = self.get_queryset().prefetch_related('modules')
        tree_data = self.build_category_tree(categories)
        return Response(tree_data)
    
    def build_category_tree(self, categories):
        """Kategorileri hierarchical tree'ye dönüştür"""
        category_dict = {cat.id: cat for cat in categories}
        tree = []
        
        for category in categories:
            if category.parent_id is None:  # Root categories
                tree_node = self.build_tree_node(category, category_dict)
                tree.append(tree_node)
        
        return tree
    
    def build_tree_node(self, category, category_dict):
        """Tekil category node'u oluştur"""
        modules = list(category.modules.filter(is_active=True))
        
        node = {
            'id': f"category-{category.id}",
            'name': category.name,
            'alias': category.display_name,
            'description': f"{len(modules)} modules available",
            'icon': category.icon,
            'type': 'category',
            'isExpanded': False,
            'children': []
        }
        
        # Alt kategorileri ekle
        child_categories = [cat for cat in category_dict.values() 
                          if cat.parent_id == category.id]
        for child_cat in child_categories:
            child_node = self.build_tree_node(child_cat, category_dict)
            node['children'].append(child_node)
        
        # Modülleri ekle
        for module in modules:
            module_node = {
                'id': module.id,
                'name': module.name,
                'alias': module.alias,
                'description': module.description,
                'provider': module.provider,
                'inputs': module.inputs,
                'outputs': module.outputs,
                'tags': module.tags,
                'defaultYaml': module.default_yaml,
                'example': module.example_usage,
                'parserSchema': module.parser_schema,
                'type': 'module'
            }
            node['children'].append(module_node)
        
        return node

class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Module.objects.filter(is_active=True)
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(alias__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__contains=[search])
            )
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by module type
        module_type = self.request.query_params.get('type', None)
        if module_type:
            queryset = queryset.filter(module_type=module_type)
        
        return queryset.order_by('category__sort_order', 'name')

class WorkflowViewSet(viewsets.ModelViewSet):
    serializer_class = WorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Kullanıcının erişebileceği workflow'lar"""
        return Workflow.objects.filter(
            Q(owner=self.request.user) | 
            Q(shared_users=self.request.user) | 
            Q(is_public=True)
        ).distinct().order_by('-updated_at')
    
    def perform_create(self, serializer):
        """Yeni workflow oluştururken owner'ı set et"""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def save_design(self, request, pk=None):
        """React Flow'dan gelen design'ı kaydet"""
        workflow = self.get_object()
        
        # Permission check
        if workflow.owner != request.user:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        nodes_data = request.data.get('nodes', [])
        edges_data = request.data.get('edges', [])
        
        try:
            # Transaction ile atomic operation
            with transaction.atomic():
                # Mevcut nodes ve edges'leri sil
                WorkflowNode.objects.filter(workflow=workflow).delete()
                WorkflowEdge.objects.filter(workflow=workflow).delete()
                
                # Yeni nodes'ları kaydet
                for node_data in nodes_data:
                    module_id = node_data['data'].get('id')
                    if not module_id:
                        continue
                    
                    try:
                        module = Module.objects.get(id=module_id)
                    except Module.DoesNotExist:
                        continue
                    
                    WorkflowNode.objects.create(
                        workflow=workflow,
                        module=module,
                        node_id=node_data['id'],
                        position_x=node_data['position']['x'],
                        position_y=node_data['position']['y'],
                        width=node_data.get('width'),
                        height=node_data.get('height'),
                        display_name=node_data['data'].get('display_name', ''),
                        custom_yaml=node_data['data'].get('yaml', ''),
                        custom_config=node_data['data'].get('config', {}),
                        custom_tags=node_data['data'].get('tags', []),
                        node_variables=node_data['data'].get('variables', {}),
                        is_enabled=node_data['data'].get('enabled', True),
                        continue_on_error=node_data['data'].get('continueOnError', False)
                    )
                
                # Yeni edges'leri kaydet
                for edge_data in edges_data:
                    WorkflowEdge.objects.create(
                        workflow=workflow,
                        edge_id=edge_data['id'],
                        source_node_id=edge_data['source'],
                        target_node_id=edge_data['target'],
                        source_handle=edge_data.get('sourceHandle', ''),
                        target_handle=edge_data.get('targetHandle', ''),
                        edge_type=edge_data.get('type', 'success'),
                        label=edge_data.get('label', ''),
                        is_animated=edge_data.get('animated', True),
                        style_config=edge_data.get('style', {}),
                        data_mapping=edge_data.get('dataMapping', {})
                    )
                
                # Workflow'u güncelle
                workflow.updated_at = timezone.now()
                workflow.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Workflow design saved successfully',
                    'nodes_count': len(nodes_data),
                    'edges_count': len(edges_data)
                })
                
        except Exception as e:
            return Response(
                {'error': f'Error saving workflow: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def load_design(self, request, pk=None):
        """Workflow design'ını React Flow formatında döndür"""
        workflow = self.get_object()
        
        nodes = []
        edges = []
        
        # Nodes'ları React Flow formatına çevir
        for node in workflow.nodes.all():
            react_flow_node = {
                'id': node.node_id,
                'type': 'moduleNode',
                'position': {
                    'x': node.position_x,
                    'y': node.position_y
                },
                'data': {
                    'id': node.module.id,
                    'name': node.module.name,
                    'alias': node.module.alias,
                    'description': node.module.description,
                    'provider': node.module.provider,
                    'inputs': node.module.inputs,
                    'outputs': node.module.outputs,
                    'tags': node.get_tags(),
                    'yaml': node.get_yaml(),
                    'example': node.module.example_usage,
                    'parserSchema': node.module.parser_schema,
                    'display_name': node.get_display_name(),
                    'config': node.custom_config,
                    'variables': node.node_variables,
                    'enabled': node.is_enabled,
                    'continueOnError': node.continue_on_error
                }
            }
            if node.width:
                react_flow_node['width'] = node.width
            if node.height:
                react_flow_node['height'] = node.height
            
            nodes.append(react_flow_node)
        
        # Edges'leri React Flow formatına çevir
        for edge in workflow.edges.all():
            react_flow_edge = {
                'id': edge.edge_id,
                'source': edge.source_node_id,
                'target': edge.target_node_id,
                'type': 'custom',
                'animated': edge.is_animated,
                'style': edge.style_config,
                'data': {
                    'edgeType': edge.edge_type,
                    'label': edge.label,
                    'condition': edge.condition,
                    'dataMapping': edge.data_mapping
                }
            }
            if edge.source_handle:
                react_flow_edge['sourceHandle'] = edge.source_handle
            if edge.target_handle:
                react_flow_edge['targetHandle'] = edge.target_handle
            
            edges.append(react_flow_edge)
        
        return Response({
            'workflow': WorkflowSerializer(workflow).data,
            'design': {
                'nodes': nodes,
                'edges': edges
            }
        })
    
    @action(detail=True, methods=['get'])
    def export_playbook(self, request, pk=None):
        """Workflow'u Ansible playbook olarak export et"""
        workflow = self.get_object()
        
        try:
            playbook_content = self.generate_ansible_playbook(workflow)
            
            response = HttpResponse(playbook_content, content_type='text/yaml')
            response['Content-Disposition'] = f'attachment; filename="{workflow.name.replace(" ", "_")}-playbook.yml"'
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error generating playbook: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Workflow'u execute et"""
        workflow = self.get_object()
        
        # Permission check
        if workflow.owner != request.user and request.user not in workflow.shared_users.all():
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Execution variables
        execution_variables = request.data.get('variables', {})
        execution_context = request.data.get('context', {})
        
        # Unique execution ID
        execution_id = str(uuid.uuid4())
        
        # Create execution record
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            execution_id=execution_id,
            started_by=request.user,
            status='queued',
            execution_variables=execution_variables,
            execution_context=execution_context
        )
        
        # Start Celery task
        try:
            execute_workflow_task.delay(execution.id)
            
            return Response({
                'status': 'queued',
                'execution_id': execution_id,
                'message': 'Workflow execution started',
                'execution_url': f'/api/workflows/executions/{execution.id}/'
            })
            
        except Exception as e:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.save()
            
            return Response(
                {'error': f'Error starting execution: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def generate_ansible_playbook(self, workflow):
        """Workflow'dan Ansible playbook oluştur"""
        nodes = workflow.nodes.filter(is_enabled=True).order_by('execution_order', 'created_at')
        
        playbook = {
            'name': f'{workflow.name} - Generated Playbook',
            'hosts': 'all',
            'gather_facts': False,
            'vars': workflow.variables,
            'tasks': []
        }
        
        for node in nodes:
            try:
                yaml_content = node.get_yaml()
                # YAML task'ını parse et
                task_data = yaml.safe_load(yaml_content)
                
                if isinstance(task_data, list):
                    playbook['tasks'].extend(task_data)
                elif isinstance(task_data, dict):
                    playbook['tasks'].append(task_data)
                    
            except yaml.YAMLError as e:
                # Invalid YAML - skip or add error task
                error_task = {
                    'name': f'ERROR: Invalid YAML in node {node.get_display_name()}',
                    'debug': {
                        'msg': f'YAML Parse Error: {str(e)}'
                    }
                }
                playbook['tasks'].append(error_task)
        
        return yaml.dump([playbook], default_flow_style=False, sort_keys=False)

class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WorkflowExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkflowExecution.objects.filter(
            workflow__in=Workflow.objects.filter(
                Q(owner=self.request.user) | 
                Q(shared_users=self.request.user)
            )
        ).order_by('-started_at')
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Execution'ı cancel et"""
        execution = self.get_object()
        
        if execution.status in ['pending', 'queued', 'running']:
            execution.status = 'cancelled'
            execution.completed_at = timezone.now()
            execution.save()
            
            # Celery task'ını cancel et
            from celery import current_app
            current_app.control.revoke(execution.execution_id, terminate=True)
            
            return Response({'status': 'cancelled'})
        else:
            return Response(
                {'error': 'Cannot cancel execution in current status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )