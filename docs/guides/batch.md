# Batch helpers

Each entity getter has a **plural** sibling — `get_tracks`, `get_albums`,
`get_artists`, `get_playlists`, `get_episodes`, `get_shows` — that fetches many
inputs in one call and returns one [`BatchItem`](#batchitem) per input, **index-
aligned** with what you passed in.

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    items = client.get_tracks([
        "4uLU6hMCjMI75M1A2tKUQC",
        "spotify:track:0VjIjW4GlUZAMYd2vXMi3b",
        "this-is-not-valid",
    ])

for item in items:
    if item.ok:
        print(item.result.name)
    else:
        print("failed:", item.value, "->", item.error)
```

## Partial failure never aborts the batch

A single dead or malformed input does **not** raise or stop the others — its
outcome is captured on that one `BatchItem` instead. Exactly one of `result` /
`error` is populated, and the input `value` is echoed back so you can correlate
outcomes even after deduplication or reordering:

- `item.ok` — `True` when the fetch succeeded;
- `item.result` — the typed model on success, else `None`;
- `item.error` — the captured `SpotifyScraperError` on failure, else `None`;
- `item.unwrap()` — returns the model, or re-raises the captured error.

```python
ok = [i.result for i in items if i.ok]
failed = {i.value: i.error for i in items if not i.ok}
```

## Async + managed concurrency

The async client runs batch fetches **concurrently**, bounded by the client's
`max_concurrency` (default `5`) so it never floods Spotify; the per-host rate
limiter still governs request pacing on top of that.

```python
from spotify_scraper import AsyncSpotifyClient

async with AsyncSpotifyClient(max_concurrency=8) as client:
    items = await client.get_tracks([id1, id2, id3, ...])
```

The sync helpers fetch sequentially. Both return the same `BatchItem` shape.

## `BatchItem`

::: spotify_scraper.batch.BatchItem
