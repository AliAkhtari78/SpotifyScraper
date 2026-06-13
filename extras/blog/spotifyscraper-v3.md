---
title: "SpotifyScraper v3: a ground-up rewrite for extracting Spotify data in Python"
date: 2026-06-13
author: Ali Akhtari
tags: [python, spotify, scraping, open-source]
canonical_url: https://spotifyscraper.readthedocs.io
---

# SpotifyScraper v3: a ground-up rewrite

I first published **SpotifyScraper** in 2020 as a small library to pull public
Spotify metadata without the official API. It got popular — and then, like a lot
of scrapers, it slowly rotted as Spotify changed their website. v3 is a complete
clean-room rewrite that fixes the root causes, not just the symptoms.

> **TL;DR** — `pip install spotifyscraper`, then:
>
> ```python
> from spotify_scraper import SpotifyClient
>
> with SpotifyClient() as client:
>     track = client.get_track("https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC")
>     print(track.name, track.artists[0].name, track.preview_url)
> ```

## Why the old versions broke

The original library scraped HTML and parsed embedded blobs out of Spotify's
pages. That works until Spotify ships a redesign — and they ship a lot. Each
redesign quietly broke a parser, and the failures were ugly: errors came back
*inside* the result (an `ERROR` key in a dict) instead of being raised, so code
kept running on half-data.

Modern Spotify is a Next.js app whose embed pages ship a JSON document called
`__NEXT_DATA__`. Buried inside it is something useful: an **anonymous access
token** that the page itself uses. That token is the key.

## The v3 strategy: anonymous token → JSON API

Instead of scraping HTML, v3 does what the web player does:

1. Fetch any public **embed page** (e.g. `open.spotify.com/embed/track/<id>`).
2. Read the anonymous token out of its `__NEXT_DATA__`.
3. Use that token against Spotify's **pathfinder GraphQL API** to get rich,
   structured JSON — play counts, full track lists, discographies, episodes.

If the GraphQL call ever fails (Spotify rotates a query hash, say), v3 **degrades
gracefully** to parsing the embed page's own data — so you still get the core
fields instead of an exception. This two-tier ladder is the reliability story.

## Typed models, not dicts

Every fetch returns a frozen, typed dataclass:

```python
track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
track.name           # "Never Gonna Give You Up"
track.artists[0].name
track.play_count     # int | None
track.to_dict()      # JSON-safe dict, if you want one
```

Failures are always raised, from one exception hierarchy (`SpotifyScraperError`
and friends). No more errors hiding inside your data.

## Everything you'd expect

```python
client.get_album(album_id)
client.get_artist(artist_id)
client.get_playlist(playlist_id, max_tracks=200)   # paginates for you
client.get_show(show_id, max_episodes=100)
client.get_episode(episode_id)
```

### Async for bulk work

```python
import asyncio
from spotify_scraper import AsyncSpotifyClient

async def main():
    async with AsyncSpotifyClient() as client:
        tracks = await asyncio.gather(*(client.get_track(i) for i in ids))

asyncio.run(main())
```

### Downloads

```python
client.download_cover(track, dest="covers/")
client.download_preview(track, dest="previews/", embed_cover=True)
```

(`download_preview` grabs the ~30-second preview Spotify publishes publicly —
not full songs.)

## Built to last this time

The thing that actually killed previous versions was **maintenance rot**. v3
fights it directly:

- **One dependency** (`httpx`) in the core; media and browser support are extras.
- **Per-host rate limiting, retries with backoff, UA rotation, proxies** built in.
- A **Playwright browser fallback** for when plain HTTP isn't enough.
- A **daily CI canary** that runs live tests against real Spotify and opens an
  issue the moment something breaks — so I find out before you do.
- GraphQL query hashes live in *one file*, so a Spotify change is a one-line fix.

## Roadmap

- **v3.1** — a command-line interface: `pip install "spotifyscraper[cli]"`, then
  `spotifyscraper track <id>` emits JSON you can pipe straight into `jq`.
- **Next** — cookie-authenticated lyrics.

## Get it

```bash
pip install spotifyscraper
```

Docs: <https://spotifyscraper.readthedocs.io> · Source:
<https://github.com/AliAkhtari78/SpotifyScraper> · Migrating from v2? There's a
[full migration guide](https://spotifyscraper.readthedocs.io/en/latest/migration/).

*SpotifyScraper is an unofficial, educational project and is not affiliated with
Spotify. Please use it responsibly and within Spotify's Terms of Service.*
