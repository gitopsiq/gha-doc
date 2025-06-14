#!/usr/bin/env python3
"""
Unit tests for the workflow analyzer module.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import WorkflowAnalyzer


class TestWorkflowAnalyzer(unittest.TestCase):
    """Test cases for the WorkflowAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflow_data = {
            'file_path': 'test_workflow.yml',
            'name': 'Test Workflow',
            'jobs': {
                'job1': {
                    'id': 'job1',
                    'name': 'First Job',
                    'runs_on': 'ubuntu-latest',
                    'steps': [
                        {'name': 'Checkout', 'uses': 'actions/checkout@v3'},
                        {'name': 'Setup Node', 'uses': 'actions/setup-node@v3'}
                    ]
                },
                'job2': {
                    'id': 'job2',
                    'name': 'Second Job',
                    'runs_on': 'ubuntu-latest',
                    'needs': ['job1'],
                    'steps': [
                        {'name': 'Run Tests', 'run': 'npm test'}
                    ]
                },
                'job3': {
                    'id': 'job3',
                    'name': 'Reusable Job',
                    'uses': 'org/repo/.github/workflows/reusable.yml',
                    'with': {'param1': 'value1'},
                    'needs': ['job2'],
                    'is_reusable_workflow': True
                }
            }
        }

        self.analyzer = WorkflowAnalyzer(self.workflow_data)

    def test_analyze_job_dependencies(self):
        """Test analyzing job dependencies."""
        dependencies = self.analyzer._analyze_job_dependencies()

        self.assertEqual(len(dependencies), 3)
        self.assertEqual(dependencies['job1'], [])
        self.assertEqual(dependencies['job2'], ['job1'])
        self.assertEqual(dependencies['job3'], ['job2'])

    def test_analyze_workflow_calls(self):
        """Test identifying calls to reusable workflows."""
        workflow_calls = self.analyzer._analyze_workflow_calls()

        self.assertEqual(len(workflow_calls), 1)
        self.assertEqual(workflow_calls[0]['job_id'], 'job3')
        self.assertEqual(workflow_calls[0]['workflow_path'], 'org/repo/.github/workflows/reusable.yml')
        self.assertEqual(workflow_calls[0]['inputs'], {'param1': 'value1'})

    def test_analyze_action_usage(self):
        """Test counting usage of various actions."""
        action_usage = self.analyzer._analyze_action_usage()

        self.assertEqual(action_usage['actions/checkout'], 1)
        self.assertEqual(action_usage['actions/setup-node'], 1)

    def test_analyze(self):
        """Test the complete analyze method."""
        result = self.analyzer.analyze()

        self.assertIn('job_dependencies', result)
        self.assertIn('workflow_calls', result)
        self.assertIn('action_usage', result)
        self.assertIn('conditional_paths', result)
        self.assertIn('matrix_usage', result)
        self.assertIn('execution_flow', result)


if __name__ == '__main__':
    unittest.main()
