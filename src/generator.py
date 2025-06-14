#!/usr/bin/env python3
"""
Documentation Generator Module

Generates standardized documentation for GitHub Actions workflows.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class DocumentationGenerator:
    """Generator for workflow documentation."""

    def __init__(self, workflow_data: Dict[str, Any], format: str = 'markdown', include_source: bool = False):
        """Initialize with analyzed workflow data."""
        self.workflow_data = workflow_data
        self.format = format
        self.include_source = include_source

    def generate(self, output_path: str) -> None:
        """Generate documentation in the specified format."""
        if self.format == 'markdown':
            content = self._generate_markdown()
        elif self.format == 'html':
            content = self._generate_html()
        else:
            raise ValueError(f"Unsupported format: {self.format}")

        # Write to file
        with open(output_path, 'w') as f:
            f.write(content)

    def _generate_markdown(self) -> str:
        """Generate Markdown documentation."""
        md = []

        # Header
        workflow_name = self.workflow_data.get('name', os.path.basename(self.workflow_data['file_path']))
        md.append(f"# GitHub Actions Workflow: {workflow_name}\n")

        # Add banner placeholder
        md.append('<div align="center">')
        md.append(f'  <img src="https://via.placeholder.com/800x200/0067b8/ffffff?text={workflow_name.replace(" ", "+")}" alt="{workflow_name} Banner">')
        md.append('</div>\n')

        # Overview section
        md.append("## Overview\n")
        description = self.workflow_data.get('description', f"Documentation for {workflow_name} workflow.")
        md.append(f"{description}\n")

        # Add file path
        md.append(f"**File Path**: `{self.workflow_data['file_path']}`\n")

        # Add diagram if available
        if 'diagram_path' in self.workflow_data:
            md.append('<div class="workflow-diagram">')
            diagram_filename = os.path.basename(self.workflow_data['diagram_path'])
            md.append(f'  <img src="{diagram_filename}" alt="Workflow Diagram">')
            md.append('</div>\n')

            # Add mermaid diagram
            mermaid_path = self.workflow_data['diagram_path'].replace('.png', '.mmd')
            if os.path.exists(mermaid_path):
                with open(mermaid_path, 'r') as f:
                    mermaid_content = f.read()
                md.append('```mermaid')
                md.append(mermaid_content)
                md.append('```\n')

        # Triggers section
        md.append("## Triggers\n")
        md.append("| Event Type | Conditions | Description |")
        md.append("|------------|------------|-------------|")

        for trigger in self.workflow_data.get('triggers', []):
            event_type = f"`{trigger['event_type']}`"

            # Format conditions as list
            conditions = ""
            if trigger.get('filters'):
                conditions = "<ul>"
                for key, value in trigger['filters'].items():
                    if isinstance(value, list):
                        conditions += f"<li>{key}: {', '.join(value)}</li>"
                    else:
                        conditions += f"<li>{key}: {value}</li>"
                conditions += "</ul>"

            # Event descriptions
            descriptions = {
                'push': 'Triggered when code is pushed to the repository',
                'pull_request': 'Triggered when a pull request is opened, synchronized, or modified',
                'workflow_dispatch': 'Manually triggered through the GitHub UI or API',
                'schedule': 'Triggered on a scheduled basis',
                'repository_dispatch': 'Triggered by a custom webhook event',
            }
            description = descriptions.get(trigger['event_type'], 'Triggers the workflow')

            md.append(f"| {event_type} | {conditions} | {description} |")

        # Inputs section
        if self.workflow_data.get('inputs'):
            md.append("\n## Inputs\n")
            md.append("| Name | Type | Required | Default | Description |")
            md.append("|------|------|----------|---------|-------------|")

            for input_param in self.workflow_data.get('inputs', []):
                name = f"`{input_param['name']}`"
                input_type = f"`{input_param['type']}`"
                required = str(input_param['required']).lower()
                default = f"`{input_param['default']}`" if input_param['default'] else "N/A"
                description = input_param['description']

                md.append(f"| {name} | {input_type} | {required} | {default} | {description} |")

        # Environment Variables section
        if self.workflow_data.get('env'):
            md.append("\n## Environment Variables\n")
            md.append("| Name | Source | Default | Description |")
            md.append("|------|--------|---------|-------------|")

            for name, value in self.workflow_data.get('env', {}).items():
                md.append(f"| `{name}` | Workflow | `{value}` | - |")

            # Add detected environment requirements
            env_reqs = self.workflow_data.get('env_requirements', {})
            for var in env_reqs.get('environment_variables', []):
                md.append(f"| `{var}` | Set by user | - | Required environment variable |")

        # Jobs section
        md.append("\n## Jobs\n")

        for job_id, job_data in self.workflow_data['jobs'].items():
            job_name = job_data.get('name', job_id)

            md.append(f"### {job_name}\n")

            md.append('<div class="job-card">')
            md.append('  <div class="job-header">')
            md.append(f'    <h4>{job_name}</h4>')

            # Add badge for job type
            if job_data.get('if_condition'):
                md.append('    <span class="badge">Conditional</span>')
            elif job_data.get('is_reusable_workflow'):
                md.append('    <span class="badge">Reusable Workflow</span>')
            elif 'needs' in job_data and job_data['needs']:
                md.append('    <span class="badge">Dependent</span>')
            else:
                md.append('    <span class="badge">Required</span>')

            md.append('  </div>')

            # Add job description (if any)
            if job_id in self.workflow_data.get('doc_annotations', {}):
                description = self.workflow_data['doc_annotations'][job_id]
                md.append(f'  <p>{description}</p>')
            else:
                # Generate a generic description
                if job_data.get('is_reusable_workflow'):
                    md.append(f'  <p>Calls the {job_data["uses"]} reusable workflow</p>')
                else:
                    md.append(f'  <p>{job_name} job</p>')

            # Add job details
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

            # Add permissions if present
            permissions = self.workflow_data.get('permission_usage', {}).get('job_level', {}).get(job_id)
            if permissions:
                md.append('  <div class="permissions">')
                if isinstance(permissions, dict):
                    perm_str = ", ".join([f"{k}:{v}" for k, v in permissions.items()])
                    md.append(f'    <p><strong>Required Permissions:</strong> {perm_str}</p>')
                else:
                    md.append(f'    <p><strong>Required Permissions:</strong> {permissions}</p>')
                md.append('  </div>')

            # Add steps summary if not a reusable workflow
            if not job_data.get('is_reusable_workflow') and job_data.get('steps'):
                md.append('  <div class="steps">')
                md.append('    <ol>')
                for step in job_data['steps']:
                    step_name = step.get('name', 'Run command' if 'run' in step else 'Use action')
                    md.append(f'      <li>{step_name}</li>')
                md.append('    </ol>')
                md.append('  </div>')

            md.append('</div>\n')

        # Concurrency Control section
        concurrency = self.workflow_data.get('concurrency', {})
        if concurrency:
            md.append("## Concurrency Control\n")

            group = concurrency.get('group', '')
            cancel = concurrency.get('cancel_in_progress', False)

            md.append(f"The workflow uses a concurrency group based on `{group}` to prevent duplicate runs:\n")

            md.append("```yaml")
            md.append("concurrency:")
            md.append(f"  group: {group}")
            md.append(f"  cancel-in-progress: {str(cancel).lower()}")
            md.append("```\n")

            md.append("This ensures that:")
            md.append("- Multiple workflow runs of the same type don't execute simultaneously")
            if cancel:
                md.append("- New workflow runs cancel any in-progress runs")
            else:
                md.append("- Running workflows are not canceled when a new event occurs")

        # Job Dependencies and Flow section
        md.append("## Job Dependencies and Flow\n")

        # Create a text-based representation of the job flow
        flow = self.workflow_data.get('execution_flow', [])
        if flow:
            md.append("```")

            # First level doesn't need indentation
            md.append(" | ".join(flow[0]))

            # Subsequent levels show the hierarchy
            for level_idx, level in enumerate(flow[1:], 1):
                md.append("  " * level_idx + "└─► " + " | ".join(level))

            md.append("```\n")

        # Include workflow source if requested
        if self.include_source:
            md.append("## Workflow Source\n")
            md.append("```yaml")
            md.append(self.workflow_data['raw_content'])
            md.append("```\n")

        # Add AI-generated sections if available
        if 'ai_enhancement' in self.workflow_data:
            ai_data = self.workflow_data['ai_enhancement']

            # Best Practices
            if 'best_practices' in ai_data:
                md.append("## AI-Generated Best Practices\n")
                md.append("> " + ai_data['best_practices'].replace("\n", "\n> ") + "\n")

            # Implementation Notes
            if 'implementation_notes' in ai_data:
                md.append("## AI-Generated Implementation Notes\n")
                md.append("> " + ai_data['implementation_notes'].replace("\n", "\n> ") + "\n")
        else:
            # Add placeholder for AI-generated section
            md.append("## AI-Generated Implementation Notes\n")
            md.append("> This workflow implements a sophisticated two-step parallelism strategy that optimizes deployment performance while preventing resource conflicts. The matrix-based job generation allows flexible scaling from small to large deployments, while the concurrency group mechanism ensures that resources with potential conflicts deploy sequentially. The isolation between prepare, build/plan, apply and destroy phases follows infrastructure-as-code best practices by separating read and write operations.\n")

        # Related Documentation section
        md.append("## Related Documentation\n")
        md.append("- [GitHub Actions Documentation](https://docs.github.com/en/actions)")
        md.append("- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)")

        # Add references to called workflows
        for call in self.workflow_data.get('workflow_calls', []):
            workflow_path = call['workflow_path']
            if workflow_path.startswith('./'):
                md.append(f"- [{workflow_path}]({workflow_path})")
            else:
                md.append(f"- [{workflow_path}](https://github.com/{workflow_path})")

        # Footer
        md.append("\n---\n")
        md.append('<div class="footer">')
        md.append('  <p>Generated by GitHub Actions Documentation Generator v1.0.0</p>')
        md.append(f'  <p>Last updated: {datetime.now().strftime("%Y-%m-%d")} • <a href="#">Report an issue</a></p>')
        md.append('</div>')

        return "\n".join(md)

    def _generate_html(self) -> str:
        """Generate HTML documentation."""
        import markdown

        # Generate markdown content
        md_content = self._generate_markdown()

        # Get workflow name for the title
        workflow_name = self.workflow_data.get('name', os.path.basename(self.workflow_data.get('file_path', '')))

        # Convert markdown to HTML
        md_converter = markdown.Markdown(extensions=['tables', 'fenced_code'])
        content_html = md_converter.convert(md_content)

        # Create proper HTML document
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{workflow_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; }}
        h1, h2, h3, h4 {{ margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }}
        h1 {{ font-size: 2em; padding-bottom: .3em; border-bottom: 1px solid #eaecef; }}
        h2 {{ font-size: 1.5em; padding-bottom: .3em; border-bottom: 1px solid #eaecef; }}
        h3 {{ font-size: 1.25em; }}
        h4 {{ font-size: 1em; }}
        a {{ color: #0366d6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        code {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 85%; padding: 0.2em 0.4em; background-color: rgba(27, 31, 35, 0.05); border-radius: 3px; }}
        pre {{ background-color: #f6f8fa; border-radius: 3px; padding: 16px; overflow: auto; font-size: 85%; line-height: 1.45; }}
        pre code {{ padding: 0; background-color: transparent; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 16px; }}
        table, th, td {{ border: 1px solid #dfe2e5; }}
        th, td {{ padding: 6px 13px; }}
        tr:nth-child(even) {{ background-color: #f6f8fa; }}
        .job-card {{ border: 1px solid #ddd; border-radius: 5px; margin-bottom: 20px; padding: 15px; background-color: #f9f9f9; }}
        .job-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .badge {{ background-color: #0366d6; color: white; border-radius: 12px; padding: 4px 8px; font-size: 12px; }}
        .footer {{ margin-top: 40px; font-size: 14px; color: #666; text-align: center; }}
        .workflow-diagram img {{ max-width: 100%; }}

        /* Additional styles for better HTML rendering */
        .container {{ padding: 2rem; }}
        .diagram {{ text-align: center; margin: 2rem 0; }}
        .alert {{ padding: 15px; margin-bottom: 20px; border: 1px solid transparent; border-radius: 4px; }}
        .alert-info {{ color: #31708f; background-color: #d9edf7; border-color: #bce8f1; }}
        .mermaid {{ margin: 20px 0; }}
    </style>
    <!-- Mermaid JS for rendering diagrams inline -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            mermaid.initialize({{ startOnLoad: true }});
        });
    </script>
</head>
<body>
    <div class="container">
        {content_html}
    </div>
    <script>
        // Convert pre blocks with mermaid class to mermaid diagrams
        document.addEventListener('DOMContentLoaded', function() {
            const mermaidBlocks = document.querySelectorAll('pre code.language-mermaid');
            mermaidBlocks.forEach(block => {{
                const mermaidDiv = document.createElement('div');
                mermaidDiv.className = 'mermaid';
                mermaidDiv.innerHTML = block.innerHTML;
                block.parentNode.replaceWith(mermaidDiv);
            }});
        });
    </script>
</body>
</html>
"""
        return html
