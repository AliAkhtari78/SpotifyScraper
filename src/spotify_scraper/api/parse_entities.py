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
from spotify_scraper.models.album import Album
from spotify_scraper.models.artist import Artist
from spotify_scraper.models.common import AlbumRef, ArtistRef, Image, ShowRef, UserRef
from spotify_scraper.models.episode import Episode
from spotify_scraper.models.playlist import Playlist, PlaylistTrack
from spotify_scraper.models.show import Show
from spotify_scraper.models.track import Track

__all__ = [
    "parse_album_embed",
    "parse_album_gql",
    "parse_album_tracks_page",
    "parse_artist_embed",
    "parse_artist_gql",
    "parse_episode_embed",
    "parse_episode_gql",
    "parse_playlist_embed",
    "parse_playlist_gql",
    "parse_playlist_tracks_page",
    "parse_show_embed",
    "parse_show_gql",
    "parse_track_embed",
    "parse_track_gql",
]

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


# --------------------------------------------------------------------------- #
# Album
# --------------------------------------------------------------------------- #


def parse_album_gql(union: Mapping[str, Any]) -> Album:
    """Build an :class:`Album` from a tier-1 ``albumUnion``.

    Args:
        union: The ``body["data"]["albumUnion"]`` object.

    Returns:
        A fully-populated tier-1 :class:`Album` including its tracks.

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    uri = _require_str(union, "uri", "albumUnion.uri")
    name = _require_str(union, "name", "albumUnion.name")
    album_type = _require_str(union, "type", "albumUnion.type").lower()

    return Album(
        id=_id_from_uri(uri),
        uri=uri,
        name=name,
        album_type=album_type,
        images=_cover_art_images(union),
        release_date=_iso_date(union.get("date")),
        artists=_artist_items(union.get("artists")),
        label=_optional_str(union, "label"),
        total_tracks=_total_count(union.get("tracksV2")),
        tracks=parse_album_tracks_page(union),
        copyrights=_copyright_texts(union.get("copyright")),
        share_url=_share_url(union),
    )


def parse_album_tracks_page(union: Mapping[str, Any]) -> tuple[Track, ...]:
    """Extract the tracks from a ``getAlbum`` page response's ``albumUnion``.

    Album-page track items carry no ``id``; it is derived from the track uri.

    Args:
        union: The ``albumUnion`` object (possibly a paged response).

    Returns:
        A tuple of sparse :class:`Track` objects in album order.
    """
    tracks_node = _optional_mapping(union, "tracksV2")
    if tracks_node is None:
        return ()
    tracks: list[Track] = []
    for item in _items(tracks_node):
        track_node = _optional_mapping(item, "track")
        if track_node is None:
            continue
        tracks.append(_album_track(track_node))
    return tuple(tracks)


def parse_album_embed(entity: Mapping[str, Any]) -> Album:
    """Build an :class:`Album` from a tier-2 embed entity.

    Args:
        entity: The ``props.pageProps.state.data.entity`` object.

    Returns:
        An :class:`Album` with tier-1-only fields left empty/``None``.

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    uri = _require_str(entity, "uri", "entity.uri")
    name = _embed_name(entity)
    subtitle = entity.get("subtitle")
    artists: tuple[ArtistRef, ...] = ()
    if isinstance(subtitle, str) and subtitle:
        artists = (ArtistRef(name=subtitle),)
    return Album(
        id=_require_str(entity, "id", "entity.id"),
        uri=uri,
        name=name,
        album_type="album",
        images=_visual_identity_images(entity),
        release_date=_iso_date(entity.get("releaseDate")),
        artists=artists,
        tracks=_embed_track_list(entity),
    )


# --------------------------------------------------------------------------- #
# Artist
# --------------------------------------------------------------------------- #


