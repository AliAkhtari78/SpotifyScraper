# Proposal: setup-project-scaffold

## Why

The v3.0.0 clean-room rewrite needs a modern, minimal foundation before any feature work: v2 accumulated 17 CI workflows, ~17 runtime dependencies, duplicated build configs (setup.py + setup.cfg + pyproject.toml), and scattered tool configs that made the project unmaintainable. Every subsequent change builds on this scaffold.

## What Changes

- **BREAKING**: v2 packaging (setup.py/setup.cfg/requirements*.txt) is replaced by a single `pyproject.toml` with hatchling and uv-locked dependencies.
- New `src/spotify_scraper/` package skeleton shipping `py.typed`, version `3.0.0.dev0`.
- One quality toolchain: ruff (lint + format, security rules), mypy strict, pytest (+asyncio, +respx, +cov), pre-commit with conventional-commit enforcement.
- Single `ci.yml` workflow (lint, type-check, test matrix on Python 3.10–3.13, build) replacing v2's 17 workflows.
- Contributor and agent onboarding: `CONTRIBUTING.md`, `CLAUDE.md`, `.claude/settings.json`, `.gitmessage`.
- Core runtime dependency policy: `httpx` only; everything else is an optional extra.

## Capabilities

### New Capabilities

- `packaging`: installable `spotifyscraper` distribution — metadata, version single-sourcing, optional extras, typed-package marker
- `dev-tooling`: local quality gates — lint, format, type-check, test, coverage, pre-commit hooks
- `ci-pipeline`: automated checks on every PR and push — lint/type/test/build across supported Python versions

### Modified Capabilities

(none — first change of the v3 rewrite)

## Impact

- Repo root: new `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml`, `Makefile`, `.gitignore` (rewritten), `CONTRIBUTING.md`, `CLAUDE.md`, `.gitmessage`, `.claude/settings.json`
- New `src/spotify_scraper/` and `tests/` skeletons
- New `.github/workflows/ci.yml`
- No runtime behavior yet — the package imports and exposes `__version__` only
