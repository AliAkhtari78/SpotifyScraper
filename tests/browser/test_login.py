"""Browser-marked smoke test for the headed login capture.

Excluded from the default suite. A real Spotify login cannot be scripted in CI,
so this only asserts the negative path: a real headed Chromium opens, no login
happens within a short timeout, and ``AuthenticationError`` is raised without
leaking a Playwright stack trace.
"""

from __future__ import annotations

import pytest

from spotify_scraper.errors import AuthenticationError


@pytest.mark.browser
def test_capture_times_out_without_login() -> None:
    """No manual login within the timeout yields AuthenticationError."""
    from spotify_scraper.browser import capture_sp_dc

    with pytest.raises(AuthenticationError) as excinfo:
        capture_sp_dc(timeout=3.0)
    message = str(excinfo.value)
    assert "sp_dc" in message
    assert "Traceback" not in message


@pytest.mark.browser
def test_extract_sp_dc_captures_value_and_expiry() -> None:
    """A Playwright cookie's value and (seconds) expiry become a CapturedLogin (ms)."""
    from spotify_scraper.browser.login import _extract_sp_dc

    captured = _extract_sp_dc(
        [
            {"name": "other", "value": "x"},
            {"name": "sp_dc", "value": "ABC", "expires": 1_900_000_000.0},
        ]
    )
    assert captured is not None
    assert captured.sp_dc == "ABC"
    assert captured.sp_dc_expires_ms == 1_900_000_000_000


@pytest.mark.browser
def test_extract_sp_dc_session_cookie_has_no_expiry() -> None:
    """A session cookie (Playwright ``expires == -1``) yields a None expiry."""
    from spotify_scraper.browser.login import _extract_sp_dc

    captured = _extract_sp_dc([{"name": "sp_dc", "value": "ABC", "expires": -1}])
    assert captured is not None
    assert captured.sp_dc_expires_ms is None


@pytest.mark.browser
def test_extract_sp_dc_absent_returns_none() -> None:
    """No sp_dc cookie present returns None."""
    from spotify_scraper.browser.login import _extract_sp_dc

    assert _extract_sp_dc([{"name": "other", "value": "x"}]) is None
