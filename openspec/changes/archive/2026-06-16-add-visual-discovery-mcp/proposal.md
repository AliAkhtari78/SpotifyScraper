# Proposal: add-visual-discovery-mcp

> **Status: shipped in v3.6.** Adds the visual, discovery, and AI-tooling
> surfaces on top of the existing two-tier ladder — all additive, mirrored
> sync+async, and live-verified with the same anonymous bearer (and, where noted,
> the cookie-derived user token) the library already uses.

## Why

v3.6 extends SpotifyScraper from "fetch a known entity" to powering visually rich,
discovery-driven, and LLM-callable experiences: cover **colors** and **Canvas**
videos for visual UIs, the discovery graph (related artists, full discography,
recommendations, public profiles), track **credits** and **concerts**, and a
Model Context Protocol **server** so Claude and other LLM hosts can call the
library as tools.

## What Changes

- New pathfinder ops in `api/pathfinder.py` (each the only place its hash may
  live): `fetchExtractedColors`, `canvas`, `queryArtistRelated`,
  `queryArtistDiscographyAll`, `similarAlbumsBasedOnThisTrack`, `ArtistConcerts`;
  new spclient request modules `api/user_profile.py` and `api/credits.py`; a
  curated chart registry `api/charts.py`.
- New frozen, slotted models: `Colors`, `Canvas`, `UserProfile`, `Credits` /
  `CreditRole` / `CreditArtist`, `Concert`.
- New client methods, mirrored sync+async and additive only: `get_colors`,
  `get_canvas` / `download_canvas`, `list_charts` / `get_chart`,
  `get_related_artists`, `get_discography`, `get_similar_albums`, `get_user`,
  `get_credits`, `get_artist_events`; matching CLI commands.
- New `spotify_scraper/mcp/` package behind a `mcp` optional extra with a
  `spotifyscraper-mcp` entry point (tools, resources, prompts, image content,
  stdio + streamable-HTTP transports), plus a container image on ghcr.io.
- Home / Made-for-you was investigated and **deferred** into its own
  `add-home-feed` change: its `home` op variable is not GET-encodable (rejects
  every JSON kind) and needs the pathfinder v2 POST path — documented rather than
  shipped broken.

## Impact

Additive only: no existing signature, model field, or CLI command changes. New
runtime dependencies (`mcp`, `uvicorn`) live behind the optional `mcp` extra with
a lazy import and a helpful `ImportError`.
