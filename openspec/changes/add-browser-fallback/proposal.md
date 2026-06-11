# Proposal: add-browser-fallback

## Why

If Spotify hardens its anti-bot defenses against plain HTTP clients, users need an escape hatch that looks like a real browser. v2 shipped a broken Selenium backend; v3 provides a Playwright-based transport behind the existing `Transport` protocols — a drop-in replacement requiring zero changes elsewhere.

## What Changes

- New `browser/` package: `PlaywrightTransport` / `AsyncPlaywrightTransport` implementing the `http-transport` protocols by driving a headless (or headed) Chromium.
- Installed via the `browser` extra (`pip install spotifyscraper[browser]` + `playwright install chromium`); importing without the extra raises a helpful `ImportError`.
- A dedicated CI job (not part of the default matrix) exercises the browser transport.

## Capabilities

### New Capabilities

- `browser-transport`: Playwright-backed implementation of the transport protocols

### Modified Capabilities

(none — this is a new implementation of existing protocols)

## Impact

- New `src/spotify_scraper/browser/`; `browser` extra already declared; optional CI job; docs guide
