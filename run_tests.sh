#!/bin/bash
# GitHub Actions Documentation Generator - Docker Test Script
# This script runs tests using Docker containers that are already built

# Use colors for output (properly escaped for echo -e)
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}GitHub Actions Documentation Generator - Docker Test Suite${NC}"
echo "------------------------------------------------"

# Ensure we're in the project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Docker images exist
if ! docker image inspect gha-doc &>/dev/null; then
    echo -e "${RED}The gha-doc Docker image does not exist!${NC}"
    echo -e "Please run ${YELLOW}./build.sh${NC} first to build the Docker containers."
    exit 1
fi

if ! docker image inspect gha-doc-unit-tests &>/dev/null; then
    echo -e "${RED}The gha-doc-unit-tests Docker image does not exist!${NC}"
    echo -e "Please run ${YELLOW}./build.sh${NC} first to build the Docker containers."
    exit 1
fi

# Display test options
echo -e "${YELLOW}Select a test mode:${NC}"
echo "1. Run standard Docker container tests (recommended)"
echo "2. Run tests with OpenAI API integration"
echo "3. Run tests with Azure OpenAI API integration"
echo "4. Run tests with Anthropic Claude API integration"
echo "5. Run tests with Hugging Face API integration"
echo "6. Run tests with Google AI API integration"
echo "7. Run tests with AWS Bedrock API integration"
echo "8. Run Python unit tests in container"
echo "9. Run all tests (container tests + unit tests)"
read -p "Enter your choice (1-9): " TEST_MODE

# Initialize variables
USE_AI_API=false
AI_PROVIDER="mock"
RUN_UNIT_TESTS=false
RUN_CONTAINER_TESTS=true

# Process test mode selection
case $TEST_MODE in
    2)
        # Configure for OpenAI
        AI_PROVIDER="openai"
        # Check if OPENAI_API_KEY is already set in the environment
        if [[ -n "$OPENAI_API_KEY" ]]; then
            USE_AI_API=true
            echo -e "${GREEN}Using OpenAI API Key from environment. Will test with actual API calls.${NC}"
        else
            # Get OpenAI API Key from user
            echo -e "${YELLOW}Enter your OpenAI API Key:${NC} "
            read -s OPENAI_API_KEY
            if [[ -n "$OPENAI_API_KEY" ]]; then
                export OPENAI_API_KEY
                USE_AI_API=true
                echo -e "${GREEN}OpenAI API Key provided. Will test with actual API calls.${NC}"
            else
                echo -e "${RED}No API key provided. Running standard tests.${NC}"
            fi
        fi
        ;;
    3)
        # Configure for Azure OpenAI
        AI_PROVIDER="azure_openai"
        echo -e "${YELLOW}Enter your Azure OpenAI API Key:${NC} "
        read -s AZURE_OPENAI_API_KEY
        echo -e "${YELLOW}Enter your Azure OpenAI Endpoint URL:${NC} "
        read AZURE_OPENAI_ENDPOINT
        echo -e "${YELLOW}Enter your Azure OpenAI Deployment Name:${NC} "
        read AZURE_OPENAI_DEPLOYMENT
        if [[ -n "$AZURE_OPENAI_API_KEY" && -n "$AZURE_OPENAI_ENDPOINT" && -n "$AZURE_OPENAI_DEPLOYMENT" ]]; then
            export AZURE_OPENAI_API_KEY
            export AZURE_OPENAI_ENDPOINT
            export AZURE_OPENAI_DEPLOYMENT
            USE_AI_API=true
            echo -e "${GREEN}Azure OpenAI credentials provided. Will test with actual API calls.${NC}"
        else
            echo -e "${RED}Missing Azure OpenAI credentials. Running standard tests.${NC}"
        fi
        ;;
    4)
        # Configure for Anthropic
        AI_PROVIDER="anthropic"
        echo -e "${YELLOW}Enter your Anthropic API Key:${NC} "
        read -s ANTHROPIC_API_KEY
        if [[ -n "$ANTHROPIC_API_KEY" ]]; then
            export ANTHROPIC_API_KEY
            USE_AI_API=true
            echo -e "${GREEN}Anthropic API Key provided. Will test with actual API calls.${NC}"
        else
            echo -e "${RED}No API key provided. Running standard tests.${NC}"
        fi
        ;;
    5)
        # Configure for Hugging Face
        AI_PROVIDER="hf"
        echo -e "${YELLOW}Enter your Hugging Face API Key:${NC} "
        read -s HF_API_KEY
        if [[ -n "$HF_API_KEY" ]]; then
            export HF_API_KEY
            USE_AI_API=true
            echo -e "${GREEN}Hugging Face API Key provided. Will test with actual API calls.${NC}"
        else
            echo -e "${RED}No API key provided. Running standard tests.${NC}"
        fi
        ;;
    6)
        # Configure for Google AI
        AI_PROVIDER="google"
        echo -e "${YELLOW}Enter your Google AI API Key:${NC} "
        read -s GOOGLE_API_KEY
        if [[ -n "$GOOGLE_API_KEY" ]]; then
            export GOOGLE_API_KEY
            USE_AI_API=true
            echo -e "${GREEN}Google AI API Key provided. Will test with actual API calls.${NC}"
        else
            echo -e "${RED}No API key provided. Running standard tests.${NC}"
        fi
        ;;
    7)
        # Configure for AWS Bedrock
        AI_PROVIDER="aws"
        echo -e "${YELLOW}Enter your AWS Access Key ID:${NC} "
        read -s AWS_API_KEY
        echo -e "${YELLOW}Enter your AWS Secret Access Key:${NC} "
        read -s AWS_SECRET_KEY
        echo -e "${YELLOW}Enter AWS Region (or press Enter for us-east-1):${NC} "
        read AWS_REGION
        AWS_REGION=${AWS_REGION:-"us-east-1"}
        if [[ -n "$AWS_API_KEY" && -n "$AWS_SECRET_KEY" ]]; then
            export AWS_API_KEY
            export AWS_SECRET_KEY
            export AWS_REGION
            USE_AI_API=true
            echo -e "${GREEN}AWS credentials provided. Will test with actual API calls.${NC}"
        else
            echo -e "${RED}Missing AWS credentials. Running standard tests.${NC}"
        fi
        ;;
    8)
        RUN_UNIT_TESTS=true
        RUN_CONTAINER_TESTS=false
        ;;
    9)
        RUN_UNIT_TESTS=true
        ;;
    *)
        echo -e "${YELLOW}Running standard Docker tests.${NC}"
        ;;
esac

# Always generate both HTML and Markdown (no prompt)
OUTPUT_FORMATS="markdown,html"

# Run unit tests if selected
if [[ "$RUN_UNIT_TESTS" == true ]]; then
    echo -e "${YELLOW}Running Python unit tests in container...${NC}"

    # Run the unit tests
    echo -e "${YELLOW}Executing unit tests...${NC}"
    docker run --rm gha-doc-unit-tests

    TEST_EXIT_CODE=$?

    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}Unit tests passed successfully!${NC}"
    else
        echo -e "${RED}Unit tests failed.${NC}"
        if [[ "$RUN_CONTAINER_TESTS" == false ]]; then
            exit 1
        fi
    fi
fi

# Run container tests if selected
if [[ "$RUN_CONTAINER_TESTS" == true ]]; then
    echo -e "${YELLOW}Testing container with sample workflow...${NC}"

    # Create test directory if it doesn't exist
    mkdir -p test-workspace/.github/workflows
    mkdir -p test-workspace/docs

    # Create a sample workflow file if it doesn't exist
    if [[ ! -f "test-workspace/.github/workflows/test-workflow.yml" ]]; then
        cat > test-workspace/.github/workflows/test-workflow.yml << 'EOF'
name: Test Workflow
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: echo "Deploying to production..."
EOF
    fi

    # Set up docker command with or without AI
    if [[ "$USE_AI_API" == true ]]; then
        # Base docker run command
        DOCKER_CMD="docker run -v $(pwd)/test-workspace:/workdir"

        # Add environment variables based on provider
        case $AI_PROVIDER in
            "openai")
                DOCKER_CMD="$DOCKER_CMD -e OPENAI_API_KEY=$OPENAI_API_KEY"
                API_KEY_PARAM="--openai-api-key $OPENAI_API_KEY"
                # Specify OpenAI model if using OpenAI provider
                DOCKER_CMD="$DOCKER_CMD -e OPENAI_MODEL=gpt-4-1106-preview"
                API_KEY_PARAM="$API_KEY_PARAM --openai-model gpt-4-1106-preview"
                ;;
            "azure_openai")
                DOCKER_CMD="$DOCKER_CMD -e AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY -e AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT -e AZURE_OPENAI_DEPLOYMENT=$AZURE_OPENAI_DEPLOYMENT"
                API_KEY_PARAM="--azure-openai-api-key $AZURE_OPENAI_API_KEY --azure-openai-endpoint $AZURE_OPENAI_ENDPOINT --azure-openai-deployment $AZURE_OPENAI_DEPLOYMENT"
                ;;
            "anthropic")
                DOCKER_CMD="$DOCKER_CMD -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
                API_KEY_PARAM="--anthropic-api-key $ANTHROPIC_API_KEY"
                ;;
            "hf")
                DOCKER_CMD="$DOCKER_CMD -e HF_API_KEY=$HF_API_KEY"
                API_KEY_PARAM="--hf-api-key $HF_API_KEY"
                ;;
            "google")
                DOCKER_CMD="$DOCKER_CMD -e GOOGLE_API_KEY=$GOOGLE_API_KEY"
                API_KEY_PARAM="--google-api-key $GOOGLE_API_KEY"
                ;;
            "aws")
                DOCKER_CMD="$DOCKER_CMD -e AWS_API_KEY=$AWS_API_KEY -e AWS_SECRET_KEY=$AWS_SECRET_KEY -e AWS_REGION=$AWS_REGION"
                API_KEY_PARAM="--aws-api-key $AWS_API_KEY --aws-secret-key $AWS_SECRET_KEY --aws-region $AWS_REGION"
                ;;
        esac

        # Run with API key for selected format(s)
        echo -e "${YELLOW}Running Docker container with AI enhancement using $AI_PROVIDER provider...${NC}"
        eval "$DOCKER_CMD \
            gha-doc \
            --workflow-files '/workdir/.github/workflows/*.yml' \
            --output-dir '/workdir/docs' \
            --formats '$OUTPUT_FORMATS' \
            --include-diagram-type 'png' \
            --include-ai-suggested-improvements \
            --include-ai-usage-information \
            --ai-provider '$AI_PROVIDER' \
            $API_KEY_PARAM"
    else
        # Run without API key for selected format(s)
        docker run -v "$(pwd)/test-workspace:/workdir" gha-doc \
            --workflow-files "/workdir/.github/workflows/*.yml" \
            --output-dir "/workdir/docs" \
            --formats "$OUTPUT_FORMATS" \
            --include-diagram-type "png"
    fi

    # Check results
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Container test successful!${NC}"
        echo "Generated documentation can be found in test-workspace/docs/"
        ls -la test-workspace/docs/

        # Optionally open the documentation in browser
        echo -e "${YELLOW}Would you like to view the generated documentation? (y/n)${NC} "
        read VIEW_DOCS
        if [[ "$VIEW_DOCS" == "y" || "$VIEW_DOCS" == "Y" ]]; then
            if command -v xdg-open &> /dev/null; then
                # Fixed xdg-open command - now correctly pointing to the directory without "--"
                xdg-open "$(pwd)/test-workspace/docs"
            elif command -v open &> /dev/null; then
                open "$(pwd)/test-workspace/docs"
            else
                echo "Documentation available at: $(pwd)/test-workspace/docs/"
            fi
        fi
    else
        echo -e "${RED}Container test failed.${NC}"
        echo "Check the logs above for details."
        exit 1
    fi
