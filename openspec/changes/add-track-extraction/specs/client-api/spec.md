# client-api

## ADDED Requirements

### Requirement: Zero-configuration clients

`SpotifyClient()` and `AsyncSpotifyClient()` SHALL work with no arguments, using built-in defaults (httpx transport, UA pool, RateLimit(2.0, 5), RetryPolicy(4), 10s timeout). Both SHALL be importable from the package root.

#### Scenario: Zero-config fetch

- **WHEN** `with SpotifyClient() as client: client.get_track(url)` runs
- **THEN** it succeeds with no configuration

### Requirement: Configurable construction

Clients SHALL accept keyword-only options: `rate_limit: RateLimit`, `retry: RetryPolicy`, `proxy: str`, `user_agent: str`, `timeout: float`, and `transport` (a `Transport`/`AsyncTransport`, overriding the other HTTP options).

#### Scenario: Injected transport

- **WHEN** a client is built with a custom transport object
- **THEN** every request flows through it

### Requirement: Deterministic lifecycle

Clients SHALL support context-manager use (`with` / `async with`) and explicit `close()` / `aclose()`. After closing, further calls SHALL raise `SpotifyScraperError`.

#### Scenario: Use after close

- **WHEN** a method is called on a closed client
- **THEN** `SpotifyScraperError` is raised

### Requirement: Sync/async parity

Every public data method on `SpotifyClient` SHALL have an identically-named, identically-typed counterpart on `AsyncSpotifyClient` (awaitable), and both SHALL return the same model types.

#### Scenario: API parity check

- **WHEN** the public method sets of both clients are compared (a parity unit test)
- **THEN** they are identical in names and signatures (modulo async)
