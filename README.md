# SpotifyScraper

[![Live demo](https://img.shields.io/badge/Live_demo-try_it_now-1DB954?logo=spotify&logoColor=white)](https://aliakhtari.com/spotify/)
[![PyPI version](https://img.shields.io/pypi/v/spotifyscraper.svg)](https://pypi.org/project/spotifyscraper/)
[![Python versions](https://img.shields.io/pypi/pyversions/spotifyscraper.svg)](https://pypi.org/project/spotifyscraper/)
[![Downloads](https://static.pepy.tech/badge/spotifyscraper/month)](https://pepy.tech/project/spotifyscraper)
[![CI](https://github.com/AliAkhtari78/SpotifyScraper/actions/workflows/ci.yml/badge.svg)](https://github.com/AliAkhtari78/SpotifyScraper/actions/workflows/ci.yml)
[![Docs](https://readthedocs.org/projects/spotifyscraper/badge/?version=latest)](https://spotifyscraper.readthedocs.io)
[![Container](https://img.shields.io/badge/ghcr.io-container-2496ED?logo=docker&logoColor=white)](https://github.com/AliAkhtari78/SpotifyScraper/pkgs/container/spotifyscraper)
[![Maintained with Claude Code](https://img.shields.io/badge/maintained%20with-Claude%20Code-d97757?logo=anthropic&logoColor=white)](https://github.com/AliAkhtari78/SpotifyScraper#reliability--maintenance)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/AliAkhtari78/SpotifyScraper?style=flat&logo=github&color=1DB954)](https://github.com/AliAkhtari78/SpotifyScraper/stargazers)

**Extract public Spotify data — tracks, albums, artists, playlists, and podcasts — without the official API or an API key.**

> 🎧 **[Try it live in your browser →](https://aliakhtari.com/spotify/)** — paste any Spotify link and watch SpotifyScraper pull typed data, cover art, and a preview, with the exact Python that does it. ([How it was built](https://aliakhtari.com/work/spotify-scraper/).)

SpotifyScraper bootstraps an anonymous token from Spotify's own public embed
pages and reads the same JSON endpoints the web player uses, returning typed,
immutable models. v3 is a ground-up rewrite focused on reliability and a clean,
modern API. Public data needs no login; the opt-in **logged-in** features
(lyrics, podcast transcripts, and account info) add your own Spotify `sp_dc`
cookie — never a password or an API key.

> **Upgrading from v2?** See the [migration guide](https://spotifyscraper.readthedocs.io/en/latest/migration/). The previous line lives on the [`v2.x` branch](https://github.com/AliAkhtari78/SpotifyScraper/tree/v2.x).

## SpotifyScraper vs. the official API ([spotipy](https://github.com/spotipy-dev/spotipy))

`spotipy` wraps Spotify's **official Web API** — the right choice when you need to
write to a user's account or read private/library data. SpotifyScraper reads the
**public** data the web player already exposes, so it skips the setup entirely.

|                                   | **SpotifyScraper** | **spotipy** (official API) |
| --------------------------------- | :----------------: | :------------------------: |
| API key / app registration        |    ❌ not needed    |        ✅ required          |
| OAuth flow                         |    ❌ not needed    |   ✅ required for most data |
| Rate-limit quota / billing         |        none        |       Spotify quota        |
| Sync **and** async                 |         ✅          |         sync only          |
| Fully typed, immutable models      |         ✅          |          partial           |
| Lyrics & podcast transcripts       |    ✅ (cookie)      |            ❌              |
| MCP server for Claude / LLM agents |         ✅          |            ❌              |
| Write / playback / private data    | ❌ (read-only public) |          ✅             |

Use **spotipy** for authenticated writes and private, market-accurate data; use
**SpotifyScraper** for fast, key-free access to public metadata, lyrics, and
previews — plus a drop-in **MCP server** for AI agents.

> **Hit by the official-API deprecations?** Spotify's `audio-features`,
> `recommendations`, and `related-artists` endpoints have returned `403` for new
> apps since Nov 2024. SpotifyScraper still returns **related artists and
> recommendations** with no API key. (It can't bring back `audio-features` —
> Spotify removed that data entirely, from every tool.)

## Install

```bash
pip install spotifyscraper                 # core (only depends on httpx)
pip install "spotifyscraper[media]"        # + cover/preview embedding (mutagen)
pip install "spotifyscraper[browser]"      # + Playwright browser fallback & login
pip install "spotifyscraper[cli]"          # + the spotifyscraper command-line tool
pip install "spotifyscraper[keyring]"      # + store the login cookie in the OS keyring
pip install "spotifyscraper[mcp]"          # + the spotifyscraper-mcp MCP server for LLM hosts
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
            client.get_album("6N9PS4QXF1D0OWPk0Sxtb4"),
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

### Localized display names

Pass `locale` — a BCP-47 **language** tag: a bare language subtag (`"de"`,
`"ja"`) or a language-region tag (`"ja-JP"`) — to localize the *language* of
display names. Set it per client or override it per call:

```python
with SpotifyClient(locale="ja-JP") as client:        # default for every call
    track = client.get_track("4uLU6hMCjMI75M1A2tKUQC")
    other = client.get_track("4uLU6hMCjMI75M1A2tKUQC", locale="de-DE")  # per-call wins
```

It is sent as the `Accept-Language` header and changes only how names are
*spelled*. It is **not** a country/market code — a bare `"US"` is meaningless as
a language and is ignored — and it does **not** filter regional **availability**
or vary **preview URLs**: anonymous Spotify resolves country from the request IP,
and its pathfinder silently ignores a `market` variable. True market/availability
filtering requires the authenticated Web API, which this library does not
implement; for region-specific results, point the client's `proxy` at the target
region. See the
[localization guide](https://spotifyscraper.readthedocs.io/en/latest/guides/localization/).

## Features

- **All core entities + podcasts** — tracks, albums, artists, playlists, shows, episodes.
- **Search** across every entity type, returning one typed `SearchResults`.
- **Charts & discovery** — editorial charts, related artists, full paginated discography, and album recommendations.
- **Cover colors & Canvas** — extract an artwork's theming palette and download a track's looping Canvas video.
- **Credits & concerts** — performers/writers/producers and an artist's upcoming live events.
- **Public user profiles** — `get_user()` (name, follower counts, public playlists).
- **MCP server** — expose everything to Claude/LLMs via `spotifyscraper-mcp` (batch tools + a one-call `get_track_visuals`); also ships as a container on ghcr.io.
- **Localized display names** — pass a BCP-47 language tag (`locale`) to set the language of names.
- **Lyrics & podcast transcripts** — cookie-authenticated, time-synced, one token for both.
- **Browser-assisted login + session persistence** — log in once, then run headless (no stored passwords).
- **Account-aware** — `get_account()` / `is_premium()`, plus cookie-free `session_info()`.
- **Batch helpers** — plural `get_*s([...])` with partial-failure-safe results and managed concurrency.
- **Sync & async** clients sharing one sans-io core.
- **Typed, frozen models** with JSON-safe `to_dict()` / `from_dict()`.
- **Two-tier resilience** — Spotify's GraphQL API with automatic fallback to the embed page.
- **One core dependency** (`httpx`); media and browser support are optional extras.
- **Optional response cache** — opt-in, persistent, token-safe (only token-free pathfinder GETs).
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

## Batch helpers

Each getter has a plural sibling (`get_tracks`, `get_albums`, …) that fetches
many inputs and returns one `BatchItem` per input — index-aligned, and a dead
input never aborts the rest:

```python
items = client.get_tracks(["4uLU6hMCjMI75M1A2tKUQC", "bad-id"])
ok = [i.result for i in items if i.ok]
failed = {i.value: i.error for i in items if not i.ok}
```

The async client runs them concurrently, bounded by `max_concurrency` (default
5). See the [batch guide](https://spotifyscraper.readthedocs.io/en/latest/guides/batch/).

## Response caching

For repeated lookups, enable an opt-in persistent cache. It only stores
**token-free** pathfinder responses — never the embed pages that carry the
anonymous token — so no credential is ever written to disk:

```python
from spotify_scraper import SpotifyClient, CacheConfig, FileCache

with SpotifyClient(cache=CacheConfig(store=FileCache())) as client:
    client.get_track("4uLU6hMCjMI75M1A2tKUQC")   # first call hits the network
    client.get_track("4uLU6hMCjMI75M1A2tKUQC")   # served from the cache
```

Default TTL is 24h; the `FileCache` is stdlib-only and the backend is pluggable.
See the [caching guide](https://spotifyscraper.readthedocs.io/en/latest/guides/caching/).

## Search

`search()` runs one anonymous, aggregate query across every entity type and
returns a typed `SearchResults`:

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    results = client.search("daft punk", types=("track", "artist"), limit=5)
    print(results.total, "track matches")
    for track in results.tracks:
        print(track.name, "—", track.artists[0].name)
```

Hits are sparse (pass an `id` to `get_album()`/`get_show()` for the full entity);
`total` is the track-match count. See the
[search guide](https://spotifyscraper.readthedocs.io/en/latest/guides/search/).

## Lyrics & transcripts

Lyrics and podcast transcripts need a Spotify account cookie (`sp_dc`); the
library handles the token handshake for you, and one cookie powers both:

```python
from spotify_scraper import SpotifyClient

with SpotifyClient(cookies="cookies.txt") as client:   # or cookies={"sp_dc": "..."}
    lyrics = client.get_lyrics("4uLU6hMCjMI75M1A2tKUQC")
    for line in lyrics.lines:
        print(line.start_ms, line.text)

    transcript = client.get_transcript("07gKzPFkbvGF0cHoeG7ARS")   # a podcast episode
    for line in transcript.lines:
        print(line.start_ms, line.text)
```

Your cookie is sent only to Spotify and never logged. An episode with no
transcript raises `NotFoundError`. See the
[lyrics & cookies guide](https://spotifyscraper.readthedocs.io/en/latest/guides/lyrics-and-cookies/).

## Browser-assisted login

Don't want to copy a cookie by hand? `login()` opens a real browser, you sign in
once, and the captured `sp_dc` is persisted (no password is ever collected or
stored). Later runs reconnect headlessly — ideal for servers:

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    client.login()                              # reuse a valid session, else open a browser
    print(client.get_lyrics("4uLU6hMCjMI75M1A2tKUQC").sync_type)

# A later, headless run — no browser needed:
with SpotifyClient.from_saved_session() as client:
    account = client.get_account()              # who am I?
    print(account.product, account.country, client.is_premium())
    transcript = client.get_transcript("07gKzPFkbvGF0cHoeG7ARS")
```

`login()` reuses a valid saved session by default (browser only the first time);
`from_saved_session()` never needs the `browser` extra. The cookie is stored in
an owner-only file, or the OS keyring with `store="keyring"` (the `keyring`
extra). `get_account()`/`is_premium()` report the logged-in account, and
`SpotifyClient.session_info()` checks a saved session without exposing the
cookie. See the
[authenticated sessions guide](https://spotifyscraper.readthedocs.io/en/latest/guides/authentication/).

## Roadmap

**Shipped**

| Version | Scope |
|---------|-------|
| **3.0** | The library: all entities, pagination, media downloads, browser fallback, docs |
| **3.1** | Command-line interface |
| **3.2** | Cookie-authenticated lyrics |
| **3.3** | Cookie-authenticated podcast transcripts (`get_transcript`); browser-assisted login, session persistence & account-awareness (`get_account`/`is_premium`) |
| **3.4** | [Search](https://github.com/AliAkhtari78/SpotifyScraper/issues/129) across every entity type (`search()`) · display-language [localization](https://github.com/AliAkhtari78/SpotifyScraper/issues/130) (`locale`) |
| **3.5** | Optional [response cache](https://github.com/AliAkhtari78/SpotifyScraper/issues/131) (`cache=CacheConfig(...)`) · [batch helpers](https://github.com/AliAkhtari78/SpotifyScraper/issues/132) with managed concurrency |
| **3.6** | **Visual & discovery**: cover colors, Canvas videos, charts, related artists, paginated discography, recommendations, public profiles, track credits, concerts · a best-in-class **MCP server** + container image |
| **3.7** | MCP **batch tools** (`get_tracks`/`get_albums`/…) · `get_track_visuals` convenience tool for visual front-ends |
| **3.8** | Maintenance: dependency, toolchain & CI modernization (all Actions on current majors, SHA-pinned) · docs & PyPI backlinks |
| **3.9** | Official **MCP registry** publishing (+ Glama/mcp.so/PulseMCP/Smithery discovery) · "vs spotipy" comparison · one-time, opt-out CLI star hint |

**What's next** — future ideas are tracked in the GitHub
[milestones](https://github.com/AliAkhtari78/SpotifyScraper/milestones) and
[issues](https://github.com/AliAkhtari78/SpotifyScraper/issues) — 👍 or weigh in
on the ones that matter most to you. Scope is subject to change.

## Reliability & maintenance

This library rides Spotify's own public endpoints, so it can break when Spotify
changes them. To keep it dependable:

- A **daily canary** runs the live test suite against Spotify. When an endpoint
  shifts, it automatically opens a `spotify-breakage` issue (and closes it on
  recovery), so regressions surface before they reach you.
- Breakages are triaged and fixed promptly with the help of **[Claude Code](https://claude.com/claude-code)**
  (Anthropic's coding agent), under the maintainer's review — the same
  agent-assisted workflow that keeps this project moving. Persisted-query hashes
  live in a single file (`api/pathfinder.py`), so a Spotify rotation is a
  one-line update.
- Every change runs through `ruff` + `mypy --strict` + a hermetic test suite
  (85% coverage floor) across Python 3.10–3.13 on Linux, macOS, and Windows.

If something is broken for you, please
[open an issue](https://github.com/AliAkhtari78/SpotifyScraper/issues) — the
monitoring has often caught it already.

## Documentation

Full docs, guides, and the API reference: **<https://spotifyscraper.readthedocs.io>**

The MCP server also ships as a container:
`docker run -p 8000:8000 ghcr.io/aliakhtari78/spotifyscraper` (set `SPOTIFY_SP_DC`
to enable the authenticated tools).

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

## Star history

If SpotifyScraper saved you the official-API OAuth dance, a ⭐ helps other
developers find it — and tells me which features to keep building.

<a href="https://star-history.com/#AliAkhtari78/SpotifyScraper&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=AliAkhtari78/SpotifyScraper&type=Date&theme=dark" />
    <img alt="Star history of AliAkhtari78/SpotifyScraper" src="https://api.star-history.com/svg?repos=AliAkhtari78/SpotifyScraper&type=Date" width="600" />
  </picture>
</a>

## License

[MIT](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/LICENSE) © [Ali Akhtari](https://aliakhtari.com) — full-stack AI engineer ([aliakhtari.com](https://aliakhtari.com)).

<!-- mcp-name: io.github.AliAkhtari78/spotifyscraper -->
