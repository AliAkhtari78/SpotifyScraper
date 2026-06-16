"""Live smoke tests for the discovery surfaces (network-dependent).

Related artists, discography, and similar albums are anonymous; ``get_user``
needs an ``sp_dc`` cookie and skips unless ``SPOTIFY_SP_DC`` is set.
"""

from __future__ import annotations

import os

import pytest

from spotify_scraper import AsyncSpotifyClient, SpotifyClient

RICK_ARTIST = "0gxyHStUsqpMadRV0Di1Qt"
NEVER_GONNA = "4uLU6hMCjMI75M1A2tKUQC"
_SP_DC = os.environ.get("SPOTIFY_SP_DC")


@pytest.mark.live
def test_get_related_artists_live() -> None:
    with SpotifyClient() as client:
        artists = client.get_related_artists(RICK_ARTIST)
    assert len(artists) > 0
    assert all(a.name and a.uri.startswith("spotify:artist:") for a in artists)


@pytest.mark.live
def test_get_discography_live() -> None:
    with SpotifyClient() as client:
        releases = client.get_discography(RICK_ARTIST, max_releases=60)
    assert len(releases) > 5
    assert all(r.name and r.uri.startswith("spotify:album:") for r in releases)


@pytest.mark.live
async def test_get_similar_albums_live_async() -> None:
    async with AsyncSpotifyClient() as client:
        albums = await client.get_similar_albums(NEVER_GONNA, limit=10)
    assert all(a.uri.startswith("spotify:album:") for a in albums)


@pytest.mark.live
@pytest.mark.skipif(not _SP_DC, reason="SPOTIFY_SP_DC env var not set")
def test_get_user_live() -> None:
    with SpotifyClient(cookies=_SP_DC) as client:
        profile = client.get_user("spotify")
    assert profile.name == "Spotify"
    assert profile.followers_count and profile.followers_count > 1_000_000
    assert len(profile.public_playlists) > 0
