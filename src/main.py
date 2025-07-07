#!/usr/bin/env python3
"""
GitHub Actions Documentation Generator (gha-doc)

This tool automatically generates comprehensive documentation for GitHub Actions workflows.
It analyzes workflow files, extracts metadata, generates diagrams,
and produces standardized documentation in various formats.

Enhanced version with improved AI integration, HTML rendering, and diagram generation.
"""

import os
import sys
import glob
import argparse
from pathlib import Path
import requests
import yaml
from collections import defaultdict

# Import local modules
from parser import WorkflowParser
from analyzer import WorkflowAnalyzer
from generator import DocumentationGenerator
from visualizer import DiagramGenerator
from ai_enhancer import AIEnhancer

# Make sure all arguments are displayed in help text
os.environ["COLUMNS"] = "120"
def parse_args():
    """Parse command line arguments or read from environment variables."""
    parser = argparse.ArgumentParser(
        description="GitHub Actions Documentation Generator",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=True
    )

    # Check if running as GitHub Action or CLI
    is_github_action = os.environ.get("GITHUB_ACTION") is not None

    if is_github_action:
        # Read from environment variables set by the GitHub Action
        workflow_files = os.environ.get("INPUT_WORKFLOW_FILES", ".github/workflows/*.yml")
        output_dir = os.environ.get("INPUT_OUTPUT_DIR", "docs/workflows")
        formats = os.environ.get("INPUT_FORMATS", "both")
        include_diagram_type = os.environ.get("INPUT_INCLUDE_DIAGRAM_TYPE", "mermaid")
        include_workflow_source = os.environ.get("INPUT_INCLUDE_WORKFLOW_SOURCE", "false").lower() == "true"
        include_ai_suggested_improvements = os.environ.get("INPUT_INCLUDE_AI_SUGGESTED_IMPROVEMENTS", "true").lower() == "true"
        include_ai_usage_information = os.environ.get("INPUT_INCLUDE_AI_USAGE_INFORMATION", "true").lower() == "true"
        ai_provider = os.environ.get("INPUT_AI_PROVIDER", "mock")
        workspace = os.environ.get("GITHUB_WORKSPACE", ".")
        deploy_to_github_pages = os.environ.get("INPUT_DEPLOY_TO_GITHUB_PAGES", "false").lower() == "true"

        # OpenAI specific settings
        openai_api_key = os.environ.get("INPUT_OPENAI_API_KEY", "")
        openai_model = os.environ.get("INPUT_OPENAI_MODEL", "gpt-3.5-turbo")

        # Azure OpenAI settings
        azure_openai_api_key = os.environ.get("INPUT_AZURE_OPENAI_API_KEY", "")
        azure_openai_endpoint = os.environ.get("INPUT_AZURE_OPENAI_ENDPOINT", "")
        azure_openai_deployment = os.environ.get("INPUT_AZURE_OPENAI_DEPLOYMENT", "")

        # Anthropic settings
        anthropic_api_key = os.environ.get("INPUT_ANTHROPIC_API_KEY", "")
        anthropic_model = os.environ.get("INPUT_ANTHROPIC_MODEL", "claude-2")

        # Hugging Face settings
        hf_api_key = os.environ.get("INPUT_HF_API_KEY", "")
        hf_model = os.environ.get("INPUT_HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")

        # Google AI settings
        google_api_key = os.environ.get("INPUT_GOOGLE_API_KEY", "")
        google_model = os.environ.get("INPUT_GOOGLE_MODEL", "gemini-1.0-pro")

        # AWS Bedrock settings
        aws_api_key = os.environ.get("INPUT_AWS_API_KEY", "")
        aws_secret_key = os.environ.get("INPUT_AWS_SECRET_KEY", "")
        aws_region = os.environ.get("INPUT_AWS_REGION", "us-east-1")
        aws_model = os.environ.get("INPUT_AWS_MODEL", "anthropic.claude-v2")

    else:
        # Parse command line arguments
        parser.add_argument("--workflow-files", default=".github/workflows/*.yml",
                            help="Glob pattern for workflow files to document")
        parser.add_argument("--output-dir", default="docs/workflows",
                            help="Directory to write documentation to")
        parser.add_argument("--formats", default="markdown,html", help="Comma-separated output formats (markdown, html). Default: both.")
        parser.add_argument("--include-diagram-type", default="mermaid", choices=["none", "mermaid", "svg", "png", "pdf"],
                            help="Type of diagram to include (none, mermaid, svg, png, pdf)")
        parser.add_argument("--include-workflow-source", action="store_true", default=False,
                            help="Include workflow source YAML in documentation")
        parser.add_argument("--include-ai-suggested-improvements", action="store_true", default=True,
                            help="Include AI-Generated Suggested Improvements in the documentation")
        parser.add_argument("--no-ai-suggested-improvements", dest="include_ai_suggested_improvements", action="store_false",
                            help="Don't include AI-Generated Suggested Improvements in the documentation")
        parser.add_argument("--include-ai-usage-information", action="store_true", default=True,
                            help="Include AI Usage Information in the documentation")
        parser.add_argument("--no-ai-usage-information", dest="include_ai_usage_information", action="store_false",
                            help="Don't include AI Usage Information in the documentation")
        parser.add_argument("--ai-provider", default="mock",
                            choices=["openai", "azure_openai", "anthropic", "hf", "google", "aws", "mock"],
                            help="AI provider to use")
        parser.add_argument("--workspace", default=".",
                            help="Workspace directory")
        parser.add_argument("--deploy-to-github-pages", action="store_true", default=False,
                            help="Deploy documentation to GitHub Pages")

        # OpenAI specific settings
        parser.add_argument("--openai-api-key", default="",
                            help="API key for OpenAI")
        parser.add_argument("--openai-model", default="gpt-3.5-turbo",
                            help="Model to use for OpenAI")

        # Azure OpenAI settings
        parser.add_argument("--azure-openai-api-key", default="",
                            help="API key for Azure OpenAI")
        parser.add_argument("--azure-openai-endpoint", default="",
                            help="Endpoint for Azure OpenAI")
        parser.add_argument("--azure-openai-deployment", default="",
                            help="Deployment name for Azure OpenAI")

        # Anthropic settings
        parser.add_argument("--anthropic-api-key", default="",
                            help="API key for Anthropic Claude")
        parser.add_argument("--anthropic-model", default="claude-2",
                            help="Model to use for Anthropic")

        # Hugging Face settings
        parser.add_argument("--hf-api-key", default="",
                            help="API key for Hugging Face")
        parser.add_argument("--hf-model", default="mistralai/Mistral-7B-Instruct-v0.1",
                            help="Model to use for Hugging Face")

        # Google AI settings
        parser.add_argument("--google-api-key", default="",
                            help="API key for Google AI")
        parser.add_argument("--google-model", default="gemini-1.0-pro",
                            help="Model to use for Google AI (e.g., gemini-1.0-pro)")

        # AWS Bedrock settings
        parser.add_argument("--aws-api-key", default="",
                            help="API key (Access Key ID) for AWS Bedrock")
        parser.add_argument("--aws-secret-key", default="",
                            help="Secret key (Secret Access Key) for AWS Bedrock")
        parser.add_argument("--aws-region", default="us-east-1",
                            help="AWS Region for Bedrock API")
        parser.add_argument("--aws-model", default="anthropic.claude-v2",
                            help="Model to use for AWS Bedrock (e.g., anthropic.claude-v2)")

        args = parser.parse_args()
        workflow_files = args.workflow_files
        output_dir = args.output_dir
        # Only allow 'markdown' and 'html' as valid formats
        valid_formats = {"markdown", "html"}
        formats = [f.strip() for f in args.formats.split(',') if f.strip() in valid_formats]
        if not formats:
            formats = ["markdown", "html"]  # Default to both if none valid
        include_diagram_type = args.include_diagram_type
        include_workflow_source = args.include_workflow_source
        include_ai_suggested_improvements = args.include_ai_suggested_improvements
        include_ai_usage_information = args.include_ai_usage_information
        ai_provider = args.ai_provider
        workspace = args.workspace
        deploy_to_github_pages = args.deploy_to_github_pages

        # OpenAI specific settings
        openai_api_key = args.openai_api_key
        openai_model = args.openai_model

        # Azure OpenAI settings
        azure_openai_api_key = args.azure_openai_api_key
        azure_openai_endpoint = args.azure_openai_endpoint
        azure_openai_deployment = args.azure_openai_deployment

        # Anthropic settings
        anthropic_api_key = args.anthropic_api_key
        anthropic_model = args.anthropic_model

        # Hugging Face settings
        hf_api_key = args.hf_api_key
        hf_model = args.hf_model

        # Google AI settings
        google_api_key = args.google_api_key
        google_model = args.google_model

        # AWS Bedrock settings
        aws_api_key = args.aws_api_key
        aws_secret_key = args.aws_secret_key
        aws_region = args.aws_region
        aws_model = args.aws_model

    # Determine if AI enhancements should be enabled
    ai_enhancement = (include_ai_suggested_improvements or include_ai_usage_information) and ai_provider != "mock"

    return {
        "workflow_files": workflow_files,
        "output_dir": output_dir,
        "formats": formats,
        "include_diagram_type": include_diagram_type,
        "include_workflow_source": include_workflow_source,
        "include_ai_suggested_improvements": include_ai_suggested_improvements,
        "include_ai_usage_information": include_ai_usage_information,
        "ai_provider": ai_provider,
        "workspace": workspace,
        "deploy_to_github_pages": deploy_to_github_pages,

        # Provider-specific settings
        "openai_api_key": openai_api_key,
        "openai_model": openai_model,
        "azure_openai_api_key": azure_openai_api_key,
        "azure_openai_endpoint": azure_openai_endpoint,
        "azure_openai_deployment": azure_openai_deployment,
        "anthropic_api_key": anthropic_api_key,
        "anthropic_model": anthropic_model,
        "hf_api_key": hf_api_key,
        "hf_model": hf_model,
        "google_api_key": google_api_key,
        "google_model": google_model,
        "aws_api_key": aws_api_key,
        "aws_secret_key": aws_secret_key,
        "aws_region": aws_region,
        "aws_model": aws_model
    }
