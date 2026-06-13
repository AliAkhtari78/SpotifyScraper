# Error handling

Every error SpotifyScraper raises derives from a single base class,
`SpotifyScraperError`, so you can catch all library failures with one `except`
clause — or catch specific subclasses for fine-grained handling. The library
**never** returns error strings or error dicts; failures are always exceptions.

## The exception tree

```text
SpotifyScraperError                 # base — catch this to catch everything
├── URLError                        # invalid Spotify URL, URI, or ID input
├── NetworkError                    # transport failure talking to Spotify
│   └── RateLimitedError            # HTTP 429 (carries retry_after)
├── TokenError                      # anonymous token bootstrap/refresh failed
├── AuthenticationError             # missing/expired credentials for an auth feature
├── NotFoundError                   # entity does not exist or is unavailable
├── ParsingError                    # Spotify payload had an unexpected shape
└── MediaError                      # media download or tagging failed
```

All of these import directly from the top-level package:

```python
from spotify_scraper import (
    SpotifyScraperError,
    URLError,
    NetworkError,
    RateLimitedError,
    TokenError,
    AuthenticationError,
    NotFoundError,
    ParsingError,
    MediaError,
)
```

## What each error means

| Exception | Raised when | Typical fix |
|---|---|---|
| `URLError` | The input is not a recognizable Spotify URL/URI/ID, or a bare ID was passed without a type. | Check the value you passed to `get_*`. |
| `NetworkError` | A connection failed, or retries were exhausted on a 403/5xx. Carries `request_url`. | Retry later; check connectivity/proxy. |
| `RateLimitedError` | A 429 could not be recovered within the retry budget. Subclass of `NetworkError`; carries `retry_after`. | Slow down — lower `RateLimit.per_second`. |
| `NotFoundError` | Spotify returned 404 — the entity does not exist or is unavailable. | Verify the ID. |
| `ParsingError` | Spotify's payload had an unexpected shape (their API changed). | Update the library; check for a release. |
| `TokenError` | The anonymous token could not be bootstrapped or refreshed. | Usually transient; retry. May indicate a needed update. |
| `AuthenticationError` | A feature requiring user credentials lacked valid ones. | Provide valid credentials (relevant to features coming in v3.1). |
| `MediaError` | A download failed: no preview/image exists, or `embed_cover` was requested without `mutagen`. | Check `preview_url`/`images`; install `[media]`. |

## Catch everything

The simplest pattern — treat any library failure uniformly:

```python
from spotify_scraper import SpotifyClient, SpotifyScraperError

with SpotifyClient() as client:
    try:
        track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    except SpotifyScraperError as exc:
        print("SpotifyScraper failed:", exc)
    else:
        print(track.name)
```

## Catch specific failures

Order `except` clauses from most specific to least, since `RateLimitedError` is a
subclass of `NetworkError`:

```python
from spotify_scraper import (
    SpotifyClient,
    NotFoundError,
    RateLimitedError,
    NetworkError,
    ParsingError,
)

with SpotifyClient() as client:
    try:
        track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    except NotFoundError:
        print("No such track.")
    except RateLimitedError as exc:
        print("Rate limited; retry after", exc.retry_after, "seconds")
    except NetworkError as exc:
        print("Network problem with", exc.request_url, ":", exc)
    except ParsingError:
        print("Spotify changed its payload — update SpotifyScraper.")
    else:
        print(track.name)
```

### Using the extra attributes

`NetworkError` (and its `RateLimitedError` subclass) carry `request_url`;
`RateLimitedError` additionally carries `retry_after`:

```python
import time
from spotify_scraper import SpotifyClient, RateLimitedError

with SpotifyClient() as client:
    try:
        track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    except RateLimitedError as exc:
        wait = exc.retry_after or 5.0
        print(f"Backing off {wait}s (was hitting {exc.request_url})")
        time.sleep(wait)
```

## Handling media errors

`download_preview` and `download_cover` raise `MediaError` when there is nothing
to download, or when tagging is requested without the extra:

```python
from spotify_scraper import SpotifyClient, MediaError

with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    try:
        client.download_preview(track, "downloads", embed_cover=True)
    except MediaError as exc:
        # No preview clip, or mutagen ([media] extra) is not installed.
        print("Could not download preview:", exc)
```

## Embed-tier degradation is *not* an error

SpotifyScraper uses a two-tier extraction ladder (see [Entities](entities.md)).
When the rich **tier-1** GraphQL payload changes shape, the library raises an
internal `ParsingError` for *that* request, **catches it**, and **falls back** to
the entity's embed page rather than surfacing the error to you. You still get a
valid model — just with the tier-1-only fields left as `None` (or empty tuples).

What this means for your code:

- A successful `get_*` call may return a model with some fields unset. Always
  guard tier-1 fields (`if track.play_count is not None:`).
- The degradation is logged at `WARNING` on the `spotify_scraper` logger, so you
  can observe it without it breaking your flow:

  ```python
  import logging
  logging.basicConfig(level=logging.WARNING)
  # A tier-1 -> embed fallback now logs:
  #   WARNING spotify_scraper: Tier-1 track fetch degraded to embed page: ...
  ```

- A `ParsingError` only propagates to you when **both** tiers fail to produce a
  usable payload — at which point updating the library is the right move, since
  payload changes are fixed upstream.
