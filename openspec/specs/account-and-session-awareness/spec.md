# account-and-session-awareness Specification

## Purpose

Expose the logged-in account's product state (premium/country/locale) and cookie-free session introspection.

## Requirements
### Requirement: Authenticated account product-state fetch

`get_account()` SHALL return an `Account` model parsed from Spotify's
`melody/v1/product_state` endpoint, using the cookie-derived web-player token.
It takes no entity argument (the body is a flat per-account object). Calling it
on a client constructed without cookies SHALL raise `AuthenticationError`
immediately, with no network request.

#### Scenario: No cookies configured

- **WHEN** `get_account` is called on a cookie-less client
- **THEN** `AuthenticationError` is raised without any HTTP request

#### Scenario: Premium account

- **WHEN** the product-state body reports `product == "premium"`
- **THEN** `get_account().is_premium` is `True` and `country`/`catalogue` are populated from the body

#### Scenario: Free account

- **WHEN** the product-state body reports `product == "free"` (or `"open"`)
- **THEN** `get_account().is_premium` is `False`

#### Scenario: Rejected token retried once

- **WHEN** the product-state endpoint returns HTTP 401 on the first attempt
- **THEN** the cached token is invalidated, re-exchanged once, and the request is
  retried; a second 401 surfaces as `AuthenticationError`

### Requirement: is_premium convenience

`is_premium()` SHALL be a convenience returning `get_account().is_premium`.
`Account.is_premium` SHALL be a derived property (`product == "premium"`), not a
stored field, and SHALL be excluded from `Account.to_dict()` so the serialized
form is a faithful mirror of the wire body.

#### Scenario: is_premium absent from to_dict

- **WHEN** `Account.to_dict()` is called
- **THEN** the result contains the wire fields but no `is_premium` key, and
  `Account.from_dict(account.to_dict()) == account`

### Requirement: Shared cookie token with lyrics and transcripts

Account extraction SHALL reuse the same cookie-derived web-player token provider
as lyrics and transcripts; a single `sp_dc` exchange SHALL serve all three
features within one client, while entity extraction continues to use the
anonymous token. A failure in either auth path SHALL not affect the other.

#### Scenario: One token, three features

- **WHEN** `get_lyrics`, `get_transcript`, and `get_account` are called on the same client
- **THEN** the cookie token is exchanged once and reused for all three, while
  `get_track` continues to use the anonymous token

### Requirement: Product-state endpoint isolated for one-line refresh

The product-state host and path SHALL be defined in exactly one module
(`api/account.py`), mirroring how lyrics/transcript hosts and pathfinder hashes
are confined, so a Spotify change is a single-file edit. The hyphen→snake key
mapping (`on-demand`, `preferred-locale`, `selected-language`) SHALL live in
exactly one place (`parse_account`).

#### Scenario: Endpoint change

- **WHEN** Spotify changes the product-state host or path
- **THEN** only `api/account.py` requires modification; the model, parser, and clients are unaffected

#### Scenario: Tolerant boolean coercion

- **WHEN** the product-state body sends `on-demand` as the string `"1"` (or `"true"`)
- **THEN** `parse_account` yields `on_demand=True`; an absent or unparseable value yields `None`

### Requirement: Malformed product-state surfaces as ParsingError

A product-state response that is not JSON SHALL raise `ParsingError` carrying the
standard update hint; the parser SHALL NOT return error strings or error dicts.
Because the body is flat and every field is independently optional, an empty or
partial JSON object SHALL parse to an `Account` with `| None` fields rather than
raising.

#### Scenario: Non-JSON body

- **WHEN** the product-state response is not JSON
- **THEN** `ParsingError` is raised with the update hint

#### Scenario: Empty JSON body

- **WHEN** the product-state response is `{}`
- **THEN** an `Account` with all fields `None` and `is_premium == False` is returned

### Requirement: Account secrets never leak

`Account` SHALL carry no cookie or token; `_fetch_account` SHALL pass the token
only into `auth_headers`, never logging or persisting it.

#### Scenario: Account carries no credential

- **WHEN** an `Account` is rendered with `repr()` or `to_dict()`
- **THEN** neither the cookie nor the bearer token appears

