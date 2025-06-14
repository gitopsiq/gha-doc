# Contributing to GitHub Actions Documentation Generator

Thank you for your interest in contributing to the GitHub Actions Documentation Generator! This document provides guidelines and instructions for contributing to this project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Node.js (for Mermaid diagram generation)

### Setup for Development

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/gha-doc.git
   cd gha-doc
   ```
3. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Install Mermaid CLI for diagram rendering:
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```

## Development Workflow

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run tests to ensure your changes don't break existing functionality:
   ```bash
   pytest
   ```
4. Add and commit your changes:
   ```bash
   git add .
   git commit -m "Add a descriptive commit message"
   ```
5. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
6. Open a Pull Request against the main branch

## Testing

Run the test suite with:

```bash
pytest
```

For specific test files:

```bash
pytest tests/test_parser.py
```

## Code Style

This project uses:

- [Black](https://black.readthedocs.io/) for code formatting
- [isort](https://pycqa.github.io/isort/) for import sorting
- [flake8](https://flake8.pycqa.org/) for linting

You can run these tools manually:

```bash
black .
isort .
flake8
```

## Documentation

If you add new features or change existing functionality, please update the documentation accordingly.

## Questions?

Feel free to open an issue if you have questions or need clarification about contributing to the project.

Thank you for your contributions!
