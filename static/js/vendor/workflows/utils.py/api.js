// API utilities for workflow operations
class WorkflowAPI {
    constructor() {
        this.baseURL = '/api/workflows';
        this.headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.CSRF_TOKEN
        };
    }

    async get(endpoint) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'GET',
            headers: this.headers
        });
        return this.handleResponse(response);
    }

    async post(endpoint, data) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    async put(endpoint, data) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'PUT',
            headers: this.headers,
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    }

    async delete(endpoint) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method: 'DELETE',
            headers: this.headers
        });
        return this.handleResponse(response);
    }

    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: 'Network error' }));
            throw new Error(error.error || 'Request failed');
        }
        return response.json();
    }

    // Specific API methods
    async getModuleTree() {
        return this.get('/categories/tree_structure/');
    }

    async getWorkflows() {
        return this.get('/workflows/');
    }

    async getWorkflow(id) {
        return this.get(`/workflows/${id}/`);
    }

    async saveWorkflow(id, data) {
        return this.post(`/workflows/${id}/save_design/`, data);
    }

    async loadWorkflowDesign(id) {
        return this.get(`/workflows/${id}/load_design/`);
    }

    async createWorkflow(data) {
        return this.post('/workflows/', data);
    }

    async executeWorkflow(id, variables = {}) {
        return this.post(`/workflows/${id}/execute/`, { variables });
    }

    async exportPlaybook(id) {
        const response = await fetch(`${this.baseURL}/workflows/${id}/export_playbook/`, {
            method: 'GET',
            headers: { 'X-CSRFToken': window.CSRF_TOKEN }
        });
        
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `workflow-${id}-playbook.yml`;
        a.click();
        window.URL.revokeObjectURL(url);
    }
}

// Global API instance
window.workflowAPI = new WorkflowAPI();