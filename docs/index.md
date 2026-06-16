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
| `spotifyscraper[browser]` | Adds a Playwright Chromium transport (and browser-assisted `login()`). |
| `spotifyscraper[cli]` | Adds the `spotifyscraper` command-line tool ([Typer](https://typer.tiangolo.com/)). |
| `spotifyscraper[keyring]` | Stores the captured login cookie in the OS keyring instead of a file. |
| `spotifyscraper[mcp]` | Adds the `spotifyscraper-mcp` [Model Context Protocol](https://modelcontextprotocol.io) server for LLM hosts. |
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

## Cover colors, Canvas & discovery

Beyond the core getters, v3.6 adds visual and discovery surfaces:

```python
colors = client.get_colors(track)                  # artwork palette (anonymous)
related = client.get_related_artists(artist_id)    # "fans also like"
releases = client.get_discography(artist_id)       # every release, paginated
albums = client.get_similar_albums(track_id)       # recommendations
playlist = client.get_chart("top-50-global")       # editorial charts

# Cookie-authenticated:
canvas = client.get_canvas(track_id)               # looping cover video (MP4)
credits = client.get_credits(track_id)             # performers/writers/producers
profile = client.get_user("spotify")               # public user profile
```

See the [Cover colors & Canvas](guides/visual.md), [Discovery](guides/discovery.md),
[Charts](guides/charts.md), and [Credits & concerts](guides/more.md) guides.

## MCP server

Expose the whole library to Claude and other LLM hosts:

```bash
pip install "spotifyscraper[mcp]"
spotifyscraper-mcp        # or: docker run -p 8000:8000 ghcr.io/aliakhtari78/spotifyscraper
```

See the [MCP server guide](guides/mcp.md) and the
[visual, voice-driven page tutorial](guides/visual-voice-page.md).

## Roadmap

SpotifyScraper ships the core library — all six entity types, media downloads,
anti-ban resilience, the browser fallback — plus the command-line interface.

| Version | Adds |
|---|---|
| 3.0.0 | Core library. |
| 3.1.0 | The command-line interface. |
| 3.2.0 | Cookie-authenticated **lyrics** extraction. |
| 3.3 | Cookie-authenticated podcast **transcripts** (`get_transcript`), **browser-assisted login** with a persistent cookie store, and **account-awareness** (`get_account`/`is_premium`). |
| 3.4 | **Search** across every entity type (`search()`) and display-language **localization** (`locale`). |
| 3.5 | Optional persistent **response cache** (`cache=CacheConfig(...)`) and **batch helpers** (`get_*s([...])`) with managed concurrency. |
| 3.6 | **Visual & discovery**: cover **colors**, **Canvas** videos, **charts**, **related artists**, paginated **discography**, **recommendations**, public **profiles**, track **credits**, **concerts** · a best-in-class **MCP server** + container image. |

### What's next

Future ideas are tracked
in the GitHub [milestones](https://github.com/AliAkhtari78/SpotifyScraper/milestones)
and [issues](https://github.com/AliAkhtari78/SpotifyScraper/issues) — 👍 the ones
that matter most to you. Scope is subject to change.

!!! success "Lyrics & transcripts are available"
    Cookie-authenticated **lyrics** and podcast **transcripts** have shipped:
    `client.get_lyrics(track)` / `client.get_transcript(episode)` and the
    `spotifyscraper lyrics` / `spotifyscraper transcript` commands. See the
    [Lyrics & cookies guide](guides/lyrics-and-cookies.md).

!!! success "Browser-assisted login has shipped"
    `client.login()` reuses a valid saved session or opens a real browser to
    capture your `sp_dc` cookie (no password) and persist it;
    `SpotifyClient.from_saved_session()` reconnects headlessly, `get_account()` /
    `is_premium()` report the logged-in account, and `session_info()` checks a
    saved session without exposing the cookie. See the
    [authenticated sessions guide](guides/authentication.md).

!!! success "Search has shipped"
    `client.search(query, types=..., limit=...)` returns a typed
    `SearchResults` across every entity type. See the
    [Search guide](guides/search.md).

!!! success "Localization has shipped"
    Pass `locale` (a BCP-47 **language** tag like `"ja-JP"`) per client or per
    call to localize display-name language. It is not a market/country toggle —
    see the [Localization guide](guides/localization.md).

!!! success "Response caching has shipped"
    Opt in with `SpotifyClient(cache=CacheConfig(store=FileCache()))`. Only
    token-free pathfinder responses are cached (never the token-bearing embed
    pages). See the [caching guide](guides/caching.md).

!!! success "Batch helpers have shipped"
    Plural `client.get_tracks([...])` / `get_albums([...])` / … return one
    partial-failure-safe `BatchItem` per input; the async client bounds
    concurrency with `max_concurrency`. See the [batch guide](guides/batch.md).

!!! success "Visual & discovery have shipped"
    Cover **colors** (`get_colors`), **Canvas** videos (`get_canvas`), **charts**
    (`get_chart`), **related artists**, **discography**, **recommendations**,
    public **profiles** (`get_user`), track **credits**, and **concerts** are all
    available — see the [visual](guides/visual.md), [discovery](guides/discovery.md),
    [charts](guides/charts.md), and [credits & concerts](guides/more.md) guides.

!!! success "MCP server has shipped"
    `spotifyscraper-mcp` (the `mcp` extra) and a `ghcr.io` container expose the
    library to Claude / LLM hosts as tools, resources, and prompts. See the
    [MCP server guide](guides/mcp.md) and the
    [visual, voice-driven page tutorial](guides/visual-voice-page.md).

!!! info "Actively maintained"
    A daily canary runs live tests against Spotify and opens a tracking issue on
    breakage; fixes ship promptly with **[Claude Code](https://claude.com/claude-code)**
    under the maintainer's review. Persisted-query hashes live in one file, so a
    Spotify rotation is a one-line update.

!!! warning "Legal & terms of service"
    SpotifyScraper is intended for **personal, educational, and research use**.
    You are responsible for complying with Spotify's
    [Terms of Service](https://www.spotify.com/legal/end-user-agreement/) and
    applicable copyright law. The preview clips and cover art returned by this
    library are owned by their respective rights holders. **Read the
    [Legal & ToS](legal.md) page before deploying.**
