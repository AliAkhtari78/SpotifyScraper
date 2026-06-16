"""Parser tests for the discovery surfaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.api.parse_entities import (
    discography_item_count,
    discography_total,
    parse_discography_releases,
    parse_related_artists,
    parse_similar_albums,
    parse_user_profile,
)
from spotify_scraper.errors import ParsingError
from spotify_scraper.models.user import UserProfile

PF = Path(__file__).resolve().parents[2] / "fixtures" / "pathfinder"
SPC = Path(__file__).resolve().parents[2] / "fixtures" / "spclient"


def _pf(name: str) -> dict[str, Any]:
    return json.loads((PF / name).read_text(encoding="utf-8"))


RELATED = _pf("artist_related.json")
DISCOGRAPHY = _pf("artist_discography.json")
SIMILAR = _pf("similar_albums.json")
USER_PROFILE = json.loads((SPC / "user_profile.json").read_text(encoding="utf-8"))


def test_parse_related_artists() -> None:
    artists = parse_related_artists(RELATED["data"]["artistUnion"])
    assert len(artists) > 0
    assert all(a.uri.startswith("spotify:artist:") and a.name for a in artists)


def test_parse_related_artists_missing_node() -> None:
    assert parse_related_artists({}) == ()


def test_parse_discography_releases_and_counts() -> None:
    union = DISCOGRAPHY["data"]["artistUnion"]
    releases = parse_discography_releases(union)
    assert len(releases) == 5
    assert all(r.uri.startswith("spotify:album:") and r.name for r in releases)
    assert discography_item_count(union) == 5
    assert discography_total(union) == 58


def test_parse_discography_missing_node() -> None:
    assert parse_discography_releases({}) == ()
    assert discography_item_count({}) == 0
    assert discography_total({}) is None


def test_parse_similar_albums() -> None:
    albums = parse_similar_albums(SIMILAR["data"]["seoRecommendedTrackAlbum"])
    assert len(albums) > 0
    assert all(a.uri.startswith("spotify:album:") for a in albums)


def test_parse_user_profile() -> None:
    profile = parse_user_profile(USER_PROFILE)
    assert isinstance(profile, UserProfile)
    assert profile.uri.startswith("spotify:user:")
    assert profile.id == profile.uri.rsplit(":", 1)[-1]
    assert profile.name
    assert profile.followers_count is not None
    assert len(profile.public_playlists) > 0
    assert all(p.uri.startswith("spotify:playlist:") for p in profile.public_playlists)
    assert UserProfile.from_dict(profile.to_dict()) == profile


def test_parse_user_profile_missing_uri_raises() -> None:
    with pytest.raises(ParsingError):
        parse_user_profile({"name": "x"})
