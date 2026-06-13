"""Cookie ingestion and the ``sp_dc`` → web-player token exchange.

Spotify's authenticated web-player endpoints (e.g. color-lyrics) require a
short-lived access token derived from a logged-in ``sp_dc`` cookie via a TOTP
handshake against ``/api/token``. :func:`load_sp_dc` normalizes the several
ways a caller may supply that cookie; :class:`CookieTokenProvider` (and its
async twin) performs the exchange, caches the token until just before expiry,
and re-exchanges on demand. Cookie and token values never reach ``repr`` output
or error messages.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from spotify_scraper.auth.totp import TOTP_SECRETS, generate
from spotify_scraper.errors import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    ParsingError,
)
from spotify_scraper.http.transport import AsyncTransport, Transport

SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
TOKEN_URL = "https://open.spotify.com/api/token"  # noqa: S105 — an endpoint URL, not a secret

#: A token is refreshed once it is within this many milliseconds of expiry.
EXPIRY_SKEW_MS = 60_000

_RENEW_HINT = "Log into open.spotify.com in a browser and re-export a fresh 'sp_dc' cookie."
_ROTATE_HINT = (
    "Spotify rotated its token secret; update SpotifyScraper or refresh "
    "TOTP_SECRETS from the current web-player bundle."
)


def load_sp_dc(source: str | Path | Mapping[str, str]) -> str:
    """Extract a raw ``sp_dc`` cookie value from a flexible source.

    Args:
        source: One of a raw ``sp_dc`` string, a mapping containing an
            ``sp_dc`` key, or a path to a Netscape-format ``cookies.txt``
            export (``#HttpOnly_`` line prefixes are tolerated).

    Returns:
        The bare ``sp_dc`` cookie value.

    Raises:
        AuthenticationError: If no ``sp_dc`` cookie can be found.
    """
    if isinstance(source, Mapping):
        value = source.get("sp_dc")
        if isinstance(value, str) and value:
            return value
        raise AuthenticationError(f"No 'sp_dc' cookie in the supplied mapping. {_RENEW_HINT}")
    if isinstance(source, Path):
        return _load_from_cookie_file(source)
    text = source.strip()
    if not text:
        raise AuthenticationError(f"Empty 'sp_dc' cookie supplied. {_RENEW_HINT}")
    candidate = Path(text)
    if "\t" not in text and "\n" not in text and candidate.is_file():
        return _load_from_cookie_file(candidate)
    return text


def _load_from_cookie_file(path: Path) -> str:
    """Parse an ``sp_dc`` value out of a Netscape ``cookies.txt`` file."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise AuthenticationError(f"Could not read cookies file {path}. {_RENEW_HINT}") from exc
    for raw in lines:
        line = raw.removeprefix("#HttpOnly_") if raw.startswith("#HttpOnly_") else raw
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) >= 7 and fields[5] == "sp_dc" and fields[6]:
            return fields[6]
    raise AuthenticationError(f"No 'sp_dc' cookie in {path}. {_RENEW_HINT}")


def _default_now_ms() -> int:
    return time.time_ns() // 1_000_000


def _cookie_header(sp_dc: str) -> dict[str, str]:
    return {"Cookie": f"sp_dc={sp_dc}"}


def _token_url(secret: str, now_s: int, server_time_s: int, version: int) -> str:
    params = (
        "reason=init"
        "&productType=web-player"
        f"&totp={generate(secret, now_s)}"
        f"&totpServer={generate(secret, server_time_s)}"
        f"&totpVer={version}"
    )
    return f"{TOKEN_URL}?{params}"


def _server_time_s(body: Any) -> int:
    if isinstance(body, Mapping):
        value = body.get("serverTime")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return int(value)
    raise ParsingError(
        "Spotify server-time response had an unexpected shape; check for a library update."
    )


class _Cached:
    """An exchanged access token and its expiry, kept off ``repr`` output."""

    __slots__ = ("expires_at_ms", "token")

    def __init__(self, token: str, expires_at_ms: int) -> None:
        self.token = token
        self.expires_at_ms = expires_at_ms


def _is_anonymous(body: Mapping[str, Any]) -> bool:
    return bool(body.get("isAnonymous", True))


def _is_totp_expired(body: Mapping[str, Any]) -> bool:
    error = body.get("error")
    if isinstance(error, str) and error == "totpVerExpired":
        return True
    return body.get("totpVerExpired") is True


def _parse_token(body: Mapping[str, Any]) -> _Cached | None:
    """Build a :class:`_Cached` from a successful token body, else ``None``."""
    token = body.get("accessToken")
    expires = body.get("accessTokenExpirationTimestampMs")
    if not isinstance(token, str) or not token:
        return None
    if isinstance(expires, bool) or not isinstance(expires, int):
        return None
    return _Cached(token, expires)


