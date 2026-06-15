# Response caching

For repeated lookups you can enable an **opt-in, off-by-default** persistent
response cache. It is a thin transport wrapper that sits in front of the normal
HTTP stack, so it composes with rate limiting, retries, and `locale` without
changing any call site.

```python
from spotify_scraper import SpotifyClient, CacheConfig, FileCache

cache = CacheConfig(store=FileCache())          # stdlib file store, no new deps
with SpotifyClient(cache=cache) as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")   # first call hits the network
    again = client.get_track("4uLU6hMCjMI75M1A2tKUQC")   # served from the cache
```

The default `FileCache` writes one file per entry under
`~/.cache/spotify_scraper` (override with `FileCache(dir=...)`); a read failure
degrades to a miss rather than raising.

## What gets cached (and what never does)

Caching is deliberately conservative — only **safe, token-free** responses:

- ✅ `GET`s to the pathfinder host (`api-partner.spotify.com/pathfinder/*`) with
  `status_code == 200`.
- ❌ The **embed pages** (`open.spotify.com/embed/*`) are never cached: their
  `__NEXT_DATA__` carries the short-lived anonymous access token, so caching them
  would persist a credential to disk *and* re-serve an expired token once it
  rotated.
- ❌ The token endpoints (`open.spotify.com/api/*`) and the cookie-authenticated
  lyrics/transcript host (`spclient.wg.spotify.com`) are never cached.

Only successful (`200`) responses are stored; transport errors propagate
uncached. The cache key includes the `Accept-Language` header, so requests asking
for different display languages never collide.

## Tuning it

`CacheConfig` is a frozen dataclass:

| Field | Default | Meaning |
|---|---|---|
| `store` | *(required)* | The `DiskCache` backend (e.g. `FileCache()`) |
| `ttl_seconds` | `86400.0` (24h) | Entries older than this are a miss |
| `cacheable_hosts` | `{"api-partner.spotify.com"}` | Hosts whose GETs may be cached |
| `denied_path_prefixes` | `{"/api/"}` | Never-cached path prefixes on a cacheable host |

```python
cache = CacheConfig(store=FileCache(), ttl_seconds=3600)   # 1-hour TTL
```

!!! warning "Never add a token-bearing host"
    Do not add `open.spotify.com` (or any token/cookie host) to
    `cacheable_hosts` — the cache would persist and re-serve a credential.

## Custom backends

`store` is any object satisfying the `DiskCache` protocol (`get`/`set`/`clear`),
so you can plug in an in-memory dict for tests or Redis in your own code:

::: spotify_scraper.http.cache.DiskCache
