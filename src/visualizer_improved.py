#!/usr/bin/env python3
"""
Diagram Generator Module (Improved Version)

Generates visual diagrams of GitHub Actions workflows with support for
both Mermaid syntax and rendered images using mmdc CLI tool.
"""

import os
import json
import tempfile
import subprocess
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path

class DiagramGenerator:
    """Generator for workflow diagrams."""

    def __init__(self, workflow_data: Dict[str, Any]):
        """Initialize with analyzed workflow data."""
        self.workflow_data = workflow_data

    def generate(self, output_path: str) -> str:
        """
        Generate diagram for the workflow and save to output_path.

        If mmdc (Mermaid CLI) is available, renders an actual image.
        Otherwise, just saves the Mermaid syntax.

        Returns the path to the generated file.
        """
        try:
            # Create Mermaid diagram definition
            mermaid_diagram = self._create_mermaid_diagram()

            # Save the mermaid source
            mermaid_path = f"{os.path.splitext(output_path)[0]}.mmd"
            os.makedirs(os.path.dirname(mermaid_path), exist_ok=True)

            with open(mermaid_path, 'w') as f:
                f.write(mermaid_diagram)

            print(f"Mermaid diagram source saved to {mermaid_path}")

            # Try to render the diagram using the Mermaid CLI tool if available
            if self._render_diagram_with_mmdc(mermaid_path, output_path):
                print(f"Diagram rendered to {output_path}")
                return output_path
            else:
                print("Mermaid CLI not available or rendering failed. Using Mermaid source only.")
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

    def _render_diagram_with_mmdc(self, mermaid_path: str, output_path: str) -> bool:
        """Render the diagram using Mermaid CLI (mmdc) if available."""
        # Check if mmdc is available
        if not self._is_mmdc_available():
            self._try_install_mmdc()
            if not self._is_mmdc_available():
                print("Mermaid CLI is not available. Install it with: npm install -g @mermaid-js/mermaid-cli")
                return False

        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Determine output format based on file extension
            output_format = os.path.splitext(output_path)[1][1:] or 'png'

            # Run mmdc to generate the diagram
            cmd = [
                "mmdc",
                "-i", mermaid_path,
                "-o", output_path,
                "-t", "forest",  # Using forest theme for better visibility
                "-b", "transparent"  # Transparent background
            ]

            subprocess.run(cmd, check=True)
            return os.path.exists(output_path)

        except subprocess.CalledProcessError as e:
            print(f"Error rendering diagram with Mermaid CLI: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error rendering diagram: {e}")
            return False

    def _is_mmdc_available(self) -> bool:
        """Check if Mermaid CLI (mmdc) is available in the system."""
        try:
            # Try to run mmdc --version
            subprocess.run(["mmdc", "--version"],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          check=False)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _try_install_mmdc(self) -> bool:
        """Try to install Mermaid CLI using npm if npm is available."""
        try:
            # Check if npm is available
            npm_check = subprocess.run(["npm", "--version"],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      check=False)

            if npm_check.returncode == 0:
                print("Trying to install Mermaid CLI...")
                # Install Mermaid CLI globally
                install_proc = subprocess.run(
                    ["npm", "install", "-g", "@mermaid-js/mermaid-cli"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False
                )

                if install_proc.returncode == 0:
                    print("Mermaid CLI installed successfully.")
                    return True
                else:
                    print("Failed to install Mermaid CLI.")
                    print(f"Error: {install_proc.stderr.decode('utf-8')}")

            return False
        except Exception as e:
            print(f"Error trying to install Mermaid CLI: {e}")
            return False

    def render_mermaid_to_png(self, mermaid_content: str, output_path: str) -> bool:
        """
        Render Mermaid diagram content directly to PNG file.

        Args:
            mermaid_content: The Mermaid diagram content as string
            output_path: Path to save the rendered PNG file

        Returns:
            bool: True if rendering succeeded, False otherwise
        """
        try:
            # Create a temporary file for the Mermaid content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp:
                temp.write(mermaid_content)
                temp_path = temp.name

            # Try to render the diagram
            result = self._render_diagram_with_mmdc(temp_path, output_path)

            # Clean up the temporary file
            os.unlink(temp_path)

            return result
        except Exception as e:
            print(f"Error rendering Mermaid content to PNG: {e}")
            return False
