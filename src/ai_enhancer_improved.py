#!/usr/bin/env python3
"""
AI Enhancement Module (Enhanced Version)

Enhances workflow documentation with AI-generated content using OpenAI API.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
import requests

class AIEnhancer:
    """Enhancer for workflow documentation using AI."""

    def __init__(self, workflow_data: Dict[str, Any], api_key: str = ""):
        """Initialize with analyzed workflow data and OpenAI API key."""
        self.workflow_data = workflow_data
        self.api_key = api_key
        self.openai_endpoint = "https://api.openai.com/v1/chat/completions"

    def enhance(self) -> Dict[str, Any]:
        """Enhance workflow documentation with AI-generated content."""
        if not self.api_key:
            print("Warning: No AI API key provided. Skipping AI enhancement.")
            return self.workflow_data

        try:
            enhanced_data = self.workflow_data.copy()

            # Add AI enhancements
            enhanced_data['ai_enhancement'] = {
                'description': self._generate_description(),
                'best_practices': self._generate_best_practices(),
                'implementation_notes': self._generate_implementation_notes(),
                'usage_examples': self._generate_usage_examples()
            }

            return enhanced_data

        except Exception as e:
            print(f"Error during AI enhancement: {e}")
            # Fall back to mock responses if the API fails
            return self._generate_fallback_enhancements()

    def _generate_description(self) -> str:
        """Generate a comprehensive description of the workflow."""
        try:
            # If no API key or running in test mode, use mock responses
            if self._should_mock_api():
                return self._mock_description_api()

            # Build prompt and call OpenAI API
            prompt = self._create_description_prompt()
            return self._call_openai_api(prompt)

        except Exception as e:
            print(f"Error generating description: {e}")
            return self._mock_description_api()

    def _generate_best_practices(self) -> str:
        """Generate best practices for the workflow."""
        try:
            if self._should_mock_api():
                return self._mock_best_practices_api()

            prompt = self._create_best_practices_prompt()
            return self._call_openai_api(prompt)

        except Exception as e:
            print(f"Error generating best practices: {e}")
            return self._mock_best_practices_api()

    def _generate_implementation_notes(self) -> str:
        """Generate implementation notes for the workflow."""
        try:
            if self._should_mock_api():
                return self._mock_implementation_notes_api()

            prompt = self._create_implementation_notes_prompt()
            return self._call_openai_api(prompt)

        except Exception as e:
            print(f"Error generating implementation notes: {e}")
            return self._mock_implementation_notes_api()

    def _generate_usage_examples(self) -> str:
        """Generate usage examples for the workflow."""
        try:
            if self._should_mock_api():
                return self._mock_usage_examples_api()

            prompt = self._create_usage_examples_prompt()
            return self._call_openai_api(prompt)

        except Exception as e:
            print(f"Error generating usage examples: {e}")
            return self._mock_usage_examples_api()

    def _create_description_prompt(self) -> str:
        """Create prompt for generating workflow description."""
        workflow_name = self.workflow_data.get('name', '')
        triggers = [t['event_type'] for t in self.workflow_data.get('triggers', [])]
        jobs = list(self.workflow_data['jobs'].keys())

        prompt = f"""
        Generate a comprehensive description for a GitHub Actions workflow named "{workflow_name}".

        This workflow is triggered by: {', '.join(triggers)}.

        It contains the following jobs: {', '.join(jobs)}.

        The workflow appears to be for: (analyze the jobs and steps to determine the purpose).

        Write a 2-3 sentence description that clearly explains what this workflow does,
        without using technical jargon. Focus on the business purpose of the workflow.
        """

        return prompt

    def _create_best_practices_prompt(self) -> str:
        """Create prompt for generating workflow best practices."""
        workflow_name = self.workflow_data.get('name', '')
        complexity = self.workflow_data.get('complexity_metrics', {}).get('complexity_score', 0)

        prompt = f"""
        Review the GitHub Actions workflow named "{workflow_name}" and suggest 3-5
        best practices or potential improvements.

        The workflow has a complexity score of {complexity}.

        Examples of best practices:
        1. Add timeouts to prevent long-running jobs
        2. Use environment secrets instead of repository secrets
        3. Add status checks before deployment
        4. Use composite actions for repeated steps
        5. Optimize caching for faster builds

        Provide specific, actionable suggestions that would improve this workflow.
        """

        return prompt

    def _create_implementation_notes_prompt(self) -> str:
        """Create prompt for generating workflow implementation notes."""
        workflow_name = self.workflow_data.get('name', '')
        job_count = len(self.workflow_data['jobs'])
        execution_flow = self.workflow_data.get('execution_flow', [])
        max_chain = len(execution_flow)

        prompt = f"""
        Analyze the GitHub Actions workflow named "{workflow_name}" and write implementation notes
        that explain the design patterns and architectural decisions.

        The workflow has {job_count} jobs with a maximum dependency chain of {max_chain} levels.

        Explain:
        1. The overall architecture of the workflow
        2. Any interesting patterns or techniques used
        3. How the workflow ensures reliability and correctness
        4. The separation of concerns between different jobs

        Write 1-2 paragraphs of technical insight that would help a developer understand
        the design decisions in this workflow.
        """

        return prompt

    def _create_usage_examples_prompt(self) -> str:
        """Create prompt for generating workflow usage examples."""
        workflow_name = self.workflow_data.get('name', '')
        inputs = self.workflow_data.get('inputs', [])
        input_names = [i['name'] for i in inputs]

        prompt = f"""
        Create 1-2 practical usage examples for the GitHub Actions workflow named "{workflow_name}".

        The workflow accepts these inputs: {', '.join(input_names) if input_names else 'No inputs'}.

        For each example, include:
        1. A title describing the use case
        2. A brief explanation of when to use this example
        3. The actual YAML code for triggering the workflow

        Make the examples realistic and practical for someone who wants to use this workflow.
        """

        return prompt

    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API with the given prompt."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required but not provided")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a GitHub Actions documentation assistant. Your task is to provide clear, concise, and helpful information about GitHub Actions workflows."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        try:
            response = requests.post(self.openai_endpoint, headers=headers, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors

            response_data = response.json()
            if 'choices' in response_data and len(response_data['choices']) > 0:
                return response_data['choices'][0]['message']['content'].strip()
            else:
                raise ValueError("Unexpected response format from OpenAI API")

        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenAI API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status code: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            raise

    def _should_mock_api(self) -> bool:
        """Determine if we should use mock API responses."""
        # Use mock responses if no API key is provided or if MOCK_AI_API env var is set
        return not self.api_key or os.environ.get("MOCK_AI_API", "").lower() == "true"

    def _mock_description_api(self) -> str:
        """Mock API response for workflow description."""
        workflow_name = self.workflow_data.get('name', '')

        descriptions = {
            "Examples Action": "This workflow orchestrates the complete infrastructure lifecycle for Terraform examples, managing building, planning, applying, and destroying resources. It implements a sophisticated parallelism strategy to optimize deployment performance while ensuring resources with potential conflicts are never deployed simultaneously.",
            "Deploy Container": "This workflow automates the deployment of containerized applications to Azure Container Instances. It handles building, testing, and deploying containers with proper error handling and notifications.",
            "Run Tests": "This workflow runs automated tests for the codebase whenever changes are pushed or a pull request is created. It ensures code quality by executing unit tests, integration tests, and linting checks."
        }

        return descriptions.get(workflow_name, "This workflow automates CI/CD processes to improve development efficiency and ensure consistent deployments. It handles building, testing, and deploying code in a controlled and repeatable manner.")

    def _mock_best_practices_api(self) -> str:
        """Mock API response for best practices."""
        return """Consider implementing the following best practices:

