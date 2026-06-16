# track-extraction Specification

## Purpose

Two-tier track fetch: pathfinder GraphQL with an embed-page fallback.

## Requirements
### Requirement: Two-tier track fetch

`get_track(value)` SHALL accept any input `url-handling` accepts, attempt tier 1 (pathfinder `getTrack`), and on tier-1 failure (`ParsingError` or auth exhaustion) degrade to tier 2 (the track's own embed page), emitting a `warning` log on degradation. `NotFoundError` SHALL NOT trigger degradation.

#### Scenario: Rich fetch

- **WHEN** tier 1 succeeds for a track
- **THEN** the returned `Track` includes tier-1 fields (`play_count`, `track_number`, `album`)

#### Scenario: Degraded fetch

- **WHEN** tier 1 raises `ParsingError` but the embed page parses
- **THEN** a `Track` is returned with tier-1-only fields `None` and a warning is logged

#### Scenario: Missing track

- **WHEN** the track does not exist
- **THEN** `NotFoundError` is raised without attempting tier 2

### Requirement: Preview URL completeness

Because tier 1 lacks preview audio, a tier-1 track fetch SHALL also read the embed entity payload when the caller requests previews (`get_track(value)` always exposes `preview_url`; implementations MAY fetch the embed page lazily or eagerly but MUST populate `preview_url` when Spotify provides a preview).

#### Scenario: Preview present

- **WHEN** a playable track with a preview is fetched via tier 1
- **THEN** `track.preview_url` is a `p.scdn.co` URL, not `None`

