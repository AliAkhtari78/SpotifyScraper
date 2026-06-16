# anonymous-auth Specification

## Purpose
TBD - created by archiving change add-anonymous-token. Update Purpose after archive.
## Requirements
### Requirement: Token bootstrap from embed pages

The library SHALL obtain an anonymous access token by fetching a Spotify embed page and reading `props.pageProps.state.settings.session` from its `__NEXT_DATA__` payload, without any user credentials.

#### Scenario: Cold start

- **WHEN** a token is requested and no cached token exists
- **THEN** one embed page is fetched and a non-empty bearer token with a future expiry is returned

### Requirement: Token caching and expiry

The provider SHALL cache the token and reuse it until 60 seconds before `accessTokenExpirationTimestampMs`, then fetch a fresh one. An explicit `invalidate()` SHALL force the next request to re-bootstrap (used on 401 responses).

#### Scenario: Cache hit

- **WHEN** a token is requested twice within its validity window
- **THEN** the embed page is fetched only once

#### Scenario: Expired token

- **WHEN** the cached token is within 60 seconds of expiry
- **THEN** the next token request fetches a fresh token

### Requirement: Bootstrap failure reporting

If the embed page cannot be fetched or its payload lacks a session token, the provider SHALL raise `TokenError` describing the stage that failed, without including any token material.

#### Scenario: Payload shape change

- **WHEN** the embed page returns HTML without a parseable session block
- **THEN** `TokenError` is raised and the message contains no token fragments