def extract_called_workflows(parsed_data, workdir, current_workflow_path):
    """Extracts all called workflow paths (local and remote) from a parsed workflow data dict."""
    called = set()
    jobs = parsed_data.get('yaml_content', {}).get('jobs', {})
    current_workflow_dir = os.path.dirname(current_workflow_path)
    for job in jobs.values():
        uses = job.get('uses')
        if uses and uses.endswith('.yml'):
            # Remote reusable workflow: owner/repo/.github/workflows/filename.yml@ref
            if '/' in uses and uses.count('/') >= 3 and '@' in uses:
                repo_part, rest = uses.split('.github/workflows/', 1)
                repo = repo_part.rstrip('/').split('/')
                if len(repo) >= 2:
                    org, repo_name = repo[-2:]
                    file_and_ref = rest.split('@')
                    if len(file_and_ref) == 2:
                        file_path, ref = file_and_ref
                        called.add(f"remote::{org}/{repo_name}::.github/workflows/{file_path}@{ref}")
            elif uses.startswith('.github/workflows/') or uses.startswith('./.github/workflows/'):
                # Remove leading './' if present
                normalized = uses[2:] if uses.startswith('./') else uses
                called.add(os.path.normpath(os.path.join(workdir, normalized)))
            elif uses.startswith('./'):
                # Relative to current workflow file
                called.add(os.path.normpath(os.path.join(current_workflow_dir, uses)))
            else:
                # Fallback: treat as relative to workdir
                called.add(os.path.normpath(os.path.join(workdir, uses)))
    return called

