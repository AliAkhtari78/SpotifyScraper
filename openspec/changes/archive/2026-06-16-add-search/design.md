# Design: add-search

## Operation and endpoint

Search uses the existing pathfinder endpoint
`https://api-partner.spotify.com/pathfinder/v1/query` with `operationName=searchDesktop`.
It is reached with the **anonymous** bearer token and `app-platform: WebPlayer`
header — the exact `auth_headers(token)` and `classify_response(status, body)`
already in `api/pathfinder.py`. No cookie is involved; the token comes from the
existing `AnonymousTokenProvider`/`AsyncAnonymousTokenProvider` via
`self._tokens.token()`.

## Why search does NOT reuse `_get_entity`/`_fetch_union`

The entity ladder is embed-first and keyed on an entity ID: `_get_entity` fetches
`embed_url(kind, entity_id)`, parses `__NEXT_DATA__` for a tier-2 model and a
per-entity `EmbedSession` token, then calls `_fetch_union(kind, entity_id,
union_key, session)`. Search has **no embed page**, **no entity ID**, and **no
tier-2 fallback** — it is tier-1-only. So `search()` gets a token directly from
`self._tokens.token()` and calls a dedicated `_search_request`, mirroring the
`TokenError → invalidate → retry-once` shape of `_fetch_union` without demanding
an `entity_id`/`union_key`/`session`. The union key is the fixed string
`"searchV2"`.

## Pathfinder builder (hash isolation)

The entity `Operation.build_variables` is `Callable[[str], dict]` (single
entity-ID arg). Search variables are query/paging-shaped, so overloading that
signature would break `mypy --strict` and the entity `build_url`. Instead a
dedicated `SEARCH_OPERATION` + `build_search_url(query, *, variable_overrides)`
is added; `OPERATIONS`/`build_url` are untouched. The `searchDesktop` hash lives
ONLY in `SEARCH_OPERATION.sha256`.

```python
SEARCH_OPERATION = Operation(
    "searchDesktop",
    "<confirmed sha256>",                # ONLY place the search hash may live
    lambda q: {
        "searchTerm": q,                 # confirm key name live (vs "query")
        "offset": 0,
        "limit": 10,
        "numberOfTopResults": 5,
        "includeAudiobooks": True,
        "includePreReleases": True,
        "includeAlbumPreReleases": False,
        "includeAuthors": False,
        "includeEpisodeContentRatingsV2": False,
    },
)

def build_search_url(query, *, variable_overrides=None):
    variables = SEARCH_OPERATION.build_variables(query)
    if variable_overrides:
        variables.update(variable_overrides)
    params = {
        "operationName": SEARCH_OPERATION.name,
        "variables": json.dumps(variables, separators=(",", ":")),
        "extensions": json.dumps(
            {"persistedQuery": {"version": 1, "sha256Hash": SEARCH_OPERATION.sha256}},
            separators=(",", ":"),
        ),
    }
    return f"{PATHFINDER_URL}?{urlencode(params)}"
```

`classify_response` works **unchanged**: a zero-hit search returns a non-null
`searchV2` union (empty section lists), so the `_has_null_union` guard (which
only fires on an empty `data` dict or all-`None` values) does NOT misfire, and
empty search results never become a spurious `NotFoundError`.

## Response shape (CONFIRMED against the live 2026-06-14 capture)

`data.searchV2` is an object keyed by per-type unions. The nesting is **NOT
uniform** — confirmed from the scrubbed `tests/fixtures/pathfinder/search.json`
(captured live, anonymous token, HTTP 200). The `tracksV2` section nests through
an extra `item` wrapper; every other section nests directly through `data`:

- `tracksV2` → `{ totalCount, items: [{ item: { __typename: "TrackResponseWrapper", data: <Track> }, matchedFields }] }` → entity at `items[].item.data`
- `albumsV2`  → `{ totalCount, items: [{ __typename: "AlbumResponseWrapper",  data: <Album>    }] }` → entity at `items[].data`
- `artists`   → `{ totalCount, items: [{ __typename: "ArtistResponseWrapper", data: <Artist>   }] }` → entity at `items[].data`
- `playlists` → `{ totalCount, items: [{ __typename: "PlaylistResponseWrapper", data: <Playlist> }] }` → entity at `items[].data`
- `podcasts`  → `{ totalCount, items: [{ __typename: "PodcastResponseWrapper", data: <Podcast> }] }` → entity at `items[].data` (mapped to `SearchResults.shows`)
- `episodes`  → `{ totalCount, items: [{ __typename: "EpisodeResponseWrapper", data: <Episode> }] }` → entity at `items[].data`
- `audiobooks`, `users`, `genres`, `topResultsV2`, `chipOrder` — present but NOT surfaced in v1.

