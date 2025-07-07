#!/usr/bin/env python3
"""
Diagram Generator Module (Improved Version)

Generates visual diagrams of GitHub Actions workflows with support for
both Mermaid syntax and rendered images.
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

    def __init__(self, workflow_data: Dict[str, Any], diagram_type: str = "mermaid"):
        """
        Initialize with analyzed workflow data.

        Args:
            workflow_data: The analyzed workflow data
            diagram_type: The type of diagram to generate ("none", "mermaid", "svg")
        """
        self.workflow_data = workflow_data
        self.diagram_type = diagram_type.lower() if diagram_type else "mermaid"
        self.supported_formats = ["svg", "png", "pdf"]

    def generate(self, output_path: str) -> str:
        """
        Generate diagram for the workflow based on the specified diagram type.

        Args:
            output_path: Path where the generated diagram should be saved

        Returns:
            The path to the generated file (mermaid or image file)
        """
        try:
            # Check if diagram generation is disabled
            if self.diagram_type == "none":
                print("Diagram generation is disabled.")
                return ""

            # Create Mermaid diagram definition
            mermaid_diagram = self._create_mermaid_diagram()

            # Save the mermaid source
            mermaid_path = f"{os.path.splitext(output_path)[0]}.mmd"
            os.makedirs(os.path.dirname(mermaid_path), exist_ok=True)

            with open(mermaid_path, 'w') as f:
                f.write(mermaid_diagram)

            print(f"Mermaid diagram source saved to {mermaid_path}")

            # If the diagram type is mermaid, we're done
            if self.diagram_type == "mermaid":
                return mermaid_path

            # For other diagram types, try to render using mmdc
            if self.diagram_type in self.supported_formats:
                # Ensure output path has the correct extension
                output_path = f"{os.path.splitext(output_path)[0]}.{self.diagram_type}"

                if self._render_diagram_with_mmdc(mermaid_path, output_path):
                    print(f"Diagram rendered to {output_path}")
                    return output_path
                else:
                    print(f"Failed to render {self.diagram_type} diagram. Falling back to Mermaid source.")
                    return mermaid_path
            else:
                print(f"Unsupported diagram type '{self.diagram_type}'. Supported types are: {', '.join(self.supported_formats)}. Using Mermaid source only.")
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
            job_name = job_name.replace('@', '\\@')  # Escape @ for Markdown viewers

            # Add styling based on job type
            if job_data.get('is_reusable_workflow', False):
                mermaid += f'    {job_id}["{job_name} (Reusable)"]\n'
            elif job_data.get('strategy', {}).get('matrix', {}):
                mermaid += f'    {job_id}["{job_name} (Matrix)"]\n'
            else:
                mermaid += f'    {job_id}["{job_name}"]\n'

        # Add edges for dependencies
        for job_id, deps in dependencies.items():
            for dep in deps:
                if dep in jobs:  # Make sure the dependency exists
                    mermaid += f'    {dep} --> {job_id};\n'

        # Add conditional jobs styling - using a professional blue color scheme
        for condition in self.workflow_data.get('conditional_paths', {}).get('jobs', []):
            job_id = condition['job_id']
            mermaid += f'    style {job_id} fill:#e0f0ff,stroke:#0067b8,stroke-dasharray: 5 5\n'

        # Add reusable workflow subgraph if any
        workflow_calls = self.workflow_data.get('workflow_calls', [])
        if workflow_calls:
            mermaid += "\n    subgraph \"Reusable Workflows\"\n"
            for i, call in enumerate(workflow_calls):
                workflow_path = call['workflow_path'].replace('/', '_').replace('.', '_')
                label = call["workflow_path"].replace('@', '\\@')  # Escape @ for Markdown viewers
                mermaid += f'    wf{i}["{label}"]\n'
            mermaid += "    end\n"

            # Add connections to reusable workflows
            for i, call in enumerate(workflow_calls):
                mermaid += f'    {call["job_id"]} -- uses --> wf{i};\n'

        return mermaid

    def _render_diagram_with_mmdc(self, mermaid_path: str, output_path: str) -> bool:
        """
        Render the diagram using Mermaid CLI (mmdc).

        Args:
            mermaid_path: Path to the mermaid source file
            output_path: Path where the rendered diagram should be saved

        Returns:
            True if rendering succeeded, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Determine output format based on file extension
            output_format = os.path.splitext(output_path)[1][1:] or 'svg'

            # Check if format is supported
            if output_format not in self.supported_formats:
                print(f"Unsupported output format: {output_format}")
                return False

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

    def render_mermaid_to_image(self, mermaid_content: str, output_path: str, image_format: str = "svg") -> bool:
        """
        Render Mermaid diagram content directly to image file.

        Args:
            mermaid_content: The Mermaid diagram content as string
            output_path: Path to save the rendered image file
            image_format: Format of the image (svg, png, pdf)

        Returns:
            bool: True if rendering succeeded, False otherwise
        """
        try:
            # Ensure the output format is supported
            if image_format not in self.supported_formats:
                print(f"Unsupported image format: {image_format}")
                return False

            # Create a temporary file for the Mermaid content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp:
                temp.write(mermaid_content)
                temp_path = temp.name

            # Make sure output path has the correct extension
            output_path = f"{os.path.splitext(output_path)[0]}.{image_format}"

            # Try to render the diagram
            result = self._render_diagram_with_mmdc(temp_path, output_path)

            # Clean up the temporary file
            os.unlink(temp_path)

            return result
        except Exception as e:
            print(f"Error rendering Mermaid content to {image_format}: {e}")
            return False
