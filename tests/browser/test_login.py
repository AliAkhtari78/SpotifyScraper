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
