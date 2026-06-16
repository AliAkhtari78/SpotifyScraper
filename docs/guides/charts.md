# Charts

Spotify's "Top 50", "Today's Top Hits", and friends are ordinary editorial
playlists, so SpotifyScraper ships a small **registry** of verified chart
playlists and fetches them with the regular playlist ladder — no new endpoint,
fully **anonymous**.

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    for chart in client.list_charts():
        print(chart.key, "—", chart.name)     # e.g. top-50-global — Top 50 - Global

    playlist = client.get_chart("todays-top-hits", max_tracks=20)
    for entry in playlist.tracks:
        print(entry.track.name)
```

## What you get

- `list_charts()` returns a tuple of
  [`ChartDef`](#chartdef) (`key`, `name`, `playlist_id`).
- `get_chart(key, max_tracks=100)` resolves the key to its backing playlist id
  and delegates to [`get_playlist()`](entities.md) — so you get a full
  [`Playlist`](../reference/models.md#playlist). An unknown key raises `URLError`.

Built-in keys include `top-50-global`, `top-50-usa`, `top-songs-global`, and
`todays-top-hits` (each verified live). Spotify rotates editorial inventory; a
chart that has gone away surfaces as `NotFoundError`, not a crash.

## ChartDef

```python
@dataclass(frozen=True, slots=True)
class ChartDef:
    key: str          # stable, lowercase, hyphenated
    name: str         # human-friendly name
    playlist_id: str  # the backing editorial playlist
```

## Async

```python
from spotify_scraper import AsyncSpotifyClient

async with AsyncSpotifyClient() as client:
    playlist = await client.get_chart("top-50-global", max_tracks=10)
```