class CookieTokenProvider:
    """Synchronous ``sp_dc`` → web-player access-token provider."""

    __slots__ = ("_cached", "_cookie", "_now_ms", "_transport")

    def __init__(
        self,
        transport: Transport,
        sp_dc: str,
        *,
        now_ms: Callable[[], int] = _default_now_ms,
    ) -> None:
        """Initialize the provider.

        Args:
            transport: Transport used for the server-time and token requests.
            sp_dc: A raw ``sp_dc`` cookie value (see :func:`load_sp_dc`).
            now_ms: Injectable clock returning Unix time in milliseconds.
        """
        self._transport = transport
        self._cookie = sp_dc
        self._now_ms = now_ms
        self._cached: _Cached | None = None

    def token(self) -> str:
        """Return a valid web-player access token, exchanging when stale.

        Returns:
            A non-empty bearer token.

        Raises:
            AuthenticationError: If the cookie is rejected or every TOTP
                version has been retired.
        """
        cached = self._cached
        now = self._now_ms()
        if cached is not None and now < cached.expires_at_ms - EXPIRY_SKEW_MS:
            return cached.token
        cached = self._exchange()
        self._cached = cached
        return cached.token

    def invalidate(self) -> None:
        """Drop the cached token so the next :meth:`token` call re-exchanges."""
        self._cached = None

    def _exchange(self) -> _Cached:
        try:
            server_response = self._transport.get(
                SERVER_TIME_URL, headers=_cookie_header(self._cookie)
            )
            server_time_s = _server_time_s(server_response.json())
            now_s = self._now_ms() // 1000
            seen_totp_expired = False
            for version, secret in TOTP_SECRETS:
                url = _token_url(secret, now_s, server_time_s, version)
                body = self._transport.get(url, headers=_cookie_header(self._cookie)).json()
                outcome = _classify(body)
                if outcome is _TOTP_EXPIRED:
                    seen_totp_expired = True
                    continue
                return outcome
        except (NetworkError, NotFoundError, ParsingError, ValueError) as exc:
            raise AuthenticationError(f"Cookie token exchange failed. {_RENEW_HINT}") from exc
        if seen_totp_expired:
            raise AuthenticationError(_ROTATE_HINT)
        raise AuthenticationError(f"Spotify rejected the 'sp_dc' cookie. {_RENEW_HINT}")

    def __repr__(self) -> str:
        """Return a credential-free representation."""
        return f"{type(self).__name__}(cached={self._cached is not None})"


class AsyncCookieTokenProvider:
    """Asynchronous ``sp_dc`` → web-player access-token provider."""

    __slots__ = ("_cached", "_cookie", "_now_ms", "_transport")

    def __init__(
        self,
        transport: AsyncTransport,
        sp_dc: str,
        *,
        now_ms: Callable[[], int] = _default_now_ms,
    ) -> None:
        """Initialize the provider.

        Args:
            transport: Transport used for the server-time and token requests.
            sp_dc: A raw ``sp_dc`` cookie value (see :func:`load_sp_dc`).
            now_ms: Injectable clock returning Unix time in milliseconds.
        """
        self._transport = transport
        self._cookie = sp_dc
        self._now_ms = now_ms
        self._cached: _Cached | None = None

    async def token(self) -> str:
        """Return a valid web-player access token, exchanging when stale.

        Returns:
            A non-empty bearer token.

        Raises:
            AuthenticationError: If the cookie is rejected or every TOTP
                version has been retired.
        """
        cached = self._cached
        now = self._now_ms()
        if cached is not None and now < cached.expires_at_ms - EXPIRY_SKEW_MS:
            return cached.token
        cached = await self._exchange()
        self._cached = cached
        return cached.token

    def invalidate(self) -> None:
        """Drop the cached token so the next :meth:`token` call re-exchanges."""
        self._cached = None

    async def _exchange(self) -> _Cached:
        try:
            server_response = await self._transport.get(
                SERVER_TIME_URL, headers=_cookie_header(self._cookie)
            )
            server_time_s = _server_time_s(server_response.json())
            now_s = self._now_ms() // 1000
            seen_totp_expired = False
            for version, secret in TOTP_SECRETS:
                url = _token_url(secret, now_s, server_time_s, version)
                response = await self._transport.get(url, headers=_cookie_header(self._cookie))
                outcome = _classify(response.json())
                if outcome is _TOTP_EXPIRED:
                    seen_totp_expired = True
                    continue
                return outcome
        except (NetworkError, NotFoundError, ParsingError, ValueError) as exc:
            raise AuthenticationError(f"Cookie token exchange failed. {_RENEW_HINT}") from exc
        if seen_totp_expired:
            raise AuthenticationError(_ROTATE_HINT)
        raise AuthenticationError(f"Spotify rejected the 'sp_dc' cookie. {_RENEW_HINT}")

    def __repr__(self) -> str:
        """Return a credential-free representation."""
        return f"{type(self).__name__}(cached={self._cached is not None})"


#: Sentinel marking a ``totpVerExpired`` response, distinct from a real token.
_TOTP_EXPIRED = _Cached("", 0)


def _classify(body: Any) -> _Cached:
    """Map a token-endpoint body to a cached token or the expired sentinel.

    Raises:
        AuthenticationError: When the cookie is anonymous or the body is
            otherwise unusable for a non-version reason.
    """
    if not isinstance(body, Mapping):
        raise AuthenticationError(f"Spotify rejected the 'sp_dc' cookie. {_RENEW_HINT}")
    if _is_totp_expired(body):
        return _TOTP_EXPIRED
    if _is_anonymous(body):
        raise AuthenticationError(f"Spotify rejected the 'sp_dc' cookie. {_RENEW_HINT}")
    cached = _parse_token(body)
    if cached is None:
        raise AuthenticationError(f"Spotify rejected the 'sp_dc' cookie. {_RENEW_HINT}")
    return cached
