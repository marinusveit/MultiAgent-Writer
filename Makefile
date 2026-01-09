.PHONY: help install install-dev test lint format clean run

help:
	@echo "Available commands:"
	@echo "  make install       - Install package in production mode"
	@echo "  make install-dev   - Install package with dev dependencies"
	@echo "  make test          - Run tests with coverage"
	@echo "  make lint          - Run linters (ruff, mypy)"
	@echo "  make format        - Format code with black"
	@echo "  make clean         - Remove build artifacts"
	@echo "  make run           - Run the application"

install:
	pip install -e .

install-dev:
	pip install -e .[dev]

test:
	pytest

lint:
	ruff check src/
	mypy src/

format:
	black src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache/ .coverage htmlcov/ .mypy_cache/ .ruff_cache/

run:
	python -m multiagent_writer.main
