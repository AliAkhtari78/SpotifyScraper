"""Tests for the Playwright browser-fallback transports.

The browser-marked tests boot a real Chromium instance (excluded from the
default suite). The ImportError-message test runs in the default suite via a
monkeypatched missing ``playwright`` module.
"""

from __future__ import annotations

import builtins
import importlib
import sys
from collections.abc import Iterator

import pytest

from spotify_scraper import SpotifyClient
from spotify_scraper.api.parse_embed import extract_next_data
from spotify_scraper.http.transport import Transport

NEVER_GONNA = "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"


def test_missing_extra_raises_with_both_install_commands(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Importing the package without playwright surfaces both install steps."""
    real_import = builtins.__import__

    def _block_playwright(name: str, *args: object, **kwargs: object) -> object:
        if name == "playwright" or name.startswith("playwright."):
            raise ImportError("No module named 'playwright'")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    for mod in list(sys.modules):
        if mod == "spotify_scraper.browser" or mod.startswith("playwright"):
            monkeypatch.delitem(sys.modules, mod, raising=False)
    monkeypatch.setattr(builtins, "__import__", _block_playwright)

    with pytest.raises(ImportError) as excinfo:
        importlib.import_module("spotify_scraper.browser")

    message = str(excinfo.value)
    assert "pip install spotifyscraper[browser]" in message
    assert "playwright install chromium" in message


@pytest.fixture
def transport() -> Iterator[object]:
    """Yield a started-on-first-use transport and close it afterwards."""
    from spotify_scraper.browser import PlaywrightTransport

    instance = PlaywrightTransport()
    try:
        yield instance
    finally:
        instance.close()


@pytest.mark.browser
def test_satisfies_transport_protocol() -> None:
    """The transport is a structural match for the runtime-checkable Transport."""
    from spotify_scraper.browser import PlaywrightTransport

    instance = PlaywrightTransport()
    try:
        assert isinstance(instance, Transport)
    finally:
        instance.close()


@pytest.mark.browser
def test_embed_fetch_returns_parseable_next_data(transport: object) -> None:
    """A real embed fetch yields HTML whose __NEXT_DATA__ parses."""
    response = transport.get(  # type: ignore[attr-defined]
        "https://open.spotify.com/embed/track/4uLU6hMCjMI75M1A2tKUQC"
    )
    assert response.status_code == 200
    next_data = extract_next_data(response.text)
    assert isinstance(next_data, dict)
    assert next_data


@pytest.mark.browser
def test_client_fetches_track_through_browser_transport(transport: object) -> None:
    """SpotifyClient drives a full track fetch over the browser transport."""
    with SpotifyClient(transport=transport) as client:  # type: ignore[arg-type]
        track = client.get_track(NEVER_GONNA)

    assert track.name == "Never Gonna Give You Up"
    assert track.id == "4uLU6hMCjMI75M1A2tKUQC"
