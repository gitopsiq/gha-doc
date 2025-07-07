# GitHub Actions Documentation Generator (gha-doc)

<div align="center">
  <img src="https://via.placeholder.com/800x200/0067b8/ffffff?text=GitHub+Actions+Documentation+Generator" alt="gha-doc Banner">
</div>

## Overview

`gha-doc` is a composite GitHub Action that automatically generates comprehensive documentation for GitHub Actions workflows in your repository. The tool analyzes workflow files, extracts metadata, generates visual diagrams, and produces standardized documentation in markdown or HTML formats.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions Marketplace](https://img.shields.io/badge/GitHub%20Actions-Marketplace-blue)](https://github.com/marketplace/actions/github-actions-documentation-generator)

## Features

- **Workflow Analysis:** Parse and analyze GitHub Actions workflow YAML files
- **Standardized Documentation:** Generate consistent, high-quality documentation
- **Visual Diagrams:** Create visual representations of workflow structure and job dependencies
- **Multiple Formats:** Output in Markdown or HTML format
- **Multi-Provider AI Enhancement:** Support for multiple LLM providers:
  - OpenAI (GPT-3.5 Turbo, GPT-4)
  - Azure OpenAI (Enterprise-grade OpenAI)
  - Anthropic Claude
  - Hugging Face (open source models)
  - Google AI (Gemini models)
  - AWS Bedrock
  - Mock provider for testing
- **GitHub Pages Integration:** Optional automatic deployment to GitHub Pages
- **Image Rendering:** Generate actual SVG/PNG/PDF images from Mermaid diagrams
- **Workflow Source Integration:** Option to include the original workflow YAML in documentation
- **Dark Mode Support:** HTML documentation with automatic dark mode
- **Simple Integration:** Easy to add to your CI/CD pipeline
- **Containerized Approach:** Runs in a Docker container with all dependencies pre-installed

## Container Structure

This action runs within a Docker container for reliable execution across different GitHub Actions runners. The container includes:

- **Base Image:** `mcr.microsoft.com/playwright:v1.52.0-jammy` which includes:
  - Ubuntu 22.04 (Jammy Jellyfish)
  - Node.js for running Mermaid CLI
  - Pre-installed browser dependencies needed for SVG/PNG rendering
- **Python Environment:** Python 3 with all required packages
- **Mermaid CLI:** Globally installed for diagram generation
- **Playwright:** Configured with Chromium browser for headless rendering

This containerized approach ensures all dependencies are properly installed and resolves common issues with missing browser dependencies when generating diagrams.

## Usage

### GitHub Actions Workflow

Add this action to your workflow:

```yaml
name: Generate Workflow Documentation

on:
  push:
    branches: [main]
    paths:
      - ".github/workflows/**"
  workflow_dispatch:

jobs:
  document:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Generate documentation
        uses: gitopsiq/gha-doc@v1
        with:
          workflow_files: ".github/workflows/*.yml"
          output_dir: "docs/workflows"
          format: "html" # Can be 'markdown' or 'html'
          include_diagram_type: "svg" # Options: 'none', 'mermaid', 'svg', 'png', 'pdf'
          include_workflow_source: false # Set to true to include workflow source YAML
          include_ai_suggested_improvements: true # Set to false to disable AI-generated improvement suggestions
          include_ai_usage_information: true # Set to false to disable AI-generated usage information
          ai_provider: "mock" # Choose from: openai, azure_openai, anthropic, hf, google, aws, mock
          # openai_api_key: ${{ secrets.OPENAI_API_KEY }} # Uncomment if using OpenAI
          # openai_model: "gpt-4" # Optional: specify OpenAI model

      - name: Commit documentation
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "docs: update workflow documentation"
          file_pattern: "docs/workflows/*"
```

### Local Usage

You can run the tool locally in two ways:

#### Using Docker (Recommended)

This is the most reliable method as it uses the same container environment as the GitHub Action:

```bash
# Clone the repository
git clone https://github.com/your-username/gha-doc.git
cd gha-doc

# Build the Docker image
docker build -t gha-doc .

# Run the tool using Docker
docker run -v $(pwd):/workdir gha-doc \
  --workflow-files "/workdir/.github/workflows/*.yml" \
  --output-dir "/workdir/docs" \
  --format "html" \
  --include-diagram-type "svg" \
  --include-workflow-source
```

#### Running with Docker (Recommended)

The recommended way to use this tool is from your repository root, mounting the entire repo as `/repo` inside the container. This ensures all workflow references and paths resolve exactly as they do in GitHub Actions and local development.

**Example:**

```sh
docker run --rm \
  -v "$(pwd):/workdir" \
  -w /workdir \
  gha-doc \
  --workflow-files ".github/workflows/*.yml" \
  --output-dir "output" \
  --format "html" \
  --include-diagram-type "svg" \
  --include-workflow-source
```

- Run this command from the root of your repository.
- All workflow references (e.g. `uses: .github/workflows/other.yml`) will resolve correctly.
- No need for complex path rewrites or symlinks.

**Tip:** You can use `--formats "md,html"` to generate both Markdown and HTML outputs in one run.

---

#### Using Local Python Environment

```bash
# Clone the repository
git clone https://github.com/your-username/gha-doc.git
cd gha-doc

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Mermaid CLI for diagram rendering (requires Node.js)
npm install -g @mermaid-js/mermaid-cli

# Install Playwright with Chromium (for diagram rendering)
python -m playwright install --with-deps chromium

# Run the tool
python src/main.py --workflow-files "../.github/workflows/*.yml" \
                  --output-dir "./docs" \
                  --format "html" \
                  --include-diagram-type "svg" \
                  --include-workflow-source \
                  --no-ai-suggested-improvements # To disable AI-generated improvement suggestions
```

## Configuration Options

| Option                              | Description                                               | Default                    |
| ----------------------------------- | --------------------------------------------------------- | -------------------------- |
| `workflow_files`                    | Glob pattern for workflow files to document               | '.github/workflows/\*.yml' |
| `output_dir`                        | Directory to write documentation to                       | 'docs/workflows'           |
| `format`                            | Output format (markdown, html)                            | 'markdown'                 |
| `include_diagram_type`              | Type of diagram to include (none, mermaid, svg, png, pdf) | 'mermaid'                  |
| `include_workflow_source`           | Include workflow source YAML in documentation             | false                      |
| `include_ai_suggested_improvements` | Include AI-generated improvement suggestions              | true                       |
| `include_ai_usage_information`      | Include AI-generated usage information                    | true                       |
| `ai_provider`                       | AI provider to use                                        | 'mock'                     |

### AI Provider-Specific Settings

For each AI provider, you need to provide the corresponding API key and optional model parameters:

#### OpenAI

- `openai_api_key`: Your OpenAI API key
- `openai_model`: Model to use (default: "gpt-3.5-turbo")

#### Azure OpenAI

- `azure_openai_api_key`: Your Azure OpenAI API key
- `azure_openai_endpoint`: Your Azure OpenAI endpoint URL
- `azure_openai_deployment`: Your Azure OpenAI deployment name

#### Anthropic

- `anthropic_api_key`: Your Anthropic API key
- `anthropic_model`: Model to use (default: "claude-2")

#### Hugging Face

- `hf_api_key`: Your Hugging Face API key
- `hf_model`: Model to use (default: "mistralai/Mistral-7B-Instruct-v0.1")

#### Google AI

- `google_api_key`: Your Google AI API key
- `google_model`: Model to use (default: "gemini-1.0-pro")

#### AWS Bedrock

- `aws_api_key`: Your AWS API key (Access Key ID)
- `aws_secret_key`: Your AWS Secret Key
- `aws_region`: AWS region (default: "us-east-1")
- `aws_model`: Model to use (default: "anthropic.claude-v2")

## Special Documentation Comments

You can add special comments in your workflow files to enhance the generated documentation:

```yaml
# @description: This workflow deploys a containerized application
# @author: DevOps Team
# @version: 1.0.0

name: Deploy Container

# @input: environment
# @description: Target environment (dev/test/prod)
# @required: true
inputs:
  environment:
    description: "Target environment (dev/test/prod)"
    required: true
```

## AI Enhanced Documentation

When enabled, the AI enhancement feature generates additional documentation sections using the full workflow YAML as context. This provides more accurate and relevant information tailored to your specific workflow.

The AI enhancement includes:

1. **Usage Information:** Practical information about how to use the workflow, including triggers, inputs, and usage examples.
2. **Suggested Improvements:** Specific recommendations for improving your particular workflow.

## Example Output

The generated documentation includes:

1. **Header:** Title, overview, and workflow diagram
2. **Triggers:** Table of events that trigger the workflow
3. **Inputs:** Table of workflow inputs with types and descriptions
4. **Environment Variables:** Required environment setup
5. **Jobs:** Detailed information for each job
6. **Concurrency:** Concurrency configuration and explanation
7. **AI-Generated Usage Information:** Practical guidelines for using the workflow
8. **AI-Suggested Improvements:** Recommended improvements and best practices
9. **Workflow Source:** Original workflow YAML (when enabled)

### Example Documentation Screenshot

<div align="center">
  <img src="https://via.placeholder.com/800x500/f5f5f5/333?text=Example+Documentation+Screenshot" alt="Example Documentation">
</div>

## Development

### Prerequisites

- Python 3.8+
- Node.js 16+ (for Mermaid CLI)
- Docker (for containerized testing)

### Local Testing with Docker

You can locally test the containerized action to ensure it works correctly:

```bash
# Build the Docker container
docker build -t gha-doc-test .

# Create a test directory with a sample workflow
mkdir -p test-workspace/.github/workflows/
cat > test-workspace/.github/workflows/test-workflow.yml << EOF
name: Test Workflow
on:
  push:
    branches: [ main ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test
        run: echo "Hello World"
EOF

# Run the container with the test workflow
docker run -v "$(pwd)/test-workspace:/workdir" gha-doc-test \
    --workflow-files "/workdir/.github/workflows/*.yml" \
    --output-dir "/workdir/docs" \
    --format "markdown" \
    --include-diagram-type "svg"

# Check the results
ls -la test-workspace/docs/
```

Alternatively, you can use the provided `run_tests.sh` script which includes Docker testing capabilities.

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests with coverage
python -m pytest --cov=src tests/

# Run the provided test script (includes Docker container tests)
./run_tests.sh
```

## Troubleshooting

### Diagram Generation Issues

The most common issues with diagram generation are related to missing browser dependencies which are required by Mermaid CLI for rendering. This action solves these problems through containerization.

If you encounter issues with diagram generation:

- Ensure your workflow has sufficient permissions to create and modify files in the output directory
- Check if the diagram format (mermaid, svg, png, pdf) is supported
- For local testing, use the provided Docker container for consistent results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
