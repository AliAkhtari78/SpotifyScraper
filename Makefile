.PHONY: lint format type test cov live build all

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

type:
	uv run mypy src

test:
	uv run pytest

cov:
	uv run pytest --cov --cov-report=term-missing

live:
	uv run pytest -m live

build:
	uv build

all: lint type test