fi

# Cleanup
if [[ "$USE_AI_API" == true ]]; then
    case $AI_PROVIDER in
        "openai")
            unset OPENAI_API_KEY
            echo -e "${GREEN}Cleared OpenAI API Key from environment.${NC}"
            ;;
        "azure_openai")
            unset AZURE_OPENAI_API_KEY
            unset AZURE_OPENAI_ENDPOINT
            unset AZURE_OPENAI_DEPLOYMENT
            echo -e "${GREEN}Cleared Azure OpenAI credentials from environment.${NC}"
            ;;
        "anthropic")
            unset ANTHROPIC_API_KEY
            echo -e "${GREEN}Cleared Anthropic API Key from environment.${NC}"
            ;;
        "hf")
            unset HF_API_KEY
            echo -e "${GREEN}Cleared Hugging Face API Key from environment.${NC}"
            ;;
        "google")
            unset GOOGLE_API_KEY
            echo -e "${GREEN}Cleared Google AI API Key from environment.${NC}"
            ;;
        "aws")
            unset AWS_API_KEY
            unset AWS_SECRET_KEY
            unset AWS_REGION
            echo -e "${GREEN}Cleared AWS credentials from environment.${NC}"
            ;;
    esac
fi

echo -e "${GREEN}Testing complete!${NC}"
