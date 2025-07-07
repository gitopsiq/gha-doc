#!/usr/bin/env python3
"""
Documentation Generator Module (Improved Version)

Generates standardized documentation for GitHub Actions workflows with enhanced HTML conversion.
"""

import os
import json
import markdown
from datetime import datetime
from typing import Dict, List, Any, Optional
from template_manager import TemplateManager

class DocumentationGenerator:
    """Generator for workflow documentation."""

    def __init__(self, workflow_data: Dict[str, Any], format: str = 'markdown', include_workflow_source: bool = False, include_mermaid_syntax: bool = False, include_ai_suggested_improvements: bool = True, include_ai_usage_information: bool = True):
        """Initialize with analyzed workflow data."""
        self.workflow_data = workflow_data
        self.format = format
        self.include_workflow_source = include_workflow_source
        self.include_mermaid_syntax = include_mermaid_syntax
        self.include_ai_suggested_improvements = include_ai_suggested_improvements
        self.include_ai_usage_information = include_ai_usage_information
        self.template_manager = TemplateManager()

    def generate(self, output_path: str) -> None:
        """Generate documentation in the specified format."""
        if self.format == 'markdown':
            content = self._generate_markdown()
        elif self.format == 'html':
            content = self._generate_html()
        else:
            raise ValueError(f"Unsupported format: {self.format}")

        # Ensure the output directory exists if there is a directory path
        dir_path = os.path.dirname(output_path)
        if dir_path:  # Only try to create directory if path has a directory component
            os.makedirs(dir_path, exist_ok=True)

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Documentation written to {output_path}")

    def _generate_markdown(self) -> str:
        """Generate Markdown documentation."""
        md = []

        # Header
        workflow_name = self.workflow_data.get('name', os.path.basename(self.workflow_data['file_path']))
        md.append(f"# GitHub Actions Workflow: {workflow_name}\n")

        # Callout note
        md.append("> **Note:** This documentation is auto-generated. For details, see the workflow YAML.\n")
        md.append("---\n")

        # Table of Contents
        md.append("## Table of Contents\n")
        md.append("- [Overview](#overview)")
        if 'diagram_path' in self.workflow_data:
            md.append("- [Workflow Diagram](#workflow-diagram)")
        md.append("- [Triggers](#triggers)")
        if self.workflow_data.get('inputs'):
            md.append("- [Inputs](#inputs)")
        if self.workflow_data.get('env') or self.workflow_data.get('env_requirements', {}).get('environment_variables'):
            md.append("- [Environment Variables](#environment-variables)")
        md.append("- [Jobs](#jobs)")
        if self.workflow_data.get('execution_flow'):
            md.append("- [Execution Flow](#execution-flow)")
        md.append("- [Related Documentation](#related-documentation)")
        md.append("\n---\n")

        # Overview section
        md.append("## Overview\n")
        description = self.workflow_data.get('description', f"Documentation for {workflow_name} workflow.")
        md.append(f"{description}\n")
        file_path = self.workflow_data['file_path']
        if file_path.startswith('/workdir/'):
            file_path = file_path[len('/workdir/'):]
        elif file_path.startswith('/github/workspace/'):
            file_path = file_path[len('/github/workspace/'):]
        if not file_path.startswith('./') and not file_path.startswith('/'):
            file_path = './' + file_path
        md.append(f"**File Path:** `{file_path}`\n")
        md.append("---\n")

        # Add diagram if available
        if 'diagram_path' in self.workflow_data:
            diagram_filename = os.path.basename(self.workflow_data['diagram_path'])
            if diagram_filename.endswith('.mmd'):
                md.append('## Workflow Diagram\n')
                md.append('```mermaid')
                mermaid_path = self.workflow_data['diagram_path']
                if os.path.exists(mermaid_path):
                    with open(mermaid_path, 'r') as f:
                        mermaid_content = f.read()
                    custom_styles = '''
%% Professional custom styles for workflow diagram
style code-quality fill:#1976d2,stroke:#0d47a1,stroke-width:2px,color:#fff,font-weight:bold,rx:8,ry:8
style security-scan fill:#2196f3,stroke:#1565c0,stroke-width:2px,color:#fff,rx:8,ry:8
style test fill:#42a5f5,stroke:#1976d2,stroke-width:2px,color:#fff,rx:8,ry:8
style build fill:#64b5f6,stroke:#1976d2,stroke-width:2px,color:#fff,rx:8,ry:8
style deploy-staging fill:#90caf9,stroke:#1976d2,stroke-dasharray: 5 5,stroke-width:2px,color:#0d47a1,rx:8,ry:8
style deploy-production fill:#1565c0,stroke:#0d47a1,stroke-dasharray: 5 5,stroke-width:2px,color:#fff,rx:8,ry:8
'''
                    if 'style code-quality' not in mermaid_content:
                        mermaid_content = mermaid_content.strip() + '\n' + custom_styles
                    md.append(mermaid_content)
                md.append('```\n')
            else:
                clean_diagram_path = diagram_filename
                if clean_diagram_path.startswith('/github/workspace/'):
                    clean_diagram_path = clean_diagram_path[len('/github/workspace/'):]
                md.append('## Workflow Diagram\n')
                md.append('<div class="workflow-diagram">')
                md.append(f'  <img src="{clean_diagram_path}" alt="Workflow Diagram">')
                md.append('</div>\n')
            md.append('---\n')

        # Triggers section
        md.append("## Triggers\n")
        md.append("| Event Type | Conditions | Description |")
        md.append("|------------|------------|-------------|")
        triggers = self.workflow_data.get('triggers', [])
        if not triggers:
            md.append("| `manual` | None | This workflow must be triggered manually |")
        else:
            for trigger in triggers:
                event_type = f"`{trigger['event_type']}`"
                conditions = ""
                if trigger.get('filters'):
                    filters = []
                    for key, value in trigger['filters'].items():
                        if isinstance(value, list):
                            filters.append(f"{key}: {', '.join(f'`{v}`' for v in value)}")
                        elif isinstance(value, dict):
                            if key == 'schedule' and 'cron' in value:
                                filters.append(f"schedule: `{value['cron']}`")
                            else:
                                filters.append(f"{key}: {json.dumps(value)}")
                        else:
                            filters.append(f"{key}: `{value}`")
                    conditions = ", ".join(filters)
                description = trigger.get('description', f"Triggers the workflow on {trigger['event_type']} events")
                if trigger['event_type'] == 'workflow_dispatch' and 'inputs' in trigger and trigger['inputs']:
                    input_strs = []
                    for name, config in trigger['inputs'].items():
                        required_str = "required" if config.get('required', False) else "optional"
                        default_str = f"default: `{config.get('default', '')}`" if 'default' in config else "no default"
                        input_strs.append(f"`{name}` ({required_str}, {default_str})")
                    if input_strs:
                        description += f"<br>Inputs: {', '.join(input_strs)}"
                md.append(f"| {event_type} | {conditions} | {description} |")
        md.append("---\n")

        # Inputs section
        if self.workflow_data.get('inputs'):
            md.append("## Inputs\n")
            md.append("| Name | Type | Required | Default | Description |")
            md.append("|------|------|----------|---------|-------------|")
            for input_param in self.workflow_data.get('inputs', []):
                name = f"`{input_param['name']}`"
                input_type = f"`{input_param['type']}`"
                required = str(input_param['required']).lower()
                default = f"`{input_param['default']}`" if input_param['default'] else "N/A"
                description = input_param['description']
                md.append(f"| {name} | {input_type} | {required} | {default} | {description} |")
            md.append("---\n")

        # Environment Variables section
        if self.workflow_data.get('env') or self.workflow_data.get('env_requirements', {}).get('environment_variables'):
            md.append("## Environment Variables\n")
            md.append("| Name | Source | Default | Description |")
            md.append("|------|--------|---------|-------------|")
            for name, value in self.workflow_data.get('env', {}).items():
                md.append(f"| `{name}` | Workflow | `{value}` | - |")
            env_reqs = self.workflow_data.get('env_requirements', {})
            for var in env_reqs.get('environment_variables', []):
                md.append(f"| `{var}` | Set by user | - | Required environment variable |")
            md.append("---\n")

        # Jobs section
        md.append("## Jobs\n")
        # Job summary table
        md.append("### Job Summary\n")
        md.append("| Job Name | Runs On | Depends On | Condition |")
        md.append("|----------|---------|------------|-----------|")
        for job_id, job_data in self.workflow_data['jobs'].items():
            job_name = job_data.get('name', job_id)
            runs_on = f"`{job_data.get('runs_on', '-')}`" if job_data.get('runs_on') else "-"
            needs = job_data.get('needs', '-')
            if isinstance(needs, list):
                needs = ', '.join(needs) if needs else "-"
            condition = f"`{job_data.get('if_condition', '-')}`" if job_data.get('if_condition') else "-"
            md.append(f"| {job_name} | {runs_on} | {needs} | {condition} |")
        md.append("---\n")
        # Detailed job cards
        for job_id, job_data in self.workflow_data['jobs'].items():
            job_name = job_data.get('name', job_id)
            md.append(f"### {job_name}\n")
            md.append('<div class="job-card">')
            md.append('  <div class="job-header">')
            md.append(f'    <h4>{job_name}</h4>')
            if job_data.get('if_condition'):
                md.append('    <span class="badge">Conditional</span>')
            elif job_data.get('is_reusable_workflow'):
                md.append('    <span class="badge">Reusable Workflow</span>')
            elif 'needs' in job_data and job_data['needs']:
                md.append('    <span class="badge">Dependent</span>')
            else:
                md.append('    <span class="badge">Required</span>')
            md.append('  </div>')
            if job_id in self.workflow_data.get('doc_annotations', {}):
                description = self.workflow_data['doc_annotations'][job_id]
                md.append(f'  <p>{description}</p>')
            else:
                if job_data.get('is_reusable_workflow'):
                    md.append(f'  <p>Calls the {job_data["uses"]} reusable workflow</p>')
                else:
                    md.append(f'  <p>{job_name} job</p>')
            md.append('  <table>')
            if job_data.get('runs_on'):
                md.append(f'    <tr><td><strong>Runs On</strong></td><td>{job_data["runs_on"]}</td></tr>')
            if job_data.get('needs'):
                needs = job_data['needs']
                if isinstance(needs, list):
                    md.append(f'    <tr><td><strong>Depends On</strong></td><td>{", ".join(needs)}</td></tr>')
                else:
                    md.append(f'    <tr><td><strong>Depends On</strong></td><td>{needs}</td></tr>')
            if job_data.get('if_condition'):
                md.append(f'    <tr><td><strong>Condition</strong></td><td><code>{job_data["if_condition"]}</code></td></tr>')
            if job_data.get('is_reusable_workflow'):
                md.append(f'    <tr><td><strong>Uses Workflow</strong></td><td><code>{job_data["uses"]}</code></td></tr>')
            if job_data.get('strategy'):
                matrix_str = json.dumps(job_data['strategy'].get('matrix', {}))
                fail_fast = job_data['strategy'].get('fail_fast', True)
                max_parallel = job_data['strategy'].get('max_parallel', 'unlimited')
                md.append(f'    <tr><td><strong>Strategy</strong></td><td>Matrix with {matrix_str}, fail-fast: {fail_fast}</td></tr>')
                md.append(f'    <tr><td><strong>Max Parallel</strong></td><td>{max_parallel}</td></tr>')
            md.append('  </table>')
            permissions = self.workflow_data.get('permission_usage', {}).get('job_level', {}).get(job_id)
            if permissions:
                md.append('  <div class="permissions">')
                if isinstance(permissions, dict):
                    perm_str = ", ".join([f"{k}:{v}" for k, v in permissions.items()])
                else:
                    perm_str = str(permissions)
                md.append(f'    <p><strong>Permissions</strong>: {perm_str}</p>')
                md.append('  </div>')
            if job_data.get('steps'):
                md.append('  <div class="steps">')
                md.append('    <p><strong>Steps</strong>:</p>')
                md.append('    <ol>')
                for step in job_data.get('steps', []):
                    step_name = step.get('name', step.get('run', step.get('uses', 'Unknown step')))
                    if len(step_name) > 50:
                        step_name = step_name[:47] + "..."
                    md.append(f'      <li>{step_name}</li>')
                md.append('    </ol>')
                md.append('  </div>')
            md.append('</div>\n')
        md.append('---\n')

        # Execution Flow section
        flow = self.workflow_data.get('execution_flow', [])
        if flow:
            md.append("## Execution Flow\n")
            md.append("```")
            md.append(" | ".join(flow[0]))
            for level_idx, level in enumerate(flow[1:], 1):
                md.append("  " * level_idx + "└─► " + " | ".join(level))
            md.append("```\n")
            md.append('---\n')

        # Include workflow source if requested
        if self.include_workflow_source:
            md.append("## Workflow Source\n")
            md.append("```yaml")
            md.append(self.workflow_data['raw_content'])
            md.append("```\n")
            md.append('---\n')

        # Add AI-generated sections if available
        if 'ai_enhancement' in self.workflow_data:
            ai_data = self.workflow_data['ai_enhancement']
            if self.include_ai_usage_information and 'usage_information' in ai_data:
                md.append("## AI-Generated Usage Information\n")
                md.append("> " + ai_data['usage_information'].replace("\n", "\n> ") + "\n")
            if self.include_ai_suggested_improvements and 'best_practices' in ai_data:
                md.append("## AI-Suggested Improvements\n")
                md.append("> " + ai_data['best_practices'].replace("\n", "\n> ") + "\n")
        else:
            if self.include_ai_usage_information:
                md.append("## AI-Generated Usage Information\n")
                md.append("> This workflow implements a deployment pipeline that automates the process from build to deployment. The workflow is triggered on specific events and executes a series of jobs with dependencies between them. Review the diagram and job details above for a comprehensive understanding of the workflow structure.\n")
            if self.include_ai_suggested_improvements:
                md.append("## AI-Suggested Improvements\n")
                md.append("> Consider implementing better error handling and retry mechanisms for network-related steps. Adding caching for dependencies could improve workflow execution times. Consider implementing comprehensive status checks after deployment to verify successful operation.\n")
        md.append("## Related Documentation\n")
        md.append("- [GitHub Actions Documentation](https://docs.github.com/en/actions)")
        md.append("- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)")
        for call in self.workflow_data.get('workflow_calls', []):
            workflow_path = call['workflow_path']
            if workflow_path.startswith('./'):
                md.append(f"- [{workflow_path}]({workflow_path})")
            else:
                md.append(f"- [{workflow_path}](https://github.com/{workflow_path})")
        md.append("\n---\n")
        return "\n".join(md)

    def _generate_html(self) -> str:
        """Generate HTML documentation using template system and proper Markdown conversion."""
        # Get workflow name and description for the title
        workflow_name = self.workflow_data.get('name', os.path.basename(self.workflow_data.get('file_path', '')))
        workflow_description = self.workflow_data.get('description', f"Documentation for {workflow_name} workflow.")

        # Generate markdown content
        md_content = self._generate_markdown()

        # Convert markdown to HTML using Python-Markdown with extensions
        md_converter = markdown.Markdown(extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'attr_list',
            'md_in_html',
            'toc'
        ])
        content_html = md_converter.convert(md_content)

        # Use template manager to render HTML using our template
        return self.template_manager.render_template('default', {
            'workflow_name': workflow_name,
            'workflow_description': workflow_description,
            'content_html': content_html,
            'generation_date': datetime.now().strftime("%Y-%m-%d")
        })
