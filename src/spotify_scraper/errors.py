"""Exception hierarchy for SpotifyScraper.

Every error raised by the library derives from :class:`SpotifyScraperError`,
so callers can catch all library failures with a single ``except`` clause.
"""

from __future__ import annotations


class SpotifyScraperError(Exception):
    """Base class for all errors raised by SpotifyScraper."""


class URLError(SpotifyScraperError):
    """Invalid Spotify URL, URI, or ID input."""


class NetworkError(SpotifyScraperError):
    """Transport failure while communicating with Spotify."""

    def __init__(self, message: str, *, request_url: str | None = None) -> None:
        """Initialize with an optional URL of the failed request.

        Args:
            message: Human-readable description of the failure.
            request_url: URL of the request that failed, when known.
        """
        super().__init__(message)
        self.request_url = request_url


class RateLimitedError(NetworkError):
    """Spotify rate-limited the request (HTTP 429)."""

    def __init__(
        self,
        message: str,
        *,
        request_url: str | None = None,
        retry_after: float | None = None,
    ) -> None:
        """Initialize with optional request URL and server-suggested delay.

        Args:
            message: Human-readable description of the failure.
            request_url: URL of the request that failed, when known.
            retry_after: Seconds to wait before retrying, when the server
                provided a ``Retry-After`` hint.
        """
        super().__init__(message, request_url=request_url)
        self.retry_after = retry_after


class TokenError(SpotifyScraperError):
    """Anonymous token bootstrap or refresh failed."""


class AuthenticationError(SpotifyScraperError):
    """Missing or expired user credentials for an authenticated feature."""


class NotFoundError(SpotifyScraperError):
    """Entity does not exist or is not available."""


class ParsingError(SpotifyScraperError):
    """Spotify payload had an unexpected shape.

    Messages raised with this error should advise users to check for a
    library update, since payload changes are usually fixed upstream.
    """


class MediaError(SpotifyScraperError):
    """Media download or tagging failed."""


class SessionError(SpotifyScraperError):
    """A saved session is missing, unreadable, insecurely permissioned, or expired."""
