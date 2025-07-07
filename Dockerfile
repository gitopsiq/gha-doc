# Dockerfile for GitHub Actions Documentation Generator
FROM mcr.microsoft.com/playwright:v1.52.0-jammy

# Install Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up a working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional Node.js dependencies
RUN npm install -g @mermaid-js/mermaid-cli

# Install Playwright browsers
# The base image already has browsers installed, but we need to ensure our Python package can use them
RUN python3 -m playwright install chromium && \
    python3 -m playwright install-deps chromium

# Copy the application
COPY src/ ./src/
COPY action.yml .

# Create directories for output
# Create a standard workdir for mounting repositories
RUN mkdir -p /workdir

# Set the entrypoint
ENTRYPOINT ["python3", "/app/src/main.py"]

# Default command (can be overridden)
CMD ["--help"]
