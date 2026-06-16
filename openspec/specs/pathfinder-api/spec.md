# pathfinder-api Specification

## Purpose

Build and classify Spotify pathfinder GraphQL persisted-query requests.

## Requirements
### Requirement: Centralized operation table

All pathfinder GraphQL operations SHALL be defined in a single table in `api/pathfinder.py` mapping each operation to its name, persisted-query sha256 hash, and variables builder. No hash literal SHALL exist anywhere else in the package.

#### Scenario: Hash rotation fix

- **WHEN** Spotify rotates a persisted-query hash
- **THEN** updating the one table entry restores functionality with no other code change

### Requirement: Persisted query requests

The library SHALL issue GET requests to `https://api-partner.spotify.com/pathfinder/v1/query` with `operationName`, JSON-encoded `variables`, and `extensions.persistedQuery` (version 1 + sha256), authorized by the anonymous bearer token.

#### Scenario: Track query

- **WHEN** a track request is built for ID `4uLU6hMCjMI75M1A2tKUQC`
- **THEN** the URL contains `operationName=getTrack` and the variables encode `spotify:track:4uLU6hMCjMI75M1A2tKUQC`

### Requirement: GraphQL error classification

Responses SHALL be classified: body `errors` containing `PersistedQueryNotFound` → `ParsingError` advising a library update; HTTP 401 → token invalidation and one retry before raising `TokenError`; missing/null entity union in `data` → `NotFoundError`.

#### Scenario: Rotated hash detected

- **WHEN** the response body reports `PersistedQueryNotFound`
- **THEN** `ParsingError` is raised mentioning that Spotify changed their API and an update may be required

