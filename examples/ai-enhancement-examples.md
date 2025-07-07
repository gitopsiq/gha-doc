# Using the GitHub Actions Documentation Generator with AI Enhancement

This document provides examples of how to use the GitHub Actions Documentation Generator with different AI provider configurations.

## Basic Usage (No AI Enhancement)

```yaml
name: Generate Documentation

on:
  push:
    paths:
      - ".github/workflows/**"

jobs:
  document:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate documentation
        uses: gitopsiq/gha-doc@v1
        with:
          workflow_files: ".github/workflows/*.yml"
          output_dir: "docs/workflows"
          format: "markdown"
```

## Using OpenAI AI Enhancement

```yaml
name: Generate Documentation with OpenAI

on:
  workflow_dispatch:

jobs:
  document:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate documentation with OpenAI
        uses: gitopsiq/gha-doc@v1
        with:
          workflow_files: ".github/workflows/*.yml"
          output_dir: "docs/workflows"
          format: "html"
          generate_diagrams: true
          ai_enhancement: true
          ai_provider: "openai"
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          openai_model: "gpt-4"
```

## Using Azure OpenAI AI Enhancement

```yaml
name: Generate Documentation with Azure OpenAI

on:
  workflow_dispatch:

jobs:
  document:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate documentation with Azure OpenAI
        uses: gitopsiq/gha-doc@v1
        with:
          workflow_files: ".github/workflows/*.yml"
          output_dir: "docs/workflows"
          format: "html"
          generate_diagrams: true
          ai_enhancement: true
          ai_provider: "azure_openai"
          azure_openai_api_key: ${{ secrets.AZURE_OPENAI_API_KEY }}
          azure_openai_endpoint: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
          azure_openai_deployment: "gpt-4"
```

## Using Anthropic Claude AI Enhancement

```yaml
name: Generate Documentation with Anthropic Claude

on:
  workflow_dispatch:

jobs:
  document:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate documentation with Anthropic
        uses: gitopsiq/gha-doc@v1
        with:
          workflow_files: ".github/workflows/*.yml"
          output_dir: "docs/workflows"
          format: "html"
          generate_diagrams: true
          ai_enhancement: true
          ai_provider: "anthropic"
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          anthropic_model: "claude-2"
```

## Using Hugging Face AI Enhancement

```yaml
name: Generate Documentation with Hugging Face

on:
  workflow_dispatch:

jobs:
  document:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate documentation with Hugging Face
        uses: gitopsiq/gha-doc@v1
        with:
          workflow_files: ".github/workflows/*.yml"
          output_dir: "docs/workflows"
          format: "html"
          generate_diagrams: true
          ai_enhancement: true
          ai_provider: "hf"
          hf_api_key: ${{ secrets.HF_API_KEY }}
          hf_model: "mistralai/Mistral-7B-Instruct-v0.1"
```

## Using Mock Provider (For Testing)

```yaml
name: Generate Documentation with Mock AI

on:
  workflow_dispatch:

jobs:
  document:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate documentation with Mock AI
        uses: gitopsiq/gha-doc@v1
        with:
          workflow_files: ".github/workflows/*.yml"
          output_dir: "docs/workflows"
          format: "html"
          generate_diagrams: true
          ai_enhancement: true
          ai_provider: "mock"
```

## Automated Documentation with GitHub Pages Deployment

```yaml
name: Generate and Publish Workflow Documentation

on:
  push:
    branches: [main]
    paths:
      - ".github/workflows/**"
  schedule:
    - cron: "0 0 * * 1" # Weekly on Monday

jobs:
  document:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pages: write

    steps:
      - uses: actions/checkout@v3

      - name: Generate documentation
        uses: gitopsiq/gha-doc@v1
        with:
          workflow_files: ".github/workflows/*.yml"
          output_dir: "docs/workflows"
          format: "html"
          generate_diagrams: true
          ai_enhancement: true
          ai_provider: "openai"
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          deploy_to_github_pages: true

      - name: Commit changes
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "docs: update workflow documentation"
          file_pattern: "docs/workflows/*"
```
