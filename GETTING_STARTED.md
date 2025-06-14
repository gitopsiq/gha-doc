# Getting Started with gha-doc

This guide will help you quickly set up and use the GitHub Actions Documentation Generator (gha-doc) in your repository.

## Installation Methods

### Method 1: Use as a GitHub Action

Add the following workflow to your repository:

```yaml
name: Generate Workflow Documentation

on:
  push:
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
          format: "markdown"
          generate_diagrams: true

      - name: Commit documentation
        uses: stefanzweifel/git-auto-commit-action@v4
        with:
          commit_message: "docs: update workflow documentation"
          file_pattern: "docs/workflows/*"
```

### Method 2: Use Locally

To use gha-doc locally:

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/gha-doc.git
   cd gha-doc
   ```

2. Set up a Python virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the tool:
   ```bash
   python src/main.py --workflow-files "../.github/workflows/*.yml" --output-dir "./docs"
   ```

## Configuration Options

| Option              | Description                                 | Default                    | Required                           |
| ------------------- | ------------------------------------------- | -------------------------- | ---------------------------------- |
| `workflow_files`    | Glob pattern for workflow files to document | '.github/workflows/\*.yml' | No                                 |
| `output_dir`        | Directory to write documentation to         | 'docs/workflows'           | No                                 |
| `format`            | Output format (markdown, html)              | 'markdown'                 | No                                 |
| `generate_diagrams` | Whether to generate diagrams                | true                       | No                                 |
| `include_source`    | Include source code in documentation        | false                      | No                                 |
| `ai_enhancement`    | Enable AI-powered enhancements              | false                      | No                                 |
| `ai_api_key`        | API key for OpenAI API                      | ''                         | No (unless ai_enhancement is true) |

## Workflow Annotations

You can use special annotations in your workflow files to enhance the documentation:

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

## Examples

Check out example workflow documentation in the [examples/docs](examples/docs) directory.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/your-username/gha-doc/issues/new) in the repository.