Inner entity field names (read off the capture):

- Track entity (`items[].item.data`): `id`, `uri`, `name`, `duration.totalMilliseconds`,
  `playability.playable`, `contentRating.label`, `albumOfTrack` (`id`/`uri`/`name`/`coverArt.sources`),
  `artists.items[]` (`profile.name`, `uri`). No `playcount`/`sharingInfo` → `play_count`/`share_url` stay `None`.
- Album entity (`items[].data`): `uri`, `name`, `coverArt.sources`, `date.year`,
  `artists.items[]`. **No `id`** → derived from the uri. (Surfaced as the lightweight `AlbumRef`.)
- Artist entity (`items[].data`): `uri`, `profile.name`, `visuals.avatarImage.sources`. **No `id`** → derived from the uri.
- Playlist entity (`items[].data`): `uri`, `name`, `description`, `images.items[].sources`,
  `ownerV2.data` (`name`/`uri`). **No `id`** → derived; **no `followers`** → `None`.
- Podcast/show entity (`items[].data`): `uri`, `name`, `publisher.name`, `coverArt.sources`,
  `mediaType`. **No `id`** → derived. (Surfaced as the lightweight `ShowRef`.)
- Episode entity (`items[].data`): `uri`, `name`, `duration.totalMilliseconds`, `description`,
  `releaseDate.isoString`, `coverArt.sources`, `podcastV2.data`. **No `id`** → derived.

The parser unwraps `tracksV2` at `items[].item.data` and every other section at
`items[].data`, deriving missing ids from the uri (`_id_from_uri`). Reused
helpers: `_items`, `_id_from_uri`, `_cover_art_images`, `_avatar_images`,
`_artist_items`, `_gql_explicit`, `_owner_ref`, `_publisher_name`,
`_playlist_images`, `_iso_date`, `_total_count`.

## Models

```python
@dataclass(frozen=True, slots=True)
class SearchResults(ModelBase):
    query: str
    tracks: tuple[Track, ...] = ()
    artists: tuple[Artist, ...] = ()
    albums: tuple[AlbumRef, ...] = ()
    playlists: tuple[Playlist, ...] = ()
    shows: tuple[ShowRef, ...] = ()
    episodes: tuple[Episode, ...] = ()
    total: int | None = None
```

Search hits are sparse — the same convention as `_album_track`,
`_artist_top_track`, `_sparse_episode`. `Track`/`Artist`/`Playlist`/`Episode` are
reused directly (tier-1-only fields stay `None`/`()`); albums and shows reuse the
lightweight `AlbumRef`/`ShowRef` (search returns only id/uri/name/cover, no
tracklist/discography). No new ref types. `to_dict()`/`from_dict()` are inherited
from `ModelBase` and handle nested tuples and models automatically.

## Types selection

`types` defaults to all six accepted kinds and is validated against
`{"track","album","artist","playlist","show","episode"}` — an unknown entry
raises `URLError` before any HTTP call (consistent with `urls._checked_type`).
`types` maps to (a) the `limit`/include override variables and/or (b) a filter on
which parsed sections are returned. The first cut is single-page (`limit` <=
Spotify's per-page max); a future offset-paginate loop modeled on `_paginate` is
out of scope.

## Errors

- `URLError` — unknown `types` entry (no HTTP).
- `TokenError` — handled by invalidate-and-retry-once in `_search_union`; a
  second 401 surfaces.
- `ParsingError` — missing `data.searchV2`, `PersistedQueryNotFound` (rotated
  hash, via `classify_response`), or unparseable section shape.
- **Never** `NotFoundError` for empty results — an empty `SearchResults` is
  returned.

## Parity

`tests/unit/test_parity.py` enforces that `search` exists on both clients with an
identical parameter list and identical return annotation, the async one a
coroutine. The async `search`/`_search_union`/`_search_request` are a literal
mirror with `await` on token/transport calls.
