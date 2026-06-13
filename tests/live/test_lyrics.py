"""Live smoke tests for cookie-authenticated lyrics (network + credentials)."""

from __future__ import annotations

import os

import pytest

from spotify_scraper import AsyncSpotifyClient, SpotifyClient

NEVER_GONNA = "4uLU6hMCjMI75M1A2tKUQC"
_SP_DC = os.environ.get("SPOTIFY_SP_DC")

pytestmark = pytest.mark.skipif(not _SP_DC, reason="SPOTIFY_SP_DC env var not set")


@pytest.mark.live
def test_get_lyrics_live() -> None:
    with SpotifyClient(cookies=_SP_DC) as client:
        lyrics = client.get_lyrics(NEVER_GONNA)

    assert lyrics.sync_type == "LINE_SYNCED"
    assert len(lyrics.lines) > 0
    assert all(line.text for line in lyrics.lines)
    assert all(line.start_ms >= 0 for line in lyrics.lines)


@pytest.mark.live
async def test_get_lyrics_live_async() -> None:
    async with AsyncSpotifyClient(cookies=_SP_DC) as client:
        lyrics = await client.get_lyrics(NEVER_GONNA)

    assert lyrics.sync_type == "LINE_SYNCED"
    assert len(lyrics.lines) > 0
    assert all(line.text for line in lyrics.lines)
