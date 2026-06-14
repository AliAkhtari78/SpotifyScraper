"""Live smoke tests for aggregate search (network-dependent, no cookie)."""

from __future__ import annotations

import pytest

from spotify_scraper import AsyncSpotifyClient, SpotifyClient


@pytest.mark.live
def test_search_live() -> None:
    with SpotifyClient() as client:
        results = client.search("daft punk")

    assert results.query == "daft punk"
    assert len(results.tracks) > 0
    assert len(results.artists) > 0
    assert any("Daft Punk" in artist.name for artist in results.artists)
    assert all(track.id for track in results.tracks)


@pytest.mark.live
async def test_search_live_async() -> None:
    async with AsyncSpotifyClient() as client:
        results = await client.search("daft punk", types=("track", "artist"))

    assert len(results.tracks) > 0
    assert len(results.artists) > 0
    assert results.albums == ()