def fetch_remote_workflow(org, repo, file_path, ref):
    """Fetch a remote workflow file from GitHub (raw.githubusercontent.com)."""
    url = f"https://raw.githubusercontent.com/{org}/{repo}/{ref}/{file_path}"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.text
    else:
        print(f"Warning: Could not fetch remote workflow {url} (status {resp.status_code})")
        return None

def parse_workflow_file(path, workdir):
    """Parse a workflow file, local or remote."""
    if path.startswith('remote::'):
        # Format: remote::org/repo::.github/workflows/xyz.yml@ref
        _, repo_part, file_and_ref = path.split('::')
        org, repo = repo_part.split('/')
        file_path, ref = file_and_ref.split('@')
        content = fetch_remote_workflow(org, repo, file_path, ref)
        if content:
            # Save to a temp file for parsing
            tmp_path = os.path.join(workdir, f"_temp_{org}_{repo}_{file_path.replace('/', '_')}")
            with open(tmp_path, 'w') as f:
                f.write(content)
            parser = WorkflowParser(tmp_path)
            return parser.parse()
        else:
            return None
    else:
        # Path should already be absolute at this point
        resolved_path = os.path.abspath(path)
        parser = WorkflowParser(resolved_path)
        return parser.parse()

def build_workflow_call_graph(workflow_files, workdir):
    """Builds a call graph and parses all workflows (local and remote)."""
    parsed = {}
    call_graph = defaultdict(set)
    for wf in workflow_files:
        parsed_data = parse_workflow_file(wf, workdir)
        if not parsed_data:
            continue
        parsed[wf] = parsed_data
        called = extract_called_workflows(parsed_data, workdir, wf)
        call_graph[wf].update(called)
    # Recursively parse all called workflows (up to 5 levels)
    for _ in range(5):
        new_calls = set()
        for wf in list(call_graph.keys()):  # Iterate over a static list of keys
            calls = call_graph[wf]
            for called in list(calls):
                if called not in parsed:
                    parsed_data = parse_workflow_file(called, workdir)
                    if parsed_data:
                        parsed[called] = parsed_data
                        new_called = extract_called_workflows(parsed_data, workdir, called)
                        call_graph[called].update(new_called)
                        new_calls.update(new_called)
        if not new_calls:
            break
    return parsed, call_graph

