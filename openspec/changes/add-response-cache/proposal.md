# Proposal: add-response-cache

> **Status: targets v3.x.** Closes issue #131. Adds an **opt-in, OFF-by-default**
> persistent on-disk HTTP response cache that cuts repeat fetches, speeds bulk
> jobs, and reduces ban risk. **No new runtime dependency** — a stdlib file store
> behind a pluggable `DiskCache` protocol. The cache sits entirely at the
> transport seam as a `CachingTransport` / `AsyncCachingTransport` wrapper, so it
> composes with rate limiting, retries, and locale and touches **no** parser,
> model, auth, or media code. Fully hermetic to test — no live step.

## Why

Repeat extraction of the same public entity (re-running a script, paging a large
playlist whose tracks were already fetched, batch jobs that revisit artists)
re-hits `open.spotify.com/embed/*` and `api-partner.spotify.com/pathfinder/*` on
every run. Each fetch costs latency and, more importantly, contributes to the
request volume that triggers Spotify rate-limiting / bans. A local response cache
makes the second-and-subsequent reads of stable public data free and fully
offline, which is the single biggest reliability win available to bulk users.

It must be **opt-in and off by default** (CLAUDE.md, prompt) and must **not add a
required dependency** — exactly like the cookie/session story, it uses a stdlib
on-disk store. Because the data it caches is anonymous public JSON/HTML, the
cache is **fully hermetically testable** with no network.

## What Changes

- **`http/cache.py`** (new) houses the entire feature at the transport boundary:
  - `CachingTransport(inner: Transport, config: CacheConfig)` and
    `AsyncCachingTransport(inner: AsyncTransport, config: CacheConfig)` — each
    **structurally satisfies** the existing `Transport` / `AsyncTransport`
    `@runtime_checkable` protocols, so it is a drop-in for the `transport=`
    constructor override. No client method, parser, or model touches the cache.
  - `CachedResponse` — a frozen slotted dataclass that satisfies the `Response`
    protocol (`status_code`, `headers`, `text`, `content`, `json()`), because a
    live `httpx.Response` cannot be re-served from disk (closed stream).
    `json()` raises `ValueError` on a non-JSON body to match the clients'
    `_safe_json` contract.
  - `CacheEntry` (frozen slotted: `status_code`, `content`, `headers`,
    `stored_at`) — the stored unit.
  - `CacheConfig` (frozen slotted): the `DiskCache` store, `ttl_seconds`, the
    `cacheable_hosts` allowlist, and the `denied_path_prefixes` denylist.
  - `DiskCache` — a `@runtime_checkable` Protocol (`get`/`set`/`clear`/`close`)
    so users can drop in their own store (in-memory dict for tests, Redis in
    their own code) **without the library taking a dependency**.
  - `FileCache(DiskCache)` — the default **stdlib-only** implementation: one
    file per sha256 key under a base dir, JSON envelope with base64'd body,
    atomic `tmp + os.replace` writes, `clear()` for invalidation. No `pickle`.
- **Cacheability is URL-pattern driven** and enforced in one private
  `_is_cacheable(url)` predicate. Only `open.spotify.com/embed/*` and
  `api-partner.spotify.com/pathfinder/*` are cacheable. Everything else passes
  straight through to the inner transport and is **never read from or written
  to** the store (see `cache_design` for the exact rule).
- **Only successful (`status_code == 200`) returned responses are stored.** The
  inner transport raises `NotFoundError`/`RateLimitedError`/`NetworkError` for
  non-success cases — those propagate uncaught and are **never cached**.
  Pass-through statuses (401/403) are returned but **not** stored.
- **Opt-in surface** (two layers, both off by default):
  1. **Pure injection (zero client change, baseline):** a user wraps their own
     transport — `SpotifyClient(transport=CachingTransport(HttpxTransport(...), config))`.
     `_owns_transport=False`, so the user owns teardown; `CachingTransport.close()`
     still propagates to the inner transport.
  2. **First-class flag:** a `cache: CacheConfig | None = None` kwarg on both
     clients. When `transport is None and cache is not None`, the client builds
     `CachingTransport(HttpxTransport(...), cache)` and keeps `_owns_transport=True`
     (owns and closes the whole stack). `cache` is **ignored when an explicit
     `transport=` is supplied**, exactly as `rate_limit`/`retry`/`proxy` already are.
- **Exports:** `CachingTransport`, `AsyncCachingTransport`, `CacheConfig`,
  `FileCache`, `DiskCache`, `CacheEntry`, `CachedResponse` from
  `spotify_scraper.http`; the user-facing trio (`CacheConfig`, `FileCache`,
  and at least one `CachingTransport`) re-exported from the top-level package
  `__all__` (sorted).
- **Hermetic tests** (`tests/unit/http/test_cache.py`): a `FileCache` in
  `tmp_path` plus a fake inner transport (a stub satisfying `Transport`) gives a
  fully offline test — first `get` records, second returns from disk with the
  stub asserted **not** called again. Explicit tests that token/server-time/
  spclient URLs pass straight through and are never written, that 401/403/
  `NotFoundError` are not cached, that TTL expiry re-fetches, that a corrupt file
  is a silent miss, and that `clear()` invalidates.

## Impact

- **New:** `src/spotify_scraper/http/cache.py`, `tests/unit/http/test_cache.py`.
- **Edited (first-class flag):** `src/spotify_scraper/http/__init__.py` (exports),
  `src/spotify_scraper/__init__.py` (top-level `__all__`),
  `src/spotify_scraper/_sync/client.py` + `src/spotify_scraper/_async/client.py`
  (a `cache=` kwarg on the `if transport is None` branch + docstring). The
  `__slots__` tuples do **not** change — the cache is owned by the transport.
- **No changes** to `transport.py`, `pathfinder.py`, `auth/*`, `api/*`,
  `media/*`, or any model. The cache is a pure I/O wrapper at the transport seam.
- **Default behavior is unchanged for everyone**: no `cache` argument / no
  wrapper ⇒ byte-identical to today. One new runtime dependency: **none**.
