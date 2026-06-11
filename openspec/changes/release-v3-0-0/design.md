# Design: release-v3-0-0

## Release checklist (ordered)

1. **Pre-flight on `v3`**: `make lint type test` green; `uv run mkdocs build --strict` green; one full `uv run pytest -m live` pass (all entities + media; lyrics if `SPOTIFY_SP_DC` available).
2. **Version + changelog**: set `__version__ = "3.0.0"`; move CHANGELOG `[Unreleased]` content into `[3.0.0] - <date>`; add compare links.
3. **PR + merge**: open `v3` → `master` PR titled `feat!: SpotifyScraper v3.0.0`; CI green; merge with a merge commit (preserve v3 history).
4. **Manual prerequisites** (must exist before tagging): PyPI trusted publisher configured for `spotifyscraper`; `pypi` GitHub environment created. (From add-release-automation.)
5. **Tag**: `git tag v3.0.0 && git push origin v3.0.0` → release pipeline builds, publishes to PyPI via OIDC, creates the GitHub release.
6. **Post-release surfaces**:
   - Close issues #86, #88, #93, #94 with a comment linking the migration guide and the relevant entity.
   - Push `extras/wiki/Home.md` to `github.com/AliAkhtari78/SpotifyScraper.wiki.git`.
   - Push `extras/gh-pages-redirect/index.html` to the `gh-pages` branch; set the repo website to the RTD URL.
   - Publish the blog post (`extras/blog/spotifyscraper-v3.md`) to aliakhtari.com.
   - Verify RTD `stable` points at the `v3.0.0` tag.
7. **Optional v2 courtesy**: cut a final `2.1.6` from `v2.x` whose README deprecation-points to v3 (separate, low priority).

## Verification

- `pip install spotifyscraper==3.0.0` in a clean venv on Python 3.10 and 3.13; run the quickstart; confirm a real track fetch.
- PyPI shows 3.0.0; GitHub release notes match the CHANGELOG; RTD stable = v3; old Pages URL redirects; the four issues are closed with links.
