# Proposal: add-models-errors-urls

## Why

Every feature of v3 consumes or produces three foundations: typed data models, a coherent exception hierarchy, and Spotify URL/URI/ID handling. They must exist (and be spec-pinned) before transports and extractors, because all later changes import them.

## What Changes

- New `errors.py`: one exception tree rooted at `SpotifyScraperError` — callers can catch one base or precise subtypes. No error strings or error dicts anywhere in the API (fixes the v2 class of bugs behind issue #94).
- New `urls.py`: parse any user input (open.spotify.com URL incl. `intl-xx` paths and query strings, `spotify:` URI, or bare 22-char ID) into `(EntityType, id)`; build canonical and embed URLs.
- New `models/` package: frozen, slotted dataclasses for Track, Album, Artist, Playlist, Episode, Show, Lyrics plus shared value objects (Image, ArtistRef, AlbumRef, ShowRef, UserRef, PlaylistTrack, LyricsLine). All models expose JSON-safe `to_dict()` and `from_dict()`.
- Field nullability encodes the two-tier extraction ladder: fields available from embed pages (tier 2) are required; tier-1-only enrichments are `| None`.

## Capabilities

### New Capabilities

- `error-handling`: typed exception hierarchy and error contracts
- `url-handling`: URL/URI/ID parsing and canonical/embed URL construction
- `data-models`: typed entity models with JSON-safe serialization

### Modified Capabilities

(none)

## Impact

- New modules: `src/spotify_scraper/errors.py`, `src/spotify_scraper/urls.py`, `src/spotify_scraper/models/`
- New tests: `tests/unit/test_errors.py`, `tests/unit/test_urls.py`, `tests/unit/models/`
- No network code; depends only on the stdlib
