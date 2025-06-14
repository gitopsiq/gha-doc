#!/bin/bash
# Script to test the GHA-DOC tool locally

# Ensure script is run from the gha-doc directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create a virtual environment
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create a test directory if it doesn't exist
mkdir -p test-output

# Create a test workflow file
mkdir -p test-workflows
cat > test-workflows/sample-workflow.yml <<EOF
name: Sample CI/CD Pipeline

# @description: This workflow handles CI/CD for the project
# @author: DevOps Team
# @version: 1.0.0

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

jobs:
  build:
    name: Build and Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test
      - name: Build
        run: npm run build

  deploy-staging:
    name: Deploy to Staging
    needs: build
    if: github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'staging'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to staging
        run: echo "Deploying to staging..."

  deploy-production:
    name: Deploy to Production
    needs: [build, deploy-staging]
    if: github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'production'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: echo "Deploying to production..."
EOF

# Run the gha-doc tool on the test workflow
echo "Running gha-doc tool..."
python src/main_improved.py --workflow-files "test-workflows/*.yml" --output-dir "test-output" --format "html" --generate-diagrams true --diagram-format "svg" --ai-enhancement true

# Check if the documentation was generated
if [ -f "test-output/sample-workflow.html" ] && [ -f "test-output/sample-workflow-diagram.svg" ]; then
  echo "Documentation generated successfully!"
  echo "Output files:"
  ls -la test-output/
else
  echo "Documentation generation failed!"
  exit 1
fi

# Open the documentation in the browser
if command -v xdg-open &> /dev/null; then
  xdg-open "test-output/sample-workflow.html"
elif command -v open &> /dev/null; then
  open "test-output/sample-workflow.html"
else
  echo "Documentation available at: $(pwd)/test-output/sample-workflow.html"
fi

# Deactivate the virtual environment
deactivate
