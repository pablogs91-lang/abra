.PHONY: help install install-dev run test lint format clean build

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install package in production mode
	pip install -e .

install-dev:  ## Install package in development mode with dev dependencies
	pip install -e ".[dev]"

run:  ## Run Streamlit app
	streamlit run app.py

test:  ## Run tests
	pytest tests/ -v

lint:  ## Run linters
	flake8 abra/ --max-line-length=100
	mypy abra/ --ignore-missing-imports

format:  ## Format code with black
	black abra/ tests/ app.py

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build distribution packages
	python -m build

upload-test:  ## Upload to TestPyPI
	python -m twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	python -m twine upload dist/*
