"""Live smoke tests for track extraction (network-dependent)."""

from __future__ import annotations

import pytest

from spotify_scraper import AsyncSpotifyClient, SpotifyClient

NEVER_GONNA = "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"


@pytest.mark.live
def test_get_track_live() -> None:
    with SpotifyClient() as client:
        track = client.get_track(NEVER_GONNA)

    assert track.name == "Never Gonna Give You Up"
    assert track.play_count is not None
    assert track.play_count > 1_000_000_000
    assert track.preview_url is not None
    assert track.preview_url.startswith("https")


@pytest.mark.live
async def test_get_track_live_async() -> None:
    async with AsyncSpotifyClient() as client:
        track = await client.get_track(NEVER_GONNA)

    assert track.name == "Never Gonna Give You Up"
    assert track.play_count is not None
    assert track.play_count > 1_000_000_000
    assert track.preview_url is not None
    assert track.preview_url.startswith("https")
