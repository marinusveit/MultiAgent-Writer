# Build and Packaging Guide

This document explains how to build, package, and distribute MultiAgent-Writer.

## Quick Start

### Development Installation

```bash
# Clone repository
git clone <repository-url>
cd MultiAgent-Writer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate    # Windows

# Install in development mode
make install-dev
# or: pip install -e .[dev]
```

### Running the Application

```bash
# Using Makefile
make run

# Using command-line script
multiagent-writer

# Using Python module
python -m multiagent_writer.main

# Legacy launcher (for compatibility)
python run_new.py
```

## Project Structure

MultiAgent-Writer uses modern Python packaging with \`pyproject.toml\`:

```
MultiAgent-Writer/
├── pyproject.toml          # Package configuration (PEP 517/518)
├── Makefile                # Development task automation
├── src/
│   └── multiagent_writer/  # Main package
│       ├── __init__.py
│       ├── main.py         # Entry point
│       └── ...             # Submodules
├── .env.example            # Environment template
└── requirements.txt        # Legacy dependencies file
```

## Makefile Commands

The \`Makefile\` provides shortcuts for common development tasks:

### Installation

```bash
make install        # Install package (production)
make install-dev    # Install with dev dependencies
```

### Running

```bash
make run           # Launch the application
```

### Code Quality

```bash
make format        # Format code with Black
make lint          # Run Ruff and MyPy
```

### Testing

```bash
make test          # Run pytest with coverage
```

### Cleanup

```bash
make clean         # Remove build artifacts
```

## Package Configuration

### pyproject.toml

The \`pyproject.toml\` file defines:

- **Package metadata**: Name, version, description, authors
- **Dependencies**: PyQt6, requests, python-dotenv
- **Optional dependencies**: Dev tools (pytest, black, ruff, mypy)
- **Entry point**: \`multiagent-writer\` command
- **Tool configurations**: Black, Ruff, MyPy, Pytest

### Entry Point

The package provides a command-line entry point:

```toml
[project.scripts]
multiagent-writer = "multiagent_writer.main:main"
```

After installation, you can run:
```bash
multiagent-writer
```

## Development Workflow

### 1. Setup Environment

```bash
git clone <repository-url>
cd MultiAgent-Writer
python3 -m venv .venv
source .venv/bin/activate
make install-dev
```

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

### 3. Make Changes

Edit files in \`src/multiagent_writer/\`

### 4. Test Changes

```bash
make run           # Manual testing
```

### 5. Code Quality

```bash
make format        # Format code
make lint          # Check code quality
```

### 6. Commit

```bash
git add .
git commit -m "Your changes"
git push
```

## Dependencies

### Production Dependencies

- **PyQt6** (>=6.6.0) - GUI framework
- **requests** (>=2.31.0) - HTTP client
- **python-dotenv** (>=1.0.0) - Environment variables

### Development Dependencies

- **pytest** (>=7.4.0) - Testing framework
- **pytest-qt** (>=4.2.0) - PyQt6 testing support
- **pytest-cov** (>=4.1.0) - Coverage reporting
- **black** (>=23.0.0) - Code formatter
- **ruff** (>=0.1.0) - Fast linter
- **mypy** (>=1.7.0) - Type checker

## Troubleshooting

### "No module named 'multiagent_writer'"

**Solution**: Install in development mode:
```bash
pip install -e .
```

### "multiagent-writer: command not found"

**Solution**: Reinstall package:
```bash
pip uninstall multiagent-writer
pip install -e .
```

### PyQt6 Import Errors

**Solution**: Check Python version (requires 3.10+) and reinstall PyQt6:
```bash
python --version
pip install --force-reinstall PyQt6
```

## References

- [PEP 517](https://peps.python.org/pep-0517/) - Build system specification
- [PEP 518](https://peps.python.org/pep-0518/) - pyproject.toml specification
- [setuptools documentation](https://setuptools.pypa.io/)
