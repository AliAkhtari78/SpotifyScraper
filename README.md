# SpotifyScraper

> **v3.0.0 is under active development on this branch.**
> For the current stable release, see the [`v2.x` branch](https://github.com/AliAkhtari78/SpotifyScraper/tree/v2.x) or install from PyPI: `pip install spotifyscraper`.

SpotifyScraper is a Python library for extracting public Spotify data — tracks, albums, artists, playlists, podcasts — without the official API or user credentials.

## What's coming in v3

A complete, spec-driven rewrite focused on reliability and maintainability:

- **Modern extraction strategy** — anonymous token bootstrap + Spotify's JSON endpoints, with an embed-page fallback tier, instead of fragile HTML parsing.
- **One runtime dependency** (`httpx`) — media, browser, and CLI features become optional extras.
- **Sync and async clients** — `SpotifyClient` and `AsyncSpotifyClient` with a shared core.
- **Typed, frozen data models** with JSON-safe serialization.
- **Built-in anti-ban resilience** — rate limiting, retries with backoff, user-agent rotation, proxy support.
- **Daily live canary CI** that detects Spotify page changes before users do.

Development follows an [OpenSpec](https://github.com/Fission-AI/OpenSpec) spec-first workflow; specs live in [`openspec/`](openspec/).

## Roadmap

| Version | Scope |
|---------|-------|
| 3.0.0 | Core library: all entities, media downloads, lyrics (cookie-auth), browser fallback, new docs |
| 3.1.0 | Command-line interface |

## License

[MIT](LICENSE) © Ali Akhtari
