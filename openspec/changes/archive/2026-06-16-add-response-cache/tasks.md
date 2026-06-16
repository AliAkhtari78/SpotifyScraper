# Tasks: add-response-cache

## 0. Ground the cacheability rule (no network — read-only audit) — design input

- [x] 0.1 Confirm the three Spotify hosts the library hits, from the URL
      constants: `open.spotify.com` (embed `embed_url`, and the NEVER-cache
      `SERVER_TIME_URL`/`TOKEN_URL` under `/api/`), `api-partner.spotify.com`
      (`PATHFINDER_URL = .../pathfinder/v1/query`), `spclient.wg.spotify.com`
      (lyrics `_LYRICS_BASE = .../color-lyrics/v2/track`, transcripts same host).
      CDN hosts (`*.scdn.co`) come from payloads at runtime and are not in
      `cacheable_hosts`.
- [x] 0.2 Pin the exact predicate: CACHE iff `host ∈ {open.spotify.com,
      api-partner.spotify.com}` AND no `denied_path_prefixes` ({"/api/"}) match.
      `spclient.wg.spotify.com` is simply absent from `cacheable_hosts` ⇒ denied.
      This single rule covers every NEVER row in the spec table.

## 1. Data types (frozen slotted, mypy --strict)

- [x] 1.1 In `src/spotify_scraper/http/cache.py` add `CachedResponse`
      (`@dataclass(frozen=True, slots=True)`): `status_code: int`,
      `content: bytes`, `_headers: Mapping[str, str]`, `_encoding: str = "utf-8"`;
      properties `headers`, `text` (`content.decode(encoding, errors="replace")`),
      method `json()` → `json.loads(self.content)` (must raise `ValueError` on a
      bad body). Assert it satisfies the `Response` protocol structurally.
- [x] 1.2 Add `CacheEntry` (frozen slotted): `status_code: int`,
      `content: bytes`, `headers: Mapping[str, str]`, `stored_at: float`.
- [x] 1.3 Add `CacheConfig` (frozen slotted): `store: DiskCache`,
      `ttl_seconds: float = 86_400.0`,
      `cacheable_hosts: frozenset[str] = frozenset({"api-partner.spotify.com",
      "open.spotify.com"})`,
      `denied_path_prefixes: frozenset[str] = frozenset({"/api/"})`.

## 2. Pluggable store protocol + stdlib default

- [x] 2.1 Add `@runtime_checkable class DiskCache(Protocol)` with
      `get(key) -> CacheEntry | None`, `set(key, entry) -> None`,
      `clear() -> None`, `close() -> None`.
- [x] 2.2 Add `FileCache(DiskCache)` — **stdlib only**. `__init__(self, dir:
      Path | None = None)` defaults to `Path.home() / ".cache" / "spotify_scraper"`;
      `mkdir(parents=True, exist_ok=True)`. Filename = the sha256 hex key.
- [x] 2.3 `set`: serialize `CacheEntry` to one JSON doc
      (`status_code`, `headers`, `stored_at`, `content` as base64) and write
      **atomically** (`tmp` file in the same dir + `os.replace`). **No `pickle`.**
- [x] 2.4 `get`: read+parse the file; on any `OSError`/`ValueError`/missing-key,
      return `None` (silent miss). Optionally log a `warning` on a corrupt file
      via `logging.getLogger("spotify_scraper")`. Never raise.
- [x] 2.5 `clear`: remove all entry files under the base dir (invalidation).
      `close`: no-op (files are flushed on `set`); keep for protocol parity.

## 3. The caching wrapper (sync)

- [x] 3.1 `CachingTransport.__init__(self, inner: Transport, config: CacheConfig)`.
      Store both; expose nothing else.
- [x] 3.2 `_is_cacheable(self, url) -> bool`: `u = httpx.URL(url)`;
      return `u.host in config.cacheable_hosts and not any(u.path.startswith(p)
      for p in config.denied_path_prefixes)`. This enforces every NEVER rule.
- [x] 3.3 `_key(self, url, headers) -> str`: `sha256` hex of the **full URL** +
      the cache-relevant header (`Accept-Language`, lowercased lookup). **Exclude
      `Authorization` entirely** from the key (the anonymous token rotates without
      changing the public response; authed hosts are already denied at step 3.2).
- [x] 3.4 `get(self, url, *, headers=None) -> Response`:
      (a) `if not self._is_cacheable(url): return self._inner.get(url, headers=headers)`
      — no store read/write;
      (b) `entry = self._config.store.get(key)`; if present and
      `time.time() - entry.stored_at < config.ttl_seconds`, return
      `CachedResponse(entry.status_code, entry.content, entry.headers)` — **no
      network**;
      (c) miss/stale ⇒ `response = self._inner.get(url, headers=headers)` (lets
      `NotFoundError`/`RateLimitedError`/`NetworkError` propagate uncaught);
      (d) if `response.status_code == 200`, `store.set(key, CacheEntry(...,
      stored_at=time.time()))` reading `response.content`/`response.headers`;
      return the original `response` either way (do NOT store 401/403).
