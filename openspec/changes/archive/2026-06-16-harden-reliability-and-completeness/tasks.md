# Tasks: harden-reliability-and-completeness

## 1. Per-host rate limiting + transient-403 handling

- [x] 1.0 Measure the partner-API 403 threshold (30 sequential + 20 concurrent → all 200; no punitive default warranted)
- [x] 1.1 ratelimit.py: PARTNER_API_HOST constant + simple resolve_rate_limit (override else default)
- [x] 1.2 transport.py: per-host bucket map + host_rate_limits param on both transports
- [x] 1.3 transport.py: retry transient HTTP 403 with backoff (raise NetworkError when exhausted)
- [x] 1.4 clients: host_rate_limits pass-through on both constructors
- [x] 1.5 Tests: resolve_rate_limit table, independent buckets, override, 403-retry + 403-exhausted

## 2. Complete show episodes

- [x] 2.1 pathfinder.py: queryPodcastEpisodes operation
- [x] 2.2 parse_entities.py: parse_show_episodes_page + show_episodes_total
- [x] 2.3 Clients: get_show(max_episodes=50) pagination + graceful page-failure
- [x] 2.4 Update show-extraction spec note; tests (fixture parse, pagination, degradation, live)

## 3. Verify

- [x] 3.1 make lint/type/test green (438 tests, 90.7% cov); live show fetch shows total_episodes 2707 + 120 episodes
