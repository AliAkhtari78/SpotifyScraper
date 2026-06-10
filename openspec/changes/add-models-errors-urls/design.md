# Design: add-models-errors-urls

Field schemas below are pinned against real captured payloads in `tests/fixtures/embed/` and `tests/fixtures/pathfinder/` (June 2026). Implementations MUST use these exact names and types.

## errors.py

```python
class SpotifyScraperError(Exception): ...
class URLError(SpotifyScraperError): ...
class NetworkError(SpotifyScraperError): ...        # __init__(message, *, request_url: str | None = None)
class RateLimitedError(NetworkError): ...           # extra attr: retry_after: float | None
class TokenError(SpotifyScraperError): ...
class AuthenticationError(SpotifyScraperError): ...
class NotFoundError(SpotifyScraperError): ...
class ParsingError(SpotifyScraperError): ...        # message should tell users to check for a library update
class MediaError(SpotifyScraperError): ...
```

## urls.py

```python
EntityType = Literal["track", "album", "artist", "playlist", "episode", "show"]
ENTITY_TYPES: frozenset[str]

def parse(value: str, *, type_hint: EntityType | None = None) -> tuple[EntityType, str]
def entity_url(entity_type: EntityType, entity_id: str) -> str       # https://open.spotify.com/<t>/<id>
def embed_url(entity_type: EntityType, entity_id: str) -> str       # https://open.spotify.com/embed/<t>/<id>
def entity_uri(entity_type: EntityType, entity_id: str) -> str      # spotify:<t>:<id>
```

ID validation: exactly 22 chars of `[0-9A-Za-z]`. Bare IDs require `type_hint`, else `URLError`.
Accepted URL hosts: `open.spotify.com`, `play.spotify.com`. Path may contain one `intl-<lang>` segment before the type and an optional `/embed` prefix. Query strings and fragments are ignored.

## models/ — shared conventions

- `models/base.py` defines `ModelBase` with `to_dict()` / `from_dict()` implemented once via `dataclasses.fields` reflection: dataclass-typed fields recurse; `datetime` ⇄ ISO-8601 string; tuples ⇄ lists. All models: `@dataclass(frozen=True, slots=True)` inheriting `ModelBase`.
- Collections are `tuple[...]` (immutable), defaulting to `()`.
- Durations are `*_ms: int` milliseconds. Dates are `datetime | None` (Spotify precision varies; keep the raw precision string where given).
- Every entity model has `id`, `uri`, `name`, plus `url` property (canonical open.spotify.com URL — derived, not stored, excluded from `to_dict()`).

## models/common.py

```python
class Image(ModelBase):      url: str; width: int | None = None; height: int | None = None
class ArtistRef(ModelBase):  name: str; uri: str = ""; id: str = ""        # embed gives name(+uri); pathfinder gives all
class AlbumRef(ModelBase):   id: str; uri: str; name: str; images: tuple[Image, ...] = ()
class ShowRef(ModelBase):    id: str; uri: str; name: str; publisher: str | None = None; images: tuple[Image, ...] = ()
class UserRef(ModelBase):    name: str; uri: str = ""
```

## models/track.py — `Track`

| field | type | source |
|---|---|---|
| id, uri, name | str | both tiers |
| duration_ms | int | both |
| explicit | bool | embed `isExplicit` / t1 `contentRating.label == "EXPLICIT"` |
| playable | bool | both (`isPlayable` / `playability.playable`) |
| preview_url | str \| None | embed `audioPreview.url` (t1 lacks it) |
| artists | tuple[ArtistRef, ...] | both |
| images | tuple[Image, ...] | both (visualIdentity / coverArt) |
| release_date | datetime \| None | embed `releaseDate.isoString` / t1 album date |
| album | AlbumRef \| None = None | t1 `albumOfTrack` |
| track_number | int \| None = None | t1 |
| play_count | int \| None = None | t1 `playcount` (string in payload — convert) |
| share_url | str \| None = None | t1 `sharingInfo.shareUrl` |

## models/album.py — `Album`

id, uri, name: str; album_type: str ("album"/"single"/"compilation", lowercased from t1 `type`); images: tuple[Image, ...]; release_date: datetime | None; artists: tuple[ArtistRef, ...]; label: str | None = None; total_tracks: int | None = None (t1 `tracksV2.totalCount`); tracks: tuple[Track, ...] = () (t1 page; tier-2-built tracks inside albums have empty images); copyrights: tuple[str, ...] = (); share_url: str | None = None.

## models/artist.py — `Artist`

id, uri, name: str; images: tuple[Image, ...] (t1 `visuals.avatarImage.sources`, embed visualIdentity); biography: str | None = None (t1 `profile.biography.text`); followers: int | None = None; monthly_listeners: int | None = None; world_rank: int | None = None (t1 `stats`); top_tracks: tuple[Track, ...] = () (t1 `discography.topTracks.items[].track` — sparse Tracks); albums: tuple[AlbumRef, ...] = (); singles: tuple[AlbumRef, ...] = () (t1 discography pages); external_links: tuple[str, ...] = (); share_url: str | None = None.

## models/playlist.py — `Playlist` + `PlaylistTrack`

`PlaylistTrack`: track: Track; added_at: datetime | None = None; added_by: UserRef | None = None.
`Playlist`: id, uri, name: str; description: str = ""; owner: UserRef | None = None (t1 `ownerV2.data`); followers: int | None = None; images: tuple[Image, ...] = (); total_tracks: int | None = None (t1 `content.totalCount`); tracks: tuple[PlaylistTrack, ...] = (); share_url: str | None = None.

## models/episode.py — `Episode`

id, uri, name: str; description: str = "" (plain, not html); duration_ms: int; explicit: bool = False; playable: bool = True; release_date: datetime | None = None; images: tuple[Image, ...] = (); preview_url: str | None = None (t1 `previewPlayback.audioPreview` / embed audioPreview); show: ShowRef | None = None (t1 `podcastV2.data`); share_url: str | None = None.

## models/show.py — `Show`

id, uri, name: str; description: str = ""; publisher: str | None = None (t1 `publisher.name`); media_type: str | None = None; images: tuple[Image, ...] = (); total_episodes: int | None = None (t1 `episodesV2.totalCount`); episodes: tuple[Episode, ...] = (); topics: tuple[str, ...] = (); rating: float | None = None (t1 `rating.averageRating` if present); share_url: str | None = None.

## models/lyrics.py — `Lyrics` + `LyricsLine`

`LyricsLine`: start_ms: int; text: str.
`Lyrics`: lines: tuple[LyricsLine, ...]; sync_type: str = "UNSYNCED" ("LINE_SYNCED"/"UNSYNCED"); provider: str | None = None; language: str | None = None.

## Testing

- `tests/unit/test_urls.py`: parametrized table — every accepted form, every entity type, intl paths, embed URLs, URIs, bare IDs with/without hint, rejection cases.
- `tests/unit/models/test_serialization.py`: round-trip `from_dict(to_dict())` equality and `json.dumps` safety for a fully-populated instance of every model.
- `tests/unit/test_errors.py`: hierarchy (`issubclass` table), `RateLimitedError.retry_after`.
