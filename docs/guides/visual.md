# Cover colors & Canvas

Two building blocks for visually rich Spotify pages: the dominant **colors** of a
cover image, and a track's **Canvas** — the short looping video Spotify shows on
the now-playing screen.

## Cover colors

`get_colors()` extracts a cover image's theming palette and returns a typed
[`Colors`](../reference/models.md#colors). It is **anonymous** (the same tier-1
bearer token as the entity getters — no cookie).

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    colors = client.get_colors(track)        # pass any entity with images
    print(colors.raw, colors.dark, colors.light)   # "#RRGGBB" each
```

`source` is flexible — pass any fetched entity that has `images` (a `Track`,
`Album`, `Artist`, `Playlist`, `Show`, or `Episode`; the first image is used), a
Spotify image URL, a `spotify:image:<id>` uri, or a bare image id:

```python
client.get_colors("https://i.scdn.co/image/ab67616d0000b273...")
client.get_colors("spotify:image:ab67616d0000b273...")
```

| Field | Type | Meaning |
|---|---|---|
| `raw` | `str` | The dominant color as extracted (`#RRGGBB`) |
| `dark` | `str` | A contrast-adjusted variant for dark backgrounds |
| `light` | `str` | A contrast-adjusted variant for light backgrounds |
| `is_fallback` | `bool` | `True` when Spotify returned its default instead of a real extraction |

Use these to theme a card, a gradient, or a player UI to match the artwork.

## Canvas

`get_canvas()` returns a track's [`Canvas`](../reference/models.md#canvas) — a
short, silent, **non-DRM** looping MP4 hosted on `canvaz.scdn.co` that you can
embed directly in a `<video>` tag — or `None` when the track has no Canvas (most
tracks don't, so `None` is a normal result).

Canvas is **cookie-authenticated**, exactly like lyrics: build the client with an
`sp_dc` cookie (see [authenticated sessions](authentication.md)).

```python
with SpotifyClient(cookies="<sp_dc>") as client:
    canvas = client.get_canvas("spotify:track:4LfCY65LvojKjWEnU7fNN4")
    if canvas is not None:
        print(canvas.url)          # https://canvaz.scdn.co/.../<id>.cnvs.mp4
        print(canvas.canvas_type)  # e.g. "VIDEO_LOOPING_RANDOM"
```

Download the MP4 with `download_canvas()`:

```python
path = client.download_canvas("spotify:track:4LfCY65LvojKjWEnU7fNN4", "out/")
# -> out/<canvas-id>.mp4   (or pass a fetched Canvas instead of a track)
```

| Field | Type | Meaning |
|---|---|---|
| `id` | `str` | The canvas id (tail of `uri`) |
| `uri` | `str` | `spotify:canvas:<id>` |
| `url` | `str` | Direct, non-DRM MP4 URL |
| `canvas_type` | `str \| None` | Loop style (`VIDEO_LOOPING`, `VIDEO_LOOPING_RANDOM`, …) |
| `file_id` | `str \| None` | Spotify's internal file id |

!!! tip "Building a page?"
    See the [Build a visual, voice-driven Spotify page](visual-voice-page.md)
    tutorial, which chains colors + Canvas + the [MCP server](mcp.md) into a
    front-end.

## Async

Both mirror on the async client:

```python
from spotify_scraper import AsyncSpotifyClient

async with AsyncSpotifyClient(cookies="<sp_dc>") as client:
    colors = await client.get_colors("spotify:image:ab67616d0000b273...")
    canvas = await client.get_canvas("4LfCY65LvojKjWEnU7fNN4")
```
