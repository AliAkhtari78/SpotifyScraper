# browser-transport Specification

## Purpose

Optional Playwright browser fallback for fetching pages the HTTP client cannot.

## Requirements
### Requirement: Protocol-compatible browser transport

`PlaywrightTransport` and `AsyncPlaywrightTransport` SHALL satisfy the `Transport` / `AsyncTransport` protocols so any client accepts them via the `transport=` argument with no other configuration changes.

#### Scenario: Drop-in use

- **WHEN** `SpotifyClient(transport=PlaywrightTransport())` fetches a track
- **THEN** the result equals what the httpx transport would return

### Requirement: Real browser fetching

The transport SHALL drive a Chromium instance (headless by default, `headless=False` available) and return page/document responses with status, headers, and body so both embed-page HTML and pathfinder JSON requests work.

#### Scenario: JSON endpoint through the browser

- **WHEN** a pathfinder URL is requested through the browser transport
- **THEN** the JSON body is returned intact

### Requirement: Graceful absence of the extra

Importing `spotify_scraper.browser` without Playwright installed SHALL raise `ImportError` whose message includes `pip install spotifyscraper[browser]` and `playwright install chromium`.

#### Scenario: Missing extra

- **WHEN** `from spotify_scraper.browser import PlaywrightTransport` runs without playwright
- **THEN** the ImportError message contains both install commands

### Requirement: Resource lifecycle

`close()` / `aclose()` SHALL shut down the page, context, browser, and Playwright driver; the transport SHALL be constructible lazily (browser starts on first request, not at import).

#### Scenario: Clean shutdown

- **WHEN** a transport is closed after use
- **THEN** no Chromium processes remain

