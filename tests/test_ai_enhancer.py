"""
Tests for the AI Enhancer module with multiple providers
"""

import os
import pytest
import unittest
from unittest.mock import MagicMock, patch
import sys
import json

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_enhancer import (
    AIEnhancer,
    LLMProvider,
    OpenAIProvider,
    AzureOpenAIProvider,
    AnthropicProvider,
    HuggingFaceProvider,
    MockProvider,
)

class TestLLMProviders(unittest.TestCase):
    """Test the LLM provider classes."""

    def test_openai_provider_initialization(self):
        """Test OpenAI provider initialization."""
        provider = OpenAIProvider(api_key="test_key", model="gpt-4")
        self.assertEqual(provider.api_key, "test_key")
        self.assertEqual(provider.model, "gpt-4")
        self.assertEqual(provider.api_url, "https://api.openai.com/v1/chat/completions")

    @pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="OpenAI API key not provided")
    def test_openai_provider_generate_text(self):
        """Test actual OpenAI API call if key is available."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self.skipTest("OpenAI API key not provided")

        provider = OpenAIProvider(api_key=api_key)
        response = provider.generate_text("Say hello world", max_tokens=20)
        self.assertIsNotNone(response)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 5)  # Should have a meaningful response

    def test_azure_openai_provider_initialization(self):
        """Test Azure OpenAI provider initialization."""
        provider = AzureOpenAIProvider(
            api_key="test_key",
            endpoint="https://test.openai.azure.com",
            deployment_name="gpt-4"
        )
        self.assertEqual(provider.api_key, "test_key")
        self.assertEqual(provider.endpoint, "https://test.openai.azure.com")
        self.assertEqual(provider.deployment_name, "gpt-4")
        self.assertEqual(
            provider.api_url,
            "https://test.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2023-07-01-preview"
        )

    def test_anthropic_provider_initialization(self):
        """Test Anthropic provider initialization."""
        provider = AnthropicProvider(api_key="test_key", model="claude-2")
        self.assertEqual(provider.api_key, "test_key")
        self.assertEqual(provider.model, "claude-2")
        self.assertEqual(provider.api_url, "https://api.anthropic.com/v1/complete")

    def test_huggingface_provider_initialization(self):
        """Test Hugging Face provider initialization."""
        provider = HuggingFaceProvider(
            api_key="test_key",
            model="mistralai/Mistral-7B-Instruct-v0.1"
        )
        self.assertEqual(provider.api_key, "test_key")
        self.assertEqual(provider.model, "mistralai/Mistral-7B-Instruct-v0.1")
        self.assertEqual(
            provider.api_url,
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
        )

    def test_mock_provider(self):
        """Test the mock provider responses."""
        provider = MockProvider()

        # Test different prompt responses
        description_response = provider.generate_text("Generate a description for this workflow")
        self.assertTrue("automates CI/CD processes" in description_response)

        best_practices_response = provider.generate_text("What are the best practice recommendations?")
        self.assertTrue("timeouts" in best_practices_response)

        implementation_response = provider.generate_text("Give some implementation notes")
        self.assertTrue("strategy" in implementation_response)

        default_response = provider.generate_text("Something else")
        self.assertTrue("Example usage" in default_response)


class TestAIEnhancer(unittest.TestCase):
    """Test the AIEnhancer class with different providers."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflow_data = {
            "name": "Test Workflow",
            "triggers": [{"event_type": "push", "branches": ["main"]}],
            "jobs": {"build": {"runs-on": "ubuntu-latest", "steps": [{"name": "Checkout", "uses": "actions/checkout@v3"}]}}
        }

    def test_provider_selection_openai(self):
        """Test that the OpenAI provider is selected correctly."""
        enhancer = AIEnhancer(
            self.workflow_data,
            api_config={
                "provider_type": "openai",
                "api_key": "test_key",
                "model": "gpt-4"
            }
        )
        self.assertIsInstance(enhancer.provider, OpenAIProvider)
        self.assertEqual(enhancer.provider.api_key, "test_key")
        self.assertEqual(enhancer.provider.model, "gpt-4")

    def test_provider_selection_azure_openai(self):
        """Test that the Azure OpenAI provider is selected correctly."""
        enhancer = AIEnhancer(
            self.workflow_data,
            api_config={
                "provider_type": "azure_openai",
                "api_key": "test_key",
                "endpoint": "https://test.openai.azure.com",
                "deployment_name": "gpt-4"
            }
        )
        self.assertIsInstance(enhancer.provider, AzureOpenAIProvider)
        self.assertEqual(enhancer.provider.api_key, "test_key")
        self.assertEqual(enhancer.provider.endpoint, "https://test.openai.azure.com")
        self.assertEqual(enhancer.provider.deployment_name, "gpt-4")

    def test_provider_selection_anthropic(self):
        """Test that the Anthropic provider is selected correctly."""
        enhancer = AIEnhancer(
            self.workflow_data,
            api_config={
                "provider_type": "anthropic",
                "api_key": "test_key",
                "model": "claude-2"
            }
        )
        self.assertIsInstance(enhancer.provider, AnthropicProvider)
        self.assertEqual(enhancer.provider.api_key, "test_key")
        self.assertEqual(enhancer.provider.model, "claude-2")

    def test_provider_selection_huggingface(self):
        """Test that the Hugging Face provider is selected correctly."""
        enhancer = AIEnhancer(
            self.workflow_data,
            api_config={
                "provider_type": "hf",
                "api_key": "test_key",
                "model": "mistralai/Mistral-7B-Instruct-v0.1"
            }
        )
        self.assertIsInstance(enhancer.provider, HuggingFaceProvider)
        self.assertEqual(enhancer.provider.api_key, "test_key")
        self.assertEqual(enhancer.provider.model, "mistralai/Mistral-7B-Instruct-v0.1")

    def test_provider_selection_mock(self):
        """Test that the mock provider is selected as fallback."""
        enhancer = AIEnhancer(
            self.workflow_data,
            api_config={
                "provider_type": "mock"
            }
        )
        self.assertIsInstance(enhancer.provider, MockProvider)

    def test_provider_selection_invalid(self):
        """Test that the mock provider is selected when invalid configuration is provided."""
        enhancer = AIEnhancer(
            self.workflow_data,
            api_config={
                "provider_type": "invalid_provider"
            }
        )
        self.assertIsInstance(enhancer.provider, MockProvider)

    @patch('ai_enhancer.OpenAIProvider.generate_text')
    def test_enhance_workflow_with_openai(self, mock_generate_text):
        """Test enhancing a workflow with OpenAI."""
        mock_generate_text.return_value = "AI-generated content"

        enhancer = AIEnhancer(
            self.workflow_data,
            api_config={
                "provider_type": "openai",
                "api_key": "test_key"
            }
        )

        enhanced_data = enhancer.enhance()

        self.assertIn("ai_enhancement", enhanced_data)
        self.assertEqual(enhanced_data["ai_enhancement"]["description"], "AI-generated content")
        self.assertEqual(enhanced_data["ai_enhancement"]["best_practices"], "AI-generated content")
        self.assertEqual(enhanced_data["ai_enhancement"]["usage_information"], "AI-generated content")
        self.assertEqual(enhanced_data["ai_enhancement"]["usage_examples"], "AI-generated content")

    def test_enhance_workflow_with_mock(self):
        """Test enhancing a workflow with the mock provider."""
        enhancer = AIEnhancer(
            self.workflow_data,
            api_config={
                "provider_type": "mock"
            }
        )

        enhanced_data = enhancer.enhance()

        self.assertIn("ai_enhancement", enhanced_data)

        # Get expected outputs from the mock provider
        mock_provider = MockProvider()
        expected_desc = mock_provider.generate_text("Generate a description for this workflow")
        expected_best = mock_provider.generate_text("What are the best practice recommendations?")
        expected_usage_info = mock_provider.generate_text("Give some implementation notes")
        expected_usage = mock_provider.generate_text("Something else")

        # Test against what the mock provider should return
        self.assertEqual(enhanced_data["ai_enhancement"]["description"], expected_desc)
        self.assertEqual(enhanced_data["ai_enhancement"]["best_practices"], expected_best)
        self.assertEqual(enhanced_data["ai_enhancement"]["usage_information"], expected_usage_info)
        self.assertEqual(enhanced_data["ai_enhancement"]["usage_examples"], expected_usage)


if __name__ == '__main__':
    unittest.main()
