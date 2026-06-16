# url-handling

## ADDED Requirements

### Requirement: Universal input parsing

`parse(value)` SHALL accept and correctly classify: full URLs (`https://open.spotify.com/track/<id>`, with or without scheme, with `intl-<lang>` path segments, query strings, and trailing slashes), embed URLs (`/embed/track/<id>`), Spotify URIs (`spotify:track:<id>`), and bare 22-character base62 IDs (which require an explicit entity type hint). It SHALL return the entity type and the 22-character ID.

#### Scenario: Localized URL

- **WHEN** `https://open.spotify.com/intl-de/track/4uLU6hMCjMI75M1A2tKUQC?si=abc` is parsed
- **THEN** the result is entity type `track` and ID `4uLU6hMCjMI75M1A2tKUQC`

#### Scenario: URI input

- **WHEN** `spotify:playlist:37i9dQZF1DXcBWIGoYBM5M` is parsed
- **THEN** the result is entity type `playlist` and ID `37i9dQZF1DXcBWIGoYBM5M`

#### Scenario: Garbage input

- **WHEN** a non-Spotify string is parsed
- **THEN** `URLError` is raised

### Requirement: Supported entity types

The parser SHALL support exactly: `track`, `album`, `artist`, `playlist`, `episode`, `show`. Other path segments (e.g. `user`, `concert`) SHALL raise `URLError` naming the unsupported type.

#### Scenario: Unsupported entity

- **WHEN** `https://open.spotify.com/concert/abc123` is parsed
- **THEN** `URLError` is raised mentioning `concert`

### Requirement: URL construction

The module SHALL build canonical URLs (`https://open.spotify.com/<type>/<id>`), embed URLs (`https://open.spotify.com/embed/<type>/<id>`), and URIs (`spotify:<type>:<id>`) from an entity type and ID.

#### Scenario: Embed URL for token bootstrap

- **WHEN** an embed URL is built for track `4uLU6hMCjMI75M1A2tKUQC`
- **THEN** it equals `https://open.spotify.com/embed/track/4uLU6hMCjMI75M1A2tKUQC`
