# Design: add-docs-site

## Layout

```
mkdocs.yml                      # Material, dark/light toggle, navigation.tabs, search, mkdocstrings
.readthedocs.yaml               # ubuntu-24.04, python 3.13, uv-based: pip install uv && uv sync --group docs; mkdocs build
docs/
├── index.md                    # pitch, 30-second example, install matrix, ToS disclaimer banner
├── getting-started/
│   ├── installation.md         # pip/uv, extras table, supported Pythons
│   └── quickstart.md           # track fetch, to_dict, download preview, async teaser
├── guides/
│   ├── entities.md             # all six get_* with examples + model field tables
│   ├── async.md                # AsyncSpotifyClient, gather patterns, rate-limit notes
│   ├── media-downloads.md      # covers, previews, embed_cover, file naming
│   ├── lyrics-and-cookies.md   # sp_dc how-to (browser devtools steps), security warning
│   ├── anti-ban.md             # RateLimit/RetryPolicy/proxy/UA knobs, what 429 means, etiquette
│   ├── browser-fallback.md     # [browser] extra, playwright install, when to use
│   └── error-handling.md       # exception tree, catch patterns, ParsingError meaning
├── reference/
│   ├── client.md async-client.md models.md errors.md http.md media.md   # mkdocstrings stubs
├── migration.md                # full v2 method map (spec lists the 13 methods) + exceptions/cookies/floor/CLI
├── changelog.md                # include via snippet from CHANGELOG.md (pymdownx.snippets)
├── contributing.md             # include CONTRIBUTING.md
├── faq.md
└── legal.md                    # ToS considerations, educational use, takedown contact
extras/gh-pages-redirect/index.html   # meta-refresh + canonical link to RTD (deployed manually to gh-pages at release)
extras/wiki/Home.md                   # wiki stub (pushed to the wiki remote at release)
```

## Decisions

- mkdocstrings handler config: `show_source: false`, `docstring_style: google`, `members_order: source`, `separate_signature: true`.
- Docs CI: extend existing `ci.yml`? No — dedicated `docs.yml` (PR path-filtered) keeps the main pipeline fast. The strict build installs the package (mkdocstrings imports it).
- Versioning on RTD: `latest` (master) + `stable` (tags); enable version warning banner.
- `pymdownx` extensions: superfences, tabbed (sync/async code tabs), admonition, snippets.
- Every code example in the guides MUST be runnable as written (doctest-style discipline; examples use the canonical fixture entities so maintainers can paste-run them).

## Testing / verification

`uv run mkdocs build --strict` green locally and in CI; link-check via strict mode; migration guide table cross-checked against the v2 client (v2.x branch) method list in the spec.
