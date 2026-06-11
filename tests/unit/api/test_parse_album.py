"""Tests for album parsing from real pathfinder and embed fixtures."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.api.parse_entities import (
    parse_album_embed,
    parse_album_gql,
    parse_album_tracks_page,
)
from spotify_scraper.errors import ParsingError

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"

EXPECTED_NAME = "Global Warming"
EXPECTED_ID = "4aawyAB9vmqN3uQ7FjRGTy"
EXPECTED_URI = "spotify:album:4aawyAB9vmqN3uQ7FjRGTy"
EXPECTED_TRACK_COUNT = 18
EXPECTED_RELEASE = datetime(2012, 11, 16, tzinfo=timezone.utc)


def _load(relative: str) -> dict[str, Any]:
    with (FIXTURES / relative).open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
        return data


@pytest.fixture
def gql_union() -> dict[str, Any]:
    union: dict[str, Any] = _load("pathfinder/album.json")["data"]["albumUnion"]
    return union


@pytest.fixture
def embed_entity() -> dict[str, Any]:
    entity: dict[str, Any] = _load("embed/album.json")["props"]["pageProps"]["state"]["data"][
        "entity"
    ]
    return entity


def test_parse_gql_core_fields(gql_union: dict[str, Any]) -> None:
    album = parse_album_gql(gql_union)
    assert album.id == EXPECTED_ID
    assert album.uri == EXPECTED_URI
    assert album.name == EXPECTED_NAME
    assert album.album_type == "album"


def test_parse_gql_track_count_is_eighteen(gql_union: dict[str, Any]) -> None:
    album = parse_album_gql(gql_union)
    assert album.total_tracks == EXPECTED_TRACK_COUNT
    assert len(album.tracks) == EXPECTED_TRACK_COUNT


def test_parse_gql_first_track_details(gql_union: dict[str, Any]) -> None:
    album = parse_album_gql(gql_union)
    first = album.tracks[0]
    assert first.id == "6OmhkSOpvYBokMKQxpIGx2"
    assert first.uri == "spotify:track:6OmhkSOpvYBokMKQxpIGx2"
    assert first.name == "Global Warming (feat. Sensato)"
    assert first.duration_ms == 85400
    assert first.explicit is True
    assert first.playable is True
    assert first.track_number == 1
    assert first.play_count == 10707285
    assert first.images == ()
    assert first.preview_url is None
    assert first.release_date is None
    assert [a.name for a in first.artists] == ["Pitbull", "Sensato"]


def test_parse_gql_album_metadata(gql_union: dict[str, Any]) -> None:
    album = parse_album_gql(gql_union)
    assert album.label == "Mr.305/Polo Grounds Music/RCA Records"
    assert album.copyrights == ("(P) 2012 RCA Records, a division of Sony Music Entertainment",)
    assert album.release_date == EXPECTED_RELEASE
    assert [a.name for a in album.artists] == ["Pitbull"]
    assert album.artists[0].id == "0TnOYISbd1XYRBk9myaseg"
    assert album.share_url is not None
    assert album.share_url.startswith("https://open.spotify.com/album/")


def test_parse_gql_images_from_cover_art(gql_union: dict[str, Any]) -> None:
    album = parse_album_gql(gql_union)
    assert len(album.images) >= 3
    assert all(img.url.startswith("https://i.scdn.co/image/") for img in album.images)


def test_parse_album_tracks_page_returns_all_tracks(gql_union: dict[str, Any]) -> None:
    tracks = parse_album_tracks_page(gql_union)
    assert len(tracks) == EXPECTED_TRACK_COUNT
    assert tracks[0].id == "6OmhkSOpvYBokMKQxpIGx2"


def test_parse_album_tracks_page_missing_tracks_returns_empty() -> None:
    assert parse_album_tracks_page({"uri": EXPECTED_URI}) == ()


def test_parse_embed_core_fields(embed_entity: dict[str, Any]) -> None:
    album = parse_album_embed(embed_entity)
    assert album.id == EXPECTED_ID
    assert album.uri == EXPECTED_URI
    assert album.name == EXPECTED_NAME


def test_parse_embed_artist_from_subtitle(embed_entity: dict[str, Any]) -> None:
    album = parse_album_embed(embed_entity)
    assert [a.name for a in album.artists] == ["Pitbull"]


def test_parse_embed_track_list(embed_entity: dict[str, Any]) -> None:
    album = parse_album_embed(embed_entity)
    assert len(album.tracks) == EXPECTED_TRACK_COUNT
    first = album.tracks[0]
    assert first.name == "Global Warming (feat. Sensato)"
    assert first.duration_ms == 85400
    assert first.explicit is True
    assert first.preview_url is not None
    assert [a.name for a in first.artists] == ["Pitbull", "Sensato"]


def test_parse_embed_images_from_visual_identity(embed_entity: dict[str, Any]) -> None:
    album = parse_album_embed(embed_entity)
    assert len(album.images) >= 1


def test_parse_embed_lacks_tier1_fields(embed_entity: dict[str, Any]) -> None:
    album = parse_album_embed(embed_entity)
    assert album.label is None
    assert album.total_tracks is None
    assert album.copyrights == ()
    assert album.share_url is None


def test_parse_gql_truncated_missing_uri_raises() -> None:
    with pytest.raises(ParsingError, match=r"albumUnion\.uri"):
        parse_album_gql({"name": EXPECTED_NAME, "type": "ALBUM"})


def test_parse_gql_truncated_missing_type_raises() -> None:
    with pytest.raises(ParsingError, match=r"albumUnion\.type"):
        parse_album_gql({"uri": EXPECTED_URI, "name": EXPECTED_NAME})
