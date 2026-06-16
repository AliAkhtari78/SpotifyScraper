# Quickstart

This page walks through fetching every entity type, turning a model into JSON,
downloading media, and a short async teaser. Every snippet is runnable as
written against real public Spotify entities.

## The client

`SpotifyClient` owns an HTTP transport and should be closed when you are done.
Use it as a context manager so it cleans up for you:

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    print(track.name)
```

You can also manage the lifecycle yourself:

```python
client = SpotifyClient()
try:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
finally:
    client.close()
```

Every `get_*` method accepts a **URL**, a **URI**, or a bare **22-character ID**.

## Fetch each entity type

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    # Track
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    print(track.name, "—", track.artists[0].name)

    # Album (its tracks are paginated in for you)
    album = client.get_album("6N9PS4QXF1D0OWPk0Sxtb4")
    print(album.name, f"({album.total_tracks} tracks)")

    # Artist
    artist = client.get_artist("0gxyHStUsqpMadRV0Di1Qt")
    print(artist.name, "— monthly listeners:", artist.monthly_listeners)

    # Playlist — cap how many tracks you collect (default 100)
    playlist = client.get_playlist(
        "37i9dQZF1DXcBWIGoYBM5M", max_tracks=50
    )
    print(playlist.name, f"({len(playlist.tracks)} tracks loaded)")

    # Podcast episode
    episode = client.get_episode("07gKzPFkbvGF0cHoeG7ARS")
    print(episode.name)

    # Podcast show — cap how many episodes you list (default 50)
    show = client.get_show("4rOoJ6Egrf8K2IrywzwOMk", max_episodes=10)
    print(show.name, f"({len(show.episodes)} episodes loaded)")
```

See the [Entities guide](../guides/entities.md) for the full field reference of
each model.

## Convert to a JSON-safe dict

Every model is a frozen dataclass with `to_dict()`. Nested models become dicts,
tuples become lists, and `datetime` values become ISO-8601 strings — so the
result drops straight into `json.dumps`:

```python
import json
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")

data = track.to_dict()
print(json.dumps(data, indent=2)[:200])
```

## Download a cover and a preview

Pass any fetched model to `download_cover`, and a track or episode to
`download_preview`. Both return the `Path` they wrote.

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")

    cover_path = client.download_cover(track, "downloads", size="largest")
    print("Cover saved to", cover_path)

    preview_path = client.download_preview(track, "downloads")
    print("Preview saved to", preview_path)
```

!!! note "Previews are short clips"
    Spotify exposes ~30-second MP3 previews, not full tracks — and not every
    item has one. If no preview exists, `download_preview` raises `MediaError`.
    To embed the cover art into the MP3, pass `embed_cover=True` (needs the
    [`media`](installation.md#extras) extra). See
    [Media downloads](../guides/media-downloads.md).

## Async teaser

The async client mirrors the sync API one-to-one — just `await` each call and
use `async with`:

```python
import asyncio
from spotify_scraper import AsyncSpotifyClient

async def main() -> None:
    async with AsyncSpotifyClient() as client:
        track = await client.get_track("4uLU6hMCjMI75M1A2tKUQC")
        print(track.name)

asyncio.run(main())
```

The real payoff is fetching many entities concurrently with `asyncio.gather` —
see the [Async guide](../guides/async.md).

## Where to next

- [Entities](../guides/entities.md) — every field on every model.
- [Media downloads](../guides/media-downloads.md) — sizing, tagging, file naming.
- [Anti-ban & resilience](../guides/anti-ban.md) — rate limits, retries, proxies.
- [Error handling](../guides/error-handling.md) — the exception tree and catch patterns.
