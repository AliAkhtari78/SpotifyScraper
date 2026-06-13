.PHONY: dev lint format type test cov live build all

# Set up (or repair) the local dev environment. On macOS, uv can leave the
# UF_HIDDEN flag on the venv's *.pth files; CPython's site module silently
# skips hidden .pth files, which breaks `uv run python -c "import ..."`.
# Clearing the flag restores ad-hoc imports. Harmless no-op on Linux.
dev:
	uv sync
	-command -v chflags >/dev/null 2>&1 && chflags nohidden .venv/lib/python*/site-packages/*.pth 2>/dev/null || true

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
