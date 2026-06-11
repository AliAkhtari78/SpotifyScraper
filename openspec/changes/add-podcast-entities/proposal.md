# Proposal: add-podcast-entities

## Why

Podcast support (shows and episodes) completes the entity set and fixes the failure class behind issue #88, where v2's episode extraction broke against Spotify's changed pages.

## What Changes

- `api/pathfinder.py` gains `episode` (`getEpisodeOrChapter`) and `show` (`queryShowMetadataV2`) operations.
- New parsers: GraphQL and embed variants for Episode and Show.
- Clients gain `get_episode()` and `get_show()` (sync + async).
- Live smoke tests covering the issue #88 scenario.

## Capabilities

### New Capabilities

- `episode-extraction`: episode fetch with show reference and preview audio
- `show-extraction`: show fetch with episode listing

### Modified Capabilities

(none)

## Impact

- `api/pathfinder.py`, `api/parse_entities.py`, both clients, unit + live tests
