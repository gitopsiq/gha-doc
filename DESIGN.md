# GitHub Actions Documentation Generator (gha-doc) Design Document

## Overview

gha-doc is a composite action for automatically generating comprehensive documentation for GitHub Actions workflows. It analyzes workflow files, extracts relevant metadata, generates visual diagrams, and produces standardized documentation in various formats.

## Goals

1. **Standardized Documentation**: Create consistent, high-quality documentation for all GitHub Actions workflows
2. **Visual Representation**: Generate diagrams showing job dependencies and workflow structure
3. **Dependency Tracking**: Track and document calls to reusable workflows and composite actions
4. **AI Enhancement**: Optionally use AI to improve descriptions, suggest best practices, and identify optimizations
5. **Simple Integration**: Easy to add to any repository as a GitHub Action
6. **Multiple Output Formats**: Support for Markdown, HTML, and potentially other formats

## Architecture

### Component Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  YAML Parser    │────▶│  Structure      │────▶│  Documentation  │
│                 │     │  Analyzer       │     │  Generator      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                      │                       │
         ▼                      ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Metadata        │     │ Dependency      │     │ Visualization   │
│ Extractor       │     │ Tracker         │     │ Engine          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │ AI Enhancement  │
                                                │ (optional)      │
                                                └─────────────────┘
```

### Key Components

1. **YAML Parser**: Parses GitHub Actions workflow files, extracting raw data structure
2. **Metadata Extractor**: Identifies triggers, inputs, outputs, permissions, environments
3. **Structure Analyzer**: Maps job dependencies, conditions, matrix strategies
4. **Dependency Tracker**: Identifies calls to reusable workflows and composite actions
5. **Visualization Engine**: Generates diagrams showing workflow structure and dependencies
6. **Documentation Generator**: Creates standardized documentation in multiple formats
7. **AI Enhancement Module**: Optional component to enhance documentation with LLM-generated content

## Implementation Details

### Core Schema

We'll define a standardized schema for workflow documentation:

```python
class Workflow:
    name: str
    description: str
    triggers: List[Trigger]
    inputs: List[Input]
    env: Dict[str, str]
    jobs: List[Job]

class Job:
    id: str
    name: str
    runs_on: str
    needs: List[str]
    steps: List[Step]
    outputs: Dict[str, str]
    if_condition: str
    uses: str  # For reusable workflow calls

class Step:
    name: str
    uses: str
    with: Dict[str, str]
    run: str
    env: Dict[str, str]
    if_condition: str

class Trigger:
    event_type: str
    filters: Dict[str, Any]

class Input:
    name: str
    description: str
    required: bool
    default: str
    type: str
```

### Documentation Format

Each generated documentation file will include:

1. **Header**: Title, overview, and workflow diagram
2. **Triggers**: Table of events that trigger the workflow
3. **Inputs**: Table of workflow inputs with types and descriptions
4. **Environment Variables**: Required environment setup
5. **Jobs**: Detailed information for each job
6. **Concurrency**: Concurrency configuration and explanation
7. **Usage Examples**: How to use the workflow
8. **Best Practices**: Recommended usage patterns
9. **Common Issues**: Troubleshooting guidance
10. **Related Documentation**: Links to other relevant documentation

### Special Documentation Comments

We'll support special comment annotations in workflow files:

```yaml
# @description: This workflow deploys a containerized application to ACI
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

## Implementation Plan

### Phase 1: Core Parser and Documentation Generator

1. Set up the project structure
2. Implement YAML parser for workflow files
3. Extract basic workflow metadata
4. Generate simple Markdown documentation
5. Create action.yml for the composite action

### Phase 2: Visualization and Structure Analysis

1. Implement job dependency analysis
2. Generate Mermaid diagrams for workflow visualization
3. Add conditional path analysis
4. Enhance Markdown output with visualization

### Phase 3: Dependency Tracking

1. Add tracking of calls to reusable workflows
2. Add tracking of composite actions
3. Generate documentation for workflow dependencies
4. Create visual representation of workflow relationships

### Phase 4: AI Enhancement (Optional)

1. Add integration with OpenAI API
2. Implement description enhancement
3. Add best practices suggestions
4. Generate usage examples

### Phase 5: Additional Features

1. Add HTML output format
2. Support for GitHub Pages integration
3. Add configuration options
4. Implement styled templates

## Usage

As a GitHub Action:

```yaml
- name: Generate GitHub Actions Documentation
  uses: your-username/gha-doc@v1
  with:
    workflow_files: ".github/workflows/*.yml"
    output_dir: "docs/workflows"
    format: "markdown"
    generate_diagrams: true
    ai_enhancement: false
    ai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

As a CLI tool:

```bash
gha-doc generate --workflow-files ".github/workflows/*.yml" --output-dir "docs/workflows" --format markdown
```

## Configuration

| Option            | Description                                 | Default                    |
| ----------------- | ------------------------------------------- | -------------------------- |
| workflow_files    | Glob pattern for workflow files to document | '.github/workflows/\*.yml' |
| output_dir        | Directory to write documentation to         | 'docs/workflows'           |
| format            | Output format (markdown, html)              | 'markdown'                 |
| generate_diagrams | Whether to generate diagrams                | true                       |
| include_source    | Include source code in documentation        | false                      |
| ai_enhancement    | Enable AI-powered enhancements              | false                      |
| ai_api_key        | API key for AI service                      | None                       |

## Success Criteria

1. Documentation is generated for all workflow files
2. Documentation includes all required sections
3. Diagrams accurately represent workflow structure
4. Reusable workflow dependencies are correctly identified
5. AI enhancements provide valuable insights (when enabled)

## Future Enhancements

1. Integration with VS Code extension
2. Live preview server
3. Linting and best practices checking
4. Performance analytics for workflows
5. Support for additional output formats
6. Integration with GitHub Actions dashboard

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Mermaid Diagram Syntax](https://mermaid-js.github.io/mermaid/#/)
- [Markdown Guide](https://www.markdownguide.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
