"""Synchronous Spotify client facade.

This is one of the two thin I/O facades in the library. It owns a
:class:`~spotify_scraper.http.transport.Transport` and an anonymous token
provider, and delegates all parsing to the sans-io helpers in
:mod:`spotify_scraper.api`. The two-tier extraction ladder lives here.
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
from spotify_scraper.auth.anonymous import AnonymousTokenProvider
from spotify_scraper.errors import ParsingError, SpotifyScraperError, TokenError
from spotify_scraper.http.ratelimit import RateLimit
from spotify_scraper.http.retry import RetryPolicy
from spotify_scraper.http.transport import HttpxTransport, Response, Transport
from spotify_scraper.models.track import Track

_LOGGER = logging.getLogger("spotify_scraper")


class SpotifyClient:
    """Synchronous client for extracting public Spotify data.

    The client is a context manager and should be closed when done, either
    via ``with`` or by calling :meth:`close`. Using it after closing raises
    :class:`~spotify_scraper.errors.SpotifyScraperError`.
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
        transport: Transport | None = None,
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
            self._transport: Transport = HttpxTransport(
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
        self._tokens = AnonymousTokenProvider(self._transport)
        self._closed = False

    def get_track(self, value: str) -> Track:
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

        next_data = self._fetch_next_data(entity_id)
        embed_track = parse_entities.parse_track_embed(parse_embed.get_entity(next_data))
        session = parse_embed.get_session(next_data)

        try:
            gql_track = self._fetch_pathfinder_track(entity_id, session)
        except ParsingError as exc:
            _LOGGER.warning("Tier-1 track fetch degraded to embed page: %s", exc)
            return embed_track
        return parse_entities._merge_tracks(gql_track, embed_track)

    def close(self) -> None:
        """Close the owned transport and mark the client closed."""
        self._closed = True
        if self._owns_transport:
            self._transport.close()

    def __enter__(self) -> SpotifyClient:
        """Return the client for use in a ``with`` block."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Close the client on exiting a ``with`` block."""
        self.close()

    def _ensure_open(self) -> None:
        if self._closed:
            raise SpotifyScraperError("SpotifyClient is closed.")

    def _fetch_next_data(self, entity_id: str) -> dict[str, Any]:
        response: Response = self._transport.get(urls.embed_url("track", entity_id))
        return parse_embed.extract_next_data(response.text)

    def _fetch_pathfinder_track(self, entity_id: str, session: EmbedSession) -> Track:
        try:
            data = self._pathfinder_request(entity_id, session.access_token)
        except TokenError:
            self._tokens.invalidate()
            data = self._pathfinder_request(entity_id, self._tokens.token())
        union = data.get("trackUnion")
        if not isinstance(union, Mapping):
            raise ParsingError(
                "Pathfinder response missing 'data.trackUnion'. "
                "Spotify may have changed its API; check for a library update."
            )
        return parse_entities.parse_track_gql(union)

    def _pathfinder_request(self, entity_id: str, token: str) -> dict[str, Any]:
        url = pathfinder.build_url("track", entity_id)
        response = self._transport.get(url, headers=pathfinder.auth_headers(token))
        body = _safe_json(response)
        return pathfinder.classify_response(response.status_code, body)


def _safe_json(response: Response) -> dict[str, Any] | None:
    try:
        body = response.json()
    except ValueError:
        return None
    return body if isinstance(body, dict) else None
