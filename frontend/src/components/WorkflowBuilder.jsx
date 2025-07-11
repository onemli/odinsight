import React, { useState } from 'react';
import { ReactFlow, Controls, Background, ReactFlowProvider } from 'reactflow';
import 'reactflow/dist/style.css';

function WorkflowBuilderContent() {
    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);

    return (
        <div style={{ height: '100vh', backgroundColor: '#f5f5f5' }}>
            <div style={{ 
                position: 'absolute', 
                top: '10px', 
                left: '10px', 
                zIndex: 10,
                background: 'white',
                padding: '10px',
                borderRadius: '5px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
                <h3>OdinSight Workflow Builder</h3>
                <p>Nodes: {nodes.length} | Edges: {edges.length}</p>
            </div>
            
            <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
            >
                <Controls />
                <Background variant="dots" />
            </ReactFlow>
        </div>
    );
}

export default function WorkflowBuilder() {
    return (
        <ReactFlowProvider>
            <WorkflowBuilderContent />
        </ReactFlowProvider>
    );
}
