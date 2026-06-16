# Design: add-home-feed

## Known constraints (from prior live investigation)

- The `home` / `homeSection` / `homePinnedSections` operations share one
  persisted-query hash, but the operation is **not GET-encodable**: its required
  variable `homeEndUserIntegration` (type `HomeEndUserIntegration!`) rejects every
  JSON kind passed in the querystring — string, number, boolean, array, null, and
  map all fail with `VALIDATION_INVALID_TYPE_VARIABLE`. The web client therefore
  sends `home` via the **pathfinder v2 POST** endpoint
  (`api-partner.spotify.com/pathfinder/v2/query`), which carries complex input
  types in the request body.
- Home requires a **user token** (anonymous bearer fails); the cookie → `/api/token`
  TOTP handshake already implemented for lyrics/canvas/credits provides it.

## Spike first (Stage 3a — go/no-go)

Drive a logged-in `open.spotify.com` home page via chrome-devtools with a real
`sp_dc` session and capture the live `pathfinder/v2/query` POST: the exact request
body (`operationName`, the real `homeEndUserIntegration` value and shape, all
variables), the persisted-query `sha256`, and the response JSON (data root,
section/item nesting). Scrub tokens, save a fixture, record the shape in the
endpoints reference.

**Decision:** if the captured request is reproducible on the v2 POST path →
implement. If the required value is session-derived in a way we cannot reconstruct
from public signals → keep Home deferred, document why, and do not ship.

## Shape (once captured)

- `Home` = ordered `sections: tuple[HomeSection, ...]`; each `HomeSection` has a
  `title` / `uri` and `items: tuple[HomeItem, ...]`; each `HomeItem` wraps an
  entity reference (playlist / album / artist / track / show / episode) with the
  shared `id` / `uri` / `name` / `images` fields, parsed defensively (Home rails
  are heterogeneous and Spotify reshapes them frequently).
- Parsing mirrors `parse_artist_gql`: `_require_*` / `_optional_*` helpers, tolerant
  of missing rails, never raising on an unknown item `__typename` (skip it).

## Transport POST

`post()` mirrors `get()` (same retry, per-host rate-limit, error classification)
but sends a JSON body. The caching transport delegates POST without caching —
personalized, authenticated responses must never be cached.

## Spike result (2026-06-16): NO-GO — keep deferred

Stage 3a ran (chrome-devtools + Playwright + the persisted Premium `sp_dc`).
Three independent blockers, any one of which is disqualifying:

1. **Automated capture can't reach Home.** A logged-in headless *and* headed
   Chromium (sp_dc injected from the saved session) authenticates, but the
   web-player SPA never bootstraps the Home view: it loads the JS shell + a
   `clienttoken`, then stalls (blank render, gstatic/reCAPTCHA traffic, sentry
   error, and **zero** `pathfinder` or `/api/token` calls). The persisted `sp_dc`
   alone does not reconstitute a full web session, so the real `home` request body
   — and thus the `homeEndUserIntegration` value — cannot be captured this way.
2. **The v2 endpoint is gated beyond the library's v1 auth.**
   `api-partner.spotify.com/pathfinder/v2/query` returns a Google-edge
   `403 Forbidden` ("your client does not have permission") for the user Bearer +
   `app-platform` headers (and a full browser header set). The web client fetches a
   **client-token** from `clienttoken.spotify.com` before any pathfinder call;
   v2 almost certainly requires it. A client-token is its own device handshake
   (protobuf-encoded `client_data`) — a new dependency and complexity at odds with
   the one-runtime-dep, sans-io core.
3. **Direct probing self-limits.** Repeated api-partner requests trip an IP-level
   edge block (observed live: even v1 then 403'd). The library degraded to the
   embed tier and kept working, so users are unaffected — but it confirms the path
   is hostile to the kind of probing implementation would require.

**Decision: keep Home deferred.** The only remaining viable capture is an
*interactive* real-browser login (a human logs in so the SPA bootstraps and the
`pathfinder/v2/query` POST fires) once the IP block clears — and even with the
captured request, shipping `get_home` would still require implementing the
client-token handshake. Revisit only if Home becomes a priority and an interactive
capture session is run.
