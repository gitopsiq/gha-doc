#!/usr/bin/env python3
"""
AI Enhancement Module

Enhances workflow documentation with AI-generated content.
Supports multiple LLM providers (OpenAI, Azure OpenAI, Anthropic, etc).
"""

import os
import json
import time
import requests
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate text from a prompt."""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """Provide a fallback response when the API call fails."""
        return f"Unable to generate response for: {prompt[:50]}..."

class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI API provider."""

    def __init__(self, api_key: str, endpoint: str, deployment_name: str):
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.api_url = f"{self.endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version=2023-07-01-preview"

    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error calling Azure OpenAI API: {e}")
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """Provide a fallback response when the API call fails."""
        return f"Unable to generate response for: {prompt[:50]}..."

class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str, model: str = "claude-2"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/complete"

    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": self.model,
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": max_tokens
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["completion"]
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """Provide a fallback response when the API call fails."""
        return f"Unable to generate response for: {prompt[:50]}..."

class HuggingFaceProvider(LLMProvider):
    """Hugging Face API provider."""

    def __init__(self, api_key: str, model: str = "mistralai/Mistral-7B-Instruct-v0.1"):
        self.api_key = api_key
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"

    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()

            # Handle different response formats from Hugging Face models
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and "generated_text" in result[0]:
                    return result[0]["generated_text"].replace(prompt, "").strip()
                else:
                    return str(result[0]).strip()
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"].replace(prompt, "").strip()

            return str(result).strip()
        except Exception as e:
            print(f"Error calling Hugging Face API: {e}")
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """Provide a fallback response when the API call fails."""
        return f"Unable to generate response for: {prompt[:50]}..."

class GoogleAIProvider(LLMProvider):
    """Google AI API provider."""

    def __init__(self, api_key: str, model: str = "gemini-1.0-pro"):
        self.api_key = api_key
        self.model = model
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "contents": [{
                "role": "user",
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": max_tokens
            }
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            content = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return content
        except Exception as e:
            print(f"Error calling Google AI API: {e}")
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """Provide a fallback response when the API call fails."""
        return f"Unable to generate response for: {prompt[:50]}..."

class AWSBedrockProvider(LLMProvider):
    """AWS Bedrock API provider."""

    def __init__(self, api_key: str, secret_key: str, region: str = "us-east-1", model: str = "anthropic.claude-v2"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.region = region
        self.model = model

        # This is a simplified implementation - in production, you'd use boto3
        self.endpoint = f"https://bedrock-runtime.{region}.amazonaws.com"
        self.api_url = f"{self.endpoint}/model/{model}/invoke"

    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        # NOTE: This is a simplified implementation
        # In production code, you'd use boto3 client for Bedrock
        headers = {
            "Content-Type": "application/json",
            "X-Amz-Content-Sha256": "required",  # In production, calculate actual SHA256
            "X-Amz-Date": time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        }

        # Different models have different request formats
        if "anthropic.claude" in self.model:
            data = {
                "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                "max_tokens_to_sample": max_tokens
            }
        else:
            data = {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": max_tokens
                }
            }

        try:
            # Note: In production code, this would use boto3 with proper AWS signature
            # This is a placeholder for the implementation
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            return "AWS Bedrock response would be parsed here"
        except Exception as e:
            print(f"Error calling AWS Bedrock API: {e}")
            return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str) -> str:
        """Provide a fallback response when the API call fails."""
        return f"Unable to generate response for: {prompt[:50]}..."

