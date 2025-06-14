#!/usr/bin/env python3
"""
Unit tests for the diagram generator module.
"""

import os
import sys
import unittest
from unittest.mock import patch, mock_open, MagicMock

# Add parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.visualizer import DiagramGenerator


class TestDiagramGenerator(unittest.TestCase):
    """Test cases for the DiagramGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflow_data = {
            'name': 'Test Workflow',
            'jobs': {
                'job1': {
                    'id': 'job1',
                    'name': 'First Job',
                    'is_reusable_workflow': False,
                    'strategy': {}
                },
                'job2': {
                    'id': 'job2',
                    'name': 'Second Job',
                    'is_reusable_workflow': False,
                    'strategy': {'matrix': {'os': ['ubuntu', 'windows']}}
                },
                'job3': {
                    'id': 'job3',
                    'name': 'Reusable Job',
                    'is_reusable_workflow': True,
                    'strategy': {}
                }
            },
            'job_dependencies': {
                'job1': [],
                'job2': ['job1'],
                'job3': ['job2']
            },
            'workflow_calls': [
                {
                    'job_id': 'job3',
                    'workflow_path': 'org/repo/.github/workflows/reusable.yml'
                }
            ],
            'conditional_paths': {
                'jobs': [
                    {
                        'job_id': 'job3',
                        'condition': 'github.ref == "refs/heads/main"'
                    }
                ],
                'steps': {}
            }
        }

        self.visualizer = DiagramGenerator(self.workflow_data)

    @patch("builtins.open", new_callable=mock_open)
    def test_generate(self, mock_file):
        """Test generating a diagram."""
        result = self.visualizer.generate("test_output.png")

        # Check that the file was written
        mock_file.assert_called_once()

        # Check that the result is the mermaid path
        self.assertTrue(result.endswith(".mmd"))

    def test_create_mermaid_diagram(self):
        """Test creating a mermaid diagram definition."""
        mermaid = self.visualizer._create_mermaid_diagram()

        # Check that the diagram includes all jobs
        self.assertIn('job1["First Job"]', mermaid)
        self.assertIn('job2["Second Job (Matrix)"]', mermaid)
        self.assertIn('job3["Reusable Job (Reusable)"]', mermaid)

        # Check that dependencies are included
        self.assertIn('job1 --> job2', mermaid)
        self.assertIn('job2 --> job3', mermaid)

        # Check that conditional jobs are styled
        self.assertIn('style job3 fill:#f9f', mermaid)

        # Check that reusable workflows are included
        self.assertIn('subgraph "Reusable Workflows"', mermaid)
        self.assertIn('org/repo/.github/workflows/reusable.yml', mermaid)


if __name__ == '__main__':
    unittest.main()
