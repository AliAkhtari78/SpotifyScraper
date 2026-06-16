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