def find_roots_and_orphans(call_graph, workflow_files):
    """Find root workflows (not called by any other) and orphans (never called)."""
    all_called = set()
    for calls in call_graph.values():
        all_called.update(calls)
    roots = [wf for wf in workflow_files if wf not in all_called]
    orphans = [wf for wf in call_graph if wf not in all_called and wf not in roots]
    return roots, orphans

def collect_all_called(wf, call_graph, depth=0, max_depth=5, seen=None):
    if seen is None:
        seen = set()
    if depth > max_depth or wf in seen:
        return set()
    seen.add(wf)
    all_called = set()
    for called in call_graph.get(wf, []):
        all_called.add(called)
        all_called.update(collect_all_called(called, call_graph, depth+1, max_depth, seen))
    return all_called

def main():
    """Main entry point for the GitHub Actions Documentation Generator."""
    print("GitHub Actions Documentation Generator (Enhanced Version)")

    # Parse arguments
    config = parse_args()

    try:
        # Ensure output directory exists
        # Handle both absolute and relative paths for output directory
        if config["output_dir"].startswith('/'):
            # Absolute path
            output_dir = config["output_dir"]
        else:
            # Relative path - join with workspace
            output_dir = os.path.join(config["workspace"], config["output_dir"])

        os.makedirs(output_dir, exist_ok=True)

        # Find workflow files
        # Handle path resolution with special consideration for paths in Docker container
        if config["workflow_files"].startswith('/github/workspace/'):
            # Already has the full path in Docker container
            workflow_pattern = config["workflow_files"]
        elif config["workflow_files"].startswith('/'):
            # Other absolute path
            workflow_pattern = config["workflow_files"]
        else:
            # Relative path - join with workspace
            workflow_pattern = os.path.join(config["workspace"], config["workflow_files"])

        # Special handling for running in Docker
        if config["workspace"] == '/github/workspace' and not workflow_pattern.startswith('/github/workspace'):
            workflow_pattern = os.path.join('/github/workspace', config["workflow_files"].lstrip('./'))

        print(f"Looking for workflow files with pattern: {workflow_pattern}")
        workflow_files = glob.glob(workflow_pattern)

        if not workflow_files:
            print(f"No workflow files found matching pattern: {workflow_pattern}")
            return 1

        print(f"Found {len(workflow_files)} workflow files")

        # Build call graph and parse all workflows
        parsed, call_graph = build_workflow_call_graph(workflow_files, config["workspace"])
        roots, orphans = find_roots_and_orphans(call_graph, workflow_files)
        documented = set()
        # Generate consolidated docs for roots
        for root in roots:
            print(f"Processing consolidated doc for root workflow: {root}")
            all_called = collect_all_called(root, call_graph)
            all_workflows = [root] + list(all_called)
            # Merge all parsed data (simple: pass as context list, or merge jobs/triggers/etc.)
            # For now, just use root as main, but you can enhance merging logic as needed
            main_workflow = parsed[root]
            # Optionally, add info about included workflows
            main_workflow['included_workflows'] = [parsed[w] for w in all_called if w in parsed]
            # Analyze workflow structure
            analyzer = WorkflowAnalyzer(main_workflow)
            analyzed_workflow = analyzer.analyze()

            # Generate diagrams based on requested type
            if config["include_diagram_type"] != "none":
                visualizer = DiagramGenerator(analyzed_workflow, diagram_type=config["include_diagram_type"])
                diagram_path = os.path.join(output_dir, f"{Path(root).stem}-diagram")
                diagram_file = visualizer.generate(diagram_path)
                analyzed_workflow['diagram_path'] = diagram_file

            # Enhance with AI if enabled (provider is not mock and at least one AI feature is enabled)
            if config["ai_provider"] != "mock" and (config["include_ai_suggested_improvements"] or config["include_ai_usage_information"]):
                # Create API config with provider-specific settings
                api_config = {
                    "provider_type": config["ai_provider"]
                }

                # Get the API key based on the provider
                if config["ai_provider"] == "openai":
                    api_config["api_key"] = config["openai_api_key"]
                elif config["ai_provider"] == "azure_openai":
                    api_config["api_key"] = config["azure_openai_api_key"]
                elif config["ai_provider"] == "anthropic":
                    api_config["api_key"] = config["anthropic_api_key"]
                elif config["ai_provider"] == "hf":
                    api_config["api_key"] = config["hf_api_key"]
                elif config["ai_provider"] == "google":
                    api_config["api_key"] = config["google_api_key"]
                elif config["ai_provider"] == "aws":
                    api_config["api_key"] = config["aws_api_key"]

                # Add provider-specific settings
                if config["ai_provider"] == "openai":
                    api_config["model"] = config["openai_model"]
                elif config["ai_provider"] == "azure_openai":
                    api_config["endpoint"] = config["azure_openai_endpoint"]
                    api_config["deployment_name"] = config["azure_openai_deployment"]
                elif config["ai_provider"] == "anthropic":
                    api_config["model"] = config["anthropic_model"]
                elif config["ai_provider"] == "hf":
                    api_config["model"] = config["hf_model"]
                elif config["ai_provider"] == "google":
                    api_config["model"] = config["google_model"]
                elif config["ai_provider"] == "aws":
                    api_config["model"] = config["aws_model"]
                    api_config["secret_key"] = config["aws_secret_key"]
                    api_config["region"] = config["aws_region"]

                enhancer = AIEnhancer(analyzed_workflow, api_config)
                enhanced_workflow = enhancer.enhance()
                print(f"[AI DEBUG] Using provider: {config['ai_provider']}")
                if config['ai_provider'] == 'mock' or not api_config.get('api_key'):
                    print("[AI DEBUG] (Fallback to mock or missing API key)")
            else:
                enhanced_workflow = analyzed_workflow

            # Check if we have AI enhancement data
            has_ai_data = 'ai_enhancement' in enhanced_workflow

            # Generate documentation in all requested formats
            for fmt in config["formats"]:
                generator = DocumentationGenerator(enhanced_workflow,
                                               format=fmt,
                                               include_workflow_source=config["include_workflow_source"],
                                               include_mermaid_syntax=(config["include_diagram_type"] == "mermaid"),
                                               include_ai_suggested_improvements=has_ai_data and config["include_ai_suggested_improvements"],
                                               include_ai_usage_information=has_ai_data and config["include_ai_usage_information"])
                if fmt == "html":
                    output_file = os.path.join(output_dir, f"{Path(root).stem}.html")
                else:
                    output_file = os.path.join(output_dir, f"{Path(root).stem}.md")
                generator.generate(output_file)
                display_path = output_file
                if display_path.startswith('/github/workspace/'):
                    display_path = display_path[len('/github/workspace/'):]
                print(f"Documentation generated: {display_path}")
            documented.update(all_workflows)
            documented.add(root)
        # Generate docs for orphan reusable workflows
        for orphan in orphans:
            if orphan in documented:
                continue
            print(f"Processing orphan reusable workflow: {orphan}")
            main_workflow = parsed[orphan]
            analyzer = WorkflowAnalyzer(main_workflow)
            analyzed_workflow = analyzer.analyze()
            if config["include_diagram_type"] != "none":
                visualizer = DiagramGenerator(analyzed_workflow, diagram_type=config["include_diagram_type"])
                diagram_path = os.path.join(output_dir, f"{Path(orphan).stem}-diagram")
                diagram_file = visualizer.generate(diagram_path)
                analyzed_workflow['diagram_path'] = diagram_file
            if config["ai_provider"] != "mock" and (config["include_ai_suggested_improvements"] or config["include_ai_usage_information"]):
                api_config = {"provider_type": config["ai_provider"]}
                if config["ai_provider"] == "openai":
                    api_config["api_key"] = config["openai_api_key"]
                    api_config["model"] = config["openai_model"]
                elif config["ai_provider"] == "azure_openai":
                    api_config["api_key"] = config["azure_openai_api_key"]
                    api_config["endpoint"] = config["azure_openai_endpoint"]
                    api_config["deployment_name"] = config["azure_openai_deployment"]
                elif config["ai_provider"] == "anthropic":
                    api_config["api_key"] = config["anthropic_api_key"]
                    api_config["model"] = config["anthropic_model"]
                elif config["ai_provider"] == "hf":
                    api_config["api_key"] = config["hf_api_key"]
                    api_config["model"] = config["hf_model"]
                elif config["ai_provider"] == "google":
                    api_config["api_key"] = config["google_api_key"]
                    api_config["model"] = config["google_model"]
                elif config["ai_provider"] == "aws":
                    api_config["api_key"] = config["aws_api_key"]
                    api_config["secret_key"] = config["aws_secret_key"]
                    api_config["region"] = config["aws_region"]
                    api_config["model"] = config["aws_model"]
                enhancer = AIEnhancer(analyzed_workflow, api_config)
                enhanced_workflow = enhancer.enhance()
                print(f"[AI DEBUG] Using provider: {config['ai_provider']}")
                if config['ai_provider'] == 'mock' or not api_config.get('api_key'):
                    print("[AI DEBUG] (Fallback to mock or missing API key)")
            else:
                enhanced_workflow = analyzed_workflow
            has_ai_data = 'ai_enhancement' in enhanced_workflow
            for fmt in config["formats"]:
                generator = DocumentationGenerator(enhanced_workflow,
                                               format=fmt,
                                               include_workflow_source=config["include_workflow_source"],
                                               include_mermaid_syntax=(config["include_diagram_type"] == "mermaid"),
                                               include_ai_suggested_improvements=has_ai_data and config["include_ai_suggested_improvements"],
                                               include_ai_usage_information=has_ai_data and config["include_ai_usage_information"])
                if fmt == "html":
                    output_file = os.path.join(output_dir, f"{Path(orphan).stem}.html")
                else:
                    output_file = os.path.join(output_dir, f"{Path(orphan).stem}.md")
                generator.generate(output_file)
                display_path = output_file
                if display_path.startswith('/github/workspace/'):
                    display_path = display_path[len('/github/workspace/'):]
                print(f"Documentation generated: {display_path}")
        print(f"Documentation generation complete. Files written to {output_dir}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
