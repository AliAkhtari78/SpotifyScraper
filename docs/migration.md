# Migration from v2

SpotifyScraper **v3** is a ground-up rewrite. The public surface is smaller,
fully typed, and immutable: every fetch returns a frozen dataclass instead of a
plain `dict`, errors are always exceptions (never error dicts), and there is one
`get_*` method per entity type. This guide maps every v2.1.5 method to its v3
replacement.

!!! info "TL;DR"
    - `client.get_<entity>_info(url)` → `client.get_<entity>(value)` returning a
      typed model.
    - The single argument now accepts a **URL, URI, or bare ID** interchangeably.
    - The CLI is available via the `cli` extra; cookie-authenticated lyrics
      shipped in v3.2 (`get_lyrics`).
    - You read fields off the model (`track.name`) instead of dict keys
      (`info["title"]`).

## The new client

```python
# v2
from spotify_scraper import SpotifyClient

client = SpotifyClient(cookie_file="cookies.txt")
info = client.get_track_info("https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC")
print(info["name"])
client.close()
```

```python
# v3
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    print(track.name)
```

The v3 client is a context manager, returns typed models, and accepts a URL,
URI, or bare 22-character ID for any `get_*` method.

## Method map

Every public method of v2.1.5's `SpotifyClient` and its v3 replacement:

| v2.1.5 method | v3 replacement | Notes |
|---|---|---|
| `get_track_info(url)` | [`get_track(value)`](reference/client.md) → `Track` | Returns a typed [`Track`](reference/models.md) instead of a dict. Read `track.name`, `track.artists`, `track.duration_ms`, etc. |
| `get_track_lyrics(url)` | [`get_lyrics(value)`](reference/client.md) → `Lyrics` | Cookie-authenticated; build the client with `cookies=`. See [Lyrics](#lyrics). |
| `get_track_info_with_lyrics(url)` | `get_track(value)` + `get_lyrics(value)` | Fetch the track and its lyrics in two calls; the lyrics call needs cookies. |
| `get_album_info(url)` | [`get_album(value)`](reference/client.md) → `Album` | Returns an [`Album`](reference/models.md) whose full track list is paginated in for you. |
| `get_artist_info(url)` | [`get_artist(value)`](reference/client.md) → `Artist` | Returns an [`Artist`](reference/models.md) with top tracks, albums, and singles. |
| `get_playlist_info(url)` | [`get_playlist(value, max_tracks=100)`](reference/client.md) → `Playlist` | Returns a [`Playlist`](reference/models.md). Bound the track count with `max_tracks` (`None` = all). |
| `get_episode_info(url)` | [`get_episode(value)`](reference/client.md) → `Episode` | Returns an [`Episode`](reference/models.md). |
| `get_show_info(url)` | [`get_show(value, max_episodes=50)`](reference/client.md) → `Show` | Returns a [`Show`](reference/models.md). Bound the episode count with `max_episodes` (`None` = all). |
| `get_all_info(url)` | Removed | There is no single "fetch everything" call. Detect the entity yourself and call the matching `get_*`, or fetch the entities you actually need. This keeps each request explicit and avoids hidden over-fetching. |
| `download_cover(...)` | [`download_cover(entity, dest=".", *, size="largest", filename=None)`](reference/media.md) | Now takes a **fetched model** (any entity with images), not a URL. Returns the written `Path`. |
| `download_episode_preview(...)` | [`download_preview(entity, dest=".", ...)`](reference/media.md) | Merged into one `download_preview` that accepts a `Track` **or** `Episode`. |
| `download_preview_mp3(...)` | [`download_preview(entity, dest=".", *, filename=None, embed_cover=False)`](reference/media.md) | Same merged method. Pass `embed_cover=True` (needs the `media` extra) to tag the MP3. |
| `close()` | [`close()`](reference/client.md) (or `with`) | Unchanged in spirit; prefer the context manager. The async client uses `aclose()`. |

## Reading data: models, not dicts

v2 returned dicts with string keys; v3 returns frozen, typed dataclasses. The
fields are attributes, and naming is normalized.

```python
# v2
info = client.get_track_info(url)
title = info["title"]
artist = info["artists"][0]["name"]

# v3
track = client.get_track(value)
title = track.name
artist = track.artists[0].name
```

Need a dict back (for JSON, a database, etc.)? Every model has a JSON-safe
`to_dict()`:

```python
data = track.to_dict()          # nested models -> dicts, datetimes -> ISO-8601
```

See the [Entities guide](guides/entities.md) for the full field reference of
each model.

## Exceptions: failures are always raised

v2 sometimes returned an error inside the result (e.g. an `ERROR` key) or raised
inconsistently. v3 **always raises**; nothing is signaled by a return value.
Every exception derives from `SpotifyScraperError`:

```python
from spotify_scraper import SpotifyClient, NotFoundError, SpotifyScraperError

with SpotifyClient() as client:
    try:
        track = client.get_track(value)
    except NotFoundError:
        ...                      # 404 — the entity does not exist
    except SpotifyScraperError as exc:
        ...                      # any other library failure
```

The full tree (`URLError`, `NetworkError` → `RateLimitedError`, `TokenError`,
`AuthenticationError`, `NotFoundError`, `ParsingError`, `MediaError`) and catch
patterns are in the [Error handling guide](guides/error-handling.md).

## Cookies

v3 accepts cookies via the `cookies=` constructor argument (a path, a string, or
a mapping), and stores them for authenticated features:

```python
client = SpotifyClient(cookies="cookies.txt")
```

Public-metadata fetches always work anonymously, with no credentials. Cookies
are load-bearing only for **cookie-authenticated lyrics** (v3.2+).

## Lyrics

As of **v3.2**, `get_lyrics(value)` returns a populated [`Lyrics`](reference/models.md)
model from Spotify's color-lyrics endpoint, using a web-player token derived
from your `sp_dc` cookie:

```python
with SpotifyClient(cookies="cookies.txt") as client:
    lyrics = client.get_lyrics("4uLU6hMCjMI75M1A2tKUQC")
    for line in lyrics.lines:
        print(line.start_ms, line.text)
```

See the [Lyrics & cookies guide](guides/lyrics-and-cookies.md) for how to obtain
an `sp_dc` cookie and the security implications.

## Command-line interface

A `spotifyscraper` command is now available via the `cli` extra:

```bash
pip install "spotifyscraper[cli]"
spotifyscraper track 4uLU6hMCjMI75M1A2tKUQC --pretty
```

It prints any entity as JSON and downloads cover art or previews. See the
[CLI guide](guides/cli.md) for every command and its options.

## Python version floor

v2 supported Python 3.6+. **v3 requires Python 3.10 or newer** (3.10, 3.11,
3.12, 3.13) to use modern typing and immutable dataclasses. If you are on an
older interpreter, upgrade before moving to v3, or stay on v2.x.

## Dependencies

v2 pulled in `requests`, `beautifulsoup4`, `pyyaml`, `eyeD3`, and optionally
Selenium. v3's core depends only on [`httpx`](https://www.python-httpx.org/).
Tagging (`mutagen`) and the browser fallback (`playwright`) are opt-in extras —
see [Installation](getting-started/installation.md).

## Where to next

- [Quickstart](getting-started/quickstart.md) — the v3 API in five minutes.
- [Entities](guides/entities.md) — every field on every model.
- [Error handling](guides/error-handling.md) — the exception tree.
- [Changelog](changelog.md) — the full v3.0 change list.
