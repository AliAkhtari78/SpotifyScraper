# SpotifyScraper

[![Live demo](https://img.shields.io/badge/Live_demo-try_it_now-1DB954?logo=spotify&logoColor=white)](https://aliakhtari.com/spotify/)
[![PyPI version](https://img.shields.io/pypi/v/spotifyscraper.svg)](https://pypi.org/project/spotifyscraper/)
[![Python versions](https://img.shields.io/pypi/pyversions/spotifyscraper.svg)](https://pypi.org/project/spotifyscraper/)
[![CI](https://github.com/AliAkhtari78/SpotifyScraper/actions/workflows/ci.yml/badge.svg)](https://github.com/AliAkhtari78/SpotifyScraper/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/LICENSE)

!!! tip "Try it live"
    Paste any Spotify link into the **[browser demo](https://aliakhtari.com/spotify/)**
    and watch SpotifyScraper return typed data, cover art, and a preview — with
    the exact Python that produced it.

**Extract public Spotify data — tracks, albums, artists, playlists, and podcasts — with one dependency and no API key.**

SpotifyScraper reads the same public pages your browser does and returns clean,
typed Python objects. There is no app to register, no client secret to manage,
and no OAuth dance: just install it and call a method.

<div class="grid cards" markdown>

- :material-package-variant: __One runtime dependency__

    The core depends only on [`httpx`](https://www.python-httpx.org/). Media
    tagging and the browser fallback are opt-in extras.

- :material-key-remove: __No API key, no credentials__

    Public metadata comes from anonymous endpoints. Nothing to register.

- :material-shield-check: __Typed & immutable__

    Every entity is a frozen dataclass with a JSON-safe `to_dict()`.

- :material-sync: __Sync *and* async__

    `SpotifyClient` and `AsyncSpotifyClient` share one core.

</div>

## 30-second example

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    print(f"{track.name} — {track.artists[0].name}")
    print(f"{track.duration_ms / 1000:.0f} seconds")

    # A JSON-safe dict you can serialize anywhere:
    data = track.to_dict()
    print(data["uri"])
```

```text
Never Gonna Give You Up — Rick Astley
213 seconds
spotify:track:4uLU6hMCjMI75M1A2tKUQC
```

You pass a Spotify **URL**, **URI**, or bare **22-character ID** — all three work
interchangeably:

```python
client.get_track("https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC")
client.get_track("spotify:track:4uLU6hMCjMI75M1A2tKUQC")
client.get_track("4uLU6hMCjMI75M1A2tKUQC")
```

## Install

```bash
pip install spotifyscraper
```

| Install target | What you get |
|---|---|
| `spotifyscraper` | Core library: all entities, cover/preview downloads (no tagging). |
| `spotifyscraper[media]` | Adds [`mutagen`](https://mutagen.readthedocs.io/) so previews can embed cover art and ID3 tags. |
| `spotifyscraper[browser]` | Adds a Playwright Chromium transport for sites that challenge plain HTTP clients. |
| `spotifyscraper[all]` | Everything above. |

See [Installation](getting-started/installation.md) for `uv`, extras, and the
Playwright browser download step.

## Supported Python versions

SpotifyScraper supports **Python 3.10, 3.11, 3.12, and 3.13**.

## What you can fetch

| Method | Returns |
|---|---|
| `get_track(value)` | A [`Track`](reference/models.md) |
| `get_album(value)` | An [`Album`](reference/models.md) with its track list |
| `get_artist(value)` | An [`Artist`](reference/models.md) |
| `get_playlist(value, max_tracks=100)` | A [`Playlist`](reference/models.md) |
| `get_episode(value)` | An [`Episode`](reference/models.md) |
| `get_show(value, max_episodes=50)` | A [`Show`](reference/models.md) with its episodes |

Head to the [Quickstart](getting-started/quickstart.md) to see each one, or the
[Entities guide](guides/entities.md) for the full field reference.

## Async in one glance

```python
import asyncio
from spotify_scraper import AsyncSpotifyClient

async def main() -> None:
    async with AsyncSpotifyClient() as client:
        track = await client.get_track("4uLU6hMCjMI75M1A2tKUQC")
        print(track.name)

asyncio.run(main())
```

The async client mirrors the sync one method-for-method. See the
[Async guide](guides/async.md) for `asyncio.gather` bulk patterns.

## Command-line interface

A `spotifyscraper` command is available now — install the `cli` extra and print
any entity as JSON or download cover art and previews:

```bash
pip install "spotifyscraper[cli]"
spotifyscraper track 4uLU6hMCjMI75M1A2tKUQC | jq -r '.name'
```

See the [CLI guide](guides/cli.md) for every command, options, and exit codes.

## Search

`search()` runs one anonymous, aggregate query across every entity type and
returns a typed `SearchResults`:

```python
results = client.search("daft punk", types=("track", "artist"), limit=5)
for track in results.tracks:
    print(track.name)
```

See the [Search guide](guides/search.md) for the result shape and filtering.

## Roadmap

SpotifyScraper ships the core library — all six entity types, media downloads,
anti-ban resilience, the browser fallback — plus the command-line interface.

| Version | Adds |
|---|---|
| 3.0.0 | Core library. |
| 3.1.0 | The command-line interface. |
| 3.2.0 | Cookie-authenticated **lyrics** extraction. |
| 3.4 | **Search** across every entity type (`search()`). |

### Planned

Upcoming work is tracked in the GitHub
[milestones](https://github.com/AliAkhtari78/SpotifyScraper/milestones):

| Version | Adds |
|---|---|
| 3.3 | Podcast [transcripts](https://github.com/AliAkhtari78/SpotifyScraper/issues/127) and first-class [authenticated sessions](https://github.com/AliAkhtari78/SpotifyScraper/issues/128) — browser-assisted login with a persistent cookie store (no stored passwords). |
| 3.4 | [market / region](https://github.com/AliAkhtari78/SpotifyScraper/issues/130) support. |
| 3.5 | Optional [response caching](https://github.com/AliAkhtari78/SpotifyScraper/issues/131) and [batch helpers](https://github.com/AliAkhtari78/SpotifyScraper/issues/132) with managed concurrency. |

Scope is subject to change — 👍 the issues that matter most to you.

!!! success "Lyrics are available"
    Cookie-authenticated **lyrics** extraction has shipped:
    `client.get_lyrics(track)` and the `spotifyscraper lyrics` command. See the
    [Lyrics & cookies guide](guides/lyrics-and-cookies.md).

!!! success "Search has shipped"
    `client.search(query, types=..., limit=...)` returns a typed
    `SearchResults` across every entity type. See the
    [Search guide](guides/search.md).

!!! warning "Legal & terms of service"
    SpotifyScraper is intended for **personal, educational, and research use**.
    You are responsible for complying with Spotify's
    [Terms of Service](https://www.spotify.com/legal/end-user-agreement/) and
    applicable copyright law. The preview clips and cover art returned by this
    library are owned by their respective rights holders. **Read the
    [Legal & ToS](legal.md) page before deploying.**
