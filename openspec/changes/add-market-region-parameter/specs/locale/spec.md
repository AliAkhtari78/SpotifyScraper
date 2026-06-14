# locale

## ADDED Requirements

### Requirement: Optional display-language localization

The clients SHALL accept an optional `locale` (an ISO-3166 alpha-2 code or a
language-region tag such as `ja-JP`) at the client level
(`SpotifyClient(locale=...)`) and as a per-call override on every entity getter
and on `search`. When provided, the library SHALL send it as the
`Accept-Language` HTTP header on the underlying requests so Spotify returns
localized display names. When omitted, behavior SHALL be byte-identical to today
(the transport's default `Accept-Language: en`). A per-call `locale` SHALL
override the per-client default.

#### Scenario: Per-client default

- **WHEN** a client is built with `SpotifyClient(locale="ja-JP")` and `get_track`
  is called without `locale`
- **THEN** the pathfinder (and embed) requests carry `Accept-Language: ja-JP`

#### Scenario: Per-call override wins

- **WHEN** a client built with `locale="de-DE"` calls `get_track(url, locale="ja-JP")`
- **THEN** the requests carry `Accept-Language: ja-JP`, not `de-DE`

#### Scenario: Omitted locale is a no-op

- **WHEN** neither the client nor the call sets `locale`
- **THEN** no per-request `Accept-Language` override is added and the request
  headers are identical to the pre-change behavior

### Requirement: Locale validation

A `locale` SHALL be validated as either an ISO-3166 alpha-2 country code
(case-insensitive, normalized to upper-case) or a language-region tag. Invalid
input SHALL raise `URLError` before any network request, at both client
construction (per-client default) and per call (override).

#### Scenario: Bare country code normalized

- **WHEN** `locale="de"` is supplied
- **THEN** it is accepted and used as `DE`

#### Scenario: Language tag accepted

- **WHEN** `locale="en-US"` is supplied
- **THEN** it is accepted unchanged

#### Scenario: Invalid code rejected before I/O

- **WHEN** `locale="USA"` (or `""`, `"u1"`, `"123"`) is supplied at construction
  or per call
- **THEN** `URLError` is raised and no HTTP request is issued

### Requirement: Anonymous market/availability is not supported

The library SHALL NOT expose a `market=`/availability parameter on the anonymous
ladder and SHALL NOT model `market` as a pathfinder GraphQL variable, because
Spotify's anonymous pathfinder silently discards such a variable and resolves
country from the request IP. Documentation SHALL state that `locale` localizes
display-name *language* only and that regional *availability*/preview filtering
requires the authenticated Web API, which this library does not implement
anonymously.

#### Scenario: No silent no-op kwarg

- **WHEN** a caller wants regional availability filtering
- **THEN** the public API offers no anonymous `market=` toggle that would appear
  to work while changing nothing; the documented path is the authenticated Web
  API (out of scope)

#### Scenario: Locale does not change availability

- **WHEN** the same entity is fetched with two different `locale` values
- **THEN** only localized display names may differ; availability/playability
  fields are unchanged
