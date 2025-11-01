# Help & Utilities
# ----------------

.PHONY: help
help:  ## Show help
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: ensure-uv
ensure-uv:
	@command -v uv >/dev/null 2>&1 || { echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'; exit 1; }


# Environment Setup
# -----------------

.PHONY: install
install: ensure-uv clean  ## Install dependencies (frozen)
	uv sync --frozen

.PHONY: dev
dev: ensure-uv clean  ## Install all dependencies (dev mode)
	uv sync --dev

.PHONY: clean
clean:  ## Remove all build artifacts
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
	rm -rf dist build .coverage *.egg-info


# Development Workflows
# ---------------------

.PHONY: shell
shell: ensure-uv  ## Start Python REPL with project environment
	uv run python


# Code Quality
# ------------

.PHONY: format
format: ensure-uv  ## Format code
	uv run ruff format
	uv run ruff check --fix --fix-only

.PHONY: lint
lint: ensure-uv  ## Lint code
	uv run ruff format --check
	uv run ruff check

.PHONY: typecheck
typecheck: ensure-uv  ## Run type checking
	uv run mypy src


# Testing
# -------

.PHONY: test
test: ensure-uv  ## Run tests
	uv run pytest tests/

.PHONY: coverage
coverage: ensure-uv  ## Check test coverage
	uv run pytest --cov=src --cov-report=term-missing tests/


# Composite Checks
# ----------------

.PHONY: check
check: typecheck lint test  ## Run all checks


# Build & Release
# ---------------

.PHONY: build
build: ensure-uv clean check  ## Build package
	uv build
	ls -l dist
