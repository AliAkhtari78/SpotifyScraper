# Proposal: add-album-artist-playlist

## Why

With the track slice proven, the remaining music entities — albums, artists, playlists — follow the same two-tier pattern. Artists and playlists are the two v2 features users reported broken (issues #93 and #94); this change replaces them with the new extraction ladder.

## What Changes

- `api/pathfinder.py` gains `album`, `artist`, `playlist` operations (hashes captured June 2026).
- New parsers in `api/parse_entities.py`: GraphQL and embed variants for Album, Artist, Playlist.
- Clients gain `get_album()`, `get_artist()`, `get_playlist()` (sync + async), with track-page pagination for albums (all tracks) and playlists (caller-bounded).
- Live smoke tests covering the scenarios from issues #93 and #94.

## Capabilities

### New Capabilities

- `album-extraction`: album fetch with full track listing
- `artist-extraction`: artist fetch with profile, stats, top tracks, and discography highlights
- `playlist-extraction`: playlist fetch with bounded track pagination

### Modified Capabilities

(none — pathfinder-api's operation table is extended, but its requirements are unchanged)

## Impact

- `api/pathfinder.py`, `api/parse_entities.py`, both clients, `tests/unit/api/`, `tests/unit/test_client*.py`, `tests/live/`
