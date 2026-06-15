# SpotifyScraper

[![Live demo](https://img.shields.io/badge/Live_demo-try_it_now-1DB954?logo=spotify&logoColor=white)](https://aliakhtari.com/spotify/)
[![PyPI version](https://img.shields.io/pypi/v/spotifyscraper.svg)](https://pypi.org/project/spotifyscraper/)
[![Python versions](https://img.shields.io/pypi/pyversions/spotifyscraper.svg)](https://pypi.org/project/spotifyscraper/)
[![CI](https://github.com/AliAkhtari78/SpotifyScraper/actions/workflows/ci.yml/badge.svg)](https://github.com/AliAkhtari78/SpotifyScraper/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/spotifyscraper/badge/?version=latest)](https://spotifyscraper.readthedocs.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/LICENSE)

**Extract public Spotify data — tracks, albums, artists, playlists, and podcasts — without the official API or any credentials.**

> 🎧 **[Try it live in your browser →](https://aliakhtari.com/spotify/)** — paste any Spotify link and watch SpotifyScraper pull typed data, cover art, and a preview, with the exact Python that does it. ([How it was built](https://aliakhtari.com/work/spotify-scraper/).)

SpotifyScraper bootstraps an anonymous token from Spotify's own public embed
pages and reads the same JSON endpoints the web player uses, returning typed,
immutable models. v3 is a ground-up rewrite focused on reliability and a clean,
modern API.

> **Upgrading from v2?** See the [migration guide](https://spotifyscraper.readthedocs.io/en/latest/migration/). The previous line lives on the [`v2.x` branch](https://github.com/AliAkhtari78/SpotifyScraper/tree/v2.x).

## Install

```bash
pip install spotifyscraper                 # core (only depends on httpx)
pip install "spotifyscraper[media]"        # + cover/preview embedding (mutagen)
pip install "spotifyscraper[browser]"      # + Playwright browser fallback
pip install "spotifyscraper[cli]"          # + the spotifyscraper command-line tool
pip install "spotifyscraper[all]"          # everything
```

Python 3.10+.

## Quickstart

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC")
    print(track.name, "—", track.artists[0].name)
    print(track.duration_ms, "ms |", track.preview_url)

    print(track.to_dict())          # JSON-safe dict, if you prefer dicts
```

Every entity has its own method — `get_track`, `get_album`, `get_artist`,
`get_playlist`, `get_episode`, `get_show` — each accepting a URL, URI, or bare
ID.

### Async

```python
import asyncio
from spotify_scraper import AsyncSpotifyClient

async def main():
    async with AsyncSpotifyClient() as client:
        track, album = await asyncio.gather(
            client.get_track("4uLU6hMCjMI75M1A2tKUQC"),
            client.get_album("4aawyAB9vmqN3uQ7FjRGTy"),
        )
        print(track.name, "|", album.name)

asyncio.run(main())
```

### Download a cover and preview

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    client.download_cover(track, dest="covers/")
    client.download_preview(track, dest="previews/", embed_cover=True)  # needs [media]
```

## Features

- **All core entities + podcasts** — tracks, albums, artists, playlists, shows, episodes.
- **Lyrics & podcast transcripts** — cookie-authenticated, time-synced, one token for both.
- **Sync & async** clients sharing one sans-io core.
- **Typed, frozen models** with JSON-safe `to_dict()` / `from_dict()`.
- **Two-tier resilience** — Spotify's GraphQL API with automatic fallback to the embed page.
- **One core dependency** (`httpx`); media and browser support are optional extras.
- **Anti-ban built in** — per-host rate limiting, retries with backoff, UA rotation, proxies.
- **Browser fallback** via Playwright when you need a real browser.

## Command line

With the `cli` extra installed, a `spotifyscraper` command is available:

```bash
spotifyscraper track 4uLU6hMCjMI75M1A2tKUQC          # entity metadata as JSON
spotifyscraper playlist <id> --max-tracks 50 --pretty
spotifyscraper download preview <id> -o ./previews --embed-cover
```

Every command emits JSON, so it composes with tools like `jq`. See the
[CLI guide](https://spotifyscraper.readthedocs.io/en/latest/guides/cli/).

## Lyrics & transcripts

Lyrics and podcast transcripts need a Spotify account cookie (`sp_dc`); the
library handles the token handshake for you, and one cookie powers both:

```python
from spotify_scraper import SpotifyClient

with SpotifyClient(cookies="cookies.txt") as client:   # or cookies={"sp_dc": "..."}
    lyrics = client.get_lyrics("4uLU6hMCjMI75M1A2tKUQC")
    for line in lyrics.lines:
        print(line.start_ms, line.text)

    transcript = client.get_transcript("512ojhOuo1ktJprKbVcKyQ")   # a podcast episode
    for line in transcript.lines:
        print(line.start_ms, line.text)
```

Your cookie is sent only to Spotify and never logged. An episode with no
transcript raises `NotFoundError`. See the
[lyrics & cookies guide](https://spotifyscraper.readthedocs.io/en/latest/guides/lyrics-and-cookies/).

## Roadmap

**Shipped**

| Version | Scope |
|---------|-------|
| **3.0** | The library: all entities, pagination, media downloads, browser fallback, docs |
| **3.1** | Command-line interface |
| **3.2** | Cookie-authenticated lyrics |
| **3.3** | Cookie-authenticated podcast transcripts (`get_transcript`) |

**Planned** — tracked in [milestones](https://github.com/AliAkhtari78/SpotifyScraper/milestones); 👍 or weigh in on the issues to help prioritize:

| Version | Scope |
|---------|-------|
| **3.3** | First-class [auth & session persistence](https://github.com/AliAkhtari78/SpotifyScraper/issues/128) (browser-assisted login, no stored passwords) |
| **3.4** | [Search](https://github.com/AliAkhtari78/SpotifyScraper/issues/129) across every entity type · [market / region](https://github.com/AliAkhtari78/SpotifyScraper/issues/130) support |
| **3.5** | Optional [response cache](https://github.com/AliAkhtari78/SpotifyScraper/issues/131) · [batch helpers](https://github.com/AliAkhtari78/SpotifyScraper/issues/132) with managed concurrency |

Planned scope is subject to change.

## Documentation

Full docs, guides, and the API reference: **<https://spotifyscraper.readthedocs.io>**

## Legal

SpotifyScraper is an unofficial, independent project, not affiliated with
Spotify. It reads publicly available data and the ~30-second previews Spotify
publishes; it does not download full tracks or circumvent DRM. Use it for
educational and personal purposes, and in line with Spotify's Terms of Service.
See the [legal notice](https://spotifyscraper.readthedocs.io/en/latest/legal/).

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/CONTRIBUTING.md). The project
is developed spec-first with [OpenSpec](https://github.com/Fission-AI/OpenSpec);
specs live in [`openspec/`](https://github.com/AliAkhtari78/SpotifyScraper/tree/master/openspec).

## License

[MIT](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/LICENSE) © Ali Akhtari
