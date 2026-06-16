# Design: add-track-extraction

## api/pathfinder.py

```python
PATHFINDER_URL = "https://api-partner.spotify.com/pathfinder/v1/query"

@dataclass(frozen=True, slots=True)
class Operation:
    name: str
    sha256: str
    build_variables: Callable[[str], dict[str, Any]]   # entity_id -> variables

OPERATIONS: dict[str, Operation] = {
    "track": Operation("getTrack", "612585ae06ba435ad26369870deaae23b5c8800a256cd8a57e08eddc25a37294",
                       lambda eid: {"uri": f"spotify:track:{eid}"}),
    # album/artist/playlist/episode/show entries land with their extraction changes;
    # hashes captured June 2026 — see scripts/capture_fixtures.py to refresh.
}

def build_url(kind: str, entity_id: str) -> str          # urlencoded GET URL
def classify_response(status: int, body: Mapping[str, Any] | None) -> ...
    # pure: returns parsed data dict or raises ParsingError (PersistedQueryNotFound),
    # NotFoundError (data present but union null), TokenError sentinel for 401 (raised by caller logic)
```

`auth_headers(token) -> dict[str, str]` lives here too (`Authorization: Bearer`, `app-platform: WebPlayer`).

## api/parse_entities.py (pure)

```python
def parse_track_gql(data: Mapping[str, Any]) -> Track     # data = body["data"]["trackUnion"]
def parse_track_embed(entity: Mapping[str, Any]) -> Track # entity from parse_embed.get_entity
```

Mapping notes (from fixtures): gql artists = `firstArtist.items + otherArtists.items` → `profile.name`, `uri`, `id`; images = `albumOfTrack.coverArt.sources`; `playcount` str→int; explicit = `contentRating.label == "EXPLICIT"`; release date = `albumOfTrack.date.isoString`. Embed: `audioPreview.url`, `releaseDate.isoString`, `visualIdentity.image` (url/maxWidth/maxHeight), `isExplicit`. Defensive access: missing optional branches → `None`/`()`; missing required keys → `ParsingError` naming the JSON path.

## Clients

```python
# _sync/client.py
class SpotifyClient:
    def __init__(self, *, rate_limit=None, retry=None, proxy=None, user_agent=None,
                 timeout=10.0, transport: Transport | None = None,
                 cookies: str | Path | Mapping[str, str] | None = None) -> None
        # cookies accepted now, used by the lyrics change
    def get_track(self, value: str) -> Track
    def close(self) -> None
    __enter__/__exit__
```

Internal flow for `get_track`:
1. `urls.parse(value, type_hint="track")`
2. embed page fetch (tier 2 + token source): on cold token, the bootstrap IS this entity's embed page — one round trip total when degraded, two when rich.
   Concretely: fetch embed page of the requested track; parse entity + session; cache token.
3. tier 1: GET pathfinder getTrack with cached/boostrapped token; 401 → invalidate, re-bootstrap, retry once; classify response.
4. merge: tier-1 Track enriched with `preview_url`/`release_date` from the already-fetched embed entity (no extra request). On tier-1 `ParsingError`: log warning, return embed-built Track.
5. `NotFoundError` from the embed entity propagates immediately (no tier-1 attempt needed when the entity is dead; embed page is fetched first).

This "embed-first" ordering satisfies the preview-completeness requirement with zero extra requests and gives every call a tier-2 fallback for free.

The async client mirrors the logic; shared pure helpers (`_merge_tracks(gql_track, embed_track) -> Track` in parse_entities) keep the two facades thin.

## __init__.py exports

`SpotifyClient`, `AsyncSpotifyClient`, `RateLimit`, `RetryPolicy`, all models, all errors, `__version__`.

## Testing

- `tests/unit/api/test_pathfinder.py`: URL building (operation/variables/extensions encoding), classify_response table (ok / PersistedQueryNotFound / null union / 401).
- `tests/unit/api/test_parse_track.py`: parse_track_gql against `fixtures/pathfinder/track.json`; parse_track_embed against `fixtures/embed/track.json`; merge behavior; ParsingError on truncated payloads.
- `tests/unit/test_client.py`: respx-driven — rich path (embed + gql), degraded path (gql 400 → warning + embed track), 401-refresh-retry, closed-client error. Async twin. Parity test comparing public method sets.
- `tests/live/test_track.py` (`@pytest.mark.live`): real `get_track` returns name "Never Gonna Give You Up", playcount > 1e9, preview_url startswith https.
