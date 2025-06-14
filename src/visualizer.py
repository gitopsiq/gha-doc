#!/usr/bin/env python3
"""
Diagram Generator Module

Generates visual diagrams of GitHub Actions workflows.
"""

import os
import json
import tempfile
from typing import Dict, List, Any, Optional

class DiagramGenerator:
    """Generator for workflow diagrams."""

    def __init__(self, workflow_data: Dict[str, Any]):
        """Initialize with analyzed workflow data."""
        self.workflow_data = workflow_data

    def generate(self, output_path: str) -> str:
        """Generate diagram for the workflow and save to output_path."""
        try:
            # Create Mermaid diagram definition
            mermaid_diagram = self._create_mermaid_diagram()

            # For now, we'll just save the mermaid source
            # In a real implementation, this would use mermaid-cli or a similar tool to render the diagram
            mermaid_path = f"{os.path.splitext(output_path)[0]}.mmd"
            with open(mermaid_path, 'w') as f:
                f.write(mermaid_diagram)

            print(f"Mermaid diagram source saved to {mermaid_path}")
            print("Note: This is a minimal implementation. In production, use mermaid-cli to render to image.")

            # In a real implementation, convert to PNG, but for now just return the source path
            return mermaid_path

        except Exception as e:
            print(f"Error generating diagram: {e}")
            return ""

    def _create_mermaid_diagram(self) -> str:
        """Create Mermaid diagram definition for the workflow."""
        jobs = self.workflow_data['jobs']
        dependencies = self.workflow_data['job_dependencies']

        # Start Mermaid graph definition
        mermaid = "graph TD;\n"

        # Add nodes for each job
        for job_id, job_data in jobs.items():
            job_name = job_data.get('name', job_id)

            # Add styling based on job type
            if job_data.get('is_reusable_workflow', False):
                mermaid += f'    {job_id}["{job_name} (Reusable)"];\n'
            elif job_data.get('strategy', {}).get('matrix', {}):
                mermaid += f'    {job_id}["{job_name} (Matrix)"];\n'
            else:
                mermaid += f'    {job_id}["{job_name}"];\n'

        # Add edges for dependencies
        for job_id, deps in dependencies.items():
            for dep in deps:
                if dep in jobs:  # Make sure the dependency exists
                    mermaid += f'    {dep} --> {job_id};\n'

        # Add conditional jobs styling
        for condition in self.workflow_data.get('conditional_paths', {}).get('jobs', []):
            job_id = condition['job_id']
            mermaid += f'    style {job_id} fill:#f9f,stroke:#333,stroke-dasharray: 5 5\n'

        # Add reusable workflow subgraph if any
        workflow_calls = self.workflow_data.get('workflow_calls', [])
        if workflow_calls:
            mermaid += "\n    subgraph \"Reusable Workflows\"\n"
            for i, call in enumerate(workflow_calls):
                workflow_path = call['workflow_path'].replace('/', '_').replace('.', '_')
                mermaid += f'    wf{i}["{call["workflow_path"]}"];\n'
            mermaid += "    end\n"

            # Add connections to reusable workflows
            for i, call in enumerate(workflow_calls):
                mermaid += f'    {call["job_id"]} -- uses --> wf{i};\n'

        return mermaid
