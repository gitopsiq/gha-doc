import unittest
from unittest.mock import patch
import os

from src.main import build_workflow_call_graph, find_roots_and_orphans, collect_all_called

class TestWorkflowConsolidation(unittest.TestCase):
    def setUp(self):
        # Simulate three workflows: root, mid, leaf
        self.workspace = "/tmp"
        self.root_wf = "/repo/.github/workflows/root.yml"
        self.mid_wf = "/repo/.github/workflows/mid.yml"
        self.leaf_wf = "/repo/.github/workflows/leaf.yml"
        self.files = [self.root_wf, self.mid_wf, self.leaf_wf]

        # Patch parse_workflow_file to simulate call structure
        self.parse_patch = patch("src.main.parse_workflow_file")
        self.mock_parse = self.parse_patch.start()
        self.mock_parse.side_effect = lambda path, ws: {
            self.root_wf: {'yaml_content': {'jobs': {'call_mid': {'uses': './mid.yml'}}}},
            self.mid_wf: {'yaml_content': {'jobs': {'call_leaf': {'uses': './leaf.yml'}}}},
            self.leaf_wf: {'yaml_content': {'jobs': {}}}
        }[path]

    def tearDown(self):
        self.parse_patch.stop()

    def test_call_graph_and_roots(self):
        parsed, call_graph = build_workflow_call_graph(self.files, self.workspace)
        roots, orphans = find_roots_and_orphans(call_graph, self.files)
        self.assertIn(self.root_wf, roots)
        self.assertNotIn(self.mid_wf, roots)
        self.assertNotIn(self.leaf_wf, roots)
        self.assertEqual(orphans, [])

    def test_collect_all_called(self):
        parsed, call_graph = build_workflow_call_graph(self.files, self.workspace)
        all_called = collect_all_called(self.root_wf, call_graph)
        self.assertIn(self.mid_wf, all_called)
        self.assertIn(self.leaf_wf, all_called)

if __name__ == "__main__":
    unittest.main()