class MockProvider(LLMProvider):
    """Mock LLM provider for testing or when no API key is available."""

    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate a mock response based on the prompt."""
        if "description" in prompt.lower():
            return "This workflow automates CI/CD processes to improve development efficiency and ensure consistent deployments."
        elif "best practice" in prompt.lower():
            return "Consider adding timeouts to prevent long-running jobs and implementing comprehensive error handling."
        elif "implementation" in prompt.lower() or "usage information" in prompt.lower():
            return "This workflow implements a sophisticated strategy that optimizes deployment performance while preventing resource conflicts."
        else:
            return "Example usage: Manually trigger the workflow to deploy resources to the development environment."

class AIEnhancer:
    """Enhancer for workflow documentation using AI."""

    def __init__(self, workflow_data: Dict[str, Any], api_config: Dict[str, Any] = None):
        """Initialize with analyzed workflow data and API configuration."""
        self.workflow_data = workflow_data
        self.api_config = api_config or {}
        self.provider = self._initialize_provider()

    def _initialize_provider(self) -> LLMProvider:
        """Initialize the appropriate LLM provider based on configuration."""
        provider_type = self.api_config.get("provider_type", "mock")

        if provider_type == "openai" and self.api_config.get("api_key"):
            return OpenAIProvider(
                api_key=self.api_config.get("api_key"),
                model=self.api_config.get("model", "gpt-3.5-turbo")
            )
        elif provider_type == "azure_openai" and self.api_config.get("api_key") and self.api_config.get("endpoint"):
            return AzureOpenAIProvider(
                api_key=self.api_config.get("api_key"),
                endpoint=self.api_config.get("endpoint"),
                deployment_name=self.api_config.get("deployment_name", "gpt-35-turbo")
            )
        elif provider_type == "anthropic" and self.api_config.get("api_key"):
            return AnthropicProvider(
                api_key=self.api_config.get("api_key"),
                model=self.api_config.get("model", "claude-2")
            )
        elif provider_type == "hf" and self.api_config.get("api_key"):
            return HuggingFaceProvider(
                api_key=self.api_config.get("api_key"),
                model=self.api_config.get("model", "mistralai/Mistral-7B-Instruct-v0.1")
            )
        elif (provider_type == "google" or provider_type == "google_ai") and self.api_config.get("api_key"):
            return GoogleAIProvider(
                api_key=self.api_config.get("api_key"),
                model=self.api_config.get("model", "gemini-1.0-pro")
            )
        elif provider_type == "aws" and self.api_config.get("api_key") and self.api_config.get("secret_key"):
            return AWSBedrockProvider(
                api_key=self.api_config.get("api_key"),
                secret_key=self.api_config.get("secret_key"),
                region=self.api_config.get("region", "us-east-1"),
                model=self.api_config.get("model", "anthropic.claude-v2")
            )
        else:
            print("Using mock provider for AI enhancement (no valid API configuration provided).")
            return MockProvider()

    def enhance(self) -> Dict[str, Any]:
        """Enhance workflow documentation with AI-generated content."""
        try:
            enhanced_data = self.workflow_data.copy()

            # Add AI enhancements
            enhanced_data['ai_enhancement'] = {
                'description': self._generate_description(),
                'best_practices': self._generate_best_practices(),
                'usage_information': self._generate_usage_information(),
                'usage_examples': self._generate_usage_examples()
            }

            return enhanced_data

        except Exception as e:
            print(f"Error during AI enhancement: {e}")
            return self.workflow_data

    def _generate_description(self) -> str:
        """Generate a comprehensive description of the workflow."""
        try:
            if self._should_mock_api():
                return self._mock_description_api()

            workflow_name = self.workflow_data.get('name', 'Untitled Workflow')
            triggers = self._get_triggers_description()
            jobs = self._get_jobs_description()

            prompt = f"""
            Generate a comprehensive description for a GitHub Actions workflow with the following details:

            Workflow Name: {workflow_name}
            Triggers: {triggers}
            Jobs: {jobs}

            The description should explain the purpose and functionality of this workflow in 2-3 sentences.
            """

            return self._call_provider(prompt, max_tokens=200).strip()

        except Exception as e:
            print(f"Error generating description: {e}")
            return ""

    def _generate_best_practices(self) -> str:
        """Generate best practices for the workflow."""
        try:
            if self._should_mock_api():
                return self._mock_best_practices_api()

            # Generate prompt and call provider
            prompt = self._create_best_practices_prompt()
            return self._call_provider(prompt)

        except Exception as e:
            print(f"Error generating best practices: {e}")
            return ""

    def _generate_usage_information(self) -> str:
        """Generate usage information for the workflow."""
        try:
            if self._should_mock_api():
                return self._mock_usage_information_api()

            # Generate prompt and call provider
            prompt = self._create_usage_information_prompt()
            return self._call_provider(prompt)

        except Exception as e:
            print(f"Error generating implementation notes: {e}")
            return ""

    def _generate_usage_examples(self) -> str:
        """Generate usage examples for the workflow."""
        try:
            if self._should_mock_api():
                return self._mock_usage_examples_api()

            # Generate prompt and call provider
            prompt = self._create_usage_examples_prompt()
            return self._call_provider(prompt)

        except Exception as e:
            print(f"Error generating usage examples: {e}")
            return ""

    def _create_description_prompt(self) -> str:
        """Create prompt for generating workflow description."""
        workflow_name = self.workflow_data.get('name', '')
        triggers = [t['event_type'] for t in self.workflow_data.get('triggers', [])]
        trigger_details = []

        for trigger in self.workflow_data.get('triggers', []):
            event_type = trigger.get('event_type', '')
            if event_type:
                filter_info = []
                for filter_key, filter_value in trigger.get('filters', {}).items():
                    filter_info.append(f"{filter_key}: {filter_value}")
                trigger_details.append(f"{event_type} ({', '.join(filter_info) if filter_info else 'no filters'})")

        jobs = list(self.workflow_data['jobs'].keys())
        job_details = []

        # Extract details about each job to provide more context
        for job_id, job_data in self.workflow_data.get('jobs', {}).items():
            job_runs_on = job_data.get('runs_on', 'unspecified')
            job_steps = []
            for step in job_data.get('steps', []):
                step_name = step.get('name', '')
                step_uses = step.get('uses', '')
                step_run = step.get('run', '')
                if step_name:
                    job_steps.append(step_name)
                elif step_uses:
                    job_steps.append(f"uses: {step_uses.split('@')[0]}")
                elif step_run:
                    job_steps.append(f"run: {step_run[:30]}...")

            job_details.append(f"Job '{job_id}' runs on {job_runs_on} and has these steps: {', '.join(job_steps) if job_steps else 'no steps'}")

        # Get full workflow YAML for context
        full_yaml_content = self.workflow_data.get('raw_content', '')

        prompt = f"""
        Generate a comprehensive overview for a GitHub Actions workflow named "{workflow_name}".

        FULL WORKFLOW YAML (for detailed analysis):
        ```yaml
        {full_yaml_content}
        ```

        WORKFLOW TRIGGER DETAILS:
        This workflow is triggered by: {', '.join(trigger_details) if trigger_details else 'unknown triggers'}.

        WORKFLOW STRUCTURE:
        It contains the following jobs: {', '.join(jobs) if jobs else 'no defined jobs'}.

        JOB DETAILS:
        {chr(10).join(job_details) if job_details else 'No job details available'}

        TASK:
        1. First, analyze the FULL WORKFLOW YAML to understand the complete implementation details
        2. Next, analyze the trigger events, job names, and steps to determine what this workflow is doing
        3. Write a 3-5 sentence overview that clearly explains:
           - The primary purpose of this workflow (build, test, deploy, etc.)
           - What types of events cause it to run
           - What it accomplishes when it runs
           - Any notable dependencies or conditions

        Write in plain language that both technical and non-technical team members can understand.
        Focus on the practical business purpose - what problem does this workflow solve?
        """

        return prompt

    def _create_best_practices_prompt(self) -> str:
        """Create prompt for generating workflow best practices."""
        workflow_name = self.workflow_data.get('name', '')
        complexity = self.workflow_data.get('complexity_metrics', {}).get('complexity_score', 0)

        # Extract specific workflow characteristics to target recommendations
        jobs_count = len(self.workflow_data.get('jobs', {}))
        has_deploy_job = False
        uses_cache = False
        uses_secrets = False
        has_timeouts = False
        has_conditional_jobs = False
        matrices_used = False
        artifact_usage = False

        # Check for specific patterns in the workflow
        for job_id, job_data in self.workflow_data.get('jobs', {}).items():
            # Check for deployment jobs
            if 'deploy' in job_id.lower() or any('deploy' in str(step.get('name', '')).lower() for step in job_data.get('steps', [])):
                has_deploy_job = True

            # Check for conditional jobs
            if job_data.get('if_condition'):
                has_conditional_jobs = True

            # Check for matrix strategy
            if job_data.get('matrix'):
                matrices_used = True

            # Check for timeouts
            if job_data.get('timeout_minutes'):
                has_timeouts = True

            # Check for steps with specific patterns
            for step in job_data.get('steps', []):
                step_name = str(step.get('name', '')).lower()
                step_uses = str(step.get('uses', '')).lower()
                step_run = str(step.get('run', '')).lower()

                # Check for caching
                if 'cache' in step_uses or 'restore' in step_uses:
                    uses_cache = True

                # Check for secrets usage
                if '${{ secrets.' in step_run or 'secrets.' in step_run:
                    uses_secrets = True

                # Check for artifacts
                if 'artifact' in step_uses or 'download-artifact' in step_uses or 'upload-artifact' in step_uses:
                    artifact_usage = True

        # Get full workflow YAML for context
        full_yaml_content = self.workflow_data.get('raw_content', '')

        prompt = f"""
        Review the GitHub Actions workflow named "{workflow_name}" and provide SPECIFIC, tailored best practices or improvement suggestions.

        FULL WORKFLOW YAML (for detailed analysis):
        ```yaml
        {full_yaml_content}
        ```

        WORKFLOW DETAILS:
        - Number of jobs: {jobs_count}
        - Has deployment job: {"Yes" if has_deploy_job else "No"}
        - Uses caching: {"Yes" if uses_cache else "No"}
        - Uses secrets: {"Yes" if uses_secrets else "No"}
        - Has job timeouts: {"Yes" if has_timeouts else "No"}
        - Has conditional jobs: {"Yes" if has_conditional_jobs else "No"}
        - Uses matrix strategy: {"Yes" if matrices_used else "No"}
        - Uses artifacts: {"Yes" if artifact_usage else "No"}

        TASK:
        1. First, analyze the FULL WORKFLOW YAML to understand the complete implementation details
        2. Provide 3-5 specific, actionable best practices or improvements that would most benefit this particular workflow.

        RULES:
        1. Tailor suggestions to THIS specific workflow's characteristics - don't give generic advice
        2. Focus on the most impactful improvements based on the workflow structure
        3. If the workflow is missing important safeguards (timeouts, error handling), prioritize those
        4. If the workflow has deployment jobs, include security and validation suggestions
        5. If the workflow is simple, suggest enhancements that would make it more robust

        FORMAT:
        For each recommendation, provide:
        - What specific improvement to make
        - Why it matters for this workflow
        - A brief example or implementation hint
        """

        return prompt

    def _create_usage_information_prompt(self) -> str:
        """Create prompt for generating workflow usage information."""
        workflow_name = self.workflow_data.get('name', '')
        job_count = len(self.workflow_data.get('jobs', {}))
        execution_flow = self.workflow_data.get('execution_flow', [])
        max_chain = len(execution_flow) if execution_flow else 0

        # Extract triggers that would be useful for explaining usage
        triggers = self.workflow_data.get('triggers', [])
        trigger_details = []
        for trigger in triggers:
            event_type = trigger.get('event_type', '')
            if event_type:
                filter_info = []
                for filter_key, filter_value in trigger.get('filters', {}).items():
                    filter_info.append(f"{filter_key}: {filter_value}")
                trigger_details.append(f"{event_type} ({', '.join(filter_info) if filter_info else 'no filters'})")

        # Extract inputs that would be needed for using the workflow
        inputs = self.workflow_data.get('inputs', [])
        input_details = []
        for input_item in inputs:
            name = input_item.get('name', '')
            required = input_item.get('required', False)
            default = input_item.get('default', '')
            description = input_item.get('description', '')

            if name:
                detail = f"{name} ({'required' if required else 'optional'}"
                if default:
                    detail += f", default: {default}"
                if description:
                    detail += f", description: {description}"
                detail += ")"
                input_details.append(detail)

        # Extract job dependencies to understand the workflow structure
        job_dependencies = {}
        for job_id, job_data in self.workflow_data.get('jobs', {}).items():
            job_dependencies[job_id] = job_data.get('needs', [])

        # Extract notable tools and actions used
        tools_and_actions = {}
        environment_usage = []

        for job_id, job_data in self.workflow_data.get('jobs', {}).items():
            environment = job_data.get('environment')
            if environment:
                environment_usage.append(f"Job '{job_id}' uses environment: {environment}")

            for step in job_data.get('steps', []):
                uses = step.get('uses', '')
                if uses and '@' in uses:
                    action_name = uses.split('@')[0]
                    if action_name not in tools_and_actions:
                        tools_and_actions[action_name] = []
                    tools_and_actions[action_name].append(job_id)

        # Get full workflow YAML for context
        full_yaml_content = self.workflow_data.get('raw_content', '')

        prompt = f"""
        Analyze the GitHub Actions workflow named "{workflow_name}" and write COMPREHENSIVE USAGE INFORMATION
        that explains how to use this workflow effectively.

        FULL WORKFLOW YAML (for detailed analysis):
        ```yaml
        {full_yaml_content}
        ```

        WORKFLOW TRIGGERS:
        - Trigger events: {', '.join(trigger_details) if trigger_details else 'No triggers specified'}

        WORKFLOW INPUTS:
        - Available inputs: {', '.join(input_details) if input_details else 'No inputs available'}

        WORKFLOW STRUCTURE:
        - Job count: {job_count}
        - Maximum dependency chain: {max_chain} level(s)
        - Job dependencies: {job_dependencies}

        TASK:
        1. First, analyze the FULL WORKFLOW YAML to understand how this workflow is meant to be used
        2. Write 2-3 paragraphs focusing on:

           a. WHAT this workflow does and when someone should use it
           b. HOW to trigger this workflow (manually, automatically, or programmatically)
           c. Required and optional inputs with example values
           d. Expected outcomes and artifacts produced by the workflow
           e. Common use cases and scenarios for this workflow

        RULES:
        - Focus on practical usage information that helps users understand how to use the workflow
        - Provide concrete examples of how to trigger the workflow with sample values
        - Explain the purpose of each important input parameter
        - Describe what the user can expect when the workflow runs successfully
        - If the workflow is part of a larger process, explain how it fits into that process
        """

        return prompt

    def _create_usage_examples_prompt(self) -> str:
        """Create prompt for generating workflow usage examples."""
        workflow_name = self.workflow_data.get('name', '')

        # Get detailed input information
        inputs = self.workflow_data.get('inputs', [])
        input_details = []
        for input_item in inputs:
            name = input_item.get('name', '')
            required = input_item.get('required', False)
            default = input_item.get('default', '')
            description = input_item.get('description', '')

            if name:
                detail = f"{name} ({'required' if required else 'optional'}"
                if default:
                    detail += f", default: {default}"
                if description:
                    detail += f", description: {description}"
                detail += ")"
                input_details.append(detail)

        # Extract trigger information for more accurate examples
        triggers = []
        for trigger in self.workflow_data.get('triggers', []):
            event_type = trigger.get('event_type', '')
            if event_type:
                filter_info = []
                for filter_key, filter_value in trigger.get('filters', {}).items():
                    filter_info.append(f"{filter_key}: {filter_value}")
                triggers.append(f"{event_type} ({', '.join(filter_info) if filter_info else 'no filters'})")

        # Check if this is a reusable workflow
        is_reusable = 'on: workflow_call' in str(self.workflow_data)

        # Get full workflow YAML for context
        full_yaml_content = self.workflow_data.get('raw_content', '')

        prompt = f"""
        Create practical, ACCURATE usage examples for the GitHub Actions workflow named "{workflow_name}".

        FULL WORKFLOW YAML (for detailed analysis):
        ```yaml
        {full_yaml_content}
        ```

        WORKFLOW DETAILS:
        - Is reusable workflow: {"Yes" if is_reusable else "No"}
        - Trigger events: {', '.join(triggers) if triggers else 'Unknown triggers'}
        - Inputs: {', '.join(input_details) if input_details else 'No inputs'}

        TASK:
        1. First, analyze the FULL WORKFLOW YAML to understand the complete implementation details
        2. Create {1 if is_reusable else 2} realistic usage example(s) that would be immediately helpful to developers.

        FOR EACH EXAMPLE:
        1. Create a descriptive title that reflects a real-world use case
        2. Write a brief paragraph explaining WHEN and WHY someone would use this example
        3. Provide complete, syntactically correct YAML code that demonstrates how to:
           - {"Call this workflow from another workflow" if is_reusable else "Trigger this workflow manually or automatically"}
           - Include all required inputs with realistic values
           - Show proper syntax for the trigger event

        RULES:
        - Your examples must match the actual trigger mechanisms and inputs of THIS workflow
        - Use realistic parameter values that make sense for the workflow's purpose
        - Include comments in the YAML to explain key parts
        - If the workflow has no inputs or is triggered automatically, explain clearly how it fits into a CI/CD process
        """

        return prompt

    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API with the given prompt."""
        # Note: In a real implementation, we would use the OpenAI API
        # For this example, we'll just return a mock response
        print("Note: This is a mock implementation. In production, use OpenAI API.")
        time.sleep(1)  # Simulate API call
        return f"This would be generated by OpenAI using this prompt: {prompt[:50]}..."

    def _get_triggers_description(self) -> str:
        """Get a description of the workflow triggers."""
        triggers = []

        # Extract triggers from workflow data
        for trigger in self.workflow_data.get('triggers', []):
            if isinstance(trigger, dict):
                event_type = trigger.get('event_type', '')
                if event_type:
                    triggers.append(event_type)

        if not triggers:
            return "no specific triggers"
        elif len(triggers) == 1:
            return triggers[0]
        elif len(triggers) == 2:
            return f"{triggers[0]} and {triggers[1]}"
        else:
            return f"{', '.join(triggers[:-1])}, and {triggers[-1]}"

    def _get_jobs_description(self) -> str:
        """Get a description of the workflow jobs."""
        jobs = list(self.workflow_data.get('jobs', {}).keys())

        if not jobs:
            return "no defined jobs"
        elif len(jobs) == 1:
            return f"a single job named '{jobs[0]}'"
        elif len(jobs) == 2:
            return f"two jobs: '{jobs[0]}' and '{jobs[1]}'"
        else:
            if len(jobs) > 3:
                job_list = [f"'{j}'" for j in jobs[:3]]
                return f"{len(jobs)} jobs including {', '.join(job_list)}..."
            else:
                job_list = [f"'{j}'" for j in jobs]
                return f"{len(jobs)} jobs: {', '.join(job_list)}"

    def _should_mock_api(self) -> bool:
        """Determine if mock responses should be used instead of API calls."""
        # Use mock responses if no provider is available
        return not hasattr(self, 'provider') or self.provider.__class__.__name__ == "MockProvider"

    def _mock_description_api(self) -> str:
        """Mock description API response."""
        return self.provider.generate_text("Generate a description for this workflow")

    def _mock_best_practices_api(self) -> str:
        """Mock best practices API response."""
        return self.provider.generate_text("What are the best practice recommendations?")

    def _mock_usage_information_api(self) -> str:
        """Mock usage information API response."""
        return self.provider.generate_text("Give some usage information about this workflow")

    def _mock_usage_examples_api(self) -> str:
        """Mock usage examples API response."""
        return self.provider.generate_text("Something else")

    def _call_provider(self, prompt: str, max_tokens: int = 1000) -> str:
        print("\n[AI DEBUG] Provider:", type(self.provider).__name__)
        if hasattr(self.provider, 'model'):
            print("[AI DEBUG] Model:", getattr(self.provider, 'model', None))
        print("[AI DEBUG] Prompt sent to AI:\n", prompt.strip()[:1000], "...\n" if len(prompt) > 1000 else "\n")
        try:
            response = self.provider.generate_text(prompt, max_tokens=max_tokens)
            print("[AI DEBUG] Raw AI response:\n", response.strip()[:1000], "...\n" if len(response) > 1000 else "\n")
            return response
        except Exception as e:
            print(f"[AI DEBUG] Error during AI call: {e}")
            return ""
