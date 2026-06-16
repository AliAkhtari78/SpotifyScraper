# search Specification

## Purpose

Cross-entity search returning a single typed SearchResults.

## Requirements
### Requirement: Anonymous aggregate search

`search(query, *, types, limit)` SHALL accept a free-text query and return a
`SearchResults` model populated from Spotify's anonymous `searchDesktop`
pathfinder operation, using the same anonymous bearer token as entity
extraction. It SHALL require no cookie and SHALL never use the cookie-derived
token.

#### Scenario: Basic query

- **WHEN** `search("daft punk", types=("track",), limit=5)` is called on a
  cookie-less client
- **THEN** a `SearchResults` is returned whose `tracks` tuple is non-empty and
  whose query is `"daft punk"`, with no cookie token exchanged

#### Scenario: Anonymous token retried once

- **WHEN** the pathfinder returns HTTP 401 on the first search attempt
- **THEN** the cached anonymous token is invalidated, re-fetched once, and the
  request retried; a second 401 surfaces as `TokenError`

### Requirement: Typed per-entity results

`SearchResults` SHALL expose a separate tuple per requested entity type
(`tracks`, `artists`, `albums`, `playlists`, `shows`, `episodes`), reusing the
existing entity and reference models. Search hits are sparse: tier-1-only fields
absent from the search payload SHALL be `None`/`()`. `to_dict()` SHALL be
JSON-safe.

#### Scenario: Sparse models

- **WHEN** results contain tracks
- **THEN** each is a `Track` with `id`, `uri`, `name`, and `artists` populated,
  while fields the search payload omits (e.g. `play_count`) MAY be `None`

#### Scenario: Round-trip serialization

- **WHEN** `SearchResults.to_dict()` is called and fed to `from_dict`
- **THEN** an equal `SearchResults` is reconstructed using only JSON-safe values

### Requirement: Type selection and validation

`types` SHALL restrict which entity sections are returned. An unrecognized entry
in `types` SHALL raise `URLError` before any network request; the accepted set
is `track`, `album`, `artist`, `playlist`, `show`, `episode`.

#### Scenario: Subset of types

- **WHEN** `types=("artist",)` is requested
- **THEN** only the `artists` tuple is populated and the others stay empty

#### Scenario: Unknown type

- **WHEN** `types=("bogus",)` is requested
- **THEN** `URLError` is raised with no HTTP request

### Requirement: Empty results are not an error

A query that legitimately matches nothing SHALL return an empty `SearchResults`,
NOT raise `NotFoundError`. Search has no single entity union, so the absence of
hits is a valid, non-error outcome.

#### Scenario: No matches

- **WHEN** a query yields a `searchV2` union with empty section lists
- **THEN** an empty `SearchResults` is returned and no exception is raised

### Requirement: Persisted-query hash isolated for one-line refresh

The `searchDesktop` `operationName` and its persisted-query sha256 SHALL live in
exactly one place (`api/pathfinder.py`, in `SEARCH_OPERATION`), mirroring the
entity operations, so a Spotify rotation is a single-line edit. The entity
`OPERATIONS` table and its `build_variables(eid)` contract SHALL remain
unchanged.

#### Scenario: Hash rotation

- **WHEN** Spotify rotates the search persisted-query hash
- **THEN** only `SEARCH_OPERATION.sha256` in `api/pathfinder.py` changes; the
  parser, models, and clients are unaffected

#### Scenario: Rotated hash detected

- **WHEN** the pathfinder reports `PersistedQueryNotFound` for search
- **THEN** `ParsingError` is raised carrying the standard update hint

### Requirement: Malformed payload surfaces as ParsingError

The parser SHALL raise `ParsingError` with the standard update hint when a search
response is missing `data.searchV2` or its section shape cannot be parsed, and
SHALL NOT return error strings or error dicts.

#### Scenario: Missing union

- **WHEN** the pathfinder response lacks `data.searchV2`
- **THEN** `ParsingError` is raised naming the missing path with the update hint

### Requirement: Sync/async parity

`search` SHALL exist on both `SpotifyClient` and `AsyncSpotifyClient` with an
identical parameter list and an identical `SearchResults` return annotation; the
async variant SHALL be a coroutine and the sync variant SHALL NOT.

#### Scenario: Parity guard

- **WHEN** the parity test inspects both clients
- **THEN** `search`'s parameters and return annotation match, and only the async
  one is a coroutine

