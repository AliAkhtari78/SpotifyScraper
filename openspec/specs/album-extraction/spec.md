# album-extraction Specification

## Purpose
TBD - created by archiving change add-album-artist-playlist. Update Purpose after archive.
## Requirements
### Requirement: Two-tier album fetch

`get_album(value)` SHALL return an `Album` via the two-tier ladder: tier 1 `getAlbum` (name, type, label, release date, copyrights, artists, cover art, tracks) with degradation to the album's embed page (name, artist subtitle, track list, images).

#### Scenario: Rich fetch

- **WHEN** tier 1 succeeds
- **THEN** the `Album` includes `label`, `copyrights`, and per-track `play_count`

#### Scenario: Degraded fetch

- **WHEN** tier 1 fails with `ParsingError`
- **THEN** an `Album` built from the embed `trackList` is returned with tier-1-only fields `None`

### Requirement: Complete track listing

A tier-1 album fetch SHALL paginate `tracksV2` (page size 50) until all `totalCount` tracks are collected.

#### Scenario: Album larger than one page

- **WHEN** an album has more than 50 tracks
- **THEN** `len(album.tracks) == album.total_tracks`

