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

from spotify_scraper import media, urls
from spotify_scraper.api import account as account_api
from spotify_scraper.api import lyrics as lyrics_api
from spotify_scraper.api import parse_embed, parse_entities, pathfinder
from spotify_scraper.api import transcripts as transcripts_api
from spotify_scraper.api.parse_embed import EmbedSession
from spotify_scraper.auth.anonymous import AsyncAnonymousTokenProvider
from spotify_scraper.auth.cookies import AsyncCookieTokenProvider, load_sp_dc
from spotify_scraper.auth.session import SessionInfo, SessionStore
from spotify_scraper.errors import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    ParsingError,
    SpotifyScraperError,
    TokenError,
)
from spotify_scraper.http.ratelimit import RateLimit
from spotify_scraper.http.retry import RetryPolicy
from spotify_scraper.http.transport import AsyncHttpxTransport, AsyncTransport, Response
from spotify_scraper.models.account import Account
from spotify_scraper.models.album import Album
from spotify_scraper.models.artist import Artist
from spotify_scraper.models.episode import Episode
from spotify_scraper.models.lyrics import Lyrics
from spotify_scraper.models.playlist import Playlist, PlaylistTrack
from spotify_scraper.models.show import Show
from spotify_scraper.models.track import Track
from spotify_scraper.models.transcript import Transcript

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

    __slots__ = (
        "_closed",
        "_cookie_tokens",
        "_cookies",
        "_owns_transport",
        "_tokens",
        "_transport",
    )

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
        self._cookie_tokens: AsyncCookieTokenProvider | None = None
        self._closed = False

    async def login(
        self,
        *,
        reuse: bool = True,
        save: bool = True,
        store: str = "file",
        timeout: float = 300.0,
        proxy: str | None = None,
        session_path: Path | None = None,
    ) -> None:
        """Authenticate, reusing a valid saved session or capturing a new one.

        When ``reuse`` is set (the default) and a valid saved session exists,
        its cookie is loaded and wired into this client WITHOUT opening the
        browser — the Playwright import is skipped entirely, so reusing a
        session never needs the ``browser`` extra. Otherwise a real Chromium
        window opens; the user signs into Spotify by hand, the captured cookie
        is wired in, and when ``save`` is set it is persisted for later reuse.

        Validity is checked locally (the saved file exists, is securely
        permissioned, parses, and is not past its known expiry), so a cookie
        Spotify has since revoked is still reused; the first authenticated call
        then surfaces :class:`AuthenticationError` per the existing 401 contract.

        The captured/loaded cookie resets the cached cookie-token provider so
        the next authenticated call re-exchanges. This method performs no HTTP
        request itself.

        Args:
            reuse: Skip the browser and load a valid saved session when present.
            save: Persist a freshly captured cookie to ``session_path``.
            store: Session backend, ``"file"`` (default) or ``"keyring"``.
            timeout: Seconds to wait for the manual login to yield a cookie.
            proxy: Optional proxy URL for the login browser. Neither client
                retains the constructor proxy, so pass it explicitly here.
            session_path: Override for where the session is saved/loaded.

        Raises:
            AuthenticationError: If no cookie is captured before the timeout.
            ImportError: If the ``browser`` extra is not installed (capture path).
            SpotifyScraperError: If the client is closed.
        """
        self._ensure_open()
        backend = SessionStore(store)
        if reuse and backend.has_session(path=session_path):
            session = backend.load(path=session_path)
            self._cookies = session.sp_dc
            self._cookie_tokens = None
            return
        from spotify_scraper.browser import capture_sp_dc_async

        sp_dc = await capture_sp_dc_async(timeout=timeout, proxy=proxy)
        self._cookies = sp_dc
        self._cookie_tokens = None
        if save:
            backend.save(sp_dc, path=session_path)

    @classmethod
    def from_saved_session(
        cls,
        *,
        store: str = "file",
        session_path: Path | None = None,
        **kwargs: Any,
    ) -> AsyncSpotifyClient:
        """Build a client from a previously saved session, no browser required.

        This is a synchronous classmethod: it only reads a file, so no event
        loop is needed.

        Args:
            store: Session backend, ``"file"`` (default) or ``"keyring"``.
            session_path: Override for the session file to load.
            **kwargs: Forwarded to :class:`AsyncSpotifyClient` (e.g.
                ``rate_limit``, ``retry``, ``proxy``, ``timeout``, ``transport``).

        Returns:
            A client wired with the saved ``sp_dc`` cookie.

        Raises:
            SessionError: If no usable saved session exists.
        """
        session = SessionStore(store).load(path=session_path)
        return cls(cookies=session.sp_dc, **kwargs)

    @classmethod
    def logout(cls, *, store: str = "file", session_path: Path | None = None) -> None:
        """Remove the saved session for local revocation; idempotent.

        Args:
            store: Session backend, ``"file"`` (default) or ``"keyring"``.
            session_path: Override for the session file to clear.
        """
        SessionStore(store).clear(path=session_path)

    @classmethod
    def session_info(cls, *, store: str = "file", session_path: Path | None = None) -> SessionInfo:
        """Report the saved session's status WITHOUT exposing the cookie.

        This is a synchronous classmethod: it only reads a file, so no event
        loop is needed.

        Args:
            store: Session backend, ``"file"`` (default) or ``"keyring"``.
            session_path: Override for the session file to inspect.

        Returns:
            A cookie-free :class:`SessionInfo` (``exists`` / ``valid`` / expiry);
            never raises for a missing, corrupt, insecure, or expired session.
        """
        return SessionStore(store).info(path=session_path)

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
        model, _, _, _ = await self._get_entity(
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
        album, session, tier1, union = await self._get_entity(
            "album",
            entity_id,
            "albumUnion",
            parse_entities.parse_album_gql,
            parse_entities.parse_album_embed,
        )
        if not tier1 or union is None:
            return album
        tracks = await self._paginate(
            "album",
            entity_id,
            session,
            union_key="albumUnion",
            container_key="tracksV2",
            raw_offset=_raw_item_count(union, "tracksV2"),
            filtered_have=len(album.tracks),
            total_raw=album.total_tracks,
            page_size=_ALBUM_PAGE,
            max_items=None,
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
        artist, _, _, _ = await self._get_entity(
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
        playlist, session, tier1, union = await self._get_entity(
            "playlist",
            entity_id,
            "playlistV2",
            lambda union: parse_entities.parse_playlist_gql(union, max_tracks=max_tracks),
            parse_entities.parse_playlist_embed,
        )
        if not tier1 or union is None:
            return playlist
        tracks = await self._paginate(
            "playlist",
            entity_id,
            session,
            union_key="playlistV2",
            container_key="content",
            raw_offset=_raw_item_count(union, "content"),
            filtered_have=len(playlist.tracks),
            total_raw=playlist.total_tracks,
            page_size=_PLAYLIST_PAGE,
            max_items=max_tracks,
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
        episode, _, _, _ = await self._get_entity(
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
        show, session, tier1, _ = await self._get_entity(
            "show",
            entity_id,
            "podcastUnionV2",
            parse_entities.parse_show_gql,
            parse_entities.parse_show_embed,
        )
        if not tier1:
            return show
        return await self._with_episodes(show, entity_id, session, max_episodes)

    async def get_lyrics(self, value: str) -> Lyrics:
        """Fetch a track's lyrics using the cookie-derived web-player token.

        Lyrics are an authenticated feature: the client must have been built
        with ``cookies=``. A client without cookies raises
        :class:`AuthenticationError` immediately, without any HTTP request.

        Args:
            value: A Spotify track URL, URI, or 22-character ID.

        Returns:
            The track's :class:`Lyrics` (synced when Spotify provides offsets).

        Raises:
            AuthenticationError: If no cookies were configured, or the cookie
                is rejected by the token exchange.
            NotFoundError: If the track exists but has no lyrics.
            SpotifyScraperError: If the client is closed.
        """
        _, entity_id = self._resolve(value, "track")
        provider = self._cookie_provider()
        token = await provider.token()
        try:
            return await self._fetch_lyrics(entity_id, token)
        except AuthenticationError:
            provider.invalidate()
            return await self._fetch_lyrics(entity_id, await provider.token())

    async def get_transcript(self, value: str) -> Transcript:
        """Fetch an episode's transcript using the cookie-derived token.

        Transcripts are an authenticated feature: the client must have been
        built with ``cookies=``. A client without cookies raises
        :class:`AuthenticationError` immediately, without any HTTP request.

        Args:
            value: A Spotify episode URL, URI, or 22-character ID.

        Returns:
            The episode's :class:`Transcript` with millisecond-offset lines.

        Raises:
            AuthenticationError: If no cookies were configured, or the cookie
                is rejected by the token exchange.
            NotFoundError: If the episode exists but has no transcript.
            SpotifyScraperError: If the client is closed.
        """
        _, entity_id = self._resolve(value, "episode")
        provider = self._cookie_provider()
        token = await provider.token()
        try:
            return await self._fetch_transcript(entity_id, token)
        except AuthenticationError:
            provider.invalidate()
            return await self._fetch_transcript(entity_id, await provider.token())

    async def get_account(self) -> Account:
        """Fetch the logged-in account's product state (Premium, country, …).

        This is an authenticated feature: the client must have been built with
        ``cookies=``. A client without cookies raises :class:`AuthenticationError`
        immediately, without any HTTP request. It takes no entity argument — the
        product-state body is a flat per-account object.

        Returns:
            The :class:`Account` parsed from Spotify's product-state endpoint.

        Raises:
            AuthenticationError: If no cookies were configured, or the cookie is
                rejected by the token exchange.
            ParsingError: If the product-state response is not JSON.
            SpotifyScraperError: If the client is closed.
        """
        provider = self._cookie_provider()
        token = await provider.token()
        try:
            return await self._fetch_account(token)
        except AuthenticationError:
            provider.invalidate()
            return await self._fetch_account(await provider.token())

    async def is_premium(self) -> bool:
        """Return ``True`` when the logged-in account is Premium.

        Convenience for ``(await get_account()).is_premium``; same auth needs.
        """
        return (await self.get_account()).is_premium

    def _cookie_provider(self) -> AsyncCookieTokenProvider:
        self._ensure_open()
        provider = self._cookie_tokens
        if provider is None:
            if self._cookies is None:
                raise AuthenticationError(
                    "This feature requires authentication; build AsyncSpotifyClient(cookies=...) "
                    "with an 'sp_dc' cookie."
                )
            provider = AsyncCookieTokenProvider(self._transport, load_sp_dc(self._cookies))
            self._cookie_tokens = provider
        return provider

    async def _fetch_lyrics(self, entity_id: str, token: str) -> Lyrics:
        url = lyrics_api.lyrics_url(entity_id)
        try:
            response = await self._transport.get(url, headers=lyrics_api.auth_headers(token))
        except NotFoundError as exc:
            raise NotFoundError(f"No lyrics for track {entity_id}.") from exc
        if response.status_code == 401:
            raise AuthenticationError("Spotify rejected the cookie token for lyrics (HTTP 401).")
        body = _safe_json(response)
        if body is None:
            raise ParsingError(
                "Lyrics response was not JSON. Spotify may have changed its API; "
                "check for a library update."
            )
        return parse_entities.parse_lyrics(body)

    async def _fetch_transcript(self, entity_id: str, token: str) -> Transcript:
        url = transcripts_api.transcript_url(entity_id)
        try:
            response = await self._transport.get(url, headers=transcripts_api.auth_headers(token))
        except NotFoundError as exc:
            raise NotFoundError(f"No transcript for episode {entity_id}.") from exc
        if response.status_code == 401:
            raise AuthenticationError(
                "Spotify rejected the cookie token for transcripts (HTTP 401)."
            )
        body = _safe_json(response)
        if body is None:
            raise ParsingError(
                "Transcript response was not JSON. Spotify may have changed its API; "
                "check for a library update."
            )
        return parse_entities.parse_transcript(transcripts_api.decode_envelope(body))

    async def _fetch_account(self, token: str) -> Account:
        response = await self._transport.get(
            account_api.product_state_url(), headers=account_api.auth_headers(token)
        )
        if response.status_code == 401:
            raise AuthenticationError(
                "Spotify rejected the cookie token for product-state (HTTP 401)."
            )
        body = _safe_json(response)
        if body is None:
            raise ParsingError(
                "Product-state response was not JSON. Spotify may have changed its API; "
                "check for a library update."
            )
        return parse_entities.parse_account(body)

    async def download_cover(
        self,
        entity: media.HasImagesAndName,
        dest: str | Path = ".",
        *,
        size: media.ImageSize = "largest",
        filename: str | None = None,
    ) -> Path:
        """Download an entity's cover art to ``dest`` and return its path.

        Args:
            entity: Any fetched model carrying ``name`` and ``images`` (a
                :class:`Track` falls back to its album's images when empty).
            dest: Destination directory; created if it does not exist.
            size: ``"largest"`` or ``"smallest"`` of the available images.
            filename: Explicit filename; defaults to a sanitized
                ``<name>.<ext>`` (extension from the response content type).

        Returns:
            The path of the written image.

        Raises:
            MediaError: If the entity has no images.
            SpotifyScraperError: If the client is closed.
        """
        self._ensure_open()
        return await media.download_cover_async(
            self._transport, entity, Path(dest), size=size, filename=filename
        )

    async def download_preview(
        self,
        entity: Track | Episode,
        dest: str | Path = ".",
        *,
        filename: str | None = None,
        embed_cover: bool = False,
    ) -> Path:
        """Download a track or episode preview MP3 and return its path.

        Args:
            entity: A :class:`Track` or :class:`Episode` with a ``preview_url``.
            dest: Destination directory; created if it does not exist.
            filename: Explicit filename; defaults to a sanitized ``<name>.mp3``.
            embed_cover: When ``True``, embed the entity's cover art and basic
                tags via mutagen (the ``media`` extra).

        Returns:
            The path of the written MP3.

        Raises:
            MediaError: If no preview exists, or ``embed_cover`` is requested
                without mutagen installed.
            SpotifyScraperError: If the client is closed.
        """
        self._ensure_open()
        return await media.download_preview_async(
            self._transport, entity, Path(dest), filename=filename, embed_cover=embed_cover
        )

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
                container_key="episodesV2",
                raw_offset=_raw_item_count(first, "episodesV2"),
                filtered_have=len(episodes),
                total_raw=total,
                page_size=_SHOW_EPISODES_PAGE,
                max_items=max_episodes,
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
    ) -> tuple[_T, EmbedSession, bool, Mapping[str, Any] | None]:
        """Run the embed-first two-tier ladder for one entity.

        Returns the resolved model, the embed session (so callers can paginate
        with the same token), a flag that is ``True`` when tier 1 succeeded, and
        the raw tier-1 union (so paginating callers can count raw items) or
        ``None`` when degraded.
        """
        next_data = await self._fetch_next_data(kind, entity_id)
        embed_model = parse_embed_fn(parse_embed.get_entity(next_data))
        session = parse_embed.get_session(next_data)

        try:
            union = await self._fetch_union(kind, entity_id, union_key, session)
            gql_model = parse_gql(union)
        except (ParsingError, NetworkError) as exc:
            _LOGGER.warning("Tier-1 %s fetch degraded to embed page: %s", kind, exc)
            return embed_model, session, False, None
        if merge is not None:
            return merge(gql_model, embed_model), session, True, union
        return gql_model, session, True, union

    async def _paginate(
        self,
        kind: str,
        entity_id: str,
        session: EmbedSession,
        *,
        union_key: str,
        container_key: str,
        raw_offset: int,
        filtered_have: int,
        total_raw: int | None,
        page_size: int,
        max_items: int | None,
        parse_page: Callable[[Mapping[str, Any]], tuple[_T, ...]],
    ) -> tuple[_T, ...]:
        """Fetch follow-up pages after the first tier-1 page.

        The cursor advances by the number of RAW items each page consumed (not
        the number kept after filtering non-Track / unavailable items), because
        Spotify's ``offset`` indexes the raw items array and ``totalCount``
        counts all items. ``max_items`` bounds the kept results. A mid-loop page
        failure logs a warning and returns what was collected so far.
        """
        extra: list[_T] = []
        offset = raw_offset
        while True:
            if max_items is not None and filtered_have + len(extra) >= max_items:
                break
            if total_raw is not None and offset >= total_raw:
                break
            try:
                union = await self._fetch_union(
                    kind,
                    entity_id,
                    union_key,
                    session,
                    overrides={"offset": offset, "limit": page_size},
                )
                page = parse_page(union)
            except (ParsingError, SpotifyScraperError) as exc:
                _LOGGER.warning("Pagination for %s stopped early: %s", kind, exc)
                break
            raw_count = _raw_item_count(union, container_key)
            if raw_count == 0:
                break
            extra.extend(page)
            offset += raw_count
        if max_items is not None:
            return tuple(extra[: max(0, max_items - filtered_have)])
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


def _raw_item_count(union: Mapping[str, Any], container_key: str) -> int:
    """Count the raw items in a paginated union page (all item types)."""
    container = union.get(container_key)
    if isinstance(container, Mapping):
        items = container.get("items")
        if isinstance(items, list):
            return len(items)
    return 0


def _safe_json(response: Response) -> dict[str, Any] | None:
    try:
        body = response.json()
    except ValueError:
        return None
    return body if isinstance(body, dict) else None