def parse_artist_gql(union: Mapping[str, Any]) -> Artist:
    """Build an :class:`Artist` from a tier-1 ``artistUnion``.

    Args:
        union: The ``body["data"]["artistUnion"]`` object.

    Returns:
        A fully-populated tier-1 :class:`Artist`.

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    uri = _require_str(union, "uri", "artistUnion.uri")
    profile = _require_mapping(union, "profile", "artistUnion.profile")
    name = _require_str(profile, "name", "artistUnion.profile.name")
    discography = _optional_mapping(union, "discography") or {}

    return Artist(
        id=_optional_str(union, "id") or _id_from_uri(uri),
        uri=uri,
        name=name,
        images=_avatar_images(union),
        biography=_biography(profile),
        followers=_stat_int(union, "followers"),
        monthly_listeners=_stat_int(union, "monthlyListeners"),
        world_rank=_world_rank(union),
        top_tracks=_artist_top_tracks(discography.get("topTracks")),
        albums=_artist_releases(discography.get("albums")),
        singles=_artist_releases(discography.get("singles")),
        external_links=_external_links(profile),
        share_url=_share_url(union),
    )


def parse_artist_embed(entity: Mapping[str, Any]) -> Artist:
    """Build an :class:`Artist` from a tier-2 embed entity.

    Args:
        entity: The ``props.pageProps.state.data.entity`` object.

    Returns:
        An :class:`Artist` with tier-1-only fields left empty/``None``.

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    uri = _require_str(entity, "uri", "entity.uri")
    name = _embed_name(entity)
    return Artist(
        id=_require_str(entity, "id", "entity.id"),
        uri=uri,
        name=name,
        images=_visual_identity_images(entity),
        top_tracks=_embed_track_list(entity),
    )


# --------------------------------------------------------------------------- #
# Playlist
# --------------------------------------------------------------------------- #


def parse_playlist_gql(union: Mapping[str, Any], *, max_tracks: int | None = None) -> Playlist:
    """Build a :class:`Playlist` from a tier-1 ``playlistV2`` page.

    Only the tracks present in this union page are parsed; the client drives
    any multi-page loop via :func:`parse_playlist_tracks_page`. ``total_tracks``
    always reflects ``content.totalCount``.

    Args:
        union: The ``body["data"]["playlistV2"]`` object.
        max_tracks: Optional cap on tracks taken from this page.

    Returns:
        A tier-1 :class:`Playlist` (single page of tracks).

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    uri = _require_str(union, "uri", "playlistV2.uri")
    name = _require_str(union, "name", "playlistV2.name")
    content = _optional_mapping(union, "content")
    tracks = parse_playlist_tracks_page(union)
    if max_tracks is not None:
        tracks = tracks[:max_tracks]

    return Playlist(
        id=_id_from_uri(uri),
        uri=uri,
        name=name,
        description=_optional_str(union, "description") or "",
        owner=_owner_ref(union.get("ownerV2")),
        followers=_optional_int(union, "followers"),
        images=_playlist_images(union),
        total_tracks=_total_count(content) if content is not None else None,
        tracks=tracks,
        share_url=_share_url(union),
    )


def parse_playlist_tracks_page(union: Mapping[str, Any]) -> tuple[PlaylistTrack, ...]:
    """Extract playlist items from a ``fetchPlaylist`` page's ``playlistV2``.

    Items whose ``itemV2.data.__typename`` is not ``"Track"`` (local files,
    episodes) are skipped.

    Args:
        union: The ``playlistV2`` object (possibly a paged response).

    Returns:
        A tuple of :class:`PlaylistTrack` objects.
    """
    content = _optional_mapping(union, "content")
    if content is None:
        return ()
    entries: list[PlaylistTrack] = []
    for item in _items(content):
        item_v2 = _optional_mapping(item, "itemV2")
        if item_v2 is None:
            continue
        data = _optional_mapping(item_v2, "data")
        if data is None or data.get("__typename") != "Track":
            continue
        entries.append(
            PlaylistTrack(
                track=_playlist_track(data),
                added_at=_iso_date(item.get("addedAt")),
                added_by=_owner_ref(item.get("addedBy")),
            )
        )
    return tuple(entries)


def parse_playlist_embed(entity: Mapping[str, Any]) -> Playlist:
    """Build a :class:`Playlist` from a tier-2 embed entity.

    Args:
        entity: The ``props.pageProps.state.data.entity`` object.

    Returns:
        A :class:`Playlist` whose tracks carry no ``added_at``.

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    uri = _require_str(entity, "uri", "entity.uri")
    name = _embed_name(entity)
    subtitle = entity.get("subtitle")
    owner = UserRef(name=subtitle) if isinstance(subtitle, str) and subtitle else None
    tracks = tuple(PlaylistTrack(track=track) for track in _embed_track_list(entity))
    return Playlist(
        id=_require_str(entity, "id", "entity.id"),
        uri=uri,
        name=name,
        owner=owner,
        images=_visual_identity_images(entity),
        tracks=tracks,
    )


# --------------------------------------------------------------------------- #
# Episode
# --------------------------------------------------------------------------- #


