# Proposal: add-cookie-auth-lyrics

> **Status: deferred to v3.1.** Spotify's `/api/token` now requires a rotating
> TOTP handshake (the fragility behind v2's issue #86). To keep v3.0.0's core
> rock-solid and verifiable, lyrics ships in v3.1 alongside the CLI, with the
> TOTP secret/version isolated in one module for easy refresh and live
> verification against a maintainer `sp_dc` cookie.

## Why

Lyrics are the one feature that genuinely requires user credentials (Spotify serves them only to logged-in sessions). v2's implementation silently broke (issue #86). v3 isolates lyrics as an explicitly authenticated feature: user-supplied `sp_dc` cookie in, clear `AuthenticationError` out when it's missing or expired — never a silent failure.

## What Changes

- New `auth/cookies.py`: load cookies from a Netscape `cookies.txt` file, a dict, or a raw `sp_dc` value; exchange `sp_dc` for a web-player access token; cache and refresh that token.
- Clients' existing `cookies=` constructor argument becomes functional.
- New `get_lyrics(value)` on both clients, calling the color-lyrics endpoint; returns the `Lyrics` model with time-synced lines when available.
- Lyrics endpoints are isolated from the anonymous-token path — a lyrics failure can never break entity extraction.

## Capabilities

### New Capabilities

- `cookie-auth`: user cookie ingestion and web-player token exchange
- `lyrics-extraction`: authenticated lyrics fetch with sync metadata

### Modified Capabilities

(none — client-api gains methods, but its requirements are unchanged)

## Impact

- `auth/cookies.py`, both clients, `models/lyrics.py` (already defined), unit + live tests
- Live lyrics tests require a real `sp_dc` (env `SPOTIFY_SP_DC`) and are skipped without it
