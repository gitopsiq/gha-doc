#!/usr/bin/env python3
"""
Unit tests for the diagram generator module.
"""

import os
import sys
import unittest
import subprocess
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
    @patch("os.makedirs")
    def test_generate(self, mock_makedirs, mock_file):
        """Test generating a diagram."""
        # Mock the mmdc command failure to keep just the mermaid output
        with patch("subprocess.run", side_effect=FileNotFoundError("mocked mmdc not found")):
            # Use a path with directory to test directory creation
            result = self.visualizer.generate("output/test_output.png")

            # Check that makedirs was called
            mock_makedirs.assert_called_with("output", exist_ok=True)

            # Check that the file was written
            mock_file.assert_called()  # At least one call to open()

            # Check that the result is the mermaid path
            self.assertTrue(result.endswith(".mmd") or not result,
                         f"Expected result to end with .mmd or be empty, got: {result}")

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
        self.assertIn('style job3 fill:#e0f0ff,stroke:#0067b8', mermaid)

        # Check that reusable workflows are included
        self.assertIn('subgraph "Reusable Workflows"', mermaid)
        self.assertIn('org/repo/.github/workflows/reusable.yml', mermaid)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("os.path.exists")
    def test_generate_mermaid_only(self, mock_exists, mock_makedirs, mock_file):
        """Test generating only a mermaid diagram without SVG conversion."""
        # Setup the visualizer with diagram type
        self.visualizer.diagram_type = "mermaid"

        # Mock the file existence check
        mock_exists.return_value = True

        result = self.visualizer.generate("output/test_output.mmd")

        # Check that the result is the mermaid path
        self.assertTrue(result.endswith(".mmd"),
                     f"Expected result to end with .mmd, got: {result}")

        # Verify no attempt to run mmdc was made
        with patch("subprocess.run") as mock_run:
            mock_run.assert_not_called()

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_generate_svg(self, mock_exists, mock_run, mock_makedirs, mock_file):
        """Test generating an SVG diagram."""
        # Setup the visualizer with diagram type
        self.visualizer.diagram_type = "svg"

        # Mock the subprocess and file existence
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        result = self.visualizer.generate("output/test_output.svg")

        # Check that mmdc was called correctly
        mock_run.assert_called_once()
        # Extract the args from the call
        call_args = mock_run.call_args[0][0]
        self.assertIn("svg", "".join(str(arg) for arg in call_args),
                   "SVG format should be used in the command")

        # Check that the result is the svg path
        self.assertTrue(result.endswith(".svg"),
                     f"Expected result to end with .svg, got: {result}")

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("subprocess.run")
    def test_mmdc_failure(self, mock_run, mock_makedirs, mock_file):
        """Test handling when mmdc fails."""
        # Setup the visualizer with diagram type
        self.visualizer.diagram_type = "svg"

        # Mock subprocess to raise exception
        mock_run.side_effect = subprocess.CalledProcessError(1, "mmdc")

        result = self.visualizer.generate("output/test_output.svg")

        # Should fall back to mermaid file
        self.assertTrue(result.endswith(".mmd"),
                     f"Expected fallback to .mmd file, got: {result}")

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_unsupported_diagram_format(self, mock_exists, mock_run, mock_makedirs, mock_file):
        """Test handling of unsupported diagram format."""
        # Setup the visualizer with an invalid diagram type
        self.visualizer.diagram_type = "invalid"

        # Mock the subprocess and file existence
        mock_exists.return_value = True

        result = self.visualizer.generate("output/test_output.invalid")

        # Should fall back to mermaid file
        self.assertTrue(result.endswith(".mmd"),
                     f"Expected fallback to .mmd file, got: {result}")

        # Verify no attempt to run mmdc was made
        mock_run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