1. Add timeouts to prevent long-running jobs from consuming excessive resources
2. Use environment secrets instead of repository secrets for better security isolation
3. Add status checks before critical deployment steps
4. Implement a retry mechanism for network-dependent operations
5. Add comprehensive error handling with detailed error messages"""

    def _mock_implementation_notes_api(self) -> str:
        """Mock API response for implementation notes."""
        return """This workflow implements a sophisticated two-step parallelism strategy that optimizes deployment performance while preventing resource conflicts. The matrix-based job generation allows flexible scaling from small to large deployments, while the concurrency group mechanism ensures that resources with potential conflicts deploy sequentially. The isolation between prepare, build/plan, apply and destroy phases follows infrastructure-as-code best practices by separating read and write operations.

The workflow's event-driven behavior adapts intelligently to different use cases: using tests for PRs, specific directories for feature branches, and configurable patterns for manual execution. This design pattern benefits from consistent naming of workflow files and clear documentation of dependencies between jobs."""

    def _mock_usage_examples_api(self) -> str:
        """Mock API response for usage examples."""
        return """Example 1: Deploy to Development Environment

This example shows how to manually trigger the workflow to deploy resources to the development environment:

```yaml
name: Deploy to Development
on:
  workflow_dispatch:
    inputs:
      branch:
        description: "Branch to deploy"
        required: true
        default: "develop"
      folder_pattern:
        description: "Resources to deploy"
        required: true
        default: "examples/corp/**"
      do-destroy:
        description: "Destroy after testing"
        type: boolean
        default: true
```

Example 2: Automated Nightly Deployment

This example runs the workflow nightly to ensure infrastructure remains consistent:

```yaml
name: Nightly Infrastructure Validation
on:
  schedule:
    - cron: '0 2 * * *'  # Runs at 2 AM every day
jobs:
  trigger-workflow:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger deployment workflow
        uses: benc-uk/workflow-dispatch@v1
        with:
          workflow: Examples Action
          inputs: '{"branch": "main", "folder_pattern": "examples/**", "do-destroy": true}'
```"""

    def _generate_fallback_enhancements(self) -> Dict[str, Any]:
        """Generate fallback enhancements in case of API failure."""
        enhanced_data = self.workflow_data.copy()

        enhanced_data['ai_enhancement'] = {
            'description': self._mock_description_api(),
            'best_practices': self._mock_best_practices_api(),
            'implementation_notes': self._mock_implementation_notes_api(),
            'usage_examples': self._mock_usage_examples_api()
        }

        return enhanced_data
