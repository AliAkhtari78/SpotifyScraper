# Proposal: add-http-transport

## Why

All Spotify access flows through HTTP. v3 needs one transport layer that gives both sync and async clients identical behavior — including the anti-ban measures (rate limiting, retries with backoff, user-agent rotation, proxy support) that v2 lacked — and that a browser-based transport can later implement as a drop-in.

## What Changes

- New `http/transport.py`: `Transport` / `AsyncTransport` protocols (the seam for the future Playwright extra) and `HttpxTransport` / `AsyncHttpxTransport` implementations.
- New `http/headers.py`: built-in browser user-agent pool with per-session rotation and default header sets.
- New `http/retry.py`: `RetryPolicy` (exponential backoff with jitter, honors `Retry-After`).
- New `http/ratelimit.py`: `RateLimit` config + token-bucket limiters (thread-safe sync and asyncio variants).
- HTTP errors map onto the `error-handling` hierarchy (`NetworkError`, `RateLimitedError`, `NotFoundError`).

## Capabilities

### New Capabilities

- `http-transport`: pluggable HTTP transports with rate limiting, retries, UA rotation, and proxy support

### Modified Capabilities

(none)

## Impact

- New package `src/spotify_scraper/http/`; tests in `tests/unit/http/` (respx-mocked)
- Uses the core `httpx` dependency only
