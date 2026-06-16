# cookie-auth Specification

## Purpose

The rotating-TOTP /api/token handshake that exchanges an sp_dc cookie for a user bearer token.

## Requirements
### Requirement: Flexible cookie ingestion

The client `cookies=` argument SHALL accept: a path to a Netscape-format `cookies.txt` export, a mapping of cookie names to values, or a raw `sp_dc` string. Inputs lacking an `sp_dc` cookie SHALL raise `AuthenticationError` at construction time.

#### Scenario: cookies.txt file

- **WHEN** a client is built with `cookies="cookies.txt"` containing an `sp_dc` line
- **THEN** construction succeeds and lyrics calls are possible

#### Scenario: Missing sp_dc

- **WHEN** a cookies mapping without `sp_dc` is supplied
- **THEN** `AuthenticationError` is raised naming the missing cookie

### Requirement: Web-player token exchange

The library SHALL exchange `sp_dc` for a web-player access token via Spotify's token endpoint, cache it, refresh before expiry, and re-exchange once on a 401. An invalid or expired `sp_dc` SHALL surface as `AuthenticationError` with renewal instructions (log into open.spotify.com and re-export the cookie).

#### Scenario: Expired sp_dc

- **WHEN** the token exchange rejects the cookie
- **THEN** `AuthenticationError` is raised telling the user how to obtain a fresh `sp_dc`

### Requirement: Credential hygiene

Cookie and token values SHALL never appear in logs, exception messages, or `repr()` output.

#### Scenario: Exception on bad cookie

- **WHEN** any cookie-auth failure is raised
- **THEN** the exception text contains no cookie or token material

