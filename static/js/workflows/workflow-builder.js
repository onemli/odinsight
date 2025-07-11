// static/workflow/js/workflow-builder.js
class WorkflowBuilder {
    constructor() {
        this.reactFlowInstance = null;
        this.currentWorkflow = null;
        this.modules = [];
        this.init();
    }
    
    async init() {
        await this.loadModules();
        this.setupReactFlow();
        this.setupEventListeners();
    }
    
    async loadModules() {
        try {
            const response = await fetch('/api/workflow/modules/tree_structure/');
            this.modules = await response.json();
            this.renderModuleTree();
        } catch (error) {
            console.error('Error loading modules:', error);
        }
    }
    
    async saveWorkflow() {
        if (!this.currentWorkflow) return;
        
        const nodes = this.reactFlowInstance.getNodes();
        const edges = this.reactFlowInstance.getEdges();
        
        try {
            const response = await fetch(`/api/workflow/workflows/${this.currentWorkflow.id}/save_design/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ nodes, edges })
            });
            
            if (response.ok) {
                this.showNotification('Workflow saved successfully', 'success');
            }
        } catch (error) {
            this.showNotification('Error saving workflow', 'error');
        }
    }
    
    async loadWorkflow(workflowId) {
        try {
            const response = await fetch(`/api/workflow/workflows/${workflowId}/`);
            const workflow = await response.json();
            
            this.currentWorkflow = workflow;
            this.loadWorkflowToCanvas(workflow);
        } catch (error) {
            console.error('Error loading workflow:', error);
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', () => {
    new WorkflowBuilder();
});