# discovery Specification

## Purpose
TBD - created by archiving change add-visual-discovery-mcp. Update Purpose after archive.
## Requirements
### Requirement: Related artists, discography, and recommendations

`get_related_artists`, `get_discography`, and `get_similar_albums` SHALL return
typed tuples anonymously (the same bearer token as entity extraction), with
`get_discography` paginating every release the artist has.

#### Scenario: Paginated discography

- **WHEN** `get_discography(artist)` is called on a cookie-less client
- **THEN** every release is returned as `AlbumRef` objects across as many pages as
  Spotify's `totalCount` reports

### Requirement: Public user profile

`get_user(user_id)` SHALL return a `UserProfile` (name, follower/following counts,
public playlists, recently-played artists) and MUST require the cookie-derived
user token, because Spotify refuses the anonymous token for profiles.

#### Scenario: No cookie configured

- **WHEN** `get_user("spotify")` is called on a client built without cookies
- **THEN** `AuthenticationError` is raised before any HTTP request

