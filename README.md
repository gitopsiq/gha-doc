# GitHub Actions Documentation Generator (gha-doc)

<div align="center">
  <img src="https://via.placeholder.com/800x200/0067b8/ffffff?text=GitHub+Actions+Documentation+Generator" alt="gha-doc Banner">
</div>

## Overview

`gha-doc` is a composite GitHub Action that automatically generates comprehensive documentation for GitHub Actions workflows in your repository. The tool analyzes workflow files, extracts metadata, generates visual diagrams, and produces standardized documentation in markdown or HTML formats.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions Marketplace](https://img.shields.io/badge/GitHub%20Actions-Marketplace-blue)](https://github.com/marketplace/actions/github-actions-documentation-generator)

> **Note**: This repository was migrated from its original company repository to a personal account. All functionality has been preserved.

## Features

- **Workflow Analysis:** Parse and analyze GitHub Actions workflow YAML files
- **Standardized Documentation:** Generate consistent, high-quality documentation
- **Visual Diagrams:** Create visual representations of workflow structure and job dependencies
- **Multiple Formats:** Output in Markdown or HTML format
- **AI Enhancement:** OpenAI-powered descriptions and best practices with fallback to mock responses
- **Image Rendering:** Generate actual PNG/SVG/PDF images from Mermaid diagrams
- **Dark Mode Support:** HTML documentation with automatic dark mode
- **Simple Integration:** Easy to add to your CI/CD pipeline

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
        uses: your-username/gha-doc@v1
        with:
          workflow_files: ".github/workflows/*.yml"
          output_dir: "docs/workflows"
          format: "html" # Can be 'markdown' or 'html'
          generate_diagrams: true
          diagram_format: "svg" # Can be 'png', 'svg', or 'pdf'
          include_source: false
          ai_enhancement: false
          # ai_api_key: ${{ secrets.OPENAI_API_KEY }} # Uncomment if using AI enhancement

      - name: Commit documentation
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "docs: update workflow documentation"
          file_pattern: "docs/workflows/*"
```

### Local Usage

You can also run the tool locally:

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

# Run the tool
python src/main_improved.py --workflow-files "../.github/workflows/*.yml" \
                           --output-dir "./docs" \
                           --format "html" \
                           --diagram-format "svg" \
                           --generate-diagrams
```

## Configuration Options

| Option              | Description                                   | Default                    |
| ------------------- | --------------------------------------------- | -------------------------- |
| `workflow_files`    | Glob pattern for workflow files to document   | '.github/workflows/\*.yml' |
| `output_dir`        | Directory to write documentation to           | 'docs/workflows'           |
| `format`            | Output format (markdown, html)                | 'markdown'                 |
| `generate_diagrams` | Whether to generate diagrams                  | true                       |
| `diagram_format`    | Format for generated diagrams (png, svg, pdf) | 'png'                      |
| `include_source`    | Include source code in documentation          | false                      |
| `ai_enhancement`    | Enable AI-powered enhancements                | false                      |
| `ai_api_key`        | API key for OpenAI API                        | ''                         |

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

## Example Output

The generated documentation includes:

1. **Header:** Title, overview, and workflow diagram
2. **Triggers:** Table of events that trigger the workflow
3. **Inputs:** Table of workflow inputs with types and descriptions
4. **Environment Variables:** Required environment setup
5. **Jobs:** Detailed information for each job
6. **Concurrency:** Concurrency configuration and explanation
7. **Usage Examples:** How to use the workflow
8. **Best Practices:** Recommended usage patterns

### Example Documentation Screenshot

<div align="center">
  <img src="https://via.placeholder.com/800x500/f5f5f5/333?text=Example+Documentation+Screenshot" alt="Example Documentation">
</div>

## Development

### Prerequisites

- Python 3.8+
- PyYAML
- Markdown
- Mermaid CLI (for diagram rendering)

### Project Structure

```
gha-doc/
├── action.yml                # GitHub Action definition
├── README.md                 # Documentation
├── DESIGN.md                 # Design document
├── GETTING_STARTED.md        # Getting started guide
├── STATUS.md                 # Project status report
├── src/                      # Source code
│   ├── main.py               # Original entry point
│   ├── main_improved.py      # Enhanced entry point with extra features
│   ├── parser.py             # YAML parser
│   ├── analyzer.py           # Structure analyzer
│   ├── visualizer.py         # Diagram generator
│   ├── visualizer_improved.py # Enhanced diagram generator with image rendering
│   ├── generator.py          # Documentation generator
│   ├── generator_improved.py # Enhanced documentation generator with better HTML
│   ├── ai_enhancer.py        # AI enhancement module (mock responses)
│   ├── ai_enhancer_improved.py # Enhanced AI module with OpenAI integration
│   ├── template_manager.py   # HTML template manager
│   └── templates/            # HTML templates
│       └── default.html      # Default HTML template with dark mode support
├── examples/                 # Example workflows and documentation
└── tests/                    # Tests
    └── ...
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov black flake8 mypy

# Run code quality checks
black --check src tests
mypy --ignore-missing-imports src
flake8 src tests

# Run tests with coverage
pytest --cov=src tests/
```

### CI/CD Pipeline

This project uses a comprehensive CI/CD pipeline that:

1. **Tests** the code with multiple Python versions (3.8, 3.10, 3.12)
2. **Validates** with code quality tools (Black, MyPy, Flake8)
3. **Runs** integration tests with sample workflows
4. **Generates** documentation for its own workflows
5. **Publishes** releases to GitHub and the Marketplace

You can manually trigger the workflow to publish a new version to the GitHub Marketplace using the workflow dispatch feature.

## Roadmap

- [x] Implement image rendering for diagrams
- [x] Add OpenAI API integration for AI enhancement
- [x] Improve HTML rendering with better formatting and dark mode
- [ ] Add GitHub Pages integration
- [ ] Support for additional output formats (PDF, DOCX)
- [ ] VSCode extension integration
- [ ] Performance analytics for workflows
- [ ] Live preview server
- [ ] Interactive HTML documentation with collapsible sections

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
