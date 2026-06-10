# Proposal: add-anonymous-token

## Why

Tier 1 of the extraction ladder needs an anonymous bearer token. Spotify's embed pages serve one to every visitor inside their `__NEXT_DATA__` JSON — no credentials required. This change builds the token bootstrap plus the embed-payload parser that doubles as the tier-2 data source.

## What Changes

- New `api/parse_embed.py`: extract and validate `__NEXT_DATA__` JSON from embed-page HTML; pull out the session block (token, expiry) and the entity block (tier-2 data).
- New `auth/anonymous.py`: `AnonymousTokenProvider` — fetches an embed page, caches the token, refreshes when expired (with clock-skew margin) or on a 401.
- Token values never appear in logs or exception messages.

## Capabilities

### New Capabilities

- `anonymous-auth`: anonymous token bootstrap, caching, and refresh
- `embed-parsing`: extraction of entity data and session data from embed pages

### Modified Capabilities

(none)

## Impact

- New modules: `src/spotify_scraper/api/parse_embed.py`, `src/spotify_scraper/auth/anonymous.py`
- Tests against `tests/fixtures/embed/*.json` (real scrubbed captures)
