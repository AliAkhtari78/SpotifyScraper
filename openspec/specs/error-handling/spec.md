# error-handling Specification

## Purpose
TBD - created by archiving change add-models-errors-urls. Update Purpose after archive.
## Requirements
### Requirement: Single exception hierarchy

All errors raised by the library SHALL derive from `SpotifyScraperError`, with subtypes: `URLError` (invalid input), `NetworkError` (transport failure; wraps the underlying httpx error), `RateLimitedError(NetworkError)` (carries `retry_after: float | None`), `TokenError` (anonymous token bootstrap/refresh failure), `AuthenticationError` (missing/expired user credentials for authenticated features), `NotFoundError` (entity does not exist or is not available), `ParsingError` (Spotify payload shape changed), and `MediaError` (download/tagging failure).

#### Scenario: Catching all library errors

- **WHEN** any library operation fails for any reason
- **THEN** the raised exception is an instance of `SpotifyScraperError`

#### Scenario: Invalid URL input

- **WHEN** a caller passes a string that is not a Spotify URL, URI, or ID
- **THEN** `URLError` is raised with the offending input in the message

### Requirement: No error values in results

Public APIs SHALL communicate failures exclusively by raising exceptions. No public method returns error strings, error dicts, or sentinel values on failure.

#### Scenario: Entity fetch failure

- **WHEN** an entity cannot be fetched or parsed
- **THEN** an appropriate `SpotifyScraperError` subtype is raised and no partial result object is returned

