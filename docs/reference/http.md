# HTTP & config

These objects tune the client's outbound HTTP behaviour. Pass `RateLimit` and
`RetryPolicy` to either client's constructor; both are frozen dataclasses with
safe defaults. The [Anti-ban guide](../guides/anti-ban.md) explains when to
adjust them.

## RateLimit

::: spotify_scraper.http.RateLimit

## RetryPolicy

::: spotify_scraper.http.RetryPolicy

## Per-host throttling

A client accepts `host_rate_limits`, a mapping of host name to `RateLimit`, to
override the global rate for specific hosts. The pathfinder GraphQL host is
exposed as a constant for exactly this purpose:

```python
from spotify_scraper import RateLimit, SpotifyClient
from spotify_scraper.http.ratelimit import PARTNER_API_HOST

client = SpotifyClient(
    host_rate_limits={PARTNER_API_HOST: RateLimit(per_second=1.0, burst=2)},
)
```

::: spotify_scraper.http.ratelimit.PARTNER_API_HOST

::: spotify_scraper.http.ratelimit.resolve_rate_limit
