# Design: add-response-cache

## Goal

An opt-in, off-by-default, stdlib-only persistent response cache that sits at the
transport seam, caches only anonymous public-data GETs, never caches credentials
or per-user data, and adds no runtime dependency.

## Placement: the transport seam

`http/transport.py` defines two `@runtime_checkable` protocols the clients depend
on (`http/transport.py:57` sync `Transport.get/close`, `:70` async
`AsyncTransport.get/aclose`) and a structural `Response` protocol
(`http/transport.py:32`: `status_code`, properties `headers`/`text`/`content`,
method `json()`). Clients own a `Transport`/`AsyncTransport` and only close it
when `_owns_transport` is True (`_sync/client.py:108-120`,
`_async/client.py:107-119`).

The cache is a **wrapper transport** that implements the same protocol, so it
composes with everything the inner `HttpxTransport` already does (rate limiting,
retry, error mapping, locale headers) without re-implementing any of it. This is
the lowest-risk, sans-io-respecting placement: the cache is pure I/O glue at the
existing transport boundary, touching no parser, model, auth, or media code.

## Why a `CachedResponse` is required

The inner transport returns a live `httpx.Response`. That object holds a closed
stream / client reference and cannot be re-served from disk on a later run. So a
cache hit must reconstruct a value object that **also satisfies the `Response`
protocol**. `CachedResponse` is a frozen slotted dataclass exposing
`status_code`, `headers`, `text` (decode with `errors="replace"`), `content`,
and `json()`. Crucially `json()` does `json.loads(self.content)`, which raises
`ValueError` on a non-JSON body — both clients' `_safe_json`
(`_sync/client.py:841`, `_async/client.py:840`) and `cookies.py`/`pathfinder.py`
rely on `ValueError` for malformed JSON, so the cached path must match that
contract exactly.

## Error semantics live in the inner transport, not the cache

`_response_delay` (`http/transport.py:124`) raises `NotFoundError` on 404,
`RateLimitedError` on unrecoverable 429, and `NetworkError` on connect failures /
exhausted 403/5xx — these never return a `Response`. So any value `get()`
**returns** is, by construction, a non-retryable status (200, or a pass-through
like 401 that `pathfinder.classify_response`/lyrics handle). The wrapper:

- **Never** intercepts or caches the raised `NotFoundError`/`RateLimitedError`/
  `NetworkError` — they propagate from the inner transport uncaught.
- Stores **only** `status_code == 200` returned responses. It does not persist
  401/403 pass-throughs (they are per-context and short-lived).

This keeps all error policy in one place (the inner transport) and the cache a
dumb success-cache.

## Cacheability: one predicate, host + path driven

The wrapper only sees a URL + headers in `get()`, so cacheability is purely a
function of host and path prefix, computed by a single `_is_cacheable(url)`:

```
u = httpx.URL(url)
return u.host in config.cacheable_hosts \
   and not any(u.path.startswith(p) for p in config.denied_path_prefixes)
```

`cacheable_hosts = {"api-partner.spotify.com", "open.spotify.com"}`,
`denied_path_prefixes = {"/api/"}`. This single rule realizes the whole §4 table:

| Caller (file) | URL | Decision |
|---|---|---|
| embed (`urls.embed_url`; `_fetch_next_data`; `anonymous.py` bootstrap) | `open.spotify.com/embed/<type>/<id>` | **CACHE** (host allowed, path not `/api/`) |
| pathfinder (`pathfinder.PATHFINDER_URL`) | `api-partner.spotify.com/pathfinder/v1/query?...` | **CACHE** |
| server-time (`cookies.SERVER_TIME_URL`) | `open.spotify.com/api/server-time` | **NEVER** (path `/api/` denied) |
| token (`cookies.TOKEN_URL`) | `open.spotify.com/api/token?...` | **NEVER** (path `/api/` denied) |
| lyrics (`lyrics._LYRICS_BASE`) | `spclient.wg.spotify.com/color-lyrics/v2/track/<id>?...` | **NEVER** (host not allowed) |
| transcripts (same host) | `spclient.wg.spotify.com/...` | **NEVER** (host not allowed) |
| CDN images/audio (`media/*`, host from payload) | `*.scdn.co` | **NEVER** (host not allowed; binaries belong on disk via `download_*`) |

