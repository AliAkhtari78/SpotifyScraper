"""Optional Playwright browser-fallback transports.

Importing this package without the ``browser`` extra installed raises a clear
:class:`ImportError` pointing at both install steps. With Playwright present it
re-exports the synchronous and asynchronous browser transports.
"""

from __future__ import annotations

try:
    from spotify_scraper.browser.login import (
        capture_sp_dc,
        capture_sp_dc_async,
    )
    from spotify_scraper.browser.playwright import (
        AsyncPlaywrightTransport,
        PlaywrightTransport,
    )
except ImportError as exc:  # pragma: no cover - exercised via monkeypatched import
    raise ImportError(
        "Browser transport requires the 'browser' extra: "
        "pip install spotifyscraper[browser] && playwright install chromium"
    ) from exc

__all__ = [
    "AsyncPlaywrightTransport",
    "PlaywrightTransport",
    "capture_sp_dc",
    "capture_sp_dc_async",
]
