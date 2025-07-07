# AI Enhancement for GitHub Actions Documentation Generator

This document provides a detailed guide to using the AI enhancement features in the GitHub Actions Documentation Generator.

## Overview

The AI enhancement module uses Large Language Models (LLMs) to augment the automatically generated documentation with:

1. **Comprehensive Descriptions**: Clear explanations of what workflows do
2. **Best Practices**: Suggestions for workflow improvements
3. **Implementation Notes**: Technical insights about workflow architecture
4. **Usage Examples**: Practical examples of how to use workflows

## Supported AI Providers

The AI enhancement module supports multiple LLM providers with a modular architecture that allows for easy addition of new providers:

### Currently Supported

1. **OpenAI** - Full API access to models like GPT-3.5 and GPT-4
2. **Azure OpenAI** - Microsoft's enterprise-grade OpenAI service
3. **Anthropic Claude** - Access to Claude models
4. **Mock Provider** - For testing without API access

### Planned Support

1. **Hugging Face** - Access to open-source models like Mistral, Llama 2, etc.
2. **Google Vertex AI** - Access to Google's AI models
3. **AWS Bedrock** - Access to Amazon's foundation models
4. **Local Models** - Support for local inference using Ollama or similar tools

## Provider Configuration

### OpenAI

```yaml
ai_provider: "openai"
openai_api_key: ${{ secrets.OPENAI_API_KEY }}
openai_model: "gpt-4" # Optional, defaults to gpt-3.5-turbo
```

### Azure OpenAI

```yaml
ai_provider: "azure_openai"
azure_openai_api_key: ${{ secrets.AZURE_OPENAI_API_KEY }}
azure_openai_endpoint: "https://your-resource.openai.azure.com"
azure_openai_deployment: "your-deployment-name"
```

### Anthropic Claude

```yaml
ai_provider: "anthropic"
anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
anthropic_model: "claude-2" # Optional
```

### Hugging Face (Planned)

```yaml
ai_provider: "hf"
hf_api_key: ${{ secrets.HF_API_KEY }}
hf_model: "mistralai/Mistral-7B-Instruct-v0.1" # Optional
```

### Mock Provider (for testing)

```yaml
ai_provider: "mock" # No key needed
```

## Example Usage

### Basic Configuration

```yaml
- name: Generate documentation with AI enhancement
  uses: gitopsiq/gha-doc@v1
  with:
    workflow_files: ".github/workflows/*.yml"
    output_dir: "docs/workflows"
    ai_enhancement: true
    ai_provider: "openai"
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

### Advanced Configuration with Azure OpenAI

```yaml
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
    azure_openai_endpoint: "https://your-resource.openai.azure.com"
    azure_openai_deployment: "gpt-4"
```

## Implementation Details

The AI enhancement module is built with a modular provider system:

- **Abstract Base Class**: `LLMProvider` defines the interface all providers must implement
- **Provider-Specific Classes**: Each provider has a dedicated class that handles the specifics of API communication
- **Factory Pattern**: The AIEnhancer uses a factory pattern to create the appropriate provider based on configuration
- **Graceful Degradation**: If AI enhancement fails for any reason, the tool continues with basic documentation

## Customization

You can customize the AI enhancement by modifying the prompt templates in the AI enhancer module. This allows you to:

1. Adjust the focus of generated content
2. Add organization-specific guidance
3. Implement custom rules or requirements for documentation

## Security Best Practices

When using AI enhancement:

1. **API Keys**: Always store API keys as GitHub Secrets, never hard-code them
2. **Token Limits**: Be aware of token usage to manage costs
3. **Data Privacy**: Understand what workflow data is being sent to external APIs
4. **Self-Hosted Options**: For sensitive workflows, consider using Azure OpenAI or self-hosted models

## Troubleshooting

If you encounter issues with AI enhancement:

1. **Check API Keys**: Ensure your API keys are valid and properly configured
2. **Check Models**: Verify the specified model is available for your account/subscription
3. **Review Logs**: Enable verbose logging to see detailed API interaction logs
4. **Try Mock Provider**: Use the mock provider to test without an external API

## Cost Management

AI enhancement can involve costs depending on the provider and usage:

1. **OpenAI**: Charges based on tokens used
2. **Azure OpenAI**: Enterprise pricing based on tokens or provisioned capacity
3. **Anthropic**: Charges based on tokens used
4. **Hugging Face**: Free tier available with limitations, paid tiers for higher usage
5. **Self-Hosted**: One-time hardware cost, but no per-token charges

Consider using the mock provider during development and testing to avoid unnecessary API costs.
