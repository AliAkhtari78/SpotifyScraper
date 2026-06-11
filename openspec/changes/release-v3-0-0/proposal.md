# Proposal: release-v3-0-0

## Why

All v3 capabilities are implemented, documented, and automated. This change ships 3.0.0: finalize the version and changelog, merge `v3` into `master`, tag, and update the public surfaces (issues, wiki, blog) so v2 users are guided to the new release.

## What Changes

- Bump `__version__` from `3.0.0.dev0` to `3.0.0`.
- Finalize `CHANGELOG.md` `[3.0.0]` section (Keep a Changelog format).
- Final `README.md` pass (badges, 30-second example, extras table, legal disclaimer, migration link).
- Merge `v3` → `master`; tag `v3.0.0` (triggers the release pipeline).
- Close v2 issues #86/#88/#93/#94 with migration-guide links; push the wiki stub; publish the gh-pages redirect; publish the blog post to aliakhtari.com.

## Capabilities

### New Capabilities

(none — this change adds no behavior; it releases existing capabilities)

### Modified Capabilities

(none)

## Impact

- `src/spotify_scraper/__init__.py` version, `CHANGELOG.md`, `README.md`
- Git: `v3` → `master` merge, `v3.0.0` tag
- GitHub: issues closed, wiki stub, gh-pages redirect; external: aliakhtari.com blog