def parse_episode_gql(union: Mapping[str, Any]) -> Episode:
    """Build an :class:`Episode` from a tier-1 ``episodeUnionV2``.

    Args:
        union: The ``body["data"]["episodeUnionV2"]`` object.

    Returns:
        A fully-populated tier-1 :class:`Episode`.

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    uri = _require_str(union, "uri", "episodeUnionV2.uri")
    name = _require_str(union, "name", "episodeUnionV2.name")
    duration = _require_mapping(union, "duration", "episodeUnionV2.duration")
    duration_ms = _require_int(
        duration, "totalMilliseconds", "episodeUnionV2.duration.totalMilliseconds"
    )
    playability = _optional_mapping(union, "playability") or {}

    return Episode(
        id=_optional_str(union, "id") or _id_from_uri(uri),
        uri=uri,
        name=name,
        duration_ms=duration_ms,
        description=_optional_str(union, "description") or "",
        explicit=_gql_explicit(union),
        playable=bool(playability.get("playable", False)),
        release_date=_iso_date(union.get("releaseDate")),
        images=_cover_art_images(union),
        preview_url=_preview_playback(union),
        show=_show_ref(union.get("podcastV2")),
        share_url=_share_url(union),
    )


def parse_episode_embed(entity: Mapping[str, Any]) -> Episode:
    """Build an :class:`Episode` from a tier-2 embed entity.

    Args:
        entity: The ``props.pageProps.state.data.entity`` object.

    Returns:
        An :class:`Episode` with tier-1-only fields left ``None``.

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    uri = _require_str(entity, "uri", "entity.uri")
    name = _embed_name(entity)
    duration_ms = _require_int(entity, "duration", "entity.duration")
    subtitle = entity.get("subtitle")
    related = entity.get("relatedEntityUri")
    show: ShowRef | None = None
    if isinstance(subtitle, str) and subtitle and isinstance(related, str) and related:
        show = ShowRef(id=_id_from_uri(related), uri=related, name=subtitle)
    return Episode(
        id=_require_str(entity, "id", "entity.id"),
        uri=uri,
        name=name,
        duration_ms=duration_ms,
        description=_optional_str(entity, "description") or "",
        explicit=_embed_explicit(entity),
        playable=bool(entity.get("isPlayable", False)),
        release_date=_iso_date(entity.get("releaseDate")),
        images=_visual_identity_images(entity),
        preview_url=_audio_preview(entity),
        show=show,
    )


# --------------------------------------------------------------------------- #
# Show
# --------------------------------------------------------------------------- #