### Requirement: Cookie-free saved-session introspection

The library SHALL provide `session_info()` and `has_saved_session()` (plus
`SessionStore.info()`/`has_session()`) that report whether a saved session
exists and is usable WITHOUT exposing the cookie. `session_info` SHALL return a
frozen, slotted `SessionInfo` carrying only non-secret metadata (`exists`,
`valid`, `saved_at_ms`, `sp_dc_expires_ms`, `reason`) and SHALL NOT raise for the
common missing/corrupt/insecure/expired cases — those SHALL be reported as flags.
A session SHALL be `valid` only when it exists, is securely permissioned (POSIX),
parses, and has not passed `sp_dc_expires_ms` when that expiry is known. For the
keyring backend, validity SHALL additionally require that the `sp_dc` secret is
actually retrievable from the OS keyring (a valid metadata file whose keyring
entry is gone is NOT usable); when the `keyring` extra is absent the secret probe
SHALL be skipped and the metadata verdict SHALL stand. `SessionInfo` SHALL expose
a cookie-free `to_dict()`.

#### Scenario: No saved session

- **WHEN** `session_info()` runs against a path with no file
- **THEN** `SessionInfo(exists=False, valid=False)` is returned and nothing is raised

#### Scenario: Keyring secret gone is invalid

- **WHEN** `keyring_info()` runs against a valid metadata file whose `sp_dc`
  secret is absent from the OS keyring
- **THEN** `valid` is `False` with a cookie-free reason, so `has_session()` is honest

#### Scenario: SessionInfo serializes without the cookie

- **WHEN** `SessionInfo.to_dict()` is called
- **THEN** it returns a JSON-safe mapping of the verdict and metadata and never the `sp_dc` value

#### Scenario: Valid saved session

- **WHEN** `session_info()` runs against a freshly saved, securely-permissioned session
- **THEN** `valid` is `True`

#### Scenario: Expired saved session

- **WHEN** the saved session's `sp_dc_expires_ms` is in the past relative to the injected clock
- **THEN** `SessionInfo(exists=True, valid=False)` is returned with a non-cookie `reason`

#### Scenario: Insecure or corrupt session

- **WHEN** the session file is group/world-readable (POSIX) or is not valid JSON
- **THEN** `valid` is `False` and the cookie-free reason is reported

#### Scenario: SessionInfo never carries the cookie

- **WHEN** a `SessionInfo` is rendered with `repr()` or its `reason` is read
- **THEN** the `sp_dc` value never appears

### Requirement: login reuse auto-skips the browser

`login(reuse=True)` (the default) SHALL load a valid saved session and wire its
cookie into the client WITHOUT opening the browser, skipping the Playwright
import entirely. When no valid saved session exists (or `reuse=False`), `login`
SHALL fall back to the existing browser-capture flow. The browser import SHALL
occur only in the non-reuse branch, so importing or reusing a session SHALL NOT
require the `browser` extra.

#### Scenario: Valid saved session present

- **WHEN** `login(reuse=True)` is called and a valid saved session exists
- **THEN** the saved cookie is loaded, the cached cookie-token provider is reset,
  and the browser is never opened (capture is not called)

#### Scenario: No valid saved session

- **WHEN** `login(reuse=True)` is called with no usable saved session
- **THEN** the headed browser-capture flow runs as before and (when `save`) persists the result

#### Scenario: Reuse disabled

- **WHEN** `login(reuse=False)` is called even though a valid saved session exists
- **THEN** the browser-capture flow runs, ignoring the saved session

#### Scenario: Empty saved secret falls through to capture

- **WHEN** `login(reuse=True)` finds a metadata-valid session whose stored `sp_dc`
  is empty or unloadable (e.g. the keyring entry vanished)
- **THEN** it does NOT wire an empty cookie; it falls through to the browser-capture flow

#### Scenario: Network-side revocation falls through to the auth contract

- **WHEN** `login(reuse=True)` skips the browser for a saved cookie that Spotify
  has since revoked
- **THEN** the skip is still performed (validity is checked locally, without a
  network call) and the first authenticated call surfaces `AuthenticationError`
  per the existing 401 contract

