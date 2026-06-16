# Tasks: add-search

## 0. Live verification (BLOCKS the hash + variable keys + fixture) — DONE

- [x] 0.1 Live probe issued with an anonymous token (no cookie):
      `operationName=searchDesktop`,
      `variables={"searchTerm":"daft punk","offset":0,"limit":10,"numberOfTopResults":5,"includeAudiobooks":true,"includePreReleases":true,"includeAlbumPreReleases":false,"includeAuthors":false,"includeEpisodeContentRatingsV2":false}`,
      `extensions={"persistedQuery":{"version":1,"sha256Hash":"eff59fa0a3d026b88b56fddbcf4bdfa16a186b8175a5c1a358c072e053c2e5b0"}}`,
      headers `Authorization: Bearer <anon>`, `app-platform: WebPlayer`.
- [x] 0.2 Hash resolves (HTTP 200, no `PersistedQueryNotFound`); the listed
      variables are accepted as-is — no extra required flag.
- [x] 0.3 Recorded from the 200 body: (a) sections present under `data.searchV2`:
      `tracksV2, albumsV2, artists, playlists, podcasts, episodes, audiobooks,
      users, genres, topResultsV2, chipOrder`; (b) **nesting is NOT uniform** —
      `tracksV2.items[].item.data` (the `{item, matchedFields}` wrapper holds a
      `TrackResponseWrapper` whose `.data` is the Track), while every other
      section is `items[].data` directly; (c) wrappers are
      `TrackResponseWrapper`/`AlbumResponseWrapper`/`ArtistResponseWrapper`/
      `PlaylistResponseWrapper`/`PodcastResponseWrapper`/`EpisodeResponseWrapper`,
      entity under `.data`; (d) `totalCount` sits on each section; (e)
      `topResultsV2.itemsV2[].item` present but not surfaced in v1.
- [x] 0.4 Variable keys confirmed (`searchTerm`, not `query`); `numberOfTopResults`
      sent but not required for a 200.
- [x] 0.5 Captured body scrubbed (no `accessToken`/`clientId`/cookie), trimmed to
      3 items per parsed section, saved as `tests/fixtures/pathfinder/search.json`.
      Confirmed shape pinned in design.md. SHOW section is named `podcasts` →
      mapped to `SearchResults.shows`.

## 1. Pathfinder operation (hash isolated)

- [x] 1.1 In `src/spotify_scraper/api/pathfinder.py` add `SEARCH_OPERATION =
      Operation("searchDesktop", "<confirmed-sha256>", lambda q: {...})` with the
      verified default variables. This is the ONLY place the search hash may live.
- [x] 1.2 Add `build_search_url(query, *, variable_overrides=None)` mirroring
      `build_url`: merge overrides over the built variables, compact-`json.dumps`
      `variables` + `extensions`, `urlencode`, target `PATHFINDER_URL`. Do NOT
      change `Operation`, `OPERATIONS`, `build_url`, `auth_headers`, or
      `classify_response`. Import `Sequence` is not needed here.

## 2. Model

- [x] 2.1 Create `src/spotify_scraper/models/search.py`: frozen slotted
      `SearchResults(ModelBase)` with `query: str`, then defaulted tuples
      `tracks: tuple[Track, ...] = ()`, `artists: tuple[Artist, ...] = ()`,
      `albums: tuple[AlbumRef, ...] = ()`, `playlists: tuple[Playlist, ...] = ()`,
      `shows: tuple[ShowRef, ...] = ()`, `episodes: tuple[Episode, ...] = ()`, and
      `total: int | None = None`. Reuse existing models/refs; no new ref types.
- [x] 2.2 Export `SearchResults` from `models/__init__.py` and the top-level
      `__init__.py` (import block + `__all__`, sorted).

## 3. Parser (sans-io)

