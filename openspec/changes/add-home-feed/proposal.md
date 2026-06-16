# Proposal: add-home-feed

> **Status: proposed — pending a live feasibility spike.** Home / "Made for you"
> was split out of `add-visual-discovery-mcp` (shipped in v3.6) because it is the
> one surface the existing two-tier ladder cannot reach: its `home` operation is
> not GET-encodable and needs the Spotify **pathfinder v2 POST** path. Before any
> implementation, a live capture spike (the authenticated `pathfinder/v2/query`
> POST, using a real `sp_dc` session) must confirm the request is reproducible. If
> it is not, this change stays proposed and Home stays deferred — we do not ship a
> broken op.

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
