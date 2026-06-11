"""Pure parsing of Spotify entity payloads into typed models.

Each entity has two parsers: one for the tier-1 pathfinder GraphQL union and
one for the tier-2 embed entity. A merge helper combines them, preferring the
richer tier-1 fields while keeping embed-only fields such as ``preview_url``.
All functions are I/O-free.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from spotify_scraper.errors import ParsingError
from spotify_scraper.models.common import AlbumRef, ArtistRef, Image
from spotify_scraper.models.track import Track

_UPDATE_HINT = "Spotify may have changed its payload format; check for a library update."


def parse_track_gql(data: Mapping[str, Any]) -> Track:
    """Build a :class:`Track` from a tier-1 pathfinder ``trackUnion``.

    Args:
        data: The ``body["data"]["trackUnion"]`` object.

    Returns:
        A fully-populated tier-1 :class:`Track`.

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    entity_id = _require_str(data, "id", "trackUnion.id")
    uri = _require_str(data, "uri", "trackUnion.uri")
    name = _require_str(data, "name", "trackUnion.name")
    duration = _require_mapping(data, "duration", "trackUnion.duration")
    duration_ms = _require_int(
        duration, "totalMilliseconds", "trackUnion.duration.totalMilliseconds"
    )
    playability = _require_mapping(data, "playability", "trackUnion.playability")
    playable = bool(playability.get("playable", False))

    album_node = _optional_mapping(data, "albumOfTrack")
    album = _album_ref(album_node) if album_node is not None else None
    images = _cover_art_images(album_node) if album_node is not None else ()
    release_date = _iso_date(album_node.get("date")) if album_node is not None else None

    return Track(
        id=entity_id,
        uri=uri,
        name=name,
        duration_ms=duration_ms,
        explicit=_gql_explicit(data),
        playable=playable,
        preview_url=None,
        artists=_gql_artists(data),
        images=images,
        release_date=release_date,
        album=album,
        track_number=_optional_int(data, "trackNumber"),
        play_count=_play_count(data),
        share_url=_share_url(data),
    )


