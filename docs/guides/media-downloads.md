# Media downloads

SpotifyScraper can download two kinds of media from public pages: **cover art**
(for any entity that carries images) and **preview clips** (the short MP3 Spotify
exposes for many tracks and episodes). Both methods reuse the client's
configured transport — same rate limiting, retries, and proxy.

!!! info "What you can and cannot download"
    These are the same public assets a browser loads: cover images and ~30-second
    preview clips. SpotifyScraper does **not** download full tracks or DRM-protected
    audio, and cannot. Review the [Legal & ToS](../legal.md) page before saving
    anything.

## Download cover art

`download_cover` works with any fetched model that has a `name` and `images` —
tracks, albums, artists, playlists, episodes, and shows. It returns the `Path` it
wrote.

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    album = client.get_album("6N9PS4QXF1D0OWPk0Sxtb4")
    path = client.download_cover(album, "downloads")
    print("Saved", path)
```

Signature:

```python
client.download_cover(
    entity,
    dest=".",            # directory; created if missing
    *,
    size="largest",      # "largest" or "smallest"
    filename=None,       # explicit name; else "<sanitized name>.<ext>"
)
```

### Choosing a size

`size` selects between the available images by pixel area:

```python
client.download_cover(album, "downloads", size="largest")    # default
client.download_cover(album, "downloads", size="smallest")   # thumbnail
```

### Track covers fall back to the album

A `Track` often has empty `images`. When you download a track's cover, the
library automatically falls back to the track's **album** images, so this just
works:

```python
with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    client.download_cover(track, "downloads")
```

If an entity has no images anywhere, `download_cover` raises `MediaError`.

## Download preview clips

`download_preview` fetches the preview MP3 for a **track or episode** and returns
the written `Path`.

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    path = client.download_preview(track, "downloads")
    print("Saved", path)
```

Signature:

```python
client.download_preview(
    entity,              # a Track or Episode
    dest=".",            # directory; created if missing
    *,
    filename=None,       # explicit name; else "<sanitized name>.mp3"
    embed_cover=False,   # embed cover art + tags (needs the [media] extra)
)
```

!!! warning "Not every item has a preview"
    Spotify does not expose a preview clip for every track or episode. When
    `preview_url` is missing, `download_preview` raises `MediaError`. Guard it:

    ```python
    from spotify_scraper import MediaError

    try:
        client.download_preview(track, "downloads")
    except MediaError as exc:
        print("No preview:", exc)
    ```

## Embedding cover art and tags

Pass `embed_cover=True` to write the cover art and basic ID3 tags (title, and
artist or show name) into the MP3. This uses [`mutagen`](https://mutagen.readthedocs.io/),
which ships in the **`media`** extra:

```bash
pip install "spotifyscraper[media]"
```

```python
with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    client.download_preview(track, "downloads", embed_cover=True)
```

If you request `embed_cover=True` without `mutagen` installed, you get a
`MediaError` telling you to install the extra. Tag mapping:

| ID3 frame | Value |
|---|---|
| `TIT2` (title) | The entity's `name`. |
| `TPE1` (artist) | The track's first artist, or the episode's show name. |
| `APIC` (cover) | The largest available cover image (JPEG). |

## File naming and sanitization

When you do not pass `filename`, the output name is derived from the entity's
`name`:

- Covers: `<sanitized name>.<ext>`, where the extension comes from the response
  content type (`jpg`, `png`, `webp`, `gif`; defaults to `jpg`).
- Previews: `<sanitized name>.mp3`.

Sanitization normalizes Unicode (NFC), replaces control characters and the path
separators ``\x00-\x1f < > : " / \ | ? *`` with spaces, collapses runs of
whitespace, trims leading/trailing dots and spaces, and caps the stem at 150
characters. An empty result becomes `untitled`. For example, a track named
`AC/DC: Back? *Live*` is written as `AC DC Back Live.mp3`.

Provide `filename` to bypass sanitization and control the name (and extension)
yourself:

```python
client.download_cover(album, "downloads", filename="cover.jpg")
client.download_preview(track, "downloads", filename="clip.mp3")
```

The `dest` directory is created automatically if it does not exist.

## Async downloads

The [async client](async.md) has the same two methods — just `await` them:

```python
import asyncio
from spotify_scraper import AsyncSpotifyClient

async def main() -> None:
    async with AsyncSpotifyClient() as client:
        track = await client.get_track("4uLU6hMCjMI75M1A2tKUQC")
        await client.download_cover(track, "downloads")
        await client.download_preview(track, "downloads", embed_cover=True)

asyncio.run(main())
```
