# release-pipeline

## ADDED Requirements

### Requirement: Tag-triggered trusted publishing

Pushing a tag matching `v3.*` SHALL build the distribution with uv and publish to PyPI via trusted publishing (OIDC through a `pypi` GitHub environment). No PyPI API tokens SHALL exist in repository secrets.

#### Scenario: Release

- **WHEN** tag `v3.0.0` is pushed
- **THEN** `spotifyscraper 3.0.0` appears on PyPI without any token secret involved

### Requirement: Version-tag consistency gate

The release workflow SHALL fail before publishing if the tag version does not equal the package `__version__`.

#### Scenario: Mismatched tag

- **WHEN** tag `v3.0.1` is pushed while `__version__` is `3.0.0`
- **THEN** the workflow fails before any upload

### Requirement: GitHub release notes

A successful publish SHALL create a GitHub release for the tag whose body is that version's CHANGELOG section.

#### Scenario: Release notes

- **WHEN** a release completes
- **THEN** the GitHub release body matches the CHANGELOG entry for that version
