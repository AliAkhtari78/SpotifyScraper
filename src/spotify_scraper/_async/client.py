"""Asynchronous Spotify client facade.

A 1:1 mirror of :mod:`spotify_scraper._sync.client` over the async transport
and async token provider. All parsing is delegated to the same sans-io
helpers, so the two facades stay thin and behaviourally identical.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from pathlib import Path
from types import TracebackType
from typing import Any, TypeVar

from spotify_scraper import urls
from spotify_scraper.api import parse_embed, parse_entities, pathfinder
from spotify_scraper.api.parse_embed import EmbedSession
from spotify_scraper.auth.anonymous import AsyncAnonymousTokenProvider
from spotify_scraper.errors import ParsingError, SpotifyScraperError, TokenError
from spotify_scraper.http.ratelimit import RateLimit
from spotify_scraper.http.retry import RetryPolicy
from spotify_scraper.http.transport import AsyncHttpxTransport, AsyncTransport, Response
from spotify_scraper.models.album import Album
from spotify_scraper.models.artist import Artist
from spotify_scraper.models.episode import Episode
from spotify_scraper.models.playlist import Playlist, PlaylistTrack
from spotify_scraper.models.show import Show
from spotify_scraper.models.track import Track

_LOGGER = logging.getLogger("spotify_scraper")

_PLAYLIST_PAGE = 100
_ALBUM_PAGE = 50
_SHOW_EPISODES_PAGE = 50

_T = TypeVar("_T")


class AsyncSpotifyClient:
    """Asynchronous client for extracting public Spotify data.

    The client is an async context manager and should be closed when done,
    either via ``async with`` or by awaiting :meth:`aclose`. Using it after
    closing raises :class:`~spotify_scraper.errors.SpotifyScraperError`.
    """

    __slots__ = ("_closed", "_cookies", "_owns_transport", "_tokens", "_transport")

    def __init__(
        self,
        *,
        rate_limit: RateLimit | None = None,
        retry: RetryPolicy | None = None,
        proxy: str | None = None,
        user_agent: str | None = None,
        timeout: float = 10.0,
        transport: AsyncTransport | None = None,
        cookies: str | Path | Mapping[str, str] | None = None,
        host_rate_limits: Mapping[str, RateLimit] | None = None,
    ) -> None:
        """Initialize the client.

        Args:
            rate_limit: Global token-bucket configuration; defaults to safe
                limits applied per host.
            retry: Retry policy; defaults to :class:`RetryPolicy`.
            proxy: Optional proxy URL for the default transport.
            user_agent: Fixed User-Agent for the default transport.
            timeout: Per-request timeout in seconds for the default transport.
            transport: A custom transport that overrides every other HTTP
                option; the client does not own its lifecycle.
            cookies: User cookies for authenticated features; accepted and
                stored now, consumed by the lyrics extraction change.
            host_rate_limits: Optional per-host rate overrides for the default
                transport (e.g. to throttle ``api-partner.spotify.com``).
        """
        if transport is None:
            self._transport: AsyncTransport = AsyncHttpxTransport(
                rate_limit=rate_limit,
                retry=retry,
                user_agent=user_agent,
                proxy=proxy,
                timeout=timeout,
                host_rate_limits=host_rate_limits,
            )
            self._owns_transport = True
        else:
            self._transport = transport
            self._owns_transport = False
        self._cookies = cookies
        self._tokens = AsyncAnonymousTokenProvider(self._transport)
        self._closed = False

    async def get_track(self, value: str) -> Track:
        """Fetch a track by URL, URI, or bare ID.

        The embed page is fetched first: it supplies the tier-2 fallback
        track and bootstraps the anonymous token. Tier 1 (pathfinder) is then
        attempted and merged in. On tier-1 :class:`ParsingError` the embed
        track is returned with a logged warning.

        Args:
            value: A Spotify track URL, URI, or 22-character ID.

        Returns:
            The richest available :class:`Track`.

        Raises:
            NotFoundError: If the track does not exist.
            SpotifyScraperError: If the client is closed.
        """
        _, entity_id = self._resolve(value, "track")
        model, _, _ = await self._get_entity(
            "track",
            entity_id,
            "trackUnion",
            parse_entities.parse_track_gql,
            parse_entities.parse_track_embed,
            merge=parse_entities._merge_tracks,
        )
        return model

    async def get_album(self, value: str) -> Album:
        """Fetch an album by URL, URI, or bare ID, paginating its tracks.

        Args:
            value: A Spotify album URL, URI, or 22-character ID.

        Returns:
            The richest available :class:`Album` with as many tracks as the
            pathfinder pages provided (all of them by default).

        Raises:
            NotFoundError: If the album does not exist.
            SpotifyScraperError: If the client is closed.
        """
        _, entity_id = self._resolve(value, "album")
        album, session, tier1 = await self._get_entity(
            "album",
            entity_id,
            "albumUnion",
            parse_entities.parse_album_gql,
            parse_entities.parse_album_embed,
        )
        if not tier1:
            return album
        tracks = await self._paginate(
            "album",
            entity_id,
            session,
            union_key="albumUnion",
            collected=len(album.tracks),
            total=album.total_tracks,
            page_size=_ALBUM_PAGE,
            max_tracks=None,
            parse_page=parse_entities.parse_album_tracks_page,
        )
        if not tracks:
            return album
        return _with_album_tracks(album, (*album.tracks, *tracks))

    async def get_artist(self, value: str) -> Artist:
        """Fetch an artist by URL, URI, or bare ID.

        Args:
            value: A Spotify artist URL, URI, or 22-character ID.

        Returns:
            The richest available :class:`Artist`.

        Raises:
            NotFoundError: If the artist does not exist.
            SpotifyScraperError: If the client is closed.
        """
        _, entity_id = self._resolve(value, "artist")
        artist, _, _ = await self._get_entity(
            "artist",
            entity_id,
            "artistUnion",
            parse_entities.parse_artist_gql,
            parse_entities.parse_artist_embed,
        )
        return artist

    async def get_playlist(self, value: str, *, max_tracks: int | None = 100) -> Playlist:
        """Fetch a playlist by URL, URI, or bare ID, paginating its tracks.

        Args:
            value: A Spotify playlist URL, URI, or 22-character ID.
            max_tracks: Upper bound on tracks to collect; ``None`` fetches all.

        Returns:
            The richest available :class:`Playlist`.

        Raises:
            NotFoundError: If the playlist does not exist.
            SpotifyScraperError: If the client is closed.
        """
        _, entity_id = self._resolve(value, "playlist")
        playlist, session, tier1 = await self._get_entity(
            "playlist",
            entity_id,
            "playlistV2",
            lambda union: parse_entities.parse_playlist_gql(union, max_tracks=max_tracks),
            parse_entities.parse_playlist_embed,
        )
        if not tier1:
            return playlist
        tracks = await self._paginate(
            "playlist",
            entity_id,
            session,
            union_key="playlistV2",
            collected=len(playlist.tracks),
            total=playlist.total_tracks,
            page_size=_PLAYLIST_PAGE,
            max_tracks=max_tracks,
            parse_page=parse_entities.parse_playlist_tracks_page,
        )
        if not tracks:
            return playlist
        return _with_playlist_tracks(playlist, (*playlist.tracks, *tracks))

    async def get_episode(self, value: str) -> Episode:
        """Fetch a podcast episode by URL, URI, or bare ID.

        Args:
            value: A Spotify episode URL, URI, or 22-character ID.

        Returns:
            The richest available :class:`Episode`.

        Raises:
            NotFoundError: If the episode does not exist.
            SpotifyScraperError: If the client is closed.
        """
        _, entity_id = self._resolve(value, "episode")
        episode, _, _ = await self._get_entity(
            "episode",
            entity_id,
            "episodeUnionV2",
            parse_entities.parse_episode_gql,
            parse_entities.parse_episode_embed,
        )
        return episode

    async def get_show(self, value: str, *, max_episodes: int | None = 50) -> Show:
        """Fetch a podcast show by URL, URI, or bare ID, listing its episodes.

        Args:
            value: A Spotify show URL, URI, or 22-character ID.
            max_episodes: Upper bound on episodes to collect; ``None`` fetches
                all of them.

        Returns:
            The richest available :class:`Show`, with ``total_episodes`` and a
            paginated ``episodes`` listing when tier 1 succeeds.

        Raises:
            NotFoundError: If the show does not exist.
            SpotifyScraperError: If the client is closed.
        """
        _, entity_id = self._resolve(value, "show")
        show, session, tier1 = await self._get_entity(
            "show",
            entity_id,
            "podcastUnionV2",
            parse_entities.parse_show_gql,
            parse_entities.parse_show_embed,
        )
        if not tier1:
            return show
        return await self._with_episodes(show, entity_id, session, max_episodes)

    async def _with_episodes(
        self, show: Show, entity_id: str, session: EmbedSession, max_episodes: int | None
    ) -> Show:
        first_limit = (
            _SHOW_EPISODES_PAGE if max_episodes is None else min(max_episodes, _SHOW_EPISODES_PAGE)
        )
        try:
            first = await self._fetch_union(
                "show_episodes",
                entity_id,
                "podcastUnionV2",
                session,
                overrides={"offset": 0, "limit": first_limit},
            )
        except (ParsingError, SpotifyScraperError) as exc:
            _LOGGER.warning("Show episode listing for %s failed: %s", entity_id, exc)
            return show
        total = parse_entities.show_episodes_total(first)
        episodes: list[Episode] = list(parse_entities.parse_show_episodes_page(first))
        episodes.extend(
            await self._paginate(
                "show_episodes",
                entity_id,
                session,
                union_key="podcastUnionV2",
                collected=len(episodes),
                total=total,
                page_size=_SHOW_EPISODES_PAGE,
                max_tracks=max_episodes,
                parse_page=parse_entities.parse_show_episodes_page,
            )
        )
        if max_episodes is not None:
            episodes = episodes[:max_episodes]
        return _with_show_episodes(show, tuple(episodes), total)

    async def aclose(self) -> None:
        """Close the owned transport and mark the client closed."""
        self._closed = True
        if self._owns_transport:
            await self._transport.aclose()

    async def __aenter__(self) -> AsyncSpotifyClient:
        """Return the client for use in an ``async with`` block."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Close the client on exiting an ``async with`` block."""
        await self.aclose()

    def _ensure_open(self) -> None:
        if self._closed:
            raise SpotifyScraperError("AsyncSpotifyClient is closed.")

    def _resolve(self, value: str, kind: urls.EntityType) -> tuple[urls.EntityType, str]:
        self._ensure_open()
        return urls.parse(value, type_hint=kind)

    async def _get_entity(
        self,
        kind: str,
        entity_id: str,
        union_key: str,
        parse_gql: Callable[[Mapping[str, Any]], _T],
        parse_embed_fn: Callable[[Mapping[str, Any]], _T],
        *,
        merge: Callable[[_T, _T], _T] | None = None,
    ) -> tuple[_T, EmbedSession, bool]:
        """Run the embed-first two-tier ladder for one entity.

        Returns the resolved model, the embed session (so callers can paginate
        with the same token), and a flag that is ``True`` when tier 1 succeeded.
        """
        next_data = await self._fetch_next_data(kind, entity_id)
        embed_model = parse_embed_fn(parse_embed.get_entity(next_data))
        session = parse_embed.get_session(next_data)

        try:
            union = await self._fetch_union(kind, entity_id, union_key, session)
            gql_model = parse_gql(union)
        except ParsingError as exc:
            _LOGGER.warning("Tier-1 %s fetch degraded to embed page: %s", kind, exc)
            return embed_model, session, False
        if merge is not None:
            return merge(gql_model, embed_model), session, True
        return gql_model, session, True

    async def _paginate(
        self,
        kind: str,
        entity_id: str,
        session: EmbedSession,
        *,
        union_key: str,
        collected: int,
        total: int | None,
        page_size: int,
        max_tracks: int | None,
        parse_page: Callable[[Mapping[str, Any]], tuple[_T, ...]],
    ) -> tuple[_T, ...]:
        """Fetch follow-up pages after the first tier-1 page.

        A mid-loop page failure logs a warning and returns what was collected
        so far, never losing the already-parsed items.
        """
        extra: list[_T] = []
        offset = collected
        while _wants_more(collected + len(extra), total, max_tracks):
            limit = _next_limit(collected + len(extra), total, max_tracks, page_size)
            if limit <= 0:
                break
            try:
                union = await self._fetch_union(
                    kind,
                    entity_id,
                    union_key,
                    session,
                    overrides={"offset": offset, "limit": limit},
                )
                page = parse_page(union)
            except (ParsingError, SpotifyScraperError) as exc:
                _LOGGER.warning("Pagination for %s stopped early: %s", kind, exc)
                break
            if not page:
                break
            extra.extend(page)
            offset += len(page)
        return tuple(extra)

    async def _fetch_next_data(self, kind: str, entity_id: str) -> dict[str, Any]:
        response: Response = await self._transport.get(urls.embed_url(kind, entity_id))  # type: ignore[arg-type]
        return parse_embed.extract_next_data(response.text)

    async def _fetch_union(
        self,
        kind: str,
        entity_id: str,
        union_key: str,
        session: EmbedSession,
        *,
        overrides: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        try:
            data = await self._pathfinder_request(kind, entity_id, session.access_token, overrides)
        except TokenError:
            self._tokens.invalidate()
            data = await self._pathfinder_request(
                kind, entity_id, await self._tokens.token(), overrides
            )
        union = data.get(union_key)
        if not isinstance(union, Mapping):
            raise ParsingError(
                f"Pathfinder response missing 'data.{union_key}'. "
                "Spotify may have changed its API; check for a library update."
            )
        return union

    async def _pathfinder_request(
        self,
        kind: str,
        entity_id: str,
        token: str,
        overrides: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        url = pathfinder.build_url(kind, entity_id, variable_overrides=overrides)
        response = await self._transport.get(url, headers=pathfinder.auth_headers(token))
        body = _safe_json(response)
        return pathfinder.classify_response(response.status_code, body)


def _with_album_tracks(album: Album, tracks: tuple[Track, ...]) -> Album:
    return Album(
        id=album.id,
        uri=album.uri,
        name=album.name,
        album_type=album.album_type,
        images=album.images,
        release_date=album.release_date,
        artists=album.artists,
        label=album.label,
        total_tracks=album.total_tracks,
        tracks=tracks,
        copyrights=album.copyrights,
        share_url=album.share_url,
    )


def _with_show_episodes(show: Show, episodes: tuple[Episode, ...], total: int | None) -> Show:
    return Show(
        id=show.id,
        uri=show.uri,
        name=show.name,
        description=show.description,
        publisher=show.publisher,
        media_type=show.media_type,
        images=show.images,
        total_episodes=total if total is not None else show.total_episodes,
        episodes=episodes,
        topics=show.topics,
        rating=show.rating,
        share_url=show.share_url,
    )


def _with_playlist_tracks(playlist: Playlist, tracks: tuple[PlaylistTrack, ...]) -> Playlist:
    return Playlist(
        id=playlist.id,
        uri=playlist.uri,
        name=playlist.name,
        description=playlist.description,
        owner=playlist.owner,
        followers=playlist.followers,
        images=playlist.images,
        total_tracks=playlist.total_tracks,
        tracks=tracks,
        share_url=playlist.share_url,
    )


def _wants_more(have: int, total: int | None, max_tracks: int | None) -> bool:
    if max_tracks is not None and have >= max_tracks:
        return False
    if total is None:
        return False
    return have < total


def _next_limit(have: int, total: int | None, max_tracks: int | None, page_size: int) -> int:
    limit = page_size
    if total is not None:
        limit = min(limit, total - have)
    if max_tracks is not None:
        limit = min(limit, max_tracks - have)
    return limit


def _safe_json(response: Response) -> dict[str, Any] | None:
    try:
        body = response.json()
    except ValueError:
        return None
    return body if isinstance(body, dict) else None
