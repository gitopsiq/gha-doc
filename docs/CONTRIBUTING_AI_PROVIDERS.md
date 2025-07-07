# Contributing AI Providers to GitHub Actions Documentation Generator

This guide explains how to contribute additional AI providers to the GitHub Actions Documentation Generator.

## Overview

The AI enhancement module is built with a modular provider system that makes it easy to add support for new LLM providers. This guide walks you through the process of implementing a new provider.

## Provider Implementation Steps

1. **Create a new provider class** that inherits from the `LLMProvider` abstract base class
2. **Implement the required methods**, especially `generate_text()`
3. **Update the factory method** in AIEnhancer to support the new provider
4. **Add input parameters** to action.yml for the new provider
5. **Update the documentation** to include the new provider
6. **Create example workflows** that demonstrate the new provider
7. **Add tests** for the new provider

## Example Implementation

Here's how a new provider might be implemented:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text from a prompt."""
        pass

class MyNewProvider(LLMProvider):
    """My new LLM provider."""

    def __init__(self, api_key: str, model: str = "default-model"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.my-provider.com/generate"

    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["generated_text"]
        except Exception as e:
            print(f"Error calling API: {e}")
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """Provide a fallback response when the API call fails."""
        return f"Unable to generate response for: {prompt[:50]}..."
```

## Factory Method Update

To integrate your new provider with the AIEnhancer, update the `_initialize_provider` method:

```python
def _initialize_provider(self) -> LLMProvider:
    """Initialize the appropriate LLM provider based on configuration."""
    provider_type = self.api_config.get("provider_type", "mock")

    # ... existing providers ...

    elif provider_type == "my_new_provider" and self.api_config.get("api_key"):
        return MyNewProvider(
            api_key=self.api_config.get("api_key"),
            model=self.api_config.get("model", "default-model")
        )
    else:
        print("Using mock provider for AI enhancement (no valid API configuration provided).")
        return MockProvider()
```

## Documentation Update

Add your provider to the AI_PROVIDERS.md file:

````markdown
### My New Provider

```yaml
ai_provider: "my_new_provider"
my_provider_api_key: ${{ secrets.MY_PROVIDER_API_KEY }}
my_provider_model: "my-model" # Optional
```
````

````

## Testing

Create tests for your new provider:

```python
def test_my_new_provider_initialization(self):
    """Test My New Provider initialization."""
    provider = MyNewProvider(
        api_key="test_key",
        model="my-model"
    )
    self.assertEqual(provider.api_key, "test_key")
    self.assertEqual(provider.model, "my-model")
    self.assertEqual(provider.api_url, "https://api.my-provider.com/generate")
````

## Submitting Your Contribution

1. Fork the repository
2. Create a new branch for your provider
3. Implement the changes following the steps above
4. Add tests for your provider
5. Submit a pull request with a clear description of your new provider
