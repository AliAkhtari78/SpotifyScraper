"""Browser-assisted ``sp_dc`` capture: the user logs in, we read the cookie.

``accounts.spotify.com`` is gated behind bot detection, CAPTCHAs, and frequent
2FA, so a headless username/password POST is fragile and would force the library
to handle a plaintext password. Instead, a real **headed** Chromium opens, the
user signs in by hand, and this helper captures the resulting ``sp_dc`` cookie.
No username or password is ever collected, prompted for, or stored.

Spotify's post-login redirect target varies (premium upsell, region
interstitial, app picker), so rather than wait for a particular URL, the helper
polls the browser context's cookies until ``sp_dc`` appears on ``.spotify.com``
or the timeout elapses. The captured value is never logged, and Playwright
errors are re-raised as :class:`AuthenticationError` without leaking a stack.

This module imports Playwright at the top level; the ``browser`` extra's
lazy-import guard lives in :mod:`spotify_scraper.browser`.
"""

from __future__ import annotations

import asyncio
import contextlib
import shutil
import tempfile
import time
from collections.abc import Mapping, Sequence
from typing import Any, NamedTuple

from playwright.async_api import Error as AsyncPlaywrightError
from playwright.async_api import async_playwright
from playwright.sync_api import Error as SyncPlaywrightError
from playwright.sync_api import ProxySettings, sync_playwright

from spotify_scraper.errors import AuthenticationError

LOGIN_URL = "https://accounts.spotify.com/login"
HOME_URL = "https://open.spotify.com/"
_DEFAULT_TIMEOUT_S = 300.0
_POLL_INTERVAL_S = 1.0

_NO_COOKIE_HINT = (
    "No 'sp_dc' cookie was captured before the login window timed out. Complete the "
    "Spotify sign-in in the opened browser (and close it WITHOUT clicking 'Log out')."
)


class CapturedLogin(NamedTuple):
    """A captured browser login: the ``sp_dc`` cookie plus its expiry.

    ``sp_dc_expires_ms`` is the cookie's expiry in Unix milliseconds, or ``None``
    for a session cookie (Playwright reports ``expires == -1``).
    """

    sp_dc: str
    sp_dc_expires_ms: int | None


def _proxy_settings(proxy: str | None) -> ProxySettings | None:
    return {"server": proxy} if proxy else None


def _expires_ms(expires: Any) -> int | None:
    """Convert a Playwright cookie ``expires`` (Unix seconds, -1 = session) to ms."""
    if isinstance(expires, (int, float)) and not isinstance(expires, bool) and expires > 0:
        return int(expires * 1000)
    return None


def _extract_sp_dc(cookies: Sequence[Mapping[str, Any]]) -> CapturedLogin | None:
    for cookie in cookies:
        if cookie.get("name") == "sp_dc":
            value = cookie.get("value")
            if isinstance(value, str) and value:
                return CapturedLogin(value, _expires_ms(cookie.get("expires")))
    return None


def capture_sp_dc(
    *, timeout: float = _DEFAULT_TIMEOUT_S, proxy: str | None = None
) -> CapturedLogin:
    """Open a headed browser and capture the ``sp_dc`` cookie after manual login.

    A real Chromium window opens at the Spotify login page. The user signs in
    interactively; this helper polls the browser cookies until an ``sp_dc``
    value is present on ``.spotify.com`` and returns it together with the
    cookie's expiry. The browser is always torn down before returning.

    Args:
        timeout: Seconds to wait for the cookie before giving up.
        proxy: Optional proxy URL (e.g. ``http://host:port``) for the browser.

    Returns:
        A :class:`CapturedLogin` carrying the bare ``sp_dc`` value and its
        expiry in Unix milliseconds (``None`` for a session cookie).

    Raises:
        AuthenticationError: If no cookie is captured before the timeout, or any
            browser/driver error occurs. Neither the cookie nor a Playwright
            stack trace appears in the message.
    """
    user_data_dir = tempfile.mkdtemp(prefix="spotifyscraper-login-")
    deadline = time.monotonic() + timeout
    driver = None
    context = None
    try:
        driver = sync_playwright().start()
        context = driver.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            proxy=_proxy_settings(proxy),
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(LOGIN_URL)
        while time.monotonic() < deadline:
            captured = _extract_sp_dc(context.cookies(HOME_URL))
            if captured is not None:
                return captured
            time.sleep(_POLL_INTERVAL_S)
        raise AuthenticationError(_NO_COOKIE_HINT)
    except SyncPlaywrightError:
        raise AuthenticationError(_NO_COOKIE_HINT) from None
    finally:
        if context is not None:
            with contextlib.suppress(SyncPlaywrightError):
                context.close()
        if driver is not None:
            driver.stop()
        shutil.rmtree(user_data_dir, ignore_errors=True)


async def capture_sp_dc_async(
    *, timeout: float = _DEFAULT_TIMEOUT_S, proxy: str | None = None
) -> CapturedLogin:
    """Async mirror of :func:`capture_sp_dc`.

    Args:
        timeout: Seconds to wait for the cookie before giving up.
        proxy: Optional proxy URL for the browser.

    Returns:
        A :class:`CapturedLogin` carrying the bare ``sp_dc`` value and its
        expiry in Unix milliseconds (``None`` for a session cookie).

    Raises:
        AuthenticationError: If no cookie is captured before the timeout, or any
            browser/driver error occurs (no cookie or stack leaks).
    """
    user_data_dir = tempfile.mkdtemp(prefix="spotifyscraper-login-")
    deadline = time.monotonic() + timeout
    driver = None
    context = None
    try:
        driver = await async_playwright().start()
        context = await driver.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            proxy=_proxy_settings(proxy),
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(LOGIN_URL)
        while time.monotonic() < deadline:
            captured = _extract_sp_dc(await context.cookies(HOME_URL))
            if captured is not None:
                return captured
            await asyncio.sleep(_POLL_INTERVAL_S)
        raise AuthenticationError(_NO_COOKIE_HINT)
    except AsyncPlaywrightError:
        raise AuthenticationError(_NO_COOKIE_HINT) from None
    finally:
        if context is not None:
            with contextlib.suppress(AsyncPlaywrightError):
                await context.close()
        if driver is not None:
            await driver.stop()
        shutil.rmtree(user_data_dir, ignore_errors=True)
