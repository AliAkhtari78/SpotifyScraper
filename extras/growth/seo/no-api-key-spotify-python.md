---
title: "Get Spotify data in Python without an API key (a spotipy alternative)"
description: "Spotify deprecated audio-features and recommendations in 2024. Here's how to pull public track, album, playlist and lyric data in Python with no API key, no OAuth, and no app registration."
canonical: "https://aliakhtari.com/notes/spotify-python-no-api-key/"
tags: [python, spotify, web-scraping, spotipy, mcp]
---

> Ready-to-publish draft for aliakhtari.com (your ranking domain). Targets the
> queries that already convert for the repo: "spotify scraper python", "spotify
> api without api key", "spotipy alternative", "spotify audio-features 403".
> Keep it honest — the honesty is what converts skeptical devs.

# Get Spotify data in Python without an API key

If you've tried to read Spotify data in Python recently, you've probably hit one
of two walls:

1. **The setup tax.** The official Web API (and `spotipy`, its excellent wrapper)
   makes you register an app, manage a client ID/secret, and run an OAuth flow —
   just to read *public* catalog data.
2. **The deprecations.** In November 2024 Spotify deprecated `audio-features`,
   `audio-analysis`, `recommendations`, `related-artists`, and
   `featured-playlists` for new apps. Eighteen months later there's still no
   official replacement, and thousands of tutorials and notebooks now return
   `403 Forbidden`.

[SpotifyScraper](https://github.com/AliAkhtari78/SpotifyScraper) takes a
different route: it reads the **public** data Spotify's own web player exposes —
no API key, no OAuth, no app registration.

## 30 seconds to data

```bash
pip install spotifyscraper
```

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track = client.get_track("https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC")
    print(track.name, "—", track.artists[0].name)
```

That's it. No credentials. You get typed, immutable models (`track.name`,
`track.duration_ms`, `track.album.images`, the 30-second `preview_url`, …),
sync **and** async clients, and a CLI.

## "Is this a spotipy replacement?"

It depends what you need — and being honest here matters:

| You need… | Use |
|---|---|
| Public metadata, lyrics, podcasts, previews — fast, no key | **SpotifyScraper** |
| Related artists / recommendations after the 2024 deprecation | **SpotifyScraper** (still works, no key) |
| Write to a user's account, playback control, private/library data | **spotipy** (official API) |
| `audio-features` (danceability/energy/tempo) | **neither** — Spotify removed that data entirely |

SpotifyScraper does **not** bring back `audio-features` — no tool can; Spotify
deleted it. But for the still-available data (catalog metadata, related artists,
recommendations) it skips the API entirely.

## Give Claude live Spotify data (MCP)

SpotifyScraper ships an MCP server, so you can wire public Spotify data into
Claude or any LLM agent with no API key:

```bash
pip install "spotifyscraper[mcp]"
spotifyscraper-mcp           # or: docker run -p 8000:8000 ghcr.io/aliakhtari78/spotifyscraper
```

It's in the official MCP registry, so MCP clients and directories can discover it.

## Scope & legality (the honest part)

It reads only **public** data and the ~30-second previews Spotify publishes. It
does **not** download full tracks or touch DRM, and it stays deliberately
metadata-only. Use it for public catalog work, analytics, and tooling, in line
with Spotify's terms.

## Links

- Repo: <https://github.com/AliAkhtari78/SpotifyScraper>
- Live demo (no install): <https://aliakhtari.com/spotify/>
- Docs: <https://spotifyscraper.readthedocs.io>
