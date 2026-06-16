# Proposal: add-docs-site

## Why

v2 maintained three diverging copies of its documentation (ReadTheDocs, GitHub Pages, the wiki) plus leftover Sphinx config — all now describing a dead API. v3 single-sources everything: one MkDocs Material site on ReadTheDocs; the other surfaces redirect to it.

## What Changes

- New `docs/` tree built with MkDocs Material + mkdocstrings (API reference generated from docstrings).
- `mkdocs.yml` and `.readthedocs.yaml` (uv-based build).
- A migration guide covering every v2 public method.
- GitHub Pages (`gh-pages` branch) replaced with a single redirect page to ReadTheDocs; the Pages deploy workflow stays deleted.
- The GitHub wiki gets a stub pointing at ReadTheDocs (pushed at release).
- `docs` dependency group (mkdocs-material, mkdocstrings[python]).

## Capabilities

### New Capabilities

- `documentation-site`: single-source documentation built from the repo and hosted on ReadTheDocs

### Modified Capabilities

(none)

## Impact

- New `docs/`, `mkdocs.yml`, `.readthedocs.yaml`; `pyproject.toml` docs group; `docs.yml` CI job (strict build on PRs)
