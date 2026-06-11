"""Transport protocols and httpx-backed implementations.

Clients depend only on the :class:`Transport` / :class:`AsyncTransport`
protocols, so alternative transports (e.g. a browser) can be injected. The
httpx implementations add browser-like headers, client-side rate limiting,
retry with backoff, and mapping of failures onto the library's error types.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

import httpx

from spotify_scraper.errors import NetworkError, NotFoundError, RateLimitedError
from spotify_scraper.http.headers import default_headers, pick_user_agent
from spotify_scraper.http.ratelimit import AsyncTokenBucket, RateLimit, TokenBucket
from spotify_scraper.http.retry import RetryPolicy, backoff_delay


class Response(Protocol):
    """Minimal response shape; ``httpx.Response`` satisfies it structurally."""

    status_code: int

    @property
    def headers(self) -> Mapping[str, str]:
        """Response headers."""
        ...

    @property
    def text(self) -> str:
        """Decoded response body."""
        ...

    @property
    def content(self) -> bytes:
        """Raw response body."""
        ...

    def json(self) -> Any:
        """Parsed JSON body."""
        ...


@runtime_checkable
class Transport(Protocol):
    """Synchronous HTTP transport."""

    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response:
        """Fetch ``url``, merging ``headers`` over the transport defaults."""
        ...

    def close(self) -> None:
        """Release underlying resources."""
        ...


@runtime_checkable
class AsyncTransport(Protocol):
    """Asynchronous HTTP transport."""

    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response:
        """Fetch ``url``, merging ``headers`` over the transport defaults."""
        ...

    async def aclose(self) -> None:
        """Release underlying resources."""
        ...


_RETRYABLE_ERRORS = (
    httpx.ConnectError,
    httpx.ConnectTimeout,
    httpx.ReadTimeout,
    httpx.RemoteProtocolError,
)


def _parse_retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _error_delay(exc: httpx.HTTPError, url: str, attempt: int, policy: RetryPolicy) -> float:
    """Return the retry delay for a transport error, or raise ``NetworkError``."""
    delay = None
    if isinstance(exc, _RETRYABLE_ERRORS):
        delay = backoff_delay(policy, attempt, None)
    if delay is None:
        raise NetworkError(f"Request to {url} failed: {exc}", request_url=url) from exc
    return delay


def _response_delay(
    response: httpx.Response, url: str, attempt: int, policy: RetryPolicy
) -> float | None:
    """Return the retry delay, ``None`` to accept the response, or raise."""
    status = response.status_code
    if status == 404:
        raise NotFoundError(f"Spotify resource not found: {url}")
    if status == 429:
        retry_after = _parse_retry_after(response.headers.get("Retry-After"))
        delay = backoff_delay(policy, attempt, retry_after)
        if delay is None:
            raise RateLimitedError(
                f"Rate limited by Spotify at {url}",
                request_url=url,
                retry_after=retry_after,
            )
        return delay
    if status >= 500:
        delay = backoff_delay(policy, attempt, None)
        if delay is None:
            raise NetworkError(
                f"HTTP {status} from {url} after {attempt} attempts", request_url=url
            )
        return delay
    return None


class HttpxTransport:
    """Synchronous :class:`Transport` backed by ``httpx.Client``."""

    def __init__(
        self,
        *,
        rate_limit: RateLimit | None = None,
        retry: RetryPolicy | None = None,
        user_agent: str | None = None,
        proxy: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        """Initialize the transport.

        Args:
            rate_limit: Token-bucket configuration; defaults to safe limits.
            retry: Retry policy; defaults to :class:`RetryPolicy`.
            user_agent: Fixed User-Agent; a pool entry is chosen when omitted.
            proxy: Optional proxy URL passed through to ``httpx.Client``.
            timeout: Per-request timeout in seconds.
        """
        self._retry = retry or RetryPolicy()
        self._bucket = TokenBucket(rate_limit or RateLimit())
        self._headers = default_headers(user_agent or pick_user_agent())
        self._client = httpx.Client(proxy=proxy, timeout=timeout, follow_redirects=True)

    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response:
        """Fetch ``url`` with throttling, retries, and error mapping.

        Args:
            url: Absolute URL to request.
            headers: Extra headers merged over the transport defaults
                (caller wins).

        Returns:
            The successful (non-retryable) response.

        Raises:
            NotFoundError: On HTTP 404.
            RateLimitedError: On an unrecoverable HTTP 429.
            NetworkError: On connection failures or exhausted retries.
        """
        merged = {**self._headers, **(headers or {})}
        attempt = 0
        while True:
            attempt += 1
            self._bucket.acquire()
            try:
                response = self._client.get(url, headers=merged)
            except httpx.HTTPError as exc:
                time.sleep(_error_delay(exc, url, attempt, self._retry))
                continue
            delay = _response_delay(response, url, attempt, self._retry)
            if delay is None:
                return response
            time.sleep(delay)

    def close(self) -> None:
        """Close the underlying ``httpx.Client``."""
        self._client.close()


class AsyncHttpxTransport:
    """Asynchronous :class:`AsyncTransport` backed by ``httpx.AsyncClient``."""

    def __init__(
        self,
        *,
        rate_limit: RateLimit | None = None,
        retry: RetryPolicy | None = None,
        user_agent: str | None = None,
        proxy: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        """Initialize the transport.

        Args:
            rate_limit: Token-bucket configuration; defaults to safe limits.
            retry: Retry policy; defaults to :class:`RetryPolicy`.
            user_agent: Fixed User-Agent; a pool entry is chosen when omitted.
            proxy: Optional proxy URL passed through to ``httpx.AsyncClient``.
            timeout: Per-request timeout in seconds.
        """
        self._retry = retry or RetryPolicy()
        self._bucket = AsyncTokenBucket(rate_limit or RateLimit())
        self._headers = default_headers(user_agent or pick_user_agent())
        self._client = httpx.AsyncClient(proxy=proxy, timeout=timeout, follow_redirects=True)

    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response:
        """Fetch ``url`` with throttling, retries, and error mapping.

        Args:
            url: Absolute URL to request.
            headers: Extra headers merged over the transport defaults
                (caller wins).

        Returns:
            The successful (non-retryable) response.

        Raises:
            NotFoundError: On HTTP 404.
            RateLimitedError: On an unrecoverable HTTP 429.
            NetworkError: On connection failures or exhausted retries.
        """
        merged = {**self._headers, **(headers or {})}
        attempt = 0
        while True:
            attempt += 1
            await self._bucket.acquire()
            try:
                response = await self._client.get(url, headers=merged)
            except httpx.HTTPError as exc:
                await asyncio.sleep(_error_delay(exc, url, attempt, self._retry))
                continue
            delay = _response_delay(response, url, attempt, self._retry)
            if delay is None:
                return response
            await asyncio.sleep(delay)

    async def aclose(self) -> None:
        """Close the underlying ``httpx.AsyncClient``."""
        await self._client.aclose()
