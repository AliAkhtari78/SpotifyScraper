# SpotifyScraper Makefile
.PHONY: help install install-dev test lint format clean build docs docker

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PROJECT_NAME := spotify_scraper
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs

# Default target
help:
	@echo "SpotifyScraper Development Commands:"
	@echo "  make install       Install the package"
	@echo "  make install-dev   Install with development dependencies"
	@echo "  make test          Run all tests"
	@echo "  make test-cov      Run tests with coverage"
	@echo "  make lint          Run all linters"
	@echo "  make format        Format code with black and isort"
	@echo "  make clean         Clean build artifacts"
	@echo "  make build         Build distribution packages"
	@echo "  make docs          Build documentation"
	@echo "  make docker        Build Docker image"
	@echo "  make run-docker    Run Docker container"
	@echo "  make pre-commit    Install pre-commit hooks"
	@echo "  make update-deps   Update all dependencies"

# Installation
install:
	$(PIP) install --upgrade pip
	$(PIP) install -e .

install-dev:
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev,test,docs]"
	$(MAKE) pre-commit

# Testing
test:
	$(PYTHON) -m pytest $(TEST_DIR) -v

test-cov:
	$(PYTHON) -m pytest $(TEST_DIR) -v --cov=$(SRC_DIR)/$(PROJECT_NAME) --cov-report=html --cov-report=term

test-watch:
	$(PYTHON) -m pytest_watch $(TEST_DIR) -v# Linting and Formatting
lint:
	$(PYTHON) -m black --check $(SRC_DIR) $(TEST_DIR)
	$(PYTHON) -m isort --check-only $(SRC_DIR) $(TEST_DIR)
	$(PYTHON) -m flake8 $(SRC_DIR) $(TEST_DIR)
	$(PYTHON) -m pylint $(SRC_DIR)
	$(PYTHON) -m mypy $(SRC_DIR) --ignore-missing-imports
	$(PYTHON) -m bandit -r $(SRC_DIR) -f json

format:
	$(PYTHON) -m black $(SRC_DIR) $(TEST_DIR)
	$(PYTHON) -m isort $(SRC_DIR) $(TEST_DIR)

# Security
security:
	$(PYTHON) -m safety check
	$(PYTHON) -m pip_audit
	$(PYTHON) -m bandit -r $(SRC_DIR)

# Build
clean:
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/ .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	$(PYTHON) -m build

# Documentation
docs:
	cd $(DOCS_DIR) && make clean && make html
	@echo "Documentation built in $(DOCS_DIR)/_build/html"

docs-serve:
	cd $(DOCS_DIR) && python -m http.server --directory _build/html 8000

# Docker
docker:
	docker build -t $(PROJECT_NAME):latest .

docker-dev:
	docker-compose up -d dev

run-docker:
	docker run --rm -it $(PROJECT_NAME):latest

# Development
pre-commit:
	pre-commit install
	pre-commit install --hook-type commit-msgupdate-deps:
	$(PIP) install pip-upgrader
	pip-upgrade requirements.txt --skip-package-check
	pip-upgrade requirements-dev.txt --skip-package-check
	pip-upgrade docs/requirements.txt --skip-package-check

# CI/CD
ci: lint test security

release:
	@echo "Creating release..."
	@read -p "Version (e.g., v2.0.1): " version; \
	git tag -a $$version -m "Release $$version"; \
	git push origin $$version

# Development helpers
shell:
	$(PYTHON)

ipython:
	ipython

.DEFAULT_GOAL := help