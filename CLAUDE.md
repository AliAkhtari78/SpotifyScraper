# CLAUDE.md

Guidance for AI coding agents (and humans) working on SpotifyScraper.

## What this project is

A Python library that extracts public Spotify data (tracks, albums, artists, playlists, shows, episodes) without the official API. v3 is a clean-room rewrite; the stable v2 line lives on the `v2.x` branch.

## Architecture rules (do not violate)

1. **Sans-io core.** All Spotify intelligence — URL parsing, token extraction, request building, payload→model parsing — lives in pure, sync-agnostic functions. Only the thin client facades in `_sync/` and `_async/` know about I/O.
2. **One runtime dependency.** Core depends on `httpx` only. New functionality that needs another package goes behind an optional extra (`media`, `browser`) with a lazy import and a helpful `ImportError`.
3. **Two-tier extraction ladder.** Tier 1: anonymous bearer token (bootstrapped from any embed page's `__NEXT_DATA__`) → Spotify pathfinder GraphQL. Tier 2 (fallback): parse the entity's own embed page. Tier-1-only model fields are `| None`. GraphQL persisted-query hashes live ONLY in `api/pathfinder.py`.
4. **Typed throughout.** Frozen slotted dataclasses for models, `to_dict()` JSON-safe; `mypy --strict` must pass; exceptions come from the `errors.py` hierarchy — never return error strings or error dicts.
5. **Hermetic tests by default.** Network tests are `@pytest.mark.live` and excluded by default. Never commit fixtures containing live `accessToken`, `clientId`, or cookie values — scrub them (see `scripts/capture_fixtures.py` once it exists).

## Workflow

- **Spec-first.** Every non-trivial change goes through OpenSpec: propose (`/opsx:propose`) → apply (`/opsx:apply`) → archive (`/opsx:archive`). Specs live in `openspec/`.
- **Conventional commits** are enforced by a commit-msg hook (template: `.gitmessage`).
- One OpenSpec change = one PR into `v3` (until v3 merges to `master`).

## Commands

| Command | Purpose |
|---|---|
| `uv sync` | Install/refresh the dev environment |
| `make lint` / `make format` | ruff check / autofix + format |
| `make type` | mypy strict on `src/` |
| `make test` | hermetic test suite |
| `make cov` | tests with coverage (85% floor) |
| `make live` | live Spotify smoke tests (network) |
| `uv build` | build wheel + sdist |

## Layout

- `src/spotify_scraper/` — the package (src layout, `py.typed`)
- `tests/unit/`, `tests/live/`, `tests/fixtures/` — mirrors module tree
- `openspec/` — specs and change proposals
- `docs/` — MkDocs Material site (ReadTheDocs is canonical hosting)
