.PHONY: lint format check test pre-commit

# Run all linters
lint:
	@echo "Running flake8..."
	@.venv/bin/flake8 mytower/ --show-source --statistics

# Auto-fix formatting
format:
	@echo "Running black..."
	@.venv/bin/black mytower/ --line-length=120
	@echo "Running isort..."
	@.venv/bin/isort mytower/

# Run type checking
typecheck:
	@echo "Running mypy..."
	@.venv/bin/mypy mytower/

# Full check (lint + typecheck)
check: lint typecheck

# Run tests
test:
	@.venv/bin/pytest

# Run pre-commit hooks manually
pre-commit:
	@.venv/bin/pre-commit run --all-files

# Clean generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage coverage.xml .pytest_cache/ .mypy_cache/

# Install dev dependencies
install:
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e flake8_max_blank_lines/
	.venv/bin/pre-commit install

# Help
help:
	@echo "Available targets:"
	@echo "  make lint       - Run flake8 with detailed output"
	@echo "  make format     - Auto-format with black + isort"
	@echo "  make typecheck  - Run mypy type checker"
	@echo "  make check      - Run lint + typecheck"
	@echo "  make test       - Run pytest"
	@echo "  make pre-commit - Run pre-commit hooks manually"
	@echo "  make clean      - Remove generated files"
	@echo "  make install    - Install dependencies + hooks"
