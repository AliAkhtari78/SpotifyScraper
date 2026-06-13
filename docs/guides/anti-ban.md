# Anti-ban & resilience

Scraping public pages politely is the difference between a tool that keeps
working and one that gets blocked. SpotifyScraper ships sensible defaults and
exposes every knob so you can tune for your environment.

All options below are constructor keyword arguments and work identically on
`SpotifyClient` and [`AsyncSpotifyClient`](async.md).

## Rate limiting

A client-side **token bucket** throttles outgoing requests *per host*. It is on
by default, so you stay polite without configuring anything.

```python
from spotify_scraper import SpotifyClient, RateLimit

client = SpotifyClient(
    rate_limit=RateLimit(per_second=2.0, burst=5),
)
```

`RateLimit` has two fields:

| Field | Default | Meaning |
|---|---|---|
| `per_second` | `2.0` | Sustained request rate — the bucket refill rate. |
| `burst` | `5` | Bucket capacity — how many requests may fire instantly before throttling kicks in. |

The bucket starts full: the first `burst` requests go out immediately, then the
rate settles to `per_second`. Lower both values to be gentler on a shared IP;
raise them cautiously if you control your own egress and are seeing no blocks.

!!! tip "Concurrency does not bypass the limiter"
    The same bucket governs the async client. Launching hundreds of
    `asyncio.gather` tasks does not send hundreds of simultaneous requests —
    they drain at the configured rate.

## Retries and backoff

Transient failures (HTTP 429/403/5xx, connection resets, timeouts) are retried
automatically with **exponential backoff and jitter**. Configure it with
`RetryPolicy`:

```python
from spotify_scraper import SpotifyClient, RetryPolicy

client = SpotifyClient(
    retry=RetryPolicy(max_attempts=4, backoff_base=0.5, backoff_max=30.0),
)
```

| Field | Default | Meaning |
|---|---|---|
| `max_attempts` | `4` | Total attempts including the first request. |
| `backoff_base` | `0.5` | Delay (seconds) before the second attempt; doubles each retry. |
| `backoff_max` | `30.0` | Ceiling for any single delay. A `Retry-After` hint above this aborts retrying. |

When the server sends a `Retry-After` header on a 429, the library honors it
(unless it exceeds `backoff_max`). Otherwise the delay is
`backoff_base * 2 ** (attempt - 1)`, capped at `backoff_max`, plus up to 25%
random jitter so concurrent clients do not retry in lockstep.

## What 429 and 403 mean

| Status | Meaning | Library behavior |
|---|---|---|
| **429 Too Many Requests** | You are being rate-limited. | Retried with backoff, honoring `Retry-After`. If attempts are exhausted, raises `RateLimitedError` (which carries `retry_after`). |
| **403 Forbidden** | Often a transient block under load on the GraphQL host, not a hard ban. | Retried with backoff. If still failing after `max_attempts`, raises `NetworkError`. |
| **404 Not Found** | The entity does not exist. | Not retried; raises `NotFoundError` immediately. |
| **5xx Server error** | Spotify-side hiccup. | Retried with backoff, then `NetworkError`. |

A persistent 429 is the clearest signal to slow down: lower `RateLimit.per_second`
and/or route through proxies. See [Error handling](error-handling.md) for catch
patterns.

## Per-host rate limits

`host_rate_limits` overrides the global rate for specific hosts. This is useful
behind a shared IP where you want to throttle Spotify's GraphQL host
(`api-partner.spotify.com`) harder than image/preview CDNs. The host constant is
exported as `PARTNER_API_HOST`:

```python
from spotify_scraper import SpotifyClient, RateLimit
from spotify_scraper.http.ratelimit import PARTNER_API_HOST

client = SpotifyClient(
    rate_limit=RateLimit(per_second=3.0, burst=6),       # global default
    host_rate_limits={
        PARTNER_API_HOST: RateLimit(per_second=1.0, burst=2),  # gentler for GraphQL
    },
)
```

A host present in `host_rate_limits` always wins over the global `rate_limit`.

!!! note "The GraphQL host is not throttled by default"
    Measured behavior is that `api-partner.spotify.com` tolerates many rapid
    anonymous requests, so the library does not throttle it specially out of the
    box — transient 403s are retried instead. Add an override here only if you
    observe blocks on a shared IP.

## Proxies

Route all traffic through an HTTP/HTTPS proxy with `proxy=`:

```python
client = SpotifyClient(proxy="http://user:pass@proxy.example:8080")
```

For large jobs, the most effective anti-ban measure is spreading requests across
several proxies — create one client per proxy and distribute work between them:

```python
proxies = ["http://p1.example:8080", "http://p2.example:8080"]
clients = [SpotifyClient(proxy=p) for p in proxies]
# round-robin your requests across `clients`, then close each one
```

## User-agent rotation

By default the transport picks a realistic browser User-Agent from a built-in
pool, so requests blend in. To pin a fixed one (e.g. to match a proxy profile),
pass `user_agent=`:

```python
client = SpotifyClient(
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
)
```

To vary it across requests, create multiple clients with different `user_agent`
values and rotate between them, much like proxies.

## Timeouts

`timeout` sets the per-request timeout in seconds (default `10.0`):

```python
client = SpotifyClient(timeout=20.0)
```

## Polite-scraping etiquette

- **Keep the defaults unless you have a reason not to.** They are tuned to be
  safe.
- **Cache results.** Re-fetching the same entity repeatedly is the fastest way
  to draw attention; persist `to_dict()` output.
- **Back off on 429.** If you see `RateLimitedError`, reduce `per_second` rather
  than hammering with more retries.
- **Bound concurrency.** With the async client, cap in-flight tasks (a semaphore)
  for very large jobs — see the [Async guide](async.md).
- **Respect the terms.** Only scrape public data, for personal/research use, and
  read the [Legal & ToS](../legal.md) page.

## When HTTP is blocked entirely

If Spotify serves a challenge page to plain HTTP clients from your network, swap
in the Playwright transport, which shares a real browser's fingerprint. See
[Browser fallback](browser-fallback.md).
