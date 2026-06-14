# Proposal: add-search

> **Status: targets v3.3.** Closes issue #129. Adds aggregate search as the
> first non-entity, **tier-1-only** capability. It reuses the existing
> anonymous-token machinery (`AnonymousTokenProvider` / `AsyncAnonymousTokenProvider`)
> and the pathfinder request/response plumbing **unchanged** — no cookie, no new
> dependency, fully live-verifiable with the same anonymous bearer `get_track`
> uses.

## Why

Issue #129 asks for first-class `search(query)`. Spotify's web player drives its
`/search` page through a single anonymous pathfinder GraphQL operation
(`searchDesktop`) on the same `api-partner.spotify.com/pathfinder/v1/query`
endpoint the library already consumes for entity extraction. It needs **no
credentials** — the anonymous bearer token (bootstrapped from any embed page's
`__NEXT_DATA__`) is sufficient, exactly as for `get_track`. Search is the most
requested missing surface and unlocks resolve-by-name workflows (find a track,
then `get_track` it). Because it is anonymous, it is fully testable both
hermetically (captured fixture + respx) and live in `make live` with no cookies.

## What Changes

- **`api/pathfinder.py`** gains a dedicated `SEARCH_OPERATION` (the
  `searchDesktop` `operationName` + its persisted-query sha256 — the **only**
  place this hash may live) and a `build_search_url(query, *, variable_overrides)`
  builder. The entity `OPERATIONS` table and its `build_variables(eid)` contract
  are left **untouched**: search variables are query/paging-shaped, not
  entity-ID-shaped, so overloading the `Callable[[str], dict]` signature is
  deliberately avoided to keep `mypy --strict` clean. `auth_headers` and
  `classify_response` are reused verbatim.
- **`models/search.py`** (new): a frozen, slotted `SearchResults` container on
  `ModelBase` holding a tuple per entity type, reusing the existing
  `Track`/`Artist`/`Playlist`/`Episode` models and the `AlbumRef`/`ShowRef`
  lightweight refs (search hits are sparse — tier-1-only fields stay `None`/`()`,
  matching the existing `_album_track`/`_artist_top_track`/`_sparse_episode`
  convention). JSON-safe `to_dict()`/`from_dict()` come free from `ModelBase`.
- **`api/parse_entities.py`** gains `parse_search_results(union, *, query)`,
  I/O-free, reusing the existing private helpers (`_items`, `_id_from_uri`,
  `_cover_art_images`, `_avatar_images`, `_artist_items`, `_gql_explicit`,
  `_play_count`, `_total_count`). Each per-type section is read at
  `searchV2.<section>.items[].item`; malformed shapes raise `ParsingError`. A
  zero-hit search returns an **empty** `SearchResults`, never `NotFoundError`.
- **`search(query, *, types=(...), limit=20)`** on **both** clients (sync +
  async). It is tier-1-only with no embed page and no entity ID, so it does
  **not** route through `_get_entity`/`_fetch_union`; instead a dedicated
  `_search_union` / `_search_request` pair gets the anonymous token directly from
  `self._tokens.token()` and mirrors the `TokenError → invalidate → retry-once`
  pattern of `_fetch_union`. `types` filters which sections are returned; unknown
  `types` raise `URLError`.
- **Exports**: `SearchResults` from `spotify_scraper.models` and the top-level
  package (`__all__`, sorted).
- Hermetic unit tests (captured `search.json` fixture + respx — no embed mock
  needed since search skips the embed page) and a credential-free
  `@pytest.mark.live` smoke test, sync + async.

## Impact

- New: `models/search.py`, `parse_search_results`, `SEARCH_OPERATION` +
  `build_search_url`, `search`/`_search_union`/`_search_request` on both clients,
  exports, `tests/fixtures/pathfinder/search.json`, three unit test files, one
  live test.
- Reused unchanged: `auth/anonymous.py`, `pathfinder.auth_headers`,
  `pathfinder.classify_response`, `errors.py`, `models/base.py`, every existing
  entity model and `common.py` ref.
- **One verification item gates the hash + variable key names** (tasks 0.x): one
  live probe with the anonymous token confirms the `searchDesktop` hash resolves
  (no `PersistedQueryNotFound`), the exact variable key names (`searchTerm` vs
  `query`), and the union item nesting (`items[].item` per the current bundle,
  NOT the legacy `items[].data`). Everything downstream is written against the
  captured, scrubbed fixture so a rotation is a one-line edit in `pathfinder.py`.
- No new runtime dependency; no public API change to existing methods; the parity
  guard (`tests/unit/test_parity.py`) keeps both clients' `search` identical.