Important subtlety: the anonymous-token **bootstrap** reads an embed page
(`anonymous.py`), which IS a cacheable embed URL. That is acceptable — the embed
page's token is short-lived and `AnonymousTokenProvider.is_stale`/`invalidate`
already re-fetch when the token rotates; the cached HTML still yields a usable
fresh token on first parse, and TTL bounds staleness. The credential **exchange**
(`/api/token`, `/api/server-time`) is denied by the `/api/` prefix, so no
short-lived secret is ever persisted.

## Key derivation

sha256 of the full URL + the cache-relevant header (`Accept-Language`, since
`_lang_header` varies pathfinder/embed responses by locale). `Authorization` is
**excluded** from the key: pathfinder uses the rotating anonymous token, which
does not change the public response, so including it would defeat the cache.
Authenticated hosts are already denied at `_is_cacheable`, so no user secret can
ever influence a key.

## The store: stdlib `FileCache` behind a `DiskCache` protocol

`DiskCache` is `@runtime_checkable` (`get`/`set`/`clear`/`close`) so users can
substitute an in-memory dict (tests) or Redis (their own code) with no library
dependency — mirroring how the session/cookie store stays stdlib. The default
`FileCache`:

- One file per sha256 hex key under a base dir (default
  `Path.home() / ".cache" / "spotify_scraper"`, or a caller `Path`).
- One JSON doc per entry: `status_code`, `headers`, `stored_at`, and `content`
  base64-encoded. **No `pickle`** (untrusted-deserialization smell on a public
  repo — professionalism rule).
- Atomic writes: `tmp` file in the same dir + `os.replace`, so a crash cannot
  leave a torn entry.
- TTL is enforced in the wrapper (compare `stored_at` to `ttl_seconds`), keeping
  the store a dumb KV. `clear()` removes all entry files for invalidation.

## Async

`AsyncCachingTransport` holds an `AsyncTransport`, `await`s the inner `get`, and
defines `aclose`. The `DiskCache` store stays **synchronous** — blocking file
I/O, exactly as `media`/`cookies` already do — so there is no event-loop concern
beyond what the codebase already accepts. The `_is_cacheable`/`_key` logic is
shared (module-level helpers) so sync and async cannot drift.

## Failure handling — only `errors.py`, else silent miss

The cache invents no errors. A store read failure (corrupt file, `OSError`) is a
**miss**: fall through to the network, never raise a bare exception, never an
error dict/string — optionally a `logging.getLogger("spotify_scraper").warning`,
matching how the clients log degradations. A write failure likewise degrades to
"didn't cache" rather than failing the request.

## Integration: two opt-in layers, both off by default

1. **Pure injection (zero client edit):** user builds
   `CachingTransport(HttpxTransport(...), config)` and passes `transport=`. Then
   `_owns_transport=False`; the user owns teardown, and `CachingTransport.close()`
   propagates to `inner.close()`.
2. **First-class `cache=` kwarg:** when `transport is None and cache is not
   None`, the client builds `CachingTransport(HttpxTransport(...), cache)` and
   keeps `_owns_transport=True` (owns and closes the whole stack — `close()`
   closes the store then the inner httpx transport). `cache` is **ignored** when
   an explicit `transport=` is supplied, exactly as `rate_limit`/`retry`/`proxy`
   are. No `__slots__` change is needed — the cache is owned by the transport,
   not the client.

The minimal shipping form is option 1 + new files only (zero edits to existing
clients). Option 2 is the ergonomic flag and is included here.

## Why this respects every architecture rule

- **Sans-io:** the cache is pure I/O glue at the transport boundary; no Spotify
  intelligence moves into it.
- **One runtime dependency:** stdlib store + `httpx.URL` (already a dep). No new
  required package.
- **Typed:** `CachedResponse`/`CacheEntry`/`CacheConfig` are frozen slotted
  dataclasses; wrappers satisfy the protocols structurally; `mypy --strict`
  passes.
- **Errors from `errors.py`:** the cache raises none; failures degrade to a miss;
  inner-transport errors propagate unchanged.
- **Hermetic by default:** a `FileCache` in `tmp_path` + a stub inner transport
  is fully offline — no `@pytest.mark.live`.
- **Opt-in, off by default:** no `cache` / no wrapper ⇒ identical to today.
