"""Live smoke tests for credits (auth) and artist events (anonymous)."""

from __future__ import annotations

import os

import pytest

from spotify_scraper import SpotifyClient

RICK_ARTIST = "0gxyHStUsqpMadRV0Di1Qt"
CREDITS_TRACK = "4LfCY65LvojKjWEnU7fNN4"
_SP_DC = os.environ.get("SPOTIFY_SP_DC")


@pytest.mark.live
def test_get_artist_events_live() -> None:
    # Event inventory is region- and time-dependent, so accept any count; the
    # point is that the anonymous op parses without error.
    with SpotifyClient() as client:
        concerts = client.get_artist_events(RICK_ARTIST)
    for concert in concerts:
        assert concert.uri.startswith("spotify:concert:")
        assert concert.title


@pytest.mark.live
@pytest.mark.skipif(not _SP_DC, reason="SPOTIFY_SP_DC env var not set")
def test_get_credits_live() -> None:
    with SpotifyClient(cookies=_SP_DC) as client:
        credits = client.get_credits(CREDITS_TRACK)
    assert credits.track_uri.startswith("spotify:track:")
    assert len(credits.roles) > 0
    assert all(role.title for role in credits.roles)
