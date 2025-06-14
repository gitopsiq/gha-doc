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

            # Parse YAML content
            self.yaml_content = yaml.safe_load(self.raw_content)

            # Extract documentation annotations from comments
            doc_annotations = self._extract_annotations()

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

        # Handle simple string trigger
        if isinstance(on_section, str):
            triggers.append({
                'event_type': on_section,
                'filters': {}
            })
        # Handle dictionary of triggers
        elif isinstance(on_section, dict):
            for event_type, config in on_section.items():
                # Handle workflow_dispatch, which might have inputs
                if event_type == 'workflow_dispatch':
                    triggers.append({
                        'event_type': event_type,
                        'filters': {},
                        'inputs': config.get('inputs', {}) if isinstance(config, dict) else {}
                    })
                # Handle other events with filters
                else:
                    triggers.append({
                        'event_type': event_type,
                        'filters': config if isinstance(config, dict) else {}
                    })
        # Handle list of triggers
        elif isinstance(on_section, list):
            for event_type in on_section:
                triggers.append({
                    'event_type': event_type,
                    'filters': {}
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
