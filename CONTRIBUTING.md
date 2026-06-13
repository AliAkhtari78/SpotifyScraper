# Contributing to SpotifyScraper

Thanks for your interest in contributing! This project is maintained spec-first; small fixes are welcome as plain PRs, larger changes start with a spec proposal.

## Development setup

Requirements: Python 3.10+, [uv](https://docs.astral.sh/uv/), git.

```bash
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper
make dev                     # uv sync + macOS .pth repair (see note below)
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
git config commit.template .gitmessage
```

> **macOS note:** `uv` can leave the `UF_HIDDEN` flag on the venv's `*.pth`
> files, and CPython's `site` module silently skips hidden `.pth` files — so
> `uv run python -c "import spotify_scraper"` may fail with `ModuleNotFoundError`
> even though `pytest` passes (pytest uses `pythonpath = ["src"]`). `make dev`
> clears the flag; re-run it if ad-hoc imports break after a `uv sync`. CI
> (Linux) is unaffected.

## Quality gates

All of these must pass before a PR can merge (CI enforces them):

```bash
make lint     # ruff check + format check
make type     # mypy --strict on src/
make test     # hermetic test suite (no network)
```

`make live` runs the live Spotify smoke tests — they hit real endpoints and are excluded from the default run and from CI PR checks.

## Spec-first workflow (larger changes)

This repo uses [OpenSpec](https://github.com/Fission-AI/OpenSpec). For any change that adds or alters behavior:

1. **Propose** — create a change under `openspec/changes/<name>/` with `proposal.md`, `design.md`, spec deltas, and `tasks.md` (in Claude Code: `/opsx:propose`).
2. **Apply** — implement the tasks; keep the checklist updated.
3. **Archive** — after merge, the change is archived and the deltas land in `openspec/specs/`.

Bug fixes that don't change specified behavior can skip this and go straight to a PR.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/) are enforced by a commit-msg hook:
`feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`, `test: ...`, `build: ...`, `ci: ...`, `chore: ...`.
Breaking changes use `!` (e.g. `feat!: ...`) and a `BREAKING CHANGE:` footer.

## Tests and fixtures

- Default tests are hermetic: HTTP is mocked with [respx](https://lundberg.github.io/respx/); page payloads come from `tests/fixtures/`.
- Live tests are marked `@pytest.mark.live`.
- **Never commit fixtures containing live tokens, client IDs, or cookies.** Scrub them first.

## Reporting issues

Use the issue templates. For extraction breakage, always include: the `spotifyscraper` version, the Spotify URL, and the full traceback.
