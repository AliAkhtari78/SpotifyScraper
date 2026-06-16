# Proposal: add-cli-framework

## Why

v3.0 deliberately shipped library-only, with the architecture designed to make a
CLI a thin add-on (JSON-safe `to_dict()` on every model, one client method per
operation). v3.1 delivers that CLI so non-Python users can extract Spotify data
and download media from the terminal.

## What Changes

- New `spotify_scraper.cli` package: a Typer app exposing one command per entity
  (`track`, `album`, `artist`, `playlist`, `episode`, `show`) plus a `download`
  group (`cover`, `preview`).
- A `spotifyscraper` console-script entry point, installed via a new `cli` extra
  (`pip install "spotifyscraper[cli]"`).
- Commands print the entity as JSON (`to_dict()`) by default, with `--pretty`
  for indented output and `-o/--output` to write to a file.
- Shared options for client tuning (`--proxy`, `--rate-limit`, `--timeout`),
  plus `--max-tracks` / `--max-episodes` where relevant.
- Typed errors are mapped to clean, non-traceback CLI messages and exit codes.

## Capabilities

### New Capabilities

- `command-line-interface`: a terminal interface over the library's public API

### Modified Capabilities

(none — the CLI consumes the existing client/model API unchanged)

## Impact

- New `src/spotify_scraper/cli/`; `cli` extra + `[project.scripts]` in pyproject
- New CLI tests (Typer `CliRunner`) and a docs CLI guide
- No change to the library API; lyrics command is deferred with lyrics support
