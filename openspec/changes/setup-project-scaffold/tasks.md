# Tasks: setup-project-scaffold

## 1. Packaging

- [x] 1.1 Write `pyproject.toml`: hatchling backend, project metadata, `httpx` core dependency, `media`/`browser`/`all` extras, `dev` dependency group, ruff/mypy/pytest/coverage config
- [x] 1.2 Create `src/spotify_scraper/__init__.py` (`__version__ = "3.0.0.dev0"`) and `py.typed`
- [x] 1.3 Generate `uv.lock` and verify `uv build` produces wheel + sdist

## 2. Dev tooling

- [x] 2.1 Rewrite `.gitignore` for a modern Python project
- [x] 2.2 Write `.pre-commit-config.yaml` (ruff, ruff-format, codespell, yaml/toml checks, conventional-pre-commit)
- [x] 2.3 Write `Makefile` (`lint`, `format`, `type`, `test`, `cov`, `build`)
- [x] 2.4 Add placeholder test `tests/unit/test_package.py`; move salvaged fixtures under `tests/fixtures/`
- [x] 2.5 Verify gates: `ruff check`, `ruff format --check`, `mypy src`, `pytest` all green

## 3. CI

- [x] 3.1 Write `.github/workflows/ci.yml` (lint, type, test matrix, build; uv `--locked`)

## 4. Onboarding

- [x] 4.1 Write `CLAUDE.md` with project map, architecture rules, and command reference
- [x] 4.2 Write `.claude/settings.json` (permissions allowlist + ruff PostToolUse hook)
- [x] 4.3 Write `CONTRIBUTING.md` (uv workflow, OpenSpec process, conventional commits)
- [x] 4.4 Write `.gitmessage` commit template
