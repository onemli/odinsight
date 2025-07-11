import React from 'react';
import { createRoot } from 'react-dom/client';
import WorkflowBuilder from './components/WorkflowBuilder';

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('workflow-builder-root');
    if (container) {
        const root = createRoot(container);
        root.render(React.createElement(WorkflowBuilder));
    }
});
