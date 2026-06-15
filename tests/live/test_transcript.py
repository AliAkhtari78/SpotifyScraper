"""Live smoke tests for cookie-authenticated transcripts (network + credentials).

The transcript-read-along envelope is confirmed plain JSON (a ``section`` array
of ``text.sentence`` cues; see ``openspec/changes/add-podcast-transcripts/``).
``EPISODE_ID`` must point at an episode that shows "Read along" in the web
player; override it with ``SPOTIFY_TRANSCRIPT_EPISODE`` for a current one.
"""

from __future__ import annotations

import os

import pytest

from spotify_scraper import AsyncSpotifyClient, SpotifyClient

# A Joe Rogan Experience episode confirmed to carry a "Read along" transcript.
EPISODE_ID = os.environ.get("SPOTIFY_TRANSCRIPT_EPISODE", "2c50dZKpJcLjAfGXhOMRxD")
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
