# home

## ADDED Requirements

### Requirement: Personalized Home feed

`get_home()` SHALL return a `Home` model — an ordered set of titled sections, each
holding heterogeneous entity items (playlists, albums, artists, tracks, shows, or
episodes) — representing the authenticated user's personalized "Made for you" feed,
fetched via the Spotify pathfinder **v2 POST** operation. It SHALL require a user
token derived from an `sp_dc` cookie; when only the anonymous bearer is available
it SHALL raise `AuthenticationError`. Parsing SHALL be tolerant of Spotify
reshaping the rails: an unrecognized item type SHALL be skipped rather than raising.

#### Scenario: Authenticated fetch

- **WHEN** a valid `sp_dc` session is configured and `get_home()` is called
- **THEN** it returns a `Home` whose `sections` each carry a title and one or more items

#### Scenario: Anonymous refusal

- **WHEN** no cookie-derived user token is available
- **THEN** `get_home()` raises `AuthenticationError` without performing the request

#### Scenario: Unknown item tolerated

- **WHEN** a Home section contains an item of an unrecognized type
- **THEN** that item is skipped and the remaining items parse without error
