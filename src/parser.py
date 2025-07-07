#!/usr/bin/env python3
"""
Workflow Parser Module

Parses GitHub Actions workflow files and extracts metadata.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

class WorkflowParser:
    """Parser for GitHub Actions workflow files."""

    def __init__(self, workflow_file_path: str):
        """Initialize with path to workflow file."""
        self.file_path = workflow_file_path
        self.raw_content = None
        self.yaml_content = None

    def parse(self) -> Dict[str, Any]:
        """Parse workflow file and extract metadata."""
        try:
            with open(self.file_path, 'r') as file:
                self.raw_content = file.read()

            # Preprocess: remove lines starting with # @ to allow YAML parsing
            yaml_lines = []
            for line in self.raw_content.splitlines():
                # Only remove annotation lines that start with '# @' and are not indented (to avoid breaking YAML structure)
                stripped = line.lstrip()
                if not stripped.startswith('# @'):
                    yaml_lines.append(line)
            yaml_content_str = '\n'.join(yaml_lines)

            # Parse YAML content
            try:
                self.yaml_content = yaml.safe_load(yaml_content_str)
            except Exception as e:
                raise

            # Workaround for PyYAML bug: if 'on' is missing but True is present, map True to 'on'
            if self.yaml_content and 'on' not in self.yaml_content and True in self.yaml_content:
                self.yaml_content['on'] = self.yaml_content[True]
                del self.yaml_content[True]

            # Extract documentation annotations from comments
            doc_annotations = self._extract_annotations()  # This still uses self.raw_content

            # Create workflow data structure
            workflow_data = {
                'file_path': self.file_path,
                'file_name': Path(self.file_path).name,
                'name': self.yaml_content.get('name', Path(self.file_path).stem),
                'description': doc_annotations.get('description', ''),
                'raw_content': self.raw_content,
                'yaml_content': self.yaml_content,
                'doc_annotations': doc_annotations,
                'triggers': self._extract_triggers(),
                'inputs': self._extract_inputs(),
                'env': self._extract_environment_variables(),
                'jobs': self._extract_jobs(),
                'concurrency': self._extract_concurrency()
            }

            return workflow_data

        except Exception as e:
            print(f"Error parsing workflow file {self.file_path}: {e}")
            raise

    def _extract_annotations(self) -> Dict[str, str]:
        """Extract documentation annotations from comments."""
        annotations = {}
        annotation_pattern = r'#\s*@(\w+):\s*(.*)'

        for line in self.raw_content.split('\n'):
            match = re.match(annotation_pattern, line)
            if match:
                key, value = match.groups()
                annotations[key] = value.strip()

        return annotations

    def _extract_triggers(self) -> List[Dict[str, Any]]:
        """Extract trigger events from the workflow."""
        triggers = []
        on_section = self.yaml_content.get('on', {})

        # Extract trigger descriptions from annotations
        trigger_descriptions = {}
        trigger_pattern = r'#\s*@trigger:\s*(\w+)\s*\n\s*#\s*@description:\s*(.*?)(?=\n\s*\w|\n\s*$|\n\s*#)'
        for match in re.finditer(trigger_pattern, self.raw_content, re.DOTALL):
            trigger_type = match.group(1)
            description = match.group(2).strip()
            trigger_descriptions[trigger_type] = description
            print(f"Found trigger annotation: {trigger_type} = {description}")

        # Standard descriptions for common triggers
        default_descriptions = {
            'push': 'Triggered when code is pushed to the repository',
            'pull_request': 'Triggered when a pull request is opened, synchronized, or modified',
            'workflow_dispatch': 'Manually triggered through the GitHub UI or API',
            'schedule': 'Triggered on a scheduled basis',
            'repository_dispatch': 'Triggered by a custom webhook event',
            'issues': 'Triggered when an issue is opened, edited, or other issue activity occurs',
            'issue_comment': 'Triggered when an issue comment is created, edited, or deleted',
            'pull_request_review': 'Triggered when a review is submitted, edited, or dismissed',
            'pull_request_review_comment': 'Triggered when a review comment is created, edited, or deleted',
            'pull_request_target': 'Similar to pull_request but with different token permissions',
            'release': 'Triggered when a release is created, edited, or other release activity occurs',
            'discussion': 'Triggered when a discussion is created, edited, or other discussion activity occurs',
            'watch': 'Triggered when someone stars a repository',
            'create': 'Triggered when a branch or tag is created',
            'delete': 'Triggered when a branch or tag is deleted',
            'label': 'Triggered when a label is created, edited, or deleted',
            'milestone': 'Triggered when a milestone is created, edited, or deleted',
            'project': 'Triggered when a project is created, updated, or deleted',
            'project_card': 'Triggered when a project card is created, moved, or deleted',
            'workflow_call': 'Allows workflow to be called by another workflow',
        }

        # Handle simple string trigger
        if isinstance(on_section, str):
            desc = trigger_descriptions.get(on_section, default_descriptions.get(on_section, 'Triggers the workflow'))
            triggers.append({
                'event_type': on_section,
                'filters': {},
                'description': desc
            })
        # Handle dictionary of triggers
        elif isinstance(on_section, dict):
            for event_type, config in on_section.items():
                desc = trigger_descriptions.get(event_type, default_descriptions.get(event_type, f"Triggered by {event_type} events"))

                # Extract filters for better descriptions
                filters = {}
                if isinstance(config, dict):
                    # Only collect known filter keys
                    for filter_key in ["branches", "branches-ignore", "paths", "paths-ignore", "types", "tags", "tags-ignore", "inputs", "schedule", "workflow_dispatch"]:
                        if filter_key in config:
                            filters[filter_key] = config[filter_key]
                # Handle workflow_dispatch, which might have inputs
                if event_type == 'workflow_dispatch':
                    triggers.append({
                        'event_type': event_type,
                        'filters': filters,
                        'inputs': config.get('inputs', {}) if isinstance(config, dict) else {},
                        'description': desc
                    })
                # Handle other events with filters
                else:
                    triggers.append({
                        'event_type': event_type,
                        'filters': filters,
                        'description': desc
                    })
        # Handle list of triggers
        elif isinstance(on_section, list):
            for event_type in on_section:
                desc = trigger_descriptions.get(event_type, default_descriptions.get(event_type, f"Triggered by {event_type} events"))
                triggers.append({
                    'event_type': event_type,
                    'filters': {},
                    'description': desc
                })

        return triggers

    def _extract_inputs(self) -> List[Dict[str, Any]]:
        """Extract workflow inputs."""
        inputs = []

        # Workflow-level inputs
        workflow_inputs = self.yaml_content.get('inputs', {})
        for name, config in workflow_inputs.items():
            inputs.append({
                'name': name,
                'description': config.get('description', ''),
                'required': config.get('required', False),
                'default': config.get('default', ''),
                'type': config.get('type', 'string')
            })

        # Also check workflow_dispatch inputs
        on_section = self.yaml_content.get('on', {})
        if isinstance(on_section, dict) and 'workflow_dispatch' in on_section:
            workflow_dispatch = on_section['workflow_dispatch']
            if isinstance(workflow_dispatch, dict) and 'inputs' in workflow_dispatch:
                for name, config in workflow_dispatch['inputs'].items():
                    # Check if this input is already added
                    if not any(i['name'] == name for i in inputs):
                        inputs.append({
                            'name': name,
                            'description': config.get('description', ''),
                            'required': config.get('required', False),
                            'default': config.get('default', ''),
                            'type': config.get('type', 'string')
                        })

        return inputs

    def _extract_environment_variables(self) -> Dict[str, str]:
        """Extract environment variables."""
        env_vars = {}

        # Workflow-level env
        workflow_env = self.yaml_content.get('env', {})
        for name, value in workflow_env.items():
            env_vars[name] = str(value)

        return env_vars

    def _extract_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Extract jobs from the workflow."""
        jobs_data = {}
        jobs_section = self.yaml_content.get('jobs', {})

        for job_id, job_config in jobs_section.items():
            # Check if this is a call to a reusable workflow
            if 'uses' in job_config:
                jobs_data[job_id] = {
                    'id': job_id,
                    'name': job_config.get('name', job_id),
                    'uses': job_config.get('uses', ''),
                    'with': job_config.get('with', {}),
                    'secrets': job_config.get('secrets', {}),
                    'if_condition': job_config.get('if', ''),
                    'needs': job_config.get('needs', []),
                    'is_reusable_workflow': True
                }
            # Regular job
            else:
                jobs_data[job_id] = {
                    'id': job_id,
                    'name': job_config.get('name', job_id),
                    'runs_on': job_config.get('runs-on', ''),
                    'if_condition': job_config.get('if', ''),
                    'needs': job_config.get('needs', []),
                    'steps': self._extract_steps(job_config.get('steps', [])),
                    'outputs': job_config.get('outputs', {}),
                    'env': job_config.get('env', {}),
                    'is_reusable_workflow': False
                }

                # Handle matrix strategy
                if 'strategy' in job_config:
                    jobs_data[job_id]['strategy'] = {
                        'matrix': job_config.get('strategy', {}).get('matrix', {}),
                        'fail_fast': job_config.get('strategy', {}).get('fail-fast', True),
                        'max_parallel': job_config.get('strategy', {}).get('max-parallel', None)
                    }

        return jobs_data

    def _extract_steps(self, steps_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract steps from a job."""
        steps_data = []

        for step in steps_list:
            step_data = {
                'name': step.get('name', ''),
                'if_condition': step.get('if', ''),
                'env': step.get('env', {})
            }

            if 'uses' in step:
                step_data['uses'] = step['uses']
                step_data['with'] = step.get('with', {})
                step_data['is_action'] = True
            elif 'run' in step:
                step_data['run'] = step['run']
                step_data['shell'] = step.get('shell', '')
                step_data['is_action'] = False

            steps_data.append(step_data)

        return steps_data

    def _extract_concurrency(self) -> Dict[str, Any]:
        """Extract concurrency configuration."""
        concurrency = self.yaml_content.get('concurrency', {})

        if isinstance(concurrency, dict):
            return {
                'group': concurrency.get('group', ''),
                'cancel_in_progress': concurrency.get('cancel-in-progress', False)
            }
        elif isinstance(concurrency, str):
            return {
                'group': concurrency,
                'cancel_in_progress': False
            }
        else:
            return {}
