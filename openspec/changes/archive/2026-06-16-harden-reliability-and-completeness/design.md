# Design: harden-reliability-and-completeness

## Per-host rate limiting (`http/transport.py`)

**Measurement first (June 2026):** before picking a partner default, the 403 from M3 was probed — 30 sequential and 20 concurrent anonymous pathfinder requests all returned 200. The 403 does not reproduce at reasonable volume, so a punitive partner default would slow real use to defend against a phantom. Decision: **no special partner throttle**; instead retry transient 403s and expose a per-host knob.

Replace the single `self._bucket` with a lazily-populated per-host map. In `ratelimit.py`, keep `PARTNER_API_HOST = "api-partner.spotify.com"` as an exported constant (so callers can target it) but no built-in partner rate. `resolve_rate_limit(host, default, overrides)`: `overrides[host]` if present, else `default or RateLimit()`.

Both transports gain `host_rate_limits: Mapping[str, RateLimit] | None = None` and store `_default_rate`, `_host_overrides`, and `_buckets: dict[str, TokenBucket]`. `get()` parses the host via `httpx.URL(url).host` and acquires from a per-host bucket. Independent buckets still matter (a slow host doesn't block another), and `host_rate_limits` lets anyone behind a shared IP throttle the partner host themselves. The clients pass `host_rate_limits` through to their default transport.

**Transient-403 handling** (`_response_delay`): treat HTTP 403 like a 5xx — retry with backoff, raising `NetworkError` only when retries are exhausted. This stops a one-off partner block from silently degrading to the embed tier.

Tests: `resolve_rate_limit` table; independent per-host buckets; `host_rate_limits` override wins; 403-then-200 retried transparently; 403 exhausted raises `NetworkError`.

## Complete show episodes (`queryPodcastEpisodes`)

Verified live (2026-06-13): operation `queryPodcastEpisodes`, hash `06046f9b939d56c8eb7cdbb687da938de1164c006871aec91dc26e4dc7d8eb08`, variables `{"uri": "spotify:show:<id>", "offset": n, "limit": L}`. Response: `data.podcastUnionV2.episodesV2` with `totalCount` and `items[].entity.data` (full Episode shape — same fields as `episodeUnionV2`). Fixture: `tests/fixtures/pathfinder/show_episodes.json`.

- `pathfinder.py`: add the `show_episodes` operation (its variable builder takes the show id; pagination via `build_url(..., variable_overrides={"offset", "limit"})`).
- `parse_entities.py`: `parse_show_episodes_page(union) -> tuple[Episode, ...]` reusing `parse_episode_gql` on each `items[].entity.data`; also surface `episodesV2.totalCount`.
- Clients: `get_show(value, *, max_episodes=50)`. After the metadata fetch (`queryShowMetadataV2`), if tier-1 succeeded, page `queryPodcastEpisodes` (size 50) until `max_episodes`/exhausted, set `total_episodes` from the first page's `totalCount`, and rebuild the `Show` with episodes. An episode-page failure logs a warning and returns the show with whatever was collected. `max_episodes=None` → fetch all. The embed-degraded path keeps `episodes=()`/`total_episodes=None`.

Show model already has `total_episodes` and `episodes` fields — no model change. Update the show-extraction spec note (the earlier "deferred" reconciliation) to reflect that listings are now populated.

Tests: `parse_show_episodes_page` against the fixture (totalCount 2707, 10 episodes with name+duration); client pagination test (respx multi-page) for `max_episodes`; episode-page-failure degradation; live smoke asserting `total_episodes` and non-empty `episodes`.
