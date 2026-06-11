"""Tests for artist parsing from real pathfinder and embed fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.api.parse_entities import parse_artist_embed, parse_artist_gql
from spotify_scraper.errors import ParsingError

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"

EXPECTED_NAME = "Rick Astley"
EXPECTED_ID = "0gxyHStUsqpMadRV0Di1Qt"
EXPECTED_URI = "spotify:artist:0gxyHStUsqpMadRV0Di1Qt"


def _load(relative: str) -> dict[str, Any]:
    with (FIXTURES / relative).open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
        return data


@pytest.fixture
def gql_union() -> dict[str, Any]:
    union: dict[str, Any] = _load("pathfinder/artist.json")["data"]["artistUnion"]
    return union


@pytest.fixture
def embed_entity() -> dict[str, Any]:
    entity: dict[str, Any] = _load("embed/artist.json")["props"]["pageProps"]["state"]["data"][
        "entity"
    ]
    return entity


def test_parse_gql_core_fields(gql_union: dict[str, Any]) -> None:
    artist = parse_artist_gql(gql_union)
    assert artist.id == EXPECTED_ID
    assert artist.uri == EXPECTED_URI
    assert artist.name == EXPECTED_NAME


def test_parse_gql_monthly_listeners_positive(gql_union: dict[str, Any]) -> None:
    artist = parse_artist_gql(gql_union)
    assert isinstance(artist.monthly_listeners, int)
    assert artist.monthly_listeners > 0
    assert isinstance(artist.followers, int)
    assert artist.followers > 0


def test_parse_gql_world_rank_zero_is_none(gql_union: dict[str, Any]) -> None:
    assert parse_artist_gql(gql_union).world_rank is None


def test_parse_gql_top_tracks_have_play_count(gql_union: dict[str, Any]) -> None:
    artist = parse_artist_gql(gql_union)
    assert len(artist.top_tracks) > 0
    first = artist.top_tracks[0]
    assert first.name == "Never Gonna Give You Up"
    assert first.id == "4PTG3Z6ehGkBFwjybzWkR8"
    assert isinstance(first.play_count, int)
    assert first.play_count > 0
    assert len(first.images) == 3
    assert [a.name for a in first.artists] == ["Rick Astley"]


def test_parse_gql_discography_refs(gql_union: dict[str, Any]) -> None:
    artist = parse_artist_gql(gql_union)
    assert len(artist.albums) > 0
    assert len(artist.singles) > 0
    album = artist.albums[0]
    assert album.id
    assert album.uri.startswith("spotify:album:")
    assert album.name
    assert len(album.images) >= 1


def test_parse_gql_profile_metadata(gql_union: dict[str, Any]) -> None:
    artist = parse_artist_gql(gql_union)
    assert artist.biography is not None
    assert artist.biography
    assert len(artist.external_links) > 0
    assert all(link.startswith("http") for link in artist.external_links)
    assert artist.share_url is not None
    assert artist.share_url.startswith("https://open.spotify.com/artist/")


def test_parse_gql_images_from_avatar(gql_union: dict[str, Any]) -> None:
    artist = parse_artist_gql(gql_union)
    assert len(artist.images) >= 1
    assert all(img.url.startswith("https://i.scdn.co/image/") for img in artist.images)


def test_parse_embed_core_fields(embed_entity: dict[str, Any]) -> None:
    artist = parse_artist_embed(embed_entity)
    assert artist.id == EXPECTED_ID
    assert artist.uri == EXPECTED_URI
    assert artist.name == EXPECTED_NAME


def test_parse_embed_top_tracks(embed_entity: dict[str, Any]) -> None:
    artist = parse_artist_embed(embed_entity)
    assert len(artist.top_tracks) > 0
    first = artist.top_tracks[0]
    assert first.name == "Never Gonna Give You Up"
    assert first.preview_url is not None
    assert [a.name for a in first.artists] == ["Rick Astley"]


def test_parse_embed_lacks_tier1_fields(embed_entity: dict[str, Any]) -> None:
    artist = parse_artist_embed(embed_entity)
    assert artist.monthly_listeners is None
    assert artist.followers is None
    assert artist.biography is None
    assert artist.albums == ()
    assert artist.share_url is None


def test_parse_gql_truncated_missing_uri_raises() -> None:
    with pytest.raises(ParsingError, match=r"artistUnion\.uri"):
        parse_artist_gql({"profile": {"name": EXPECTED_NAME}})


def test_parse_gql_truncated_missing_profile_name_raises() -> None:
    with pytest.raises(ParsingError, match=r"artistUnion\.profile\.name"):
        parse_artist_gql({"uri": EXPECTED_URI, "profile": {}})
