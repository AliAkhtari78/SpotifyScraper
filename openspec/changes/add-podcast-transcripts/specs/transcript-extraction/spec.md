# transcript-extraction

## ADDED Requirements

### Requirement: Authenticated transcript fetch

`get_transcript(value)` SHALL accept any podcast-episode input the URL handling
accepts (URL, URI, or 22-character ID) and return a `Transcript` model from
Spotify's `transcript-read-along` endpoint, using the cookie-derived web-player
token. Calling it on a client constructed without cookies SHALL raise
`AuthenticationError` immediately, with no network request.

#### Scenario: No cookies configured

- **WHEN** `get_transcript` is called on a cookie-less client
- **THEN** `AuthenticationError` is raised without any HTTP request

#### Scenario: Episode with a transcript

- **WHEN** a transcript exists for an episode
- **THEN** the returned `Transcript` has a non-empty `lines` tuple and every
  `TranscriptLine` carries non-empty `text` and a non-negative `start_ms`

#### Scenario: Full URL input

- **WHEN** `get_transcript` is given `https://open.spotify.com/episode/{id}`
- **THEN** the same `Transcript` is returned as for the bare ID

### Requirement: Transcript absence is distinct from auth failure

Episodes without a transcript SHALL raise `NotFoundError` (the episode exists;
the transcript does not). Cookie/token problems SHALL raise
`AuthenticationError`. The two SHALL never be conflated.

#### Scenario: Episode without a transcript

- **WHEN** a transcript is requested for an episode the endpoint 404s
- **THEN** `NotFoundError` is raised, not `AuthenticationError`

#### Scenario: Rejected token retried once

- **WHEN** the transcript endpoint returns HTTP 401 on the first attempt
- **THEN** the cached token is invalidated, re-exchanged once, and the request
  is retried; a second 401 surfaces as `AuthenticationError`

### Requirement: Shared cookie token with lyrics

Transcript extraction SHALL reuse the same cookie-derived web-player token
provider as lyrics; a single `sp_dc` exchange SHALL serve both features within
one client, and entity extraction SHALL continue to use only the anonymous
token. A failure in either auth path SHALL not affect the other.

#### Scenario: One token, two features

- **WHEN** `get_lyrics` and `get_transcript` are called on the same client
- **THEN** the cookie token is exchanged once and reused for both, while
  `get_track` continues to use the anonymous token

#### Scenario: Broken cookie, working extraction

- **WHEN** a client has an expired `sp_dc` but calls `get_episode`
- **THEN** the episode fetch succeeds normally and only `get_transcript`/
  `get_lyrics` raise `AuthenticationError`

### Requirement: Endpoint isolated for one-line refresh

The transcript endpoint host, path, and query parameters SHALL be defined in
exactly one module (`api/transcripts.py`), mirroring how pathfinder
persisted-query hashes are confined to `api/pathfinder.py`, so a Spotify change
is a single-file edit.

#### Scenario: Endpoint change

- **WHEN** Spotify changes the transcript path or query
- **THEN** only `api/transcripts.py` requires modification; models, parser, and
  clients are unaffected

### Requirement: Malformed payload surfaces as ParsingError

A transcript response that cannot be decoded into the expected lines container
SHALL raise `ParsingError` carrying the standard update hint; the parser SHALL
NOT return error strings or error dicts.

#### Scenario: Unexpected payload shape

- **WHEN** the decoded transcript payload lacks its lines container
- **THEN** `ParsingError` is raised naming the missing path with the update hint
