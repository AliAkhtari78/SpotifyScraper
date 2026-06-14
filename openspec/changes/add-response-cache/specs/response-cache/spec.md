# response-cache

## ADDED Requirements

### Requirement: Opt-in, off-by-default response cache

The library SHALL provide an optional persistent HTTP response cache that is
**disabled by default**. With no `cache` argument and no caching transport, the
client's HTTP behavior SHALL be byte-identical to a build without this feature.
The cache SHALL add **no new required runtime dependency** (stdlib-only default
store). It SHALL be enabled either by wrapping a transport
(`CachingTransport`/`AsyncCachingTransport`) or by a first-class `cache:
CacheConfig` client kwarg.

#### Scenario: Disabled by default

- **WHEN** a `SpotifyClient` is constructed with no `cache` argument and no
  custom transport
- **THEN** no cache directory is created, every fetch goes to the network, and
  behavior is identical to today

#### Scenario: Enabled by injection

- **WHEN** a client is built with
  `transport=CachingTransport(HttpxTransport(...), CacheConfig(store=FileCache(path)))`
- **THEN** cacheable GETs are served from disk on repeat without a network call

#### Scenario: Enabled by first-class flag

- **WHEN** a client is built with `cache=CacheConfig(store=FileCache(path))` and
  no custom `transport`
- **THEN** the client owns a caching transport stack and closes it on `close()`

#### Scenario: cache ignored under a custom transport

- **WHEN** both `cache=...` and an explicit `transport=...` are supplied
- **THEN** the custom transport wins and `cache` is ignored, exactly as
  `rate_limit`/`retry`/`proxy` are ignored under a custom transport

### Requirement: Only public-data GETs are cacheable

The cache SHALL store responses **only** for safe GETs to the public-data hosts
and paths: `open.spotify.com/embed/*` and
`api-partner.spotify.com/pathfinder/*`. It SHALL **never** read from or write to
the store for any other request. In particular it SHALL never cache the
token-exchange endpoints (`open.spotify.com/api/token`,
`open.spotify.com/api/server-time`) nor any request to the cookie-authenticated
host `spclient.wg.spotify.com` (lyrics, transcripts). Non-cacheable requests
SHALL pass straight through to the inner transport.

#### Scenario: Embed and pathfinder are cached

- **WHEN** a GET to `https://open.spotify.com/embed/track/<id>` or
  `https://api-partner.spotify.com/pathfinder/v1/query?...` succeeds with 200
- **THEN** the response is stored and a subsequent identical GET is served from
  the store with no network call

#### Scenario: Token endpoints are never cached

- **WHEN** a GET to `https://open.spotify.com/api/token?...` or
  `https://open.spotify.com/api/server-time` is made
- **THEN** it passes straight through to the inner transport, is repeated on
  every call, and nothing is written to the store

#### Scenario: spclient host is never cached

- **WHEN** any GET to `https://spclient.wg.spotify.com/...` (lyrics or
  transcripts) is made
- **THEN** it passes straight through and is never written to the store,
  regardless of status

### Requirement: Only successful responses are cached; errors are not

The cache SHALL store a response **only** when it is a returned
`status_code == 200`. Errors raised by the inner transport
(`NotFoundError`, `RateLimitedError`, `NetworkError`) SHALL propagate uncaught
and SHALL NOT be cached. Returned non-200 pass-through statuses (e.g. 401, 403)
SHALL NOT be stored.

#### Scenario: NotFound is not cached

- **WHEN** the inner transport raises `NotFoundError` for a cacheable URL
- **THEN** the error propagates and nothing is written; a later success for the
  same URL is cached normally

#### Scenario: 401/403 pass-throughs are not cached

- **WHEN** the inner transport returns a 401 or 403 for a cacheable URL
- **THEN** the response is returned to the caller but not stored, and a later
  200 for the same URL is cached

### Requirement: Cache key derivation

The cache key SHALL be the sha256 of the full request URL combined with the
cache-relevant request header(s) that vary the response — specifically
`Accept-Language` (locale). The key SHALL **exclude `Authorization`** so that
anonymous-token rotation does not defeat the cache. (Authenticated hosts are
already excluded from caching, so no user secret can influence a key.)

#### Scenario: Locale varies the key

- **WHEN** the same URL is fetched with `Accept-Language: DE` and then with
  `Accept-Language: JA`
- **THEN** two distinct entries are stored and each locale is served its own body

#### Scenario: Authorization does not vary the key

- **WHEN** the same pathfinder URL is fetched twice with different
  `Authorization` bearer tokens but the same `Accept-Language`
- **THEN** the second fetch hits the same cached entry and makes no network call

### Requirement: TTL expiry

Cached entries SHALL carry a stored-at timestamp and SHALL be treated as a miss
once `now - stored_at >= ttl_seconds` (default 86 400 s / 24 h, configurable on
`CacheConfig`). An expired entry SHALL trigger a fresh fetch.

#### Scenario: Expired entry re-fetches

- **WHEN** a cached entry's age exceeds `ttl_seconds`
- **THEN** the next GET ignores it, fetches from the network, and overwrites it

### Requirement: Pluggable store, stdlib default, safe failure, invalidation

The store SHALL be a `@runtime_checkable DiskCache` protocol
(`get`/`set`/`clear`/`close`) so callers can substitute their own backend with no
new library dependency. The default `FileCache` SHALL be **stdlib-only**, write
entries atomically, and never use `pickle`. A store read failure (corrupt file,
`OSError`) SHALL be treated as a **miss** (fall through to the network) and SHALL
NOT raise a bare exception or return an error string/dict. The store SHALL expose
`clear()` for cache invalidation.

#### Scenario: Corrupt entry is a silent miss

- **WHEN** an on-disk entry is unreadable or malformed
- **THEN** the cache treats it as a miss and fetches from the network without
  raising

#### Scenario: Clear invalidates

- **WHEN** `store.clear()` is called
- **THEN** all stored entries are removed and the next GET re-fetches

#### Scenario: Custom in-memory store

- **WHEN** a user passes a dict-backed object satisfying `DiskCache` as the store
- **THEN** the cache works against it with no `FileCache` or filesystem use

### Requirement: Close propagation

Closing a caching wrapper SHALL close both the store and the inner transport.
For client-owned stacks (`cache=` flag), `close()`/`aclose()` SHALL tear down the
underlying httpx transport. For injected wrappers, the wrapper's
`close()`/`aclose()` SHALL still propagate to the inner transport when called.

#### Scenario: Owned stack tears down httpx

- **WHEN** a client built with `cache=...` is closed
- **THEN** the inner httpx transport is closed and the store is closed

#### Scenario: Injected wrapper propagates close

- **WHEN** a user calls `close()` on a `CachingTransport` they constructed
- **THEN** the inner transport's `close()` is invoked
