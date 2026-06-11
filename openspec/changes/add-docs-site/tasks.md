# Tasks: add-docs-site

## 1. Infrastructure

- [ ] 1.1 Add `docs` dependency group (mkdocs-material, mkdocstrings[python], pymdownx via mkdocs-material)
- [ ] 1.2 Write mkdocs.yml (Material, nav, mkdocstrings, snippets/tabs extensions)
- [ ] 1.3 Write .readthedocs.yaml (uv build)
- [ ] 1.4 Add docs.yml CI workflow (strict build on PRs)

## 2. Content

- [ ] 2.1 index.md + getting-started/ (installation, quickstart)
- [ ] 2.2 guides/ (entities, async, media-downloads, lyrics-and-cookies, anti-ban, browser-fallback, error-handling)
- [ ] 2.3 reference/ mkdocstrings stubs for client, async-client, models, errors, http, media
- [ ] 2.4 migration.md (full v2 method map per spec)
- [ ] 2.5 changelog.md/contributing.md includes, faq.md, legal.md

## 3. Redirect surfaces

- [ ] 3.1 extras/gh-pages-redirect/index.html
- [ ] 3.2 extras/wiki/Home.md stub

## 4. Verify

- [ ] 4.1 `uv run mkdocs build --strict` green; nav covers every file; migration table covers all 13 v2 methods