- [x] 3.5 `close(self) -> None`: `self._config.store.close()` then
      `self._inner.close()` (store first so a store error still tears down httpx —
      or guard the store close so the inner always closes).

## 4. The caching wrapper (async)

- [x] 4.1 `AsyncCachingTransport.__init__(self, inner: AsyncTransport,
      config: CacheConfig)`; reuse `_is_cacheable`/`_key` (module-level helpers or
      a shared mixin — keep `mypy --strict` clean, no duplicated logic drift).
- [x] 4.2 `async def get(...)` mirrors 3.4 with `await self._inner.get(...)`. The
      `DiskCache` store stays **synchronous** (blocking file I/O, as media/cookies
      already do) — no event-loop concern.
- [x] 4.3 `async def aclose(self)`: `self._config.store.close()` then
      `await self._inner.aclose()`.

## 5. Exports

- [x] 5.1 Add to `http/__init__.py` imports + `__all__` (sorted):
      `CachingTransport`, `AsyncCachingTransport`, `CacheConfig`, `FileCache`,
      `DiskCache`, `CacheEntry`, `CachedResponse`.
- [x] 5.2 Re-export the user-facing trio (`CacheConfig`, `FileCache`,
      `CachingTransport`, `AsyncCachingTransport`) from the top-level
      `src/spotify_scraper/__init__.py` (`__all__`, sorted).

## 6. First-class client flag (opt-in; off by default)

- [x] 6.1 `_sync/client.py`: add `cache: CacheConfig | None = None` to
      `__init__`. In the `if transport is None` branch, when `cache is not None`
      wrap: `self._transport = CachingTransport(HttpxTransport(...), cache)`,
      `_owns_transport = True`. When `transport is not None`, `cache` is **ignored**
      (document it, mirroring `rate_limit`/`retry`/`proxy`). No `__slots__` change.
- [x] 6.2 `_async/client.py`: same with `AsyncCachingTransport` +
      `AsyncHttpxTransport`.
- [x] 6.3 Update both constructor docstrings: `cache` is opt-in, off by default,
      ignored when a custom `transport` is supplied; the client owns/closes the
      wrapped stack.

## 7. Hermetic tests (no live step)

- [x] 7.1 A `_StubTransport` satisfying `Transport`/`AsyncTransport` that records
      calls and returns a canned `httpx.Response` (or a `CachedResponse`-shaped
      object). Assert wrappers satisfy the `@runtime_checkable` protocols.
- [x] 7.2 **Hit path:** first `get` to a pathfinder URL records via the stub;
      second `get` returns from `FileCache` in `tmp_path` with the stub asserted
      **not** called again; bytes/headers/status round-trip.
- [x] 7.3 **NEVER rules:** `https://open.spotify.com/api/token`,
      `.../api/server-time`, and any `https://spclient.wg.spotify.com/...` URL are
      passed straight through and **never written** to the store (assert empty dir
      / stub called every time).
- [x] 7.4 **No-cache-on-error:** a `NotFoundError` raised by the stub propagates
      and writes nothing; a returned 401 and a returned 403 are passed through and
      **not** stored.
- [x] 7.5 **TTL:** a stored entry with `stored_at` older than `ttl_seconds` is
      treated as a miss and re-fetched (monkeypatch `time.time` or set
      `ttl_seconds` low).
- [x] 7.6 **Locale key:** two `get`s to the same URL with different
      `Accept-Language` produce two distinct entries; identical headers hit.
- [x] 7.7 **Authorization excluded:** two `get`s to the same pathfinder URL with
      different `Authorization` headers (same `Accept-Language`) hit the **same**
      entry (second served from cache).
- [x] 7.8 **Corrupt file = silent miss:** a garbage file at the key path causes a
      re-fetch, no raised exception.
- [x] 7.9 **clear():** after `store.clear()` the next `get` re-fetches.
- [x] 7.10 **close propagation:** `CachingTransport.close()` /
      `AsyncCachingTransport.aclose()` calls the inner transport's close/aclose.
- [x] 7.11 Async variants of 7.2–7.4 with `pytest.mark.asyncio`.

## 8. Quality gates

- [x] 8.1 `make type` (mypy --strict) clean — every signature annotated; wrappers
      rely on structural typing.
- [x] 8.2 `make lint` / `make format` clean.
- [x] 8.3 `make cov` stays above the 85% floor; new module well-covered.
- [x] 8.4 No new runtime dependency in `pyproject.toml` (stdlib `hashlib`,
      `json`, `base64`, `os`, `time`, `pathlib`, `logging` only; `httpx.URL`
      already a dep).

## 9. Review fixes

- [x] 9.1 (code, prior session) stop caching the token-bearing embed page; only
      the token-free pathfinder response is cached; cache dir is 0700.
- [x] 9.2 Docs: new `guides/caching.md` (opt-in, token-safe scope, TTL, pluggable
      `DiskCache`) + nav; README Caching section + Features bullet + roadmap (3.5
      cache shipped); index roadmap + success admonition; CHANGELOG Unreleased.