def parse_show_gql(union: Mapping[str, Any]) -> Show:
    """Build a :class:`Show` from a tier-1 ``podcastUnionV2``.

    Args:
        union: The ``body["data"]["podcastUnionV2"]`` object.

    Returns:
        A fully-populated tier-1 :class:`Show`.

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    uri = _require_str(union, "uri", "podcastUnionV2.uri")
    name = _require_str(union, "name", "podcastUnionV2.name")
    episodes_node = _optional_mapping(union, "episodesV2")

    return Show(
        id=_optional_str(union, "id") or _id_from_uri(uri),
        uri=uri,
        name=name,
        description=_optional_str(union, "description") or "",
        publisher=_publisher_name(union.get("publisher")),
        media_type=_optional_str(union, "mediaType"),
        images=_cover_art_images(union),
        total_episodes=_total_count(episodes_node) if episodes_node is not None else None,
        episodes=_show_episodes(episodes_node),
        topics=_topic_titles(union.get("topics")),
        rating=_average_rating(union.get("rating")),
        share_url=_share_url(union),
    )


def parse_show_embed(entity: Mapping[str, Any]) -> Show:
    """Build a :class:`Show` from a tier-2 embed entity.

    The show embed page carries the latest-episode envelope, so the show name
    and uri are taken from the episode's ``subtitle`` and ``relatedEntityUri``;
    no episode listing is fabricated.

    Args:
        entity: The ``props.pageProps.state.data.entity`` object.

    Returns:
        A :class:`Show` with tier-1-only fields left ``None`` and no episodes.

    Raises:
        ParsingError: If a required key is missing, naming the JSON path.
    """
    subtitle = entity.get("subtitle")
    related = entity.get("relatedEntityUri")
    if isinstance(subtitle, str) and subtitle and isinstance(related, str) and related:
        return Show(
            id=_id_from_uri(related),
            uri=related,
            name=subtitle,
            images=_related_entity_images(entity),
        )
    uri = _require_str(entity, "uri", "entity.uri")
    return Show(
        id=_require_str(entity, "id", "entity.id"),
        uri=uri,
        name=_embed_name(entity),
        images=_visual_identity_images(entity),
    )


# --------------------------------------------------------------------------- #
# Private helpers
# --------------------------------------------------------------------------- #


def _id_from_uri(uri: str) -> str:
    """Return the entity id (last colon-delimited segment) of a Spotify uri."""
    return uri.rsplit(":", 1)[-1]


def _optional_str(container: Mapping[str, Any], key: str) -> str | None:
    value = container.get(key)
    return value if isinstance(value, str) else None


def _total_count(node: Mapping[str, Any] | None) -> int | None:
    if node is None:
        return None
    return _optional_int(node, "totalCount")


def _artist_items(node: Any) -> tuple[ArtistRef, ...]:
    """Build artist refs from an ``{items: [{profile, uri, id?}]}`` node."""
    if not isinstance(node, Mapping):
        return ()
    refs: list[ArtistRef] = []
    for item in _items(node):
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


def _copyright_texts(node: Any) -> tuple[str, ...]:
    if not isinstance(node, Mapping):
        return ()
    texts: list[str] = []
    for item in _items(node):
        text = item.get("text")
        if isinstance(text, str) and text:
            texts.append(text)
    return tuple(texts)


def _album_track(track_node: Mapping[str, Any]) -> Track:
    """Build a sparse album-page :class:`Track` (id derived from uri)."""
    uri = _require_str(track_node, "uri", "albumUnion.tracksV2.items[].track.uri")
    name = _require_str(track_node, "name", "albumUnion.tracksV2.items[].track.name")
    duration = _optional_mapping(track_node, "duration") or {}
    playability = _optional_mapping(track_node, "playability") or {}
    return Track(
        id=_id_from_uri(uri),
        uri=uri,
        name=name,
        duration_ms=_optional_int(duration, "totalMilliseconds") or 0,
        explicit=_gql_explicit(track_node),
        playable=bool(playability.get("playable", False)),
        preview_url=None,
        artists=_artist_items(track_node.get("artists")),
        images=(),
        release_date=None,
        track_number=_optional_int(track_node, "trackNumber"),
        play_count=_play_count(track_node),
    )


def _playlist_track(data: Mapping[str, Any]) -> Track:
    """Build a :class:`Track` from a playlist ``itemV2.data`` node."""
    uri = _require_str(data, "uri", "playlistV2.content.items[].itemV2.data.uri")
    name = _require_str(data, "name", "playlistV2.content.items[].itemV2.data.name")
    duration = _optional_mapping(data, "trackDuration") or {}
    playability = _optional_mapping(data, "playability") or {}
    album_node = _optional_mapping(data, "albumOfTrack")
    album = _album_ref_lenient(album_node) if album_node is not None else None
    images = _cover_art_images(album_node) if album_node is not None else ()
    return Track(
        id=_id_from_uri(uri),
        uri=uri,
        name=name,
        duration_ms=_optional_int(duration, "totalMilliseconds") or 0,
        explicit=_gql_explicit(data),
        playable=bool(playability.get("playable", False)),
        preview_url=None,
        artists=_artist_items(data.get("artists")),
        images=images,
        release_date=None,
        album=album,
        track_number=_optional_int(data, "trackNumber"),
        play_count=_play_count(data),
    )


def _album_ref_lenient(album_node: Mapping[str, Any]) -> AlbumRef:
    """Build an :class:`AlbumRef`, deriving ``id`` from the uri when absent."""
    uri = _require_str(album_node, "uri", "albumOfTrack.uri")
    return AlbumRef(
        id=_optional_str(album_node, "id") or _id_from_uri(uri),
        uri=uri,
        name=_require_str(album_node, "name", "albumOfTrack.name"),
        images=_cover_art_images(album_node),
    )


def _embed_track_list(entity: Mapping[str, Any]) -> tuple[Track, ...]:
    """Build sparse tracks from an embed ``trackList`` (skip non-track rows)."""
    track_list = entity.get("trackList")
    if not isinstance(track_list, Sequence):
        return ()
    tracks: list[Track] = []
    for row in track_list:
        if not isinstance(row, Mapping):
            continue
        if row.get("entityType") not in (None, "track"):
            continue
        uri = row.get("uri")
        name = row.get("title") or row.get("name")
        if not isinstance(uri, str) or not uri or not isinstance(name, str) or not name:
            continue
        subtitle = row.get("subtitle")
        artists: tuple[ArtistRef, ...] = ()
        if isinstance(subtitle, str) and subtitle:
            artists = tuple(
                ArtistRef(name=part.strip()) for part in subtitle.split(",") if part.strip()
            )
        duration = row.get("duration")
        tracks.append(
            Track(
                id=_id_from_uri(uri),
                uri=uri,
                name=name,
                duration_ms=duration
                if isinstance(duration, int) and not isinstance(duration, bool)
                else 0,
                explicit=bool(row.get("isExplicit", False)),
                playable=bool(row.get("isPlayable", False)),
                preview_url=_audio_preview(row),
                artists=artists,
                images=(),
                release_date=None,
            )
        )
    return tuple(tracks)


def _avatar_images(union: Mapping[str, Any]) -> tuple[Image, ...]:
    visuals = _optional_mapping(union, "visuals")
    if visuals is None:
        return ()
    avatar = _optional_mapping(visuals, "avatarImage")
    if avatar is None:
        return ()
    sources = avatar.get("sources")
    if not isinstance(sources, Sequence):
        return ()
    return tuple(
        Image(url=str(s["url"]), width=s.get("width"), height=s.get("height"))
        for s in sources
        if isinstance(s, Mapping) and "url" in s
    )


def _biography(profile: Mapping[str, Any]) -> str | None:
    bio = _optional_mapping(profile, "biography")
    if bio is None:
        return None
    text = bio.get("text")
    return text if isinstance(text, str) and text else None


def _external_links(profile: Mapping[str, Any]) -> tuple[str, ...]:
    links = _optional_mapping(profile, "externalLinks")
    if links is None:
        return ()
    urls: list[str] = []
    for item in _items(links):
        url = item.get("url")
        if isinstance(url, str) and url:
            urls.append(url)
    return tuple(urls)


def _stat_int(union: Mapping[str, Any], key: str) -> int | None:
    stats = _optional_mapping(union, "stats")
    if stats is None:
        return None
    return _optional_int(stats, key)


def _world_rank(union: Mapping[str, Any]) -> int | None:
    rank = _stat_int(union, "worldRank")
    return rank if rank else None


def _artist_top_tracks(node: Any) -> tuple[Track, ...]:
    if not isinstance(node, Mapping):
        return ()
    tracks: list[Track] = []
    for item in _items(node):
        track_node = _optional_mapping(item, "track")
        if track_node is None:
            continue
        tracks.append(_artist_top_track(track_node))
    return tuple(tracks)


def _artist_top_track(track_node: Mapping[str, Any]) -> Track:
    uri = _require_str(track_node, "uri", "artistUnion.discography.topTracks.items[].track.uri")
    name = _require_str(track_node, "name", "artistUnion.discography.topTracks.items[].track.name")
    duration = _optional_mapping(track_node, "duration") or {}
    playability = _optional_mapping(track_node, "playability") or {}
    album_node = _optional_mapping(track_node, "albumOfTrack")
    images = _cover_art_images(album_node) if album_node is not None else ()
    return Track(
        id=_optional_str(track_node, "id") or _id_from_uri(uri),
        uri=uri,
        name=name,
        duration_ms=_optional_int(duration, "totalMilliseconds") or 0,
        explicit=_gql_explicit(track_node),
        playable=bool(playability.get("playable", False)),
        preview_url=None,
        artists=_artist_items(track_node.get("artists")),
        images=images,
        release_date=None,
        play_count=_play_count(track_node),
    )


def _artist_releases(node: Any) -> tuple[AlbumRef, ...]:
    if not isinstance(node, Mapping):
        return ()
    refs: list[AlbumRef] = []
    for item in _items(node):
        releases = _optional_mapping(item, "releases")
        if releases is None:
            continue
        release_items = _items(releases)
        if not release_items:
            continue
        release = release_items[0]
        uri = release.get("uri")
        name = release.get("name")
        if not isinstance(uri, str) or not uri or not isinstance(name, str) or not name:
            continue
        refs.append(
            AlbumRef(
                id=_optional_str(release, "id") or _id_from_uri(uri),
                uri=uri,
                name=name,
                images=_cover_art_images(release),
            )
        )
    return tuple(refs)


def _owner_ref(node: Any) -> UserRef | None:
    if not isinstance(node, Mapping):
        return None
    data = _optional_mapping(node, "data")
    if data is None:
        return None
    name = data.get("name")
    if not isinstance(name, str):
        return None
    return UserRef(name=name, uri=str(data.get("uri", "")))


def _playlist_images(union: Mapping[str, Any]) -> tuple[Image, ...]:
    images = _optional_mapping(union, "images")
    if images is None:
        return ()
    items = _items(images)
    if not items:
        return ()
    sources = items[0].get("sources")
    if not isinstance(sources, Sequence):
        return ()
    return tuple(
        Image(url=str(s["url"]), width=s.get("width"), height=s.get("height"))
        for s in sources
        if isinstance(s, Mapping) and "url" in s
    )


def _preview_playback(union: Mapping[str, Any]) -> str | None:
    playback = _optional_mapping(union, "previewPlayback")
    if playback is None:
        return None
    preview = _optional_mapping(playback, "audioPreview")
    if preview is None:
        return None
    for key in ("url", "cdnUrl"):
        url = preview.get(key)
        if isinstance(url, str) and url:
            return url
    return None


def _show_ref(node: Any) -> ShowRef | None:
    if not isinstance(node, Mapping):
        return None
    data = _optional_mapping(node, "data")
    if data is None:
        return None
    uri = data.get("uri")
    name = data.get("name")
    if not isinstance(uri, str) or not uri or not isinstance(name, str):
        return None
    return ShowRef(
        id=_id_from_uri(uri),
        uri=uri,
        name=name,
        publisher=_publisher_name(data.get("publisher")),
        images=_cover_art_images(data),
    )


def _publisher_name(node: Any) -> str | None:
    if not isinstance(node, Mapping):
        return None
    name = node.get("name")
    return name if isinstance(name, str) and name else None


def _topic_titles(node: Any) -> tuple[str, ...]:
    if not isinstance(node, Mapping):
        return ()
    titles: list[str] = []
    for item in _items(node):
        title = item.get("title")
        if isinstance(title, str) and title:
            titles.append(title)
    return tuple(titles)


def _average_rating(node: Any) -> float | None:
    if not isinstance(node, Mapping):
        return None
    average = node.get("averageRating")
    if isinstance(average, (int, float)) and not isinstance(average, bool):
        return float(average)
    if isinstance(average, Mapping):
        value = average.get("average")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
    return None


def _show_episodes(node: Mapping[str, Any] | None) -> tuple[Episode, ...]:
    if node is None:
        return ()
    episodes: list[Episode] = []
    for item in _items(node):
        entity = _optional_mapping(item, "entity")
        if entity is None:
            continue
        data = _optional_mapping(entity, "data")
        if data is None:
            continue
        episode = _sparse_episode(data)
        if episode is not None:
            episodes.append(episode)
    return tuple(episodes)


def _sparse_episode(data: Mapping[str, Any]) -> Episode | None:
    uri = data.get("uri")
    if not isinstance(uri, str) or not uri:
        return None
    name = data.get("name")
    duration = _optional_mapping(data, "duration") or {}
    playability = _optional_mapping(data, "playability") or {}
    return Episode(
        id=_optional_str(data, "id") or _id_from_uri(uri),
        uri=uri,
        name=name if isinstance(name, str) else "",
        duration_ms=_optional_int(duration, "totalMilliseconds") or 0,
        description=_optional_str(data, "description") or "",
        explicit=_gql_explicit(data),
        playable=bool(playability.get("playable", True)),
        release_date=_iso_date(data.get("releaseDate")),
        images=_cover_art_images(data),
        show=None,
    )


def _related_entity_images(entity: Mapping[str, Any]) -> tuple[Image, ...]:
    images = entity.get("relatedEntityCoverArt")
    if not isinstance(images, Sequence):
        return ()
    return tuple(
        Image(url=str(i["url"]), width=i.get("maxWidth"), height=i.get("maxHeight"))
        for i in images
        if isinstance(i, Mapping) and "url" in i
    )


def _embed_explicit(entity: Mapping[str, Any]) -> bool:
    if bool(entity.get("isExplicit", False)):
        return True
    ratings = entity.get("contentRatings")
    if isinstance(ratings, Mapping):
        labels = ratings.get("labels")
        if isinstance(labels, Sequence):
            return any(isinstance(label, str) and label.upper() == "EXPLICIT" for label in labels)
    return False
