# Proposal: harden-reliability-and-completeness

## Why

Two issues surfaced during M3 verification that block "perfect":

1. **Partner-API throttling.** `api-partner.spotify.com` returns 403 under bursty requests from one IP. The single global `RateLimit` default is too aggressive for that host, causing avoidable degradation to the embed tier (losing tier-1 richness like play counts).
2. **Incomplete shows.** `queryShowMetadataV2` returns no episode listing or count, so `Show.total_episodes`/`episodes` were left empty. The dedicated `queryPodcastEpisodes` operation (verified live: `totalCount` + full episode items) makes a complete listing achievable.

## What Changes

- Per-host rate limiting in the transport: each host gets its own token bucket, and `api-partner.spotify.com` gets a conservative built-in default so pathfinder calls don't trip the 403 throttle while embed-page fetches stay fast.
- `get_show` paginates `queryPodcastEpisodes` to populate `Show.total_episodes` and `Show.episodes` (bounded by a `max_episodes` argument), restoring the original show-extraction intent.

## Capabilities

### New Capabilities

- `per-host-rate-limiting`: independent throttling per destination host with a safe partner-API default
- `show-episodes`: complete, paginated show episode listings

### Modified Capabilities

(none archived yet; these refine http-transport and show-extraction behavior)

## Impact

- `http/ratelimit.py`, `http/transport.py` (sync + async)
- `api/pathfinder.py` (queryPodcastEpisodes operation), `api/parse_entities.py` (episode-page parser), both clients (`get_show` pagination)
- New fixture `tests/fixtures/pathfinder/show_episodes.json`; unit + live tests
