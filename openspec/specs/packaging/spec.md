# packaging Specification

## Purpose
TBD - created by archiving change setup-project-scaffold. Update Purpose after archive.
## Requirements
### Requirement: Single-file build configuration

The project SHALL be packaged exclusively via `pyproject.toml` using the hatchling build backend. No `setup.py`, `setup.cfg`, `MANIFEST.in`, or `requirements*.txt` files SHALL exist.

#### Scenario: Building a wheel

- **WHEN** `uv build` runs on a clean checkout
- **THEN** it produces a wheel and sdist for the `spotifyscraper` distribution without errors

### Requirement: Version single-sourcing

The package version SHALL be defined once, in `src/spotify_scraper/__init__.py` as `__version__`, and read by the build backend from there.

#### Scenario: Version consistency

- **WHEN** the built wheel metadata and `spotify_scraper.__version__` are compared
- **THEN** they are identical

### Requirement: Minimal core dependencies

The core distribution SHALL depend on `httpx` only. All other functionality SHALL be provided through optional extras: `media` (audio tagging), `browser` (browser-based transport), and `all` (everything).

#### Scenario: Core install

- **WHEN** `pip install spotifyscraper` runs in a clean environment
- **THEN** only `httpx` and its transitive dependencies are installed alongside the package

#### Scenario: Extras install

- **WHEN** `pip install spotifyscraper[all]` runs
- **THEN** media and browser dependencies are installed as well

### Requirement: Typed package marker

The package SHALL ship a `py.typed` marker so type checkers consume the inline annotations.

#### Scenario: Type checking a consumer project

- **WHEN** mypy checks code that imports `spotify_scraper`
- **THEN** the package's type annotations are used rather than treated as `Any`

### Requirement: Supported Python versions

The package SHALL declare `requires-python = ">=3.10"` and be tested against CPython 3.10 through 3.13.

#### Scenario: Unsupported interpreter

- **WHEN** installation is attempted on Python 3.9
- **THEN** the installer refuses with a clear version constraint error

