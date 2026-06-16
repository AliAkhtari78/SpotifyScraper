# ci-pipeline Specification

## Purpose

Continuous integration: lint, type-check, and test across supported Python versions and OSes.

## Requirements
### Requirement: Quality gates on every change

A single `ci.yml` GitHub Actions workflow SHALL run on every pull request and on pushes to `master` and `v3`, with jobs for lint (ruff check + format check), type check (mypy strict), tests, and package build.

#### Scenario: Pull request validation

- **WHEN** a pull request is opened against `v3`
- **THEN** lint, type, test, and build jobs all run and must pass before merge

### Requirement: Python version matrix

The test job SHALL run on CPython 3.10, 3.11, 3.12, and 3.13 on Linux, and on 3.13 on macOS and Windows.

#### Scenario: Matrix coverage

- **WHEN** the CI workflow completes on a pull request
- **THEN** test results exist for all six matrix combinations

### Requirement: Reproducible CI environments

CI SHALL install dependencies with uv from the committed `uv.lock`.

#### Scenario: Lockfile drift

- **WHEN** `pyproject.toml` dependencies and `uv.lock` are out of sync in CI
- **THEN** the dependency installation step fails rather than silently resolving new versions

