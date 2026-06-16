# lyrics-extraction Specification

## Purpose

Fetch time-synced lyrics via the cookie-derived user token.

## Requirements
### Requirement: Authenticated lyrics fetch

`get_lyrics(value)` SHALL accept any track input `url-handling` accepts and return a `Lyrics` model from Spotify's color-lyrics endpoint, using the cookie-derived web-player token. Calling it on a client constructed without cookies SHALL raise `AuthenticationError` immediately (no network).

#### Scenario: No cookies configured

- **WHEN** `get_lyrics` is called on a cookie-less client
- **THEN** `AuthenticationError` is raised without any HTTP request

#### Scenario: Synced lyrics

- **WHEN** lyrics exist for a track with line synchronization
- **THEN** the returned `Lyrics` has `sync_type == "LINE_SYNCED"` and every line carries a non-negative `start_ms`

### Requirement: Lyrics absence is not an error class confusion

Tracks without lyrics SHALL raise `NotFoundError` (the entity exists; lyrics do not). Authentication problems SHALL raise `AuthenticationError`. The two SHALL never be conflated (the v2 issue #86 failure mode).

#### Scenario: Instrumental track

- **WHEN** lyrics are requested for a track with no lyrics (endpoint 404)
- **THEN** `NotFoundError` is raised, not `AuthenticationError`

### Requirement: Isolation from anonymous extraction

Lyrics calls SHALL use only the cookie-derived token; entity extraction SHALL use only the anonymous token. A failure in either auth path SHALL not affect the other.

#### Scenario: Broken cookie, working extraction

- **WHEN** a client has an expired `sp_dc` but calls `get_track`
- **THEN** the track fetch succeeds normally

