# Design: add-release-automation

## release.yml

```yaml
on: push: tags: ["v3*"]
jobs:
  build:    # uv build; version gate: python -c compare tag vs __version__; upload dist artifact
  publish:  # needs build; environment: pypi; permissions: id-token: write;
            # pypa/gh-action-pypi-publish@release/v1
  github-release:  # needs publish; extracts CHANGELOG section (awk between '## [X.Y.Z]' headers);
                   # gh release create "$TAG" --notes-file
```

One-time manual setup (documented in CONTRIBUTING release section): PyPI → project `spotifyscraper` → Publishing → add GitHub publisher (owner AliAkhtari78, repo SpotifyScraper, workflow release.yml, environment pypi); create the `pypi` environment in repo settings.

## canary.yml

```yaml
on: { schedule: [{cron: "17 4 * * *"}], workflow_dispatch: {} }
jobs:
  live:    # uv sync --locked; uv run pytest -m live --timeout=120 -q (excluding lyrics: -k "not lyrics")
  lyrics:  # continue-on-error: true; runs only lyrics live tests with SPOTIFY_SP_DC secret if set
  report:  # needs: [live]; if: failure() -> gh issue: reuse open 'spotify-breakage' labeled issue
           # (gh issue list --label spotify-breakage --state open) else create; append run link + failed test names.
           # if: success() and an open breakage issue exists -> comment "recovered in <run>" and close.
```

Permissions: `issues: write`. Failed-test names extracted from pytest output (`--tb=no -q` tail) into the issue body.

## dependabot.yml

Weekly; `pip` ecosystem (groups: `dev-dependencies` for the dev group, `runtime` for httpx) and `github-actions` (one group); `open-pull-requests-limit: 3`; conventional-commit prefixes (`build(deps)`, `ci(deps)`).

## Issue forms / PR template

- `.github/ISSUE_TEMPLATE/bug_report.yml`: required fields — spotifyscraper version (`pip show spotifyscraper`), Python version, the Spotify URL, the exact code, the full traceback; checkbox "I checked the pinned spotify-breakage issue".
- `.github/ISSUE_TEMPLATE/feature_request.yml`, `config.yml` (blank issues off, links to docs + discussions).
- `pull_request_template.md`: summary, OpenSpec change reference, gates checklist.

## SECURITY.md

Supported: 3.x only. Report via GitHub private vulnerability reporting (Security tab). 90-day disclosure window. Out of scope: Spotify's own services.
