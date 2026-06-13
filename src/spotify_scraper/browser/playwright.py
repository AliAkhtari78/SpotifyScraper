"""Playwright-backed transports that satisfy the transport protocols.

These transports drive a real Chromium instance and fetch through Playwright's
:class:`APIRequestContext`, which shares the browser's TLS/HTTP2 fingerprint
and cookie jar. That makes them a drop-in fallback for the httpx transports
when Spotify serves a challenge page to plain HTTP clients. Both embed-page
HTML and pathfinder JSON requests work through the same path.

The browser boots lazily on the first :meth:`PlaywrightTransport.get` call, not
at construction, so building a transport is cheap and side-effect free.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from playwright.async_api import APIResponse as AsyncAPIResponse
from playwright.async_api import Error as AsyncPlaywrightError
from playwright.async_api import async_playwright
from playwright.sync_api import APIResponse as SyncAPIResponse
from playwright.sync_api import Error as SyncPlaywrightError
from playwright.sync_api import sync_playwright

from spotify_scraper.errors import NetworkError, NotFoundError, RateLimitedError


class _BrowserResponse:
    """Adapter exposing a Playwright ``APIResponse`` as a :class:`Response`."""

    __slots__ = ("_headers", "_text", "content", "status_code")

    def __init__(
        self, status_code: int, headers: Mapping[str, str], body: bytes, text: str
    ) -> None:
        """Capture the response eagerly so it survives the browser shutdown.

        Args:
            status_code: HTTP status code.
            headers: Response headers (lowercased keys, as Playwright returns).
            body: Raw response body.
            text: Decoded response body.
        """
        self.status_code = status_code
        self._headers = dict(headers)
        self.content = body
        self._text = text

    @property
    def headers(self) -> Mapping[str, str]:
        """Response headers."""
        return self._headers

    @property
    def text(self) -> str:
        """Decoded response body."""
        return self._text

    def json(self) -> Any:
        """Parse the body as JSON.

        Raises:
            ValueError: If the body is not valid JSON (``json.JSONDecodeError``).
        """
        return json.loads(self._text)


def _proxy_settings(proxy: str | None) -> dict[str, str] | None:
    return {"server": proxy} if proxy else None


def _map_status(status: int, url: str) -> None:
    """Raise the library error matching a non-success status, mirroring httpx.

    A 404 maps to :class:`NotFoundError` and a 429 to :class:`RateLimitedError`;
    every other status (including 2xx) is left for the caller to interpret, so
    pathfinder JSON with an embedded error body still reaches the parser.
    """
    if status == 404:
        raise NotFoundError(f"Spotify resource not found: {url}")
    if status == 429:
        raise RateLimitedError(f"Rate limited by Spotify at {url}", request_url=url)


def _adapt_sync(response: SyncAPIResponse) -> _BrowserResponse:
    return _BrowserResponse(response.status, response.headers, response.body(), response.text())


def _adapt_async(response: AsyncAPIResponse, body: bytes, text: str) -> _BrowserResponse:
    return _BrowserResponse(response.status, response.headers, body, text)


class PlaywrightTransport:
    """Synchronous transport that fetches through a headless Chromium browser.

    Satisfies the :class:`~spotify_scraper.http.transport.Transport` protocol,
    so ``SpotifyClient(transport=PlaywrightTransport())`` works with no other
    changes. The browser starts on the first :meth:`get` and must be released
    with :meth:`close`.
    """

    def __init__(
        self,
        *,
        headless: bool = True,
        proxy: str | None = None,
        timeout: float = 30.0,
        user_agent: str | None = None,
        use_page_navigation: bool = False,
    ) -> None:
        """Initialize the transport without starting a browser.

        Args:
            headless: Run Chromium headless (default); pass ``False`` to watch.
            proxy: Optional proxy URL, e.g. ``http://host:port``.
            timeout: Per-request timeout in seconds.
            user_agent: Fixed User-Agent for the browser context; Playwright's
                Chromium default is used when omitted.
            use_page_navigation: Reserved knob for routing fetches through
                ``page.goto`` instead of the request context to clear challenge
                pages. The request-context path covers both HTML and JSON, so
                this is off by default.
        """
        self._headless = headless
        self._proxy = proxy
        self._timeout_ms = timeout * 1000
        self._user_agent = user_agent
        self._use_page_navigation = use_page_navigation
        self._driver: Any = None
        self._browser: Any = None
        self._context: Any = None

    def _ensure_started(self) -> None:
        if self._context is not None:
            return
        self._driver = sync_playwright().start()
        self._browser = self._driver.chromium.launch(headless=self._headless)
        self._context = self._browser.new_context(
            user_agent=self._user_agent,
            proxy=_proxy_settings(self._proxy),
        )

    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> _BrowserResponse:
        """Fetch ``url`` through the browser's request context.

        Args:
            url: Absolute URL to request.
            headers: Extra request headers (caller wins).

        Returns:
            The fetched response as a :class:`_BrowserResponse`.

        Raises:
            NotFoundError: On HTTP 404.
            RateLimitedError: On HTTP 429.
            NetworkError: On any Playwright driver/transport failure.
        """
        self._ensure_started()
        try:
            response = self._context.request.get(
                url,
                headers=dict(headers) if headers else None,
                timeout=self._timeout_ms,
            )
        except SyncPlaywrightError as exc:
            raise NetworkError(f"Request to {url} failed: {exc}", request_url=url) from exc
        _map_status(response.status, url)
        return _adapt_sync(response)

    def close(self) -> None:
        """Shut down the context, browser, and Playwright driver.

        Safe to call when the browser never started or has already been closed.
        """
        if self._context is not None:
            self._context.close()
            self._context = None
        if self._browser is not None:
            self._browser.close()
            self._browser = None
        if self._driver is not None:
            self._driver.stop()
            self._driver = None


class AsyncPlaywrightTransport:
    """Asynchronous mirror of :class:`PlaywrightTransport`.

    Satisfies the :class:`~spotify_scraper.http.transport.AsyncTransport`
    protocol. The browser starts on the first :meth:`get` and must be released
    with :meth:`aclose`.
    """

    def __init__(
        self,
        *,
        headless: bool = True,
        proxy: str | None = None,
        timeout: float = 30.0,
        user_agent: str | None = None,
        use_page_navigation: bool = False,
    ) -> None:
        """Initialize the transport without starting a browser.

        Args:
            headless: Run Chromium headless (default); pass ``False`` to watch.
            proxy: Optional proxy URL, e.g. ``http://host:port``.
            timeout: Per-request timeout in seconds.
            user_agent: Fixed User-Agent for the browser context; Playwright's
                Chromium default is used when omitted.
            use_page_navigation: Reserved knob for routing fetches through
                ``page.goto`` instead of the request context to clear challenge
                pages. The request-context path covers both HTML and JSON, so
                this is off by default.
        """
        self._headless = headless
        self._proxy = proxy
        self._timeout_ms = timeout * 1000
        self._user_agent = user_agent
        self._use_page_navigation = use_page_navigation
        self._driver: Any = None
        self._browser: Any = None
        self._context: Any = None

    async def _ensure_started(self) -> None:
        if self._context is not None:
            return
        self._driver = await async_playwright().start()
        self._browser = await self._driver.chromium.launch(headless=self._headless)
        self._context = await self._browser.new_context(
            user_agent=self._user_agent,
            proxy=_proxy_settings(self._proxy),
        )

    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> _BrowserResponse:
        """Fetch ``url`` through the browser's request context.

        Args:
            url: Absolute URL to request.
            headers: Extra request headers (caller wins).

        Returns:
            The fetched response as a :class:`_BrowserResponse`.

        Raises:
            NotFoundError: On HTTP 404.
            RateLimitedError: On HTTP 429.
            NetworkError: On any Playwright driver/transport failure.
        """
        await self._ensure_started()
        try:
            response = await self._context.request.get(
                url,
                headers=dict(headers) if headers else None,
                timeout=self._timeout_ms,
            )
            body = await response.body()
            text = await response.text()
        except AsyncPlaywrightError as exc:
            raise NetworkError(f"Request to {url} failed: {exc}", request_url=url) from exc
        _map_status(response.status, url)
        return _adapt_async(response, body, text)

    async def aclose(self) -> None:
        """Shut down the context, browser, and Playwright driver.

        Safe to call when the browser never started or has already been closed.
        """
        if self._context is not None:
            await self._context.close()
            self._context = None
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._driver is not None:
            await self._driver.stop()
            self._driver = None
