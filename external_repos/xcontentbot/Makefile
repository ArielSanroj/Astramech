.PHONY: help install test lint format clean run

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests with coverage"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo "  make clean      - Clean cache files"
	@echo "  make run        - Run the bot"

install:
	pip install -r requirements.txt
	playwright install chromium
	pre-commit install

test:
	pytest --cov=. --cov-report=html --cov-report=term-missing

lint:
	flake8 . --max-line-length=120 --ignore=E203,W503
	mypy . --ignore-missing-imports

format:
	black .
	isort .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

run:
	python x_mcp.py & 
	sleep 2
	python x_client.py
