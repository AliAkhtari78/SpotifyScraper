# Proposal: add-mcp-batch-tools

> **Status: shipped in v3.7.** An additive, MCP-server-only surface over
> capabilities the library already ships — no new Spotify endpoints, no library
> getter/model/CLI change.

## Why

Front-ends built on the `spotifyscraper-mcp` server — notably the visual,
voice-driven Spotify pages this server targets — want two things the tool surface
didn't yet offer: fetching **many** entities in one call (instead of one tool call
per ID), and getting a track's **visual payload** (cover colors + Canvas) without
chaining three tools. The library already has the plural batch getters and the
colors/Canvas getters; this change simply surfaces them through MCP.

## What Changes

- **Batch tools** on the FastMCP server — `get_tracks`, `get_albums`,
  `get_artists`, `get_playlists`, `get_episodes`, `get_shows` — each taking a list
  of URLs/URIs/IDs and returning one ordered `{value, ok, result, error}` item per
  input (mirroring `BatchItem`'s partial-failure capture). `get_playlists` /
  `get_shows` accept `max_tracks` / `max_episodes`.
- **`get_track_visuals`** — returns `{track, colors, canvas}` in one round-trip;
  `track` and `colors` are always present (anonymous), `canvas` is best-effort
  (null without a cookie or when the track has none).

## Impact

Additive only, MCP package only. No library getter, model, or CLI signature
changes; the container entrypoint is unchanged. Authenticated behavior is
unchanged — the batch tools are anonymous, and `get_track_visuals` degrades
gracefully without `SPOTIFY_SP_DC`.
