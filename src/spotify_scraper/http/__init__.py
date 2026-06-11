"""HTTP layer: transport protocols, httpx implementations, retry, rate limiting."""

from __future__ import annotations

from spotify_scraper.http.ratelimit import RateLimit
from spotify_scraper.http.retry import RetryPolicy
from spotify_scraper.http.transport import (
    AsyncHttpxTransport,
    AsyncTransport,
    HttpxTransport,
    Response,
    Transport,
)

__all__ = [
    "AsyncHttpxTransport",
    "AsyncTransport",
    "HttpxTransport",
    "RateLimit",
    "Response",
    "RetryPolicy",
    "Transport",
]
