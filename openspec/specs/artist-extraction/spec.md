# artist-extraction Specification

## Purpose
TBD - created by archiving change add-album-artist-playlist. Update Purpose after archive.
## Requirements
### Requirement: Two-tier artist fetch

`get_artist(value)` SHALL return an `Artist` via tier 1 `queryArtistOverview` (profile, stats, top tracks, discography highlights, external links) with degradation to the artist's embed page (name, top-10 track list, images).

#### Scenario: Rich fetch

- **WHEN** tier 1 succeeds
- **THEN** the `Artist` includes `monthly_listeners`, `followers`, non-empty `top_tracks`, and discography refs (`albums`/`singles`)

#### Scenario: Issue #93 regression

- **WHEN** a popular artist is fetched live
- **THEN** top tracks and discography are populated (the v2 failure mode reported in issue #93 does not occur)

### Requirement: Top tracks carry play counts

Artist top tracks SHALL be `Track` values including tier-1 `play_count`.

#### Scenario: Play count present

- **WHEN** an artist with billions of streams is fetched via tier 1
- **THEN** `artist.top_tracks[0].play_count` is a positive integer

