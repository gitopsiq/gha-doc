#!/usr/bin/env python3
"""
Workflow Analyzer Module

Analyzes parsed workflow data to identify structure, dependencies, and patterns.
"""

import os
from typing import Dict, List, Any, Set, Tuple

class WorkflowAnalyzer:
    """Analyzer for GitHub Actions workflow structures."""

    def __init__(self, workflow_data: Dict[str, Any]):
        """Initialize with parsed workflow data."""
        self.workflow_data = workflow_data

    def analyze(self) -> Dict[str, Any]:
        """Analyze workflow structure and identify patterns."""
        analyzed_data = self.workflow_data.copy()

        # Add analysis data
        analyzed_data.update({
            'job_dependencies': self._analyze_job_dependencies(),
            'workflow_calls': self._analyze_workflow_calls(),
            'action_usage': self._analyze_action_usage(),
            'conditional_paths': self._analyze_conditional_paths(),
            'matrix_usage': self._analyze_matrix_usage(),
            'execution_flow': self._generate_execution_flow(),
            'env_requirements': self._analyze_env_requirements(),
            'permission_usage': self._analyze_permission_usage(),
            'complexity_metrics': self._calculate_complexity_metrics()
        })

        return analyzed_data

    def _analyze_job_dependencies(self) -> Dict[str, List[str]]:
        """Analyze job dependencies and create a dependency map."""
        dependencies = {}

        for job_id, job_data in self.workflow_data['jobs'].items():
            needs = job_data.get('needs', [])

            # Handle both string and list formats for 'needs'
            if isinstance(needs, str):
                dependencies[job_id] = [needs]
            elif isinstance(needs, list):
                dependencies[job_id] = needs
            else:
                dependencies[job_id] = []

        return dependencies

    def _analyze_workflow_calls(self) -> List[Dict[str, Any]]:
        """Identify calls to reusable workflows."""
        workflow_calls = []

        for job_id, job_data in self.workflow_data['jobs'].items():
            if 'uses' in job_data and not job_data['uses'].startswith('actions/'):
                workflow_calls.append({
                    'job_id': job_id,
                    'workflow_path': job_data['uses'],
                    'inputs': job_data.get('with', {}),
                    'secrets': job_data.get('secrets', {}),
                    'condition': job_data.get('if_condition', '')
                })

        return workflow_calls

    def _analyze_action_usage(self) -> Dict[str, int]:
        """Count usage of various actions in the workflow."""
        action_counts = {}

        for job_id, job_data in self.workflow_data['jobs'].items():
            if not job_data.get('is_reusable_workflow', False):
                for step in job_data.get('steps', []):
                    if 'uses' in step:
                        action_name = step['uses'].split('@')[0]
                        action_counts[action_name] = action_counts.get(action_name, 0) + 1

        return action_counts

    def _analyze_conditional_paths(self) -> Dict[str, List[str]]:
        """Identify conditional execution paths in the workflow."""
        conditional_paths = {
            'jobs': [],
            'steps': {}
        }

        # Check job-level conditions
        for job_id, job_data in self.workflow_data['jobs'].items():
            if job_data.get('if_condition'):
                conditional_paths['jobs'].append({
                    'job_id': job_id,
                    'condition': job_data['if_condition']
                })

        # Check step-level conditions
        for job_id, job_data in self.workflow_data['jobs'].items():
            conditional_steps = []
            for i, step in enumerate(job_data.get('steps', [])):
                if step.get('if_condition'):
                    conditional_steps.append({
                        'step_index': i,
                        'step_name': step.get('name', f"Step {i+1}"),
                        'condition': step['if_condition']
                    })

            if conditional_steps:
                conditional_paths['steps'][job_id] = conditional_steps

        return conditional_paths

    def _analyze_matrix_usage(self) -> Dict[str, Any]:
        """Analyze matrix strategy usage in the workflow."""
        matrix_usage = {
            'jobs_with_matrix': [],
            'total_combinations': 0,
            'has_matrix': False
        }

        for job_id, job_data in self.workflow_data['jobs'].items():
            if 'strategy' in job_data and 'matrix' in job_data['strategy']:
                matrix = job_data['strategy']['matrix']
                combinations = 1

                # Calculate total combinations
                for key, values in matrix.items():
                    if isinstance(values, list):
                        combinations *= len(values)

                matrix_usage['jobs_with_matrix'].append({
                    'job_id': job_id,
                    'matrix_dimensions': list(matrix.keys()),
                    'combinations': combinations
                })

                matrix_usage['total_combinations'] += combinations
                matrix_usage['has_matrix'] = True

        return matrix_usage

    def _generate_execution_flow(self) -> List[List[str]]:
        """Generate a representation of the execution flow based on dependencies."""
        # Create a dependency graph
        graph = {job_id: set(deps) for job_id, deps in self._analyze_job_dependencies().items()}

        # Add jobs that are only dependencies and not defined at the top level
        all_deps = set()
        for deps in graph.values():
            all_deps.update(deps)

        for dep in all_deps:
            if dep not in graph:
                graph[dep] = set()

        # Generate levels (topological sort)
        remaining = set(graph.keys())
        levels = []

        while remaining:
            # Find jobs with no dependencies within remaining set
            level = {job for job in remaining if not any(dep in remaining for dep in graph[job])}

            # If we can't find any, there must be a cycle
            if not level:
                print("Warning: Dependency cycle detected in workflow jobs")
                level = {next(iter(remaining))}  # Just pick one to break the cycle

            levels.append(sorted(list(level)))
            remaining -= level

        return levels

    def _analyze_env_requirements(self) -> Dict[str, Set[str]]:
        """Analyze environment variables required by the workflow."""
        required_vars = set()
        secret_refs = set()
        context_refs = set()

        # Extract references to env, secrets, and contexts from the raw content
        raw_content = self.workflow_data.get('raw_content', '')

        # Look for ${{ env.VAR_NAME }} patterns
        import re
        env_pattern = r'\$\{\{\s*env\.([A-Za-z0-9_]+)\s*\}\}'
        for match in re.finditer(env_pattern, raw_content):
            required_vars.add(match.group(1))

        # Look for ${{ secrets.SECRET_NAME }} patterns
        secret_pattern = r'\$\{\{\s*secrets\.([A-Za-z0-9_]+)\s*\}\}'
        for match in re.finditer(secret_pattern, raw_content):
            secret_refs.add(match.group(1))

        # Look for ${{ github.X }}, ${{ runner.X }} etc.
        context_pattern = r'\$\{\{\s*([a-z]+)\.([A-Za-z0-9_]+)\s*\}\}'
        for match in re.finditer(context_pattern, raw_content):
            if match.group(1) not in ['env', 'secrets']:
                context_refs.add(f"{match.group(1)}.{match.group(2)}")

        return {
            'environment_variables': required_vars,
            'secrets': secret_refs,
            'contexts': context_refs
        }

    def _analyze_permission_usage(self) -> Dict[str, Any]:
        """Analyze permission usage in the workflow."""
        permissions = {
            'workflow_level': self.workflow_data.get('yaml_content', {}).get('permissions', {}),
            'job_level': {}
        }

        # Check job-level permissions
        for job_id, job_data in self.workflow_data['jobs'].items():
            job_permissions = self.workflow_data.get('yaml_content', {}).get('jobs', {}).get(job_id, {}).get('permissions')
            if job_permissions:
                permissions['job_level'][job_id] = job_permissions

        return permissions

    def _calculate_complexity_metrics(self) -> Dict[str, int]:
        """Calculate various complexity metrics for the workflow."""
        jobs_count = len(self.workflow_data['jobs'])

        # Count total steps
        total_steps = 0
        for job_data in self.workflow_data['jobs'].values():
            if not job_data.get('is_reusable_workflow', False):
                total_steps += len(job_data.get('steps', []))

        # Measure dependency complexity (average number of dependencies per job)
        dependencies = self._analyze_job_dependencies()
        total_dependencies = sum(len(deps) for deps in dependencies.values())
        avg_dependencies = total_dependencies / max(1, jobs_count)

        # Max dependency chain length
        levels = self._generate_execution_flow()
        max_chain = len(levels)

        return {
            'jobs_count': jobs_count,
            'total_steps': total_steps,
            'avg_steps_per_job': total_steps / max(1, jobs_count),
            'avg_dependencies': avg_dependencies,
            'max_chain_length': max_chain,
            'complexity_score': (jobs_count * 0.5) + (total_steps * 0.3) + (avg_dependencies * 2) + (max_chain * 1.5)
        }
