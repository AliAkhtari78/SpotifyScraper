# dev-tooling

## ADDED Requirements

### Requirement: Unified lint and format tooling

The project SHALL use ruff as the only linter and formatter, configured in `pyproject.toml`, with security (`S`) rules enabled for `src/`.

#### Scenario: Lint gate

- **WHEN** `uv run ruff check .` and `uv run ruff format --check .` run on a clean checkout
- **THEN** both exit with status 0

### Requirement: Strict static typing

All code under `src/` SHALL pass `mypy --strict`.

#### Scenario: Type gate

- **WHEN** `uv run mypy src` runs
- **THEN** it reports no errors

### Requirement: Hermetic test suite by default

`uv run pytest` SHALL run only hermetic tests (no network). Tests requiring live Spotify access SHALL be marked `live` and excluded by default configuration.

#### Scenario: Default run is offline

- **WHEN** `uv run pytest` runs with networking disabled
- **THEN** all collected tests pass

#### Scenario: Live tests are opt-in

- **WHEN** `uv run pytest -m live` runs
- **THEN** only tests marked `live` are collected

### Requirement: Coverage floor

The test suite SHALL enforce a minimum of 85% line coverage over `src/` when run with coverage enabled.

#### Scenario: Coverage regression

- **WHEN** coverage of `src/` drops below 85% in a coverage-enabled run
- **THEN** the test command exits non-zero

### Requirement: Pre-commit quality hooks

The repository SHALL provide a `.pre-commit-config.yaml` running ruff (lint + format), codespell, YAML/TOML validation, and conventional-commit message enforcement.

#### Scenario: Bad commit message rejected

- **WHEN** a commit message that does not follow Conventional Commits is committed with hooks installed
- **THEN** the commit-msg hook rejects it
