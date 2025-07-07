#!/bin/bash
# GitHub Actions Documentation Generator - Docker Build Script
# This script builds both the main and test Docker containers

# Use colors for output (properly escaped for echo -e)
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}GitHub Actions Documentation Generator - Docker Builder${NC}"
echo "------------------------------------------------"

# Ensure we're in the project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Build the main Docker container
echo -e "${YELLOW}Building main Docker container (gha-doc)...${NC}"
docker build -t gha-doc .

if [ $? -ne 0 ]; then
    echo -e "${RED}Main Docker build failed.${NC}"
    echo "Check the logs above for details."
    exit 1
fi

echo -e "${GREEN}Main Docker container built successfully!${NC}"

# Build the test Docker container
echo -e "${YELLOW}Building test Docker container (gha-doc-unit-tests)...${NC}"
docker build -t gha-doc-unit-tests -f Dockerfile.test .

if [ $? -ne 0 ]; then
    echo -e "${RED}Test Docker build failed.${NC}"
    echo "Check the logs above for details."
    exit 1
fi

echo -e "${GREEN}Test Docker container built successfully!${NC}"
echo -e "${GREEN}All Docker containers built successfully!${NC}"

echo ""
echo -e "${YELLOW}Available containers:${NC}"
echo "1. gha-doc - Main container for the GitHub Actions Documentation Generator"
echo "2. gha-doc-unit-tests - Container for running unit tests"
echo ""
echo -e "${YELLOW}To run tests, use ./run_tests.sh${NC}"
