"""Live smoke tests for cookie-authenticated transcripts (network + credentials).

NOTE: The transcript envelope shape is unconfirmed (see
``openspec/changes/add-podcast-transcripts/design.md``). This test is the real
confirmation that ``decode_envelope`` matches Spotify's live response; pick an
episode that shows "Read along" in the web player.
"""

from __future__ import annotations

import os

import pytest

from spotify_scraper import AsyncSpotifyClient, SpotifyClient

# An episode known to carry a transcript in the web player.
EPISODE_ID = os.environ.get("SPOTIFY_TRANSCRIPT_EPISODE", "512ojhOuo1ktJprKbVcKyQ")
_SP_DC = os.environ.get("SPOTIFY_SP_DC")

pytestmark = pytest.mark.skipif(not _SP_DC, reason="SPOTIFY_SP_DC env var not set")


@pytest.mark.live
def test_get_transcript_live() -> None:
    with SpotifyClient(cookies=_SP_DC) as client:
        transcript = client.get_transcript(EPISODE_ID)

    assert len(transcript.lines) > 0
    assert all(line.text for line in transcript.lines)
    assert all(line.start_ms >= 0 for line in transcript.lines)


@pytest.mark.live
async def test_get_transcript_live_async() -> None:
    async with AsyncSpotifyClient(cookies=_SP_DC) as client:
        transcript = await client.get_transcript(EPISODE_ID)

    assert len(transcript.lines) > 0
    assert all(line.text for line in transcript.lines)