- [x] 3.1 Add `parse_search_results(union, *, query)` to `api/parse_entities.py`
      and to `__all__`. Read each section at `searchV2.<key>.items[].item`,
      build sparse models via the existing helpers (`_id_from_uri`,
      `_cover_art_images`/`_avatar_images`, `_artist_items`, `_gql_explicit`,
      `_play_count`, `_total_count`, `_iso_date`). Add small `_search_<type>`
      helpers only where a section's wrapper differs; reuse low-level helpers.
- [x] 3.2 Empty sections → empty tuples (NEVER raise `NotFoundError`); a section
      present but not a `Mapping`, or an item missing required `uri`/`name`, →
      skip the item rather than crash; a `union` that is not a `Mapping` is the
      client's responsibility (it raises `ParsingError` before calling the parser).

## 4. Client exposure (anonymous, tier-1-only)

- [x] 4.1 Add to `_sync/client.py`: import `Sequence` from `collections.abc` and
      `SearchResults`. Implement `search(self, query, *, types=("track","album",
      "artist","playlist","show","episode"), limit=20) -> SearchResults`:
      `_ensure_open()`, validate `types` against the accepted set (`URLError` on
      unknown), call `_search_union`, return `parse_entities.parse_search_results`.
- [x] 4.2 Add `_search_union(query, types, limit)` and `_search_request(query,
      token, overrides)` mirroring `_fetch_union`/`_pathfinder_request`: token
      from `self._tokens.token()`; on `TokenError` → `self._tokens.invalidate()`
      → retry once with a fresh token; pull `data["searchV2"]`, raising
      `ParsingError` (with the standard hint) if it is not a `Mapping`. `overrides`
      carries `{"limit": limit}` plus any per-type flags derived from `types`.
- [x] 4.3 Mirror 1:1 in `_async/client.py`: `async def search`, `async def
      _search_union`, `async def _search_request` with `await self._tokens.token()`
      and `await self._transport.get(...)`. Identical parameter list and
      `-> SearchResults` return annotation (parity guard).

## 5. Tests

- [x] 5.1 `tests/unit/api/test_pathfinder.py` (extend): `build_search_url` targets
      `PATHFINDER_URL`, `operationName == "searchDesktop"`, `variables` encodes the
      query (`parse_qs` round-trip), `extensions` carries the confirmed sha256,
      and `variable_overrides` (e.g. `limit`) win.
- [x] 5.2 `tests/unit/api/test_parse_search.py` (new): load `search.json`, call
      `parse_search_results(..., query="daft punk")`, assert per-type counts and
      representative fields, empty-section → empty tuple, and `to_dict()` round-trip.
- [x] 5.3 `tests/unit/test_client_entities.py` + `..._async.py` (extend): respx
      the `PATHFINDER_RE` returning `search.json`; assert
      `client.search("daft punk", types=("track",), limit=5)` yields the expected
      `SearchResults` (NO embed mock needed); `app-platform`/Bearer header asserts;
      401-then-200 retry-once; unknown `types` → `URLError`; use-after-close →
      `SpotifyScraperError`.
- [x] 5.4 `tests/live/test_search.py` (new): `@pytest.mark.live`, credential-free,
      sync + async; `search("Never Gonna Give You Up", types=("track",), limit=5)`
      finds the known track. Confirms the captured hash still resolves.

## 6. Verify

- [x] 6.1 `make lint`, `make type`, `make test`, `make cov` (>=85%) green;
      `test_parity.py` passes with `search` on both clients.
- [x] 6.2 `make live` green (no cookie); confirm `search.json` still matches the
      live `searchV2` shape.
- [x] 6.3 Docs: add a search usage section to the docs site next to the entity
      getters.

## 7. Review fixes

- [x] 7.1 (code, prior session) search never aborts on a partial album;
      `SearchResults.total` is tracks-only and cleared when tracks aren't requested.
- [x] 7.2 Docs: new `guides/search.md` + nav; `SearchResults` autodoc in
      `reference/models.md`; README Search section + Features bullet + roadmap
      (3.4 search shipped); index Search section + roadmap + success admonition;
      CHANGELOG Unreleased entry.
