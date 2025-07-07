# Multi-Provider LLM Support for AI Enhancement

This document describes the enhanced multi-provider LLM support in the GitHub Actions Documentation Generator.

## Overview

The GitHub Actions Documentation Generator now supports multiple Large Language Model (LLM) providers for AI-enhanced documentation generation. This includes:

- **OpenAI API** - Access to models like GPT-3.5 and GPT-4
- **Azure OpenAI** - Microsoft's managed OpenAI service
- **Anthropic Claude** - Access to Claude models
- **Mock Provider** - For testing without API access

## Configuration

When using the action, you can configure the AI provider with the following inputs:

```yaml
- name: Generate documentation
  uses: gitopsiq/gha-doc@v1
  with:
    # Basic configuration
    workflow_files: ".github/workflows/*.yml"
    output_dir: "docs/workflows"

    # AI Enhancement options
    ai_enhancement: true
    ai_provider: "openai" # Options: openai, azure_openai, anthropic, hf, mock

    # OpenAI specific settings (when ai_provider: "openai")
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    openai_model: "gpt-4" # Optional: specify model


    # Azure OpenAI specific settings (when ai_provider: "azure_openai")
    # azure_openai_api_key: ${{ secrets.AZURE_OPENAI_API_KEY }}
    # azure_openai_endpoint: "https://your-resource.openai.azure.com"
    # azure_openai_deployment: "your-deployment-name"
```

### Provider Configuration

#### OpenAI

```yaml
ai_provider: "openai"
openai_api_key: ${{ secrets.OPENAI_API_KEY }}
openai_model: "gpt-3.5-turbo" # Optional
```

#### Azure OpenAI

```yaml
ai_provider: "azure_openai"
azure_openai_api_key: ${{ secrets.AZURE_OPENAI_API_KEY }}
azure_openai_endpoint: "https://your-resource.openai.azure.com"
azure_openai_deployment: "your-deployment-name"
ai_deployment_name: "your-deployment-name"
```

#### Anthropic Claude

```yaml
ai_provider: "anthropic"
anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
anthropic_model: "claude-2" # Optional
```

#### Hugging Face

```yaml
ai_provider: "hf"
hf_api_key: ${{ secrets.HF_API_KEY }}
hf_model: "mistralai/Mistral-7B-Instruct-v0.1" # Optional
```

#### Mock Provider (for testing)

```yaml
ai_provider: "mock"
# No key needed
```

## Generated Content

The AI enhancement generates the following content for each workflow:

1. **Description** - A clear explanation of what the workflow does
2. **Best Practices** - Suggestions for improving the workflow
3. **Implementation Notes** - Technical details about the workflow architecture
4. **Usage Examples** - Practical examples of how to use the workflow

## Implementation Details

The AI enhancement system uses a modular provider design pattern:

- Abstract LLMProvider base class
- Concrete implementations for each supported provider
- Factory method to instantiate the appropriate provider
- Graceful fallbacks when API calls fail

This design makes it easy to add new providers in the future without modifying the core logic.

## Security Considerations

- Never commit API keys directly in workflow files
- Always use GitHub Secrets to store API keys
- Consider using Azure OpenAI for enterprise environments
- Set appropriate token limits to control costs

## Troubleshooting

If you encounter issues with AI enhancement:

1. Ensure your API key is valid and has correct permissions
2. Check that the model you specified is available for your account
3. For Azure OpenAI, verify the deployment name matches exactly
4. Check for rate limiting issues if you're making many API calls
