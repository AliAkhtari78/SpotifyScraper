# Proposal: add-track-extraction

## Why

The first vertical slice: a user calls `client.get_track(...)` and receives a typed `Track`. This proves the whole architecture — URL parsing → token → tier-1 pathfinder GraphQL → model, with automatic degradation to tier-2 embed parsing — and establishes the pattern every other entity follows.

## What Changes

- New `api/pathfinder.py`: the single table of pathfinder GraphQL operations (operation name, persisted-query sha256 hash, variables builder) and request-URL builder. Hash rotation by Spotify is fixed by editing this one file.
- New `api/parse_entities.py`: `parse_track_gql(payload) -> Track` (tier 1) and `parse_track_embed(entity) -> Track` (tier 2).
- New `_sync/client.py` / `_async/client.py`: `SpotifyClient` / `AsyncSpotifyClient` with `get_track()`, context-manager lifecycle, two-tier fetch with degradation, and 401→token-refresh retry.
- Package `__init__.py` re-exports the public API.

## Capabilities

### New Capabilities

- `pathfinder-api`: building and issuing pathfinder GraphQL persisted queries
- `track-extraction`: end-to-end track fetch through the two-tier ladder
- `client-api`: public client construction, configuration, and lifecycle

### Modified Capabilities

(none)

## Impact

- New modules: `api/pathfinder.py`, `api/parse_entities.py`, `_sync/client.py`, `_async/client.py`; `__init__.py` exports
- Tests: unit (fixtures + respx) and `tests/live/test_track.py` (marked `live`)
