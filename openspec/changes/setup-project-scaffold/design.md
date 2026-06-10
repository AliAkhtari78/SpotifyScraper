# Design: setup-project-scaffold

## Toolchain decisions

| Concern | Choice | Rationale |
|---|---|---|
| Package/dependency manager | uv (committed `uv.lock`) | Reproducible installs locally and in CI; replaces pip/venv/tox juggling |
| Build backend | hatchling | src-layout native; version read from `__init__.py` via `[tool.hatch.version]` |
| Lint + format | ruff (incl. `S` security rules) | One tool replaces black/isort/flake8/pylint; configured in `pyproject.toml` |
| Type checking | mypy `--strict`, CI-gated | Library ships `py.typed`; strictness from day one is cheap on an empty package |
| Tests | pytest, pytest-asyncio (auto mode), respx, pytest-cov, pytest-timeout | respx mocks httpx natively (sync + async); `addopts = -m "not live"` keeps the default run hermetic |
| Task runner | `uv run` + a small Makefile | CI matrix replaces tox; Makefile is muscle-memory glue (`make lint type test`) |
| Python floor | 3.10 (matrix 3.10–3.13) | 3.10 is supported until Oct 2026; floor moves to 3.11 in the first minor after that |

## Dependency policy

Core `dependencies = ["httpx>=0.27"]` — nothing else. Optional extras:

- `media`: `mutagen` (preview-MP3 cover embedding; replaces v2's abandoned eyeD3)
- `browser`: `playwright` (browser transport, added in a later change)
- `all`: union of the above

Dev tooling lives in `[dependency-groups]` (`dev`, and later `docs`), which uv installs by default for contributors but never ships.

## Package skeleton

```
src/spotify_scraper/
├── __init__.py     # __version__ = "3.0.0.dev0"
└── py.typed
tests/
├── unit/test_package.py   # imports package, asserts version shape
└── fixtures/              # salvaged v2 HTML/JSON fixtures (audited in later changes)
```

Sub-modules (`models/`, `http/`, `auth/`, `api/`, `media/`) arrive with their own OpenSpec changes; the scaffold deliberately ships no behavior.

## CI shape

One workflow, four jobs, all using `astral-sh/setup-uv` with `uv sync --locked`:

1. `lint` — `ruff check .` + `ruff format --check .`
2. `type` — `mypy src`
3. `test` — matrix {ubuntu × 3.10/3.11/3.12/3.13} + {macos, windows × 3.13}, `pytest --cov`
4. `build` — `uv build` + `twine check dist/*`

`--locked` makes lockfile drift a hard failure (ci-pipeline spec, "Reproducible CI environments").

## Agent/contributor onboarding

- `CLAUDE.md`: project map, architecture rules (sans-io core, one-dependency policy, two-tier extraction ladder), command reference, conventional-commit requirement, fixture-token hygiene rule.
- `.claude/settings.json`: allowlist for read-only and quality-gate commands; PostToolUse hook running `ruff format` on edited Python files.
- `CONTRIBUTING.md`: uv workflow, OpenSpec change process (propose → apply → archive), commit conventions.
- `.gitmessage`: conventional-commit template wired via `git config commit.template`.

## Alternatives considered

- **Poetry / PDM**: both viable; uv chosen for speed, lockfile-first CI, and zero extra config surface.
- **pyright instead of mypy**: pyright stays an editor-side helper; mypy `--strict` is the single CI gate to avoid double-reporting.
- **tox/nox**: redundant with a CI matrix + uv-managed environments.
