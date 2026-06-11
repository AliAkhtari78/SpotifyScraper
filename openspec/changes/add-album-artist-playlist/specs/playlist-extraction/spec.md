# playlist-extraction

## ADDED Requirements

### Requirement: Two-tier playlist fetch

`get_playlist(value, *, max_tracks=100)` SHALL return a `Playlist` via tier 1 `fetchPlaylist` (name, description, owner, followers, items with added-at metadata) with degradation to the playlist's embed page (name, subtitle, first ~50 track list entries).

#### Scenario: Issue #94 regression

- **WHEN** a public playlist is fetched successfully
- **THEN** a `Playlist` is returned and no error of any kind is surfaced (the v2 error-on-success failure mode does not occur)

### Requirement: Bounded pagination

Tier-1 playlist fetches SHALL paginate (page size 100) until `max_tracks` items are collected or the playlist is exhausted; `max_tracks=None` SHALL fetch every track. `playlist.total_tracks` SHALL always report the playlist's full size regardless of how many tracks were fetched.

#### Scenario: Default bound

- **WHEN** a 10,000-track playlist is fetched with defaults
- **THEN** 100 tracks are returned and `total_tracks == 10000`

#### Scenario: Fetch everything

- **WHEN** `max_tracks=None` on a 250-track playlist
- **THEN** all 250 tracks are returned

### Requirement: Local-file entries are skipped

Playlist items that are not Spotify tracks (local files, removed episodes) SHALL be skipped without error.

#### Scenario: Mixed playlist

- **WHEN** a playlist contains local-file items
- **THEN** the returned tracks contain only real Spotify tracks and no exception is raised
