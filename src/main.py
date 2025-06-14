#!/usr/bin/env python3
"""
GitHub Actions Documentation Generator (gha-doc)

This tool automatically generates comprehensive documentation for GitHub Actions workflows.
It analyzes workflow files, extracts metadata, creates visual diagrams,
and produces standardized documentation in various formats.
"""

import os
import sys
import glob
import argparse
from pathlib import Path

# Import local modules
from parser import WorkflowParser
from analyzer import WorkflowAnalyzer
from generator import DocumentationGenerator
from visualizer import DiagramGenerator
from ai_enhancer import AIEnhancer

def parse_args():
    """Parse command line arguments or read from environment variables."""
    parser = argparse.ArgumentParser(description="GitHub Actions Documentation Generator")

    # Check if running as GitHub Action or CLI
    is_github_action = os.environ.get("GITHUB_ACTION") is not None

    if is_github_action:
        # Read from environment variables set by the GitHub Action
        workflow_files = os.environ.get("INPUT_WORKFLOW_FILES", ".github/workflows/*.yml")
        output_dir = os.environ.get("INPUT_OUTPUT_DIR", "docs/workflows")
        format_type = os.environ.get("INPUT_FORMAT", "markdown")
        generate_diagrams = os.environ.get("INPUT_GENERATE_DIAGRAMS", "true").lower() == "true"
        include_source = os.environ.get("INPUT_INCLUDE_SOURCE", "false").lower() == "true"
        ai_enhancement = os.environ.get("INPUT_AI_ENHANCEMENT", "false").lower() == "true"
        ai_api_key = os.environ.get("INPUT_AI_API_KEY", "")
        workspace = os.environ.get("GITHUB_WORKSPACE", ".")
    else:
        # Parse command line arguments
        parser.add_argument("--workflow-files", default=".github/workflows/*.yml",
                            help="Glob pattern for workflow files to document")
        parser.add_argument("--output-dir", default="docs/workflows",
                            help="Directory to write documentation to")
        parser.add_argument("--format", default="markdown", choices=["markdown", "html"],
                            help="Output format (markdown, html)")
        parser.add_argument("--generate-diagrams", action="store_true", default=True,
                            help="Generate diagrams")
        parser.add_argument("--include-source", action="store_true", default=False,
                            help="Include source code in documentation")
        parser.add_argument("--ai-enhancement", action="store_true", default=False,
                            help="Enable AI-powered enhancements")
        parser.add_argument("--ai-api-key", default="",
                            help="API key for AI service")
        parser.add_argument("--workspace", default=".",
                            help="Workspace directory")

        args = parser.parse_args()
        workflow_files = args.workflow_files
        output_dir = args.output_dir
        format_type = args.format
        generate_diagrams = args.generate_diagrams
        include_source = args.include_source
        ai_enhancement = args.ai_enhancement
        ai_api_key = args.ai_api_key
        workspace = args.workspace

    return {
        "workflow_files": workflow_files,
        "output_dir": output_dir,
        "format": format_type,
        "generate_diagrams": generate_diagrams,
        "include_source": include_source,
        "ai_enhancement": ai_enhancement,
        "ai_api_key": ai_api_key,
        "workspace": workspace
    }

def main():
    """Main entry point for the GitHub Actions Documentation Generator."""
    print("GitHub Actions Documentation Generator")

    # Parse arguments
    config = parse_args()

    # Ensure output directory exists
    output_dir = os.path.join(config["workspace"], config["output_dir"])
    os.makedirs(output_dir, exist_ok=True)

    # Find workflow files
    workflow_pattern = os.path.join(config["workspace"], config["workflow_files"])
    workflow_files = glob.glob(workflow_pattern)

    if not workflow_files:
        print(f"No workflow files found matching pattern: {workflow_pattern}")
        return 1

    print(f"Found {len(workflow_files)} workflow files")

    # Process each workflow file
    for workflow_file in workflow_files:
        print(f"Processing {workflow_file}...")

        # Parse workflow file
        parser = WorkflowParser(workflow_file)
        workflow_data = parser.parse()

        # Analyze workflow structure
        analyzer = WorkflowAnalyzer(workflow_data)
        analyzed_workflow = analyzer.analyze()

        # Generate diagrams if requested
        if config["generate_diagrams"]:
            visualizer = DiagramGenerator(analyzed_workflow)
            diagram_path = os.path.join(output_dir, f"{Path(workflow_file).stem}-diagram.png")
            visualizer.generate(diagram_path)
            analyzed_workflow['diagram_path'] = diagram_path

        # Enhance with AI if enabled
        if config["ai_enhancement"] and config["ai_api_key"]:
            enhancer = AIEnhancer(analyzed_workflow, api_key=config["ai_api_key"])
            enhanced_workflow = enhancer.enhance()
        else:
            enhanced_workflow = analyzed_workflow

        # Generate documentation
        generator = DocumentationGenerator(enhanced_workflow,
                                          format=config["format"],
                                          include_source=config["include_source"])

        output_file = os.path.join(output_dir, f"{Path(workflow_file).stem}.md")
        if config["format"] == "html":
            output_file = os.path.join(output_dir, f"{Path(workflow_file).stem}.html")

        generator.generate(output_file)
        print(f"Documentation generated: {output_file}")

    print(f"Documentation generation complete. Files written to {output_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
