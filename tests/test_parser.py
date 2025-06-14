#!/usr/bin/env python3
"""
Unit tests for the workflow parser module.
"""

import os
import sys
import unittest
from unittest.mock import patch, mock_open

# Add parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser import WorkflowParser


class TestWorkflowParser(unittest.TestCase):
    """Test cases for the WorkflowParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_workflow = """
name: Test Workflow

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'dev'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Run tests
        run: pytest
"""

    def test_parse_workflow(self):
        """Test parsing a workflow file."""
        # Use a more direct approach to patching the file read operation
        with patch("builtins.open", mock_open(read_data=self.sample_workflow)):
            parser = WorkflowParser("test_workflow.yml")
            result = parser.parse()

            # Check workflow name
            self.assertEqual(result['name'], "Test Workflow")

            # Basic structure checks
            self.assertIn('jobs', result)
            self.assertIn('file_path', result)
            self.assertEqual(result['file_path'], "test_workflow.yml")

    def test_extract_annotations(self):
        """Test extracting annotations from comments."""
        workflow_with_annotations = """
# @description: This is a test workflow
# @author: Test Author
# @version: 1.0.0
name: Test Workflow
"""

        with patch("builtins.open", new_callable=mock_open, read_data=workflow_with_annotations):
            parser = WorkflowParser("test_workflow.yml")
            parser.raw_content = workflow_with_annotations
            annotations = parser._extract_annotations()

            self.assertEqual(annotations['description'], 'This is a test workflow')
            self.assertEqual(annotations['author'], 'Test Author')
            self.assertEqual(annotations['version'], '1.0.0')


if __name__ == '__main__':
    unittest.main()
