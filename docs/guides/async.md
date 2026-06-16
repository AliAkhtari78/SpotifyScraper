# Async

`AsyncSpotifyClient` is a one-to-one mirror of `SpotifyClient` over an async
transport. Every fetch and download method has the same name and signature —
you just `await` it and manage the client with `async with`.

## The async client

```python
import asyncio
from spotify_scraper import AsyncSpotifyClient

async def main() -> None:
    async with AsyncSpotifyClient() as client:
        track = await client.get_track("4uLU6hMCjMI75M1A2tKUQC")
        print(track.name)

asyncio.run(main())
```

The same methods are available as on the sync client:

```python
await client.get_track(value)
await client.get_album(value)
await client.get_artist(value)
await client.get_playlist(value, max_tracks=100)
await client.get_episode(value)
await client.get_show(value, max_episodes=50)
await client.download_cover(entity, dest, size="largest", filename=None)
await client.download_preview(entity, dest, filename=None, embed_cover=False)
```

## Closing the client

`async with` closes the client for you. To manage it manually, await `aclose`:

```python
client = AsyncSpotifyClient()
try:
    track = await client.get_track("4uLU6hMCjMI75M1A2tKUQC")
finally:
    await client.aclose()
```

Using the client after it is closed raises `SpotifyScraperError`.

## Fetch many entities concurrently

The reason to go async is concurrency. `asyncio.gather` runs many fetches at
once over a single client and connection pool:

```python
import asyncio
from spotify_scraper import AsyncSpotifyClient

TRACK_IDS = [
    "4uLU6hMCjMI75M1A2tKUQC",
    "7ouMYWpwJ422jRcDASZB7P",
    "0VjIjW4GlUZAMYd2vXMi3b",
]

async def main() -> None:
    async with AsyncSpotifyClient() as client:
        tracks = await asyncio.gather(
            *(client.get_track(track_id) for track_id in TRACK_IDS)
        )
        for track in tracks:
            print(track.name, "—", track.artists[0].name)

asyncio.run(main())
```

You can mix entity types in one batch:

```python
async with AsyncSpotifyClient() as client:
    track, album, artist = await asyncio.gather(
        client.get_track("4uLU6hMCjMI75M1A2tKUQC"),
        client.get_album("6N9PS4QXF1D0OWPk0Sxtb4"),
        client.get_artist("0gxyHStUsqpMadRV0Di1Qt"),
    )
```

## Handle partial failures

By default `asyncio.gather` cancels the whole batch on the first exception. Pass
`return_exceptions=True` to collect successes and failures side by side:

```python
import asyncio
from spotify_scraper import AsyncSpotifyClient, NotFoundError

async def main() -> None:
    ids = ["4uLU6hMCjMI75M1A2tKUQC", "0000000000000000000000"]
    async with AsyncSpotifyClient() as client:
        results = await asyncio.gather(
            *(client.get_track(i) for i in ids),
            return_exceptions=True,
        )
    for entity_id, result in zip(ids, results):
        if isinstance(result, NotFoundError):
            print(entity_id, "-> not found")
        elif isinstance(result, Exception):
            print(entity_id, "-> error:", result)
        else:
            print(entity_id, "->", result.name)

asyncio.run(main())
```

See [Error handling](error-handling.md) for the full exception tree.

!!! warning "Rate limiting still applies"
    Concurrency does **not** bypass the throttle. The same token-bucket rate
    limiter that protects the sync client governs every async request, *per
    host*, across the whole event loop. Firing 500 `gather` tasks does not send
    500 simultaneous requests — they drain at the configured rate. This is what
    keeps you from getting blocked; see [Anti-ban & resilience](anti-ban.md) to
    tune `RateLimit`, `RetryPolicy`, and proxies. The async client accepts every
    one of those knobs:

    ```python
    from spotify_scraper import AsyncSpotifyClient, RateLimit, RetryPolicy

    client = AsyncSpotifyClient(
        rate_limit=RateLimit(per_second=2.0, burst=5),
        retry=RetryPolicy(max_attempts=4),
        proxy="http://user:pass@proxy.example:8080",
    )
    ```

## Bounding concurrency yourself

For very large batches, cap in-flight work with a semaphore so you do not build
an enormous task list at once:

```python
import asyncio
from spotify_scraper import AsyncSpotifyClient

async def fetch_all(ids: list[str]) -> list:
    semaphore = asyncio.Semaphore(10)
    async with AsyncSpotifyClient() as client:
        async def one(track_id: str):
            async with semaphore:
                return await client.get_track(track_id)
        return await asyncio.gather(*(one(i) for i in ids))
```
