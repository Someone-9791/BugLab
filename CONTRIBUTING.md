# Contributing to BugLab

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites
- Python 3.10+
- Git
- Docker (for deployment testing)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/python-debug-env.git
cd python-debug-env

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Follow Python best practices (PEP 8)
- Add type hints where possible
- Update docstrings
- Include comments for complex logic

### 3. Test Your Changes

```bash
# Run the application locally
python -m server.app

# Run tests (when available)
pytest tests/

# Build Docker image locally
docker build -t python-debug-env:test .
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "Clear description of changes"
```

Follow conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `refactor:` for code refactoring
- `test:` for tests
- `chore:` for maintenance

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub with:
- Clear title and description
- Link to related issues
- Explanation of changes

## Coding Standards

### Python Style
- Follow PEP 8
- Use `black` for formatting
- Use `ruff` for linting
- Type hints for function signatures

### Documentation
- Update docstrings using Google style
- Update README.md if adding features
- Include examples for new features

### Commit Messages
- Clear and descriptive
- Use imperative mood ("Add feature" not "Added feature")
- Reference issues: "Fixes #123"

## Reporting Issues

When reporting a bug, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Relevant logs or error messages

## Pull Request Process

1. Ensure your code passes all checks
2. Update documentation as needed
3. Add yourself to CONTRIBUTORS.md (optional)
4. Ensure CI/CD pipeline passes
5. Request review from maintainers

## Questions?

Feel free to:
- Open an issue with the "question" label
- Ask in discussions
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the project's license (typically MIT or Apache 2.0).

Thank you for contributing! 🎉
