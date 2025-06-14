#!/usr/bin/env python3
"""
Unit tests for the documentation generator module.
"""

import os
import sys
import unittest
from unittest.mock import patch, mock_open

# Add parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generator import DocumentationGenerator


class TestDocumentationGenerator(unittest.TestCase):
    """Test cases for the DocumentationGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflow_data = {
            'file_path': 'test_workflow.yml',
            'name': 'Test Workflow',
            'description': 'A test workflow for unit testing',
            'triggers': [
                {
                    'event_type': 'push',
                    'filters': {'branches': ['main']}
                },
                {
                    'event_type': 'pull_request',
                    'filters': {'branches': ['main']}
                }
            ],
            'inputs': [
                {
                    'name': 'environment',
                    'description': 'Target environment',
                    'required': True,
                    'default': 'dev',
                    'type': 'string'
                }
            ],
            'env': {
                'NODE_ENV': 'production'
            },
            'jobs': {
                'job1': {
                    'id': 'job1',
                    'name': 'Build',
                    'runs_on': 'ubuntu-latest',
                    'steps': [
                        {'name': 'Checkout', 'uses': 'actions/checkout@v3'},
                        {'name': 'Build', 'run': 'npm build'}
                    ]
                },
                'job2': {
                    'id': 'job2',
                    'name': 'Deploy',
                    'runs_on': 'ubuntu-latest',
                    'needs': ['job1'],
                    'steps': [
                        {'name': 'Deploy', 'run': 'npm deploy'}
                    ]
                }
            },
            'diagram_path': 'test_diagram.png'
        }

        self.generator = DocumentationGenerator(self.workflow_data, format='markdown')

    @patch("builtins.open", new_callable=mock_open)
    def test_generate_markdown(self, mock_file):
        """Test generating markdown documentation."""
        self.generator.generate("test_output.md")

        # Check that the file was written
        mock_file.assert_called_once_with("test_output.md", 'w')

        # Get the written content
        content = ''.join(call_args[0][0] for call_args in mock_file().write.call_args_list)

        # Check some expected content
        self.assertIn("# GitHub Actions Workflow: Test Workflow", content)
        self.assertIn("A test workflow for unit testing", content)
        self.assertIn("## Triggers", content)
        self.assertIn("| `push` |", content)
        self.assertIn("| `pull_request` |", content)
        self.assertIn("## Inputs", content)
        self.assertIn("| `environment` |", content)
        self.assertIn("## Jobs", content)
        self.assertIn("### Build", content)
        self.assertIn("### Deploy", content)

    @patch("builtins.open", new_callable=mock_open)
    def test_generate_html(self, mock_file):
        """Test generating HTML documentation."""
        generator = DocumentationGenerator(self.workflow_data, format='html')
        generator.generate("test_output.html")

        # Check that the file was written
        mock_file.assert_called_once_with("test_output.html", 'w')

        # Get the written content
        content = ''.join(call_args[0][0] for call_args in mock_file().write.call_args_list)

        # Check some expected content
        self.assertIn("<html", content)
        self.assertIn("<title>Test Workflow</title>", content)
        # Our current implementation just wraps markdown in pre tags
        self.assertIn("<pre># GitHub Actions Workflow: Test Workflow", content)


if __name__ == '__main__':
    unittest.main()
