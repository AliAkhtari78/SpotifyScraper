"""Anonymous bearer-token providers bootstrapped from embed pages.

A Spotify embed page exposes a short-lived anonymous access token in its
``__NEXT_DATA__`` payload. These providers fetch that token, cache it until it
nears expiry, and re-bootstrap on demand. Tokens are never written to ``repr``
output or error messages.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from spotify_scraper.api.parse_embed import EmbedSession, extract_next_data, get_session
from spotify_scraper.errors import NetworkError, ParsingError, TokenError
from spotify_scraper.http.transport import AsyncTransport, Transport
from spotify_scraper.urls import embed_url

DEFAULT_BOOTSTRAP_ID = "4uLU6hMCjMI75M1A2tKUQC"
EXPIRY_SKEW_MS = 60_000


def is_stale(expires_at_ms: int, now_ms: int) -> bool:
    """Return whether a token expiring at ``expires_at_ms`` is stale at ``now_ms``.

    A token is stale once it is within :data:`EXPIRY_SKEW_MS` of its expiry, so
    it is refreshed before it can lapse mid-request.

    Args:
        expires_at_ms: Token expiry as a Unix timestamp in milliseconds.
        now_ms: Current time as a Unix timestamp in milliseconds.

    Returns:
        ``True`` if the token should be refreshed.
    """
    return now_ms >= expires_at_ms - EXPIRY_SKEW_MS


def _default_now_ms() -> int:
    return time.time_ns() // 1_000_000


class AnonymousTokenProvider:
    """Synchronous anonymous token provider over a :class:`Transport`."""

    __slots__ = ("_bootstrap_url", "_now_ms", "_session", "_transport")

    def __init__(
        self,
        transport: Transport,
        *,
        bootstrap_track_id: str = DEFAULT_BOOTSTRAP_ID,
        now_ms: Callable[[], int] = _default_now_ms,
    ) -> None:
        """Initialize the provider.

        Args:
            transport: Transport used to fetch the bootstrap embed page.
            bootstrap_track_id: Public track ID whose embed page seeds the
                token; any public track works.
            now_ms: Injectable clock returning the current Unix time in
                milliseconds, for testing.
        """
        self._transport = transport
        self._bootstrap_url = embed_url("track", bootstrap_track_id)
        self._now_ms = now_ms
        self._session: EmbedSession | None = None

    def token(self) -> str:
        """Return a valid anonymous bearer token, bootstrapping when stale.

        Returns:
            A non-empty bearer token.

        Raises:
            TokenError: If the bootstrap embed page cannot be fetched or its
                payload lacks a session token.
        """
        session = self._session
        if session is None or is_stale(session.expires_at_ms, self._now_ms()):
            session = self._bootstrap()
            self._session = session
        return session.access_token

    def invalidate(self) -> None:
        """Drop the cached token so the next :meth:`token` call re-bootstraps."""
        self._session = None

    def _bootstrap(self) -> EmbedSession:
        try:
            response = self._transport.get(self._bootstrap_url)
            return get_session(extract_next_data(response.text))
        except (NetworkError, ParsingError) as exc:
            raise TokenError("Failed to bootstrap an anonymous token from the embed page.") from exc

    def __repr__(self) -> str:
        """Return a token-free representation."""
        return f"{type(self).__name__}(cached={self._session is not None})"


class AsyncAnonymousTokenProvider:
    """Asynchronous anonymous token provider over an :class:`AsyncTransport`."""

    __slots__ = ("_bootstrap_url", "_now_ms", "_session", "_transport")

    def __init__(
        self,
        transport: AsyncTransport,
        *,
        bootstrap_track_id: str = DEFAULT_BOOTSTRAP_ID,
        now_ms: Callable[[], int] = _default_now_ms,
    ) -> None:
        """Initialize the provider.

        Args:
            transport: Transport used to fetch the bootstrap embed page.
            bootstrap_track_id: Public track ID whose embed page seeds the
                token; any public track works.
            now_ms: Injectable clock returning the current Unix time in
                milliseconds, for testing.
        """
        self._transport = transport
        self._bootstrap_url = embed_url("track", bootstrap_track_id)
        self._now_ms = now_ms
        self._session: EmbedSession | None = None

    async def token(self) -> str:
        """Return a valid anonymous bearer token, bootstrapping when stale.

        Returns:
            A non-empty bearer token.

        Raises:
            TokenError: If the bootstrap embed page cannot be fetched or its
                payload lacks a session token.
        """
        session = self._session
        if session is None or is_stale(session.expires_at_ms, self._now_ms()):
            session = await self._bootstrap()
            self._session = session
        return session.access_token

    def invalidate(self) -> None:
        """Drop the cached token so the next :meth:`token` call re-bootstraps."""
        self._session = None

    async def _bootstrap(self) -> EmbedSession:
        try:
            response = await self._transport.get(self._bootstrap_url)
            return get_session(extract_next_data(response.text))
        except (NetworkError, ParsingError) as exc:
            raise TokenError("Failed to bootstrap an anonymous token from the embed page.") from exc

    def __repr__(self) -> str:
        """Return a token-free representation."""
        return f"{type(self).__name__}(cached={self._session is not None})"
