.PHONY: format lint

format:
	black .
	isort .

lint:
	mypy .
	black . --check
	ruff check .
	isort . --check
	flake8 .

test:
	pytest tests