"""Asynchronous Spotify client facade.

A 1:1 mirror of :mod:`spotify_scraper._sync.client` over the async transport
and async token provider. All parsing is delegated to the same sans-io
helpers, so the two facades stay thin and behaviourally identical.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from pathlib import Path
from types import TracebackType
from typing import Any

from spotify_scraper import urls
from spotify_scraper.api import parse_embed, parse_entities, pathfinder
from spotify_scraper.api.parse_embed import EmbedSession
from spotify_scraper.auth.anonymous import AsyncAnonymousTokenProvider
from spotify_scraper.errors import ParsingError, SpotifyScraperError, TokenError
from spotify_scraper.http.ratelimit import RateLimit
from spotify_scraper.http.retry import RetryPolicy
from spotify_scraper.http.transport import AsyncHttpxTransport, AsyncTransport, Response
from spotify_scraper.models.track import Track

_LOGGER = logging.getLogger("spotify_scraper")


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
    ) -> None:
        """Initialize the client.

        Args:
            rate_limit: Token-bucket configuration; defaults to safe limits.
            retry: Retry policy; defaults to :class:`RetryPolicy`.
            proxy: Optional proxy URL for the default transport.
            user_agent: Fixed User-Agent for the default transport.
            timeout: Per-request timeout in seconds for the default transport.
            transport: A custom transport that overrides every other HTTP
                option; the client does not own its lifecycle.
            cookies: User cookies for authenticated features; accepted and
                stored now, consumed by the lyrics extraction change.
        """
        if transport is None:
            self._transport: AsyncTransport = AsyncHttpxTransport(
                rate_limit=rate_limit,
                retry=retry,
                user_agent=user_agent,
                proxy=proxy,
                timeout=timeout,
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
        self._ensure_open()
        _, entity_id = urls.parse(value, type_hint="track")

        next_data = await self._fetch_next_data(entity_id)
        embed_track = parse_entities.parse_track_embed(parse_embed.get_entity(next_data))
        session = parse_embed.get_session(next_data)

        try:
            gql_track = await self._fetch_pathfinder_track(entity_id, session)
        except ParsingError as exc:
            _LOGGER.warning("Tier-1 track fetch degraded to embed page: %s", exc)
            return embed_track
        return parse_entities._merge_tracks(gql_track, embed_track)

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

    async def _fetch_next_data(self, entity_id: str) -> dict[str, Any]:
        response: Response = await self._transport.get(urls.embed_url("track", entity_id))
        return parse_embed.extract_next_data(response.text)

    async def _fetch_pathfinder_track(self, entity_id: str, session: EmbedSession) -> Track:
        try:
            data = await self._pathfinder_request(entity_id, session.access_token)
        except TokenError:
            self._tokens.invalidate()
            data = await self._pathfinder_request(entity_id, await self._tokens.token())
        union = data.get("trackUnion")
        if not isinstance(union, Mapping):
            raise ParsingError(
                "Pathfinder response missing 'data.trackUnion'. "
                "Spotify may have changed its API; check for a library update."
            )
        return parse_entities.parse_track_gql(union)

    async def _pathfinder_request(self, entity_id: str, token: str) -> dict[str, Any]:
        url = pathfinder.build_url("track", entity_id)
        response = await self._transport.get(url, headers=pathfinder.auth_headers(token))
        body = _safe_json(response)
        return pathfinder.classify_response(response.status_code, body)


def _safe_json(response: Response) -> dict[str, Any] | None:
    try:
        body = response.json()
    except ValueError:
        return None
    return body if isinstance(body, dict) else None
