"""Live smoke tests for the visual/discovery primitives (network-dependent).

Colors and charts are anonymous; Canvas needs an ``sp_dc`` cookie, so those
cases skip unless ``SPOTIFY_SP_DC`` is set.
"""

from __future__ import annotations

import os

import pytest

from spotify_scraper import AsyncSpotifyClient, Canvas, SpotifyClient

NEVER_GONNA = "4uLU6hMCjMI75M1A2tKUQC"
_SP_DC = os.environ.get("SPOTIFY_SP_DC")
_HEX = 7  # "#RRGGBB"


@pytest.mark.live
def test_get_colors_live() -> None:
    with SpotifyClient() as client:
        track = client.get_track(NEVER_GONNA)
        colors = client.get_colors(track)
    for value in (colors.raw, colors.dark, colors.light):
        assert value.startswith("#") and len(value) == _HEX


@pytest.mark.live
async def test_get_colors_live_async() -> None:
    async with AsyncSpotifyClient() as client:
        colors = await client.get_colors(
            "https://i.scdn.co/image/ab67616d0000b273fe8a8d62b127592ff546d9c8"
        )
    assert colors.raw.startswith("#") and len(colors.raw) == _HEX


@pytest.mark.live
def test_get_chart_live() -> None:
    with SpotifyClient() as client:
        assert len(client.list_charts()) >= 1
        playlist = client.get_chart("todays-top-hits", max_tracks=5)
    assert playlist.name
    assert len(playlist.tracks) > 0


@pytest.mark.live
@pytest.mark.skipif(not _SP_DC, reason="SPOTIFY_SP_DC env var not set")
def test_get_canvas_live() -> None:
    # Canvas inventory is volatile, so accept either a valid Canvas or None;
    # what matters is that the authenticated op parses without error.
    with SpotifyClient(cookies=_SP_DC) as client:
        canvas = client.get_canvas("4LfCY65LvojKjWEnU7fNN4")
    if canvas is not None:
        assert isinstance(canvas, Canvas)
        assert canvas.url.startswith("https://")
        assert canvas.uri.startswith("spotify:canvas:")


@pytest.mark.live
@pytest.mark.skipif(not _SP_DC, reason="SPOTIFY_SP_DC env var not set")
async def test_get_canvas_live_async() -> None:
    async with AsyncSpotifyClient(cookies=_SP_DC) as client:
        canvas = await client.get_canvas(NEVER_GONNA)
    assert canvas is None or canvas.url.startswith("https://")
