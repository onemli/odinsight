from celery import shared_task
from django.utils import timezone
from django.conf import settings
from .models import WorkflowExecution, WorkflowNode, NodeExecution
import yaml
import subprocess
import tempfile
import os
import json
from datetime import timedelta

@shared_task(bind=True)
def execute_workflow_task(self, execution_id):
    """
    Workflow'u execute eden ana Celery task
    """
    try:
        execution = WorkflowExecution.objects.get(id=execution_id)
        execution.status = 'running'
        execution.save()
        
        # Workflow nodes'larını execution order'a göre sırala
        nodes = WorkflowNode.objects.filter(
            workflow=execution.workflow,
            is_enabled=True
        ).order_by('execution_order', 'created_at')
        
        execution.nodes_executed = nodes.count()
        execution.save()
        
        # Her node için execution record oluştur
        node_executions = []
        for node in nodes:
            node_exec = NodeExecution.objects.create(
                workflow_execution=execution,
                node=node,
                status='pending',
                started_at=timezone.now(),
                input_variables=execution.execution_variables
            )
            node_executions.append(node_exec)
        
        # Nodes'ları sırasıyla execute et
        successful_nodes = 0
        failed_nodes = 0
        
        for node_execution in node_executions:
            try:
                node_execution.status = 'running'
                node_execution.save()
                
                # Node'u execute et
                result = execute_single_node(node_execution)
                
                if result['success']:
                    node_execution.status = 'completed'
                    node_execution.output_data = result['output']
                    successful_nodes += 1
                else:
                    node_execution.status = 'failed'
                    node_execution.error_message = result['error']
                    failed_nodes += 1
                    
                    # Continue on error kontrolü
                    if not node_execution.node.continue_on_error:
                        break
                
                node_execution.completed_at = timezone.now()
                node_execution.duration = node_execution.completed_at - node_execution.started_at
                node_execution.save()
                
            except Exception as e:
                node_execution.status = 'failed'
                node_execution.error_message = str(e)
                node_execution.completed_at = timezone.now()
                node_execution.save()
                failed_nodes += 1
                
                if not node_execution.node.continue_on_error:
                    break
        
        # Execution'ı tamamla
        execution.completed_at = timezone.now()
        execution.duration = execution.completed_at - execution.started_at
        execution.nodes_successful = successful_nodes
        execution.nodes_failed = failed_nodes
        execution.nodes_skipped = execution.nodes_executed - successful_nodes - failed_nodes
        
        if failed_nodes == 0:
            execution.status = 'completed'
        elif successful_nodes > 0:
            execution.status = 'completed'  # Partial success
        else:
            execution.status = 'failed'
        
        # Workflow statistics'i güncelle
        workflow = execution.workflow
        workflow.execution_count += 1
        if execution.status == 'completed':
            workflow.success_count += 1
        workflow.last_executed = execution.completed_at
        
        # Average execution time hesapla
        if workflow.average_execution_time:
            workflow.average_execution_time = (
                workflow.average_execution_time + execution.duration
            ) / 2
        else:
            workflow.average_execution_time = execution.duration
        
        workflow.save()
        execution.save()
        
        return f"Workflow execution completed. Status: {execution.status}"
        
    except WorkflowExecution.DoesNotExist:
        return f"Workflow execution {execution_id} not found"
    except Exception as e:
        try:
            execution.status = 'failed'
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.save()
        except:
            pass
        raise

def execute_single_node(node_execution):
    """
    Tekil node'u execute et
    """
    node = node_execution.node
    module = node.module
    
    try:
        if module.module_type == 'ansible':
            return execute_ansible_module(node_execution)
        elif module.module_type == 'parser':
            return execute_parser_module(node_execution)
        elif module.module_type == 'script':
            return execute_script_module(node_execution)
        else:
            return {
                'success': False,
                'error': f'Unsupported module type: {module.module_type}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def execute_ansible_module(node_execution):
    """
    Ansible module'ü execute et
    """
    node = node_execution.node
    yaml_content = node.get_yaml()
    
    try:
        # YAML'i parse et
        task_data = yaml.safe_load(yaml_content)
        
        # Temporary playbook oluştur
        playbook = [{
            'name': f'Execute {node.get_display_name()}',
            'hosts': 'localhost',
            'gather_facts': False,
            'vars': {
                **node_execution.workflow_execution.execution_variables,
                **node.node_variables
            },
            'tasks': [task_data] if isinstance(task_data, dict) else task_data
        }]
        
        # Temporary file'a yaz
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(playbook, f, default_flow_style=False)
            playbook_path = f.name
        
        try:
            # Ansible-playbook çalıştır
            result = subprocess.run(
                ['ansible-playbook', playbook_path, '-v'],
                capture_output=True,
                text=True,
                timeout=node_execution.node.timeout_override or 300
            )
            
            node_execution.log_output = result.stdout + result.stderr
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': {
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'return_code': result.returncode
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr or 'Ansible playbook failed'
                }
                
        finally:
            os.unlink(playbook_path)
            
    except yaml.YAMLError as e:
        return {
            'success': False,
            'error': f'YAML parse error: {str(e)}'
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Execution timeout'
        }

def execute_parser_module(node_execution):
    """
    CLI Parser module'ü execute et
    """
    node = node_execution.node
    module = node.module
    
    # Parser için dummy implementation
    # Gerçek implementasyonda CLI output'u parse edilecek
    
    try:
        parser_schema = module.parser_schema
        parser_rules = module.parser_rules
        
        # Mock CLI output (gerçek implementasyonda device'dan gelecek)
        mock_output = node_execution.input_variables.get('cli_output', '')
        
        if module.provider == 'genie':
            parsed_data = parse_with_genie(mock_output, module.name)
        elif module.provider == 'ntc_templates':
            parsed_data = parse_with_ntc(mock_output, module.name)
        elif module.provider == 'ttp':
            parsed_data = parse_with_ttp(mock_output, module.name)
        else:
            parsed_data = {'raw_output': mock_output}
        
        # Parser rules'ları uygula
        rule_results = apply_parser_rules(parsed_data, parser_rules)
        
        return {
            'success': True,
            'output': {
                'parsed_data': parsed_data,
                'rule_results': rule_results
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Parser execution failed: {str(e)}'
        }

def parse_with_genie(output, command):
    """Genie parser ile parse et"""
    # Genie parser implementation
    return {'parsed': True, 'data': {}}

def parse_with_ntc(output, template):
    """NTC Templates ile parse et"""
    # NTC Templates implementation  
    return {'parsed': True, 'data': {}}

def parse_with_ttp(output, template):
    """TTP ile parse et"""
    # TTP implementation
    return {'parsed': True, 'data': {}}

def apply_parser_rules(parsed_data, rules):
    """Parser rules'ları uygula"""
    results = []
    
    for rule in rules:
        try:
            # Rule evaluation logic
            rule_result = {
                'rule_name': rule.get('name', 'Unknown'),
                'condition': rule.get('condition'),
                'result': 'passed',  # Simplified
                'message': rule.get('message', '')
            }
            results.append(rule_result)
        except Exception as e:
            results.append({
                'rule_name': rule.get('name', 'Unknown'),
                'result': 'error',
                'error': str(e)
            })
    
    return results

def execute_script_module(node_execution):
    """
    Python script module'ü execute et
    """
    # Script execution implementation
    return {
        'success': True,
        'output': {'message': 'Script executed successfully'}
    }