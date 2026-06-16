# documentation-site Specification

## Purpose

The MkDocs Material documentation site published to ReadTheDocs.

## Requirements
### Requirement: Strict-building MkDocs Material site

The repository SHALL contain a MkDocs Material documentation site whose `mkdocs build --strict` passes (no broken links, no missing nav targets), with navigation: Home, Getting Started (installation, quickstart), Guides (entities, async, media downloads, lyrics & cookies, anti-ban, browser fallback, error handling), API Reference (mkdocstrings-generated), Migration from v2, and Project pages (changelog, contributing, FAQ, legal).

#### Scenario: Docs CI gate

- **WHEN** a pull request changes docs or docstrings
- **THEN** `mkdocs build --strict` runs in CI and must pass

### Requirement: Generated API reference

API reference pages SHALL be generated from package docstrings via mkdocstrings covering: both clients, all models, all errors, transports/config (RateLimit, RetryPolicy), and the media helpers.

#### Scenario: Docstring drift

- **WHEN** a public symbol is renamed without updating docs
- **THEN** the strict build fails

### Requirement: Complete v2 migration guide

The migration guide SHALL contain a method-map table covering every public method of v2.1.5's `SpotifyClient` (`get_track_info`, `get_track_lyrics`, `get_track_info_with_lyrics`, `get_album_info`, `get_artist_info`, `get_playlist_info`, `get_episode_info`, `get_show_info`, `get_all_info`, `download_cover`, `download_episode_preview`, `download_preview_mp3`, `close`) with its v3 replacement or removal rationale, plus sections on exceptions, cookies, Python floor, and the CLI's return in v3.1.

#### Scenario: v2 user lands on the guide

- **WHEN** a v2 user searches the guide for any v2 method name
- **THEN** they find its row in the method map

### Requirement: Single documentation source

ReadTheDocs SHALL be the only content host: the repo SHALL include a redirect `index.html` for the `gh-pages` branch and a wiki stub document, both pointing at ReadTheDocs.

#### Scenario: Legacy bookmark

- **WHEN** a user opens the old GitHub Pages site
- **THEN** they are redirected to spotifyscraper.readthedocs.io

