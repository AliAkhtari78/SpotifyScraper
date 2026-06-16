# per-host-rate-limiting Specification

## Purpose

Pace requests per host and honor Retry-After to stay within Spotify's limits.

## Requirements
### Requirement: Independent per-host throttling

The transport SHALL maintain a separate token bucket per destination host, so a strict limit on one host does not slow requests to another. Buckets SHALL be created lazily from the resolved rate for that host.

#### Scenario: Two hosts, independent budgets

- **WHEN** requests are issued to two different hosts
- **THEN** each host is throttled by its own bucket, not a shared one

### Requirement: Caller-tunable per-host rates

Transports and clients SHALL accept an optional `host_rate_limits` mapping so callers can throttle a specific host (e.g. `api-partner.spotify.com`, exported as `PARTNER_API_HOST`) harder than the global default. A per-host override SHALL take precedence over the global rate.

#### Scenario: Override a single host

- **WHEN** a caller sets a stricter rate for the pathfinder host via `host_rate_limits`
- **THEN** only that host uses the stricter rate; other hosts use the global default

### Requirement: Transient partner 403 is retried, not fatal

Because the pathfinder host can return an occasional transient HTTP 403 under load, the transport SHALL retry a 403 with backoff (like a 5xx) and only raise `NetworkError` once retries are exhausted — rather than letting the 403 body degrade extraction to the embed tier. The library SHALL NOT impose a punitive default rate on the pathfinder host (measured June 2026: it tolerates dozens of rapid anonymous requests).

#### Scenario: One-off 403 then success

- **WHEN** a pathfinder request returns 403 once and 200 on retry
- **THEN** the caller receives the 200 response transparently

#### Scenario: Persistent 403

- **WHEN** a pathfinder request returns 403 on every attempt
- **THEN** `NetworkError` is raised after retries are exhausted

