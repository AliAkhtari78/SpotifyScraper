# Proposal: add-home-feed

> **Status: DEFERRED — feasibility spike ran 2026-06-16, result NO-GO.** Home /
> "Made for you" was split out of `add-visual-discovery-mcp` (shipped in v3.6)
> because it is the one surface the existing two-tier ladder cannot reach: its
> `home` operation is not GET-encodable and needs the Spotify **pathfinder v2 POST**
> path. The spike (chrome-devtools + Playwright + a real `sp_dc`) found the request
> is **not reproducible by automation** — see `design.md` → "Spike result": the web
> SPA won't bootstrap Home with an injected cookie, and `pathfinder/v2/query` is
> edge-gated behind a `clienttoken` device handshake the v1 path doesn't use. Per
> the don't-ship-a-broken-op rule, this change stays proposed and Home stays
> deferred; revisit only with an interactive real-browser capture if Home becomes a
> priority.

## Why

Home is the personalized "Made for you" feed: the titled rails Spotify shows a
logged-in user (recommended playlists, recent listening, new releases, mixes). It
is the highest-value discovery surface still missing from the library and the #1
gap for visual, voice-driven front-ends built on top of SpotifyScraper, which want
a personalized landing payload rather than only known-entity lookups.

## What Changes

- **Transport gains POST.** Add a `post(url, *, headers, json)` method to the
  `Transport` / `AsyncTransport` protocols and the `HttpxTransport` /
  `AsyncHttpxTransport` implementations, reusing the existing retry / per-host
  rate-limit handling. POST responses are never cached (the caching transport
  passes them straight through).
- **Pathfinder v2.** Add a `PATHFINDER_V2_URL`
  (`https://api-partner.spotify.com/pathfinder/v2/query`) constant and a `home`
  operation in `api/pathfinder.py` (the only place its persisted-query hash may
  live), plus a `build_post_request(...)` that returns the v2 URL and a JSON body
  (`operationName`, `variables` — including the captured `homeEndUserIntegration`
  value — and the persisted-query `extensions`).
- **Model + parser.** A new frozen, slotted `Home` model (titled `HomeSection`s
  of entity `HomeItem`s) with a JSON-safe `to_dict()`, parsed in
  `api/parse_entities.py` following the existing `parse_*_gql` pattern.
- **Client + tooling.** New `get_home()` on both clients (mirrored sync+async,
  additive), over the cookie-derived **user token** (anonymous bearer is refused);
  a `home` CLI command and a `get_home` MCP tool (authenticated).

## Impact

Additive only: no existing signature, model field, or CLI command changes. Home
requires a valid `sp_dc` session, like `get_canvas` / `get_credits` / `get_user`.
The new POST capability is internal plumbing reused by any future v2 operation.
