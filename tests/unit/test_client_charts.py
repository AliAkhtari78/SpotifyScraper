"""Tests for the editorial-chart registry helpers on both clients.

``get_chart`` resolves a chart key to its backing playlist id and delegates to
``get_playlist``; the delegation is verified by stubbing ``get_playlist`` so the
full playlist ladder need not be mocked here (it has its own tests).
"""

from __future__ import annotations

from typing import Any

import pytest

from spotify_scraper import AsyncSpotifyClient, SpotifyClient
from spotify_scraper.errors import URLError


def test_list_charts_returns_known_registry() -> None:
    with SpotifyClient() as client:
        charts = client.list_charts()
    keys = {chart.key for chart in charts}
    assert "top-50-global" in keys
    assert "todays-top-hits" in keys
    for chart in charts:
        assert chart.playlist_id and chart.name


def test_get_chart_delegates_to_get_playlist(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_get_playlist(self: SpotifyClient, value: str, *, max_tracks: int | None = 100) -> str:
        captured["value"] = value
        captured["max_tracks"] = max_tracks
        return "PLAYLIST"

    monkeypatch.setattr(SpotifyClient, "get_playlist", fake_get_playlist)
    with SpotifyClient() as client:
        result = client.get_chart("todays-top-hits", max_tracks=5)
    assert result == "PLAYLIST"
    assert captured["value"] == "37i9dQZF1DXcBWIGoYBM5M"
    assert captured["max_tracks"] == 5


def test_get_chart_unknown_key_raises_url_error() -> None:
    with SpotifyClient() as client, pytest.raises(URLError, match="Unknown chart"):
        client.get_chart("not-a-real-chart")


async def test_get_chart_delegates_to_get_playlist_async(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def fake_get_playlist(
        self: AsyncSpotifyClient, value: str, *, max_tracks: int | None = 100
    ) -> str:
        captured["value"] = value
        return "PLAYLIST"

    monkeypatch.setattr(AsyncSpotifyClient, "get_playlist", fake_get_playlist)
    async with AsyncSpotifyClient() as client:
        result = await client.get_chart("top-50-global")
    assert result == "PLAYLIST"
    assert captured["value"] == "37i9dQZEVXbMDoHDwVN2tF"


async def test_get_chart_unknown_key_raises_url_error_async() -> None:
    async with AsyncSpotifyClient() as client:
        with pytest.raises(URLError):
            await client.get_chart("not-a-real-chart")
