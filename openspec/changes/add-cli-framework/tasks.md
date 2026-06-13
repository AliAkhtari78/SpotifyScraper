# Tasks: add-cli-framework

## 1. Packaging

- [x] 1.1 Add `cli` extra (typer) + `[project.scripts]` entry point; add typer to dev group; re-lock

## 2. CLI module

- [x] 2.1 cli/_output.py (emit JSON, run-wrapper error/exit-code mapping)
- [x] 2.2 cli/main.py (Typer app, --version callback, build_client, entity commands)
- [x] 2.3 cli/download.py (cover + preview subcommands)
- [x] 2.4 cli/__init__.py (app export + helpful ImportError without the extra)

## 3. Tests

- [x] 3.1 tests/unit/cli/ with CliRunner: per-command JSON, --pretty, -o, bounds, errors+exit codes, --version/--help
- [x] 3.2 tests/live/test_cli.py (marked live): real `track` command smoke

## 4. Docs

- [x] 4.1 docs/guides/cli.md (+ nav); update index/FAQ/migration to mark the CLI as shipped

## 5. Verify

- [x] 5.1 make lint/type/test green; `spotifyscraper --help`, `track`, `download preview` work live