def parse_track_embed(entity: Mapping[str, Any]) -> Track:
    """Build a :class:`Track` from a tier-2 embed entity.

    Args:
        entity: The ``props.pageProps.state.data.entity`` object.

    Returns:
        A :class:`Track` with tier-1-only fields left ``None``.

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    entity_id = _require_str(entity, "id", "entity.id")
    uri = _require_str(entity, "uri", "entity.uri")
    name = _embed_name(entity)
    duration_ms = _require_int(entity, "duration", "entity.duration")

    return Track(
        id=entity_id,
        uri=uri,
        name=name,
        duration_ms=duration_ms,
        explicit=bool(entity.get("isExplicit", False)),
        playable=bool(entity.get("isPlayable", False)),
        preview_url=_audio_preview(entity),
        artists=_embed_artists(entity),
        images=_visual_identity_images(entity),
        release_date=_iso_date(entity.get("releaseDate")),
    )


def _merge_tracks(gql: Track, embed: Track) -> Track:
    """Merge a tier-1 and tier-2 :class:`Track`, preferring tier-1 fields.

    ``preview_url`` and ``release_date`` are taken from the embed track when
    the pathfinder track lacks them.

    Args:
        gql: The tier-1 :class:`Track`.
        embed: The tier-2 :class:`Track`.

    Returns:
        The enriched :class:`Track`.
    """
    return Track(
        id=gql.id,
        uri=gql.uri,
        name=gql.name,
        duration_ms=gql.duration_ms,
        explicit=gql.explicit,
        playable=gql.playable,
        preview_url=gql.preview_url if gql.preview_url is not None else embed.preview_url,
        artists=gql.artists,
        images=gql.images,
        release_date=gql.release_date if gql.release_date is not None else embed.release_date,
        album=gql.album,
        track_number=gql.track_number,
        play_count=gql.play_count,
        share_url=gql.share_url,
    )


def _gql_artists(data: Mapping[str, Any]) -> tuple[ArtistRef, ...]:
    items: list[Mapping[str, Any]] = []
    for key in ("firstArtist", "otherArtists"):
        node = _optional_mapping(data, key)
        if node is None:
            continue
        for item in _items(node):
            items.append(item)
    refs: list[ArtistRef] = []
    for item in items:
        profile = item.get("profile")
        name = profile.get("name", "") if isinstance(profile, Mapping) else ""
        refs.append(
            ArtistRef(
                name=str(name),
                uri=str(item.get("uri", "")),
                id=str(item.get("id", "")),
            )
        )
    return tuple(refs)


def _album_ref(album_node: Mapping[str, Any]) -> AlbumRef:
    return AlbumRef(
        id=_require_str(album_node, "id", "trackUnion.albumOfTrack.id"),
        uri=_require_str(album_node, "uri", "trackUnion.albumOfTrack.uri"),
        name=_require_str(album_node, "name", "trackUnion.albumOfTrack.name"),
        images=_cover_art_images(album_node),
    )


def _cover_art_images(album_node: Mapping[str, Any]) -> tuple[Image, ...]:
    cover_art = album_node.get("coverArt")
    if not isinstance(cover_art, Mapping):
        return ()
    sources = cover_art.get("sources")
    if not isinstance(sources, Sequence):
        return ()
    return tuple(
        Image(url=str(s["url"]), width=s.get("width"), height=s.get("height"))
        for s in sources
        if isinstance(s, Mapping) and "url" in s
    )


def _gql_explicit(data: Mapping[str, Any]) -> bool:
    rating = data.get("contentRating")
    if not isinstance(rating, Mapping):
        return False
    return rating.get("label") == "EXPLICIT"


def _play_count(data: Mapping[str, Any]) -> int | None:
    raw = data.get("playcount")
    if not isinstance(raw, str):
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _share_url(data: Mapping[str, Any]) -> str | None:
    sharing = data.get("sharingInfo")
    if not isinstance(sharing, Mapping):
        return None
    url = sharing.get("shareUrl")
    return url if isinstance(url, str) else None


def _embed_name(entity: Mapping[str, Any]) -> str:
    for key in ("title", "name"):
        value = entity.get(key)
        if isinstance(value, str) and value:
            return value
    raise ParsingError(f"Embed payload missing 'entity.title'/'entity.name'. {_UPDATE_HINT}")


def _embed_artists(entity: Mapping[str, Any]) -> tuple[ArtistRef, ...]:
    artists = entity.get("artists")
    if not isinstance(artists, Sequence):
        return ()
    refs: list[ArtistRef] = []
    for artist in artists:
        if not isinstance(artist, Mapping):
            continue
        refs.append(ArtistRef(name=str(artist.get("name", "")), uri=str(artist.get("uri", ""))))
    return tuple(refs)


def _audio_preview(entity: Mapping[str, Any]) -> str | None:
    preview = entity.get("audioPreview")
    if not isinstance(preview, Mapping):
        return None
    url = preview.get("url")
    return url if isinstance(url, str) else None


def _visual_identity_images(entity: Mapping[str, Any]) -> tuple[Image, ...]:
    visual = entity.get("visualIdentity")
    if not isinstance(visual, Mapping):
        return ()
    images = visual.get("image")
    if not isinstance(images, Sequence):
        return ()
    return tuple(
        Image(url=str(i["url"]), width=i.get("maxWidth"), height=i.get("maxHeight"))
        for i in images
        if isinstance(i, Mapping) and "url" in i
    )


def _iso_date(node: Any) -> datetime | None:
    if not isinstance(node, Mapping):
        return None
    iso = node.get("isoString")
    if not isinstance(iso, str) or not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return None


def _items(node: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    items = node.get("items")
    if not isinstance(items, Sequence):
        return []
    return [item for item in items if isinstance(item, Mapping)]


def _require_str(container: Mapping[str, Any], key: str, path: str) -> str:
    value = container.get(key)
    if not isinstance(value, str):
        raise ParsingError(f"Payload missing {path!r}. {_UPDATE_HINT}")
    return value


def _require_int(container: Mapping[str, Any], key: str, path: str) -> int:
    value = container.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ParsingError(f"Payload missing {path!r}. {_UPDATE_HINT}")
    return value


def _require_mapping(container: Mapping[str, Any], key: str, path: str) -> Mapping[str, Any]:
    value = container.get(key)
    if not isinstance(value, Mapping):
        raise ParsingError(f"Payload missing {path!r}. {_UPDATE_HINT}")
    return value


def _optional_mapping(container: Mapping[str, Any], key: str) -> Mapping[str, Any] | None:
    value = container.get(key)
    return value if isinstance(value, Mapping) else None


def _optional_int(container: Mapping[str, Any], key: str) -> int | None:
    value = container.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value
