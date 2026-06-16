# Proposal: add-release-automation

## Why

v1 and v2 both died of maintainer rot: manual releases, no early warning when Spotify changed pages, dependency drift. v3 automates the whole loop so a breakage fix is: edit one file → merge → tag.

## What Changes

- `release.yml`: tag-triggered build + publish to PyPI via trusted publishing (OIDC, no token secrets) + GitHub release with changelog notes.
- `canary.yml`: daily live test run (`pytest -m live`); on failure it opens/updates a pinned `spotify-breakage` issue — the early-warning system.
- `dependabot.yml`: weekly grouped updates for pip and GitHub Actions.
- Issue forms (bug report demanding version/URL/traceback, feature request) and a PR template.
- `SECURITY.md` (3.x supported, private vulnerability reporting).

## Capabilities

### New Capabilities

- `release-pipeline`: tag-to-PyPI publishing with provenance
- `canary-monitoring`: scheduled live verification with automated breakage reporting

### Modified Capabilities

(none)

## Impact

- `.github/workflows/release.yml`, `canary.yml`; `.github/dependabot.yml`, issue forms, PR template; `SECURITY.md`
- One-time manual step: configure the trusted publisher for `spotifyscraper` on pypi.org
