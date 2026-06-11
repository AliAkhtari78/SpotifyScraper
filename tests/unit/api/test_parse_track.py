"""Tests for track parsing from real pathfinder and embed fixtures."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.api.parse_entities import (
    _merge_tracks,
    parse_track_embed,
    parse_track_gql,
)
from spotify_scraper.errors import ParsingError
from spotify_scraper.models.common import ArtistRef
from spotify_scraper.models.track import Track

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"

EXPECTED_NAME = "Never Gonna Give You Up"
EXPECTED_ID = "4uLU6hMCjMI75M1A2tKUQC"
EXPECTED_URI = "spotify:track:4uLU6hMCjMI75M1A2tKUQC"
EXPECTED_DURATION_MS = 213573
EXPECTED_RELEASE = datetime(1987, 11, 12, tzinfo=timezone.utc)


def _load(relative: str) -> dict[str, Any]:
    with (FIXTURES / relative).open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
        return data


@pytest.fixture
def gql_union() -> dict[str, Any]:
    union: dict[str, Any] = _load("pathfinder/track.json")["data"]["trackUnion"]
    return union


@pytest.fixture
def embed_entity() -> dict[str, Any]:
    entity: dict[str, Any] = _load("embed/track.json")["props"]["pageProps"]["state"]["data"][
        "entity"
    ]
    return entity


def test_parse_gql_core_fields(gql_union: dict[str, Any]) -> None:
    track = parse_track_gql(gql_union)
    assert track.id == EXPECTED_ID
    assert track.uri == EXPECTED_URI
    assert track.name == EXPECTED_NAME
    assert track.duration_ms == EXPECTED_DURATION_MS


def test_parse_gql_artist(gql_union: dict[str, Any]) -> None:
    track = parse_track_gql(gql_union)
    assert track.artists == (
        ArtistRef(
            name="Rick Astley",
            uri="spotify:artist:0gxyHStUsqpMadRV0Di1Qt",
            id="0gxyHStUsqpMadRV0Di1Qt",
        ),
    )


def test_parse_gql_play_count_is_int(gql_union: dict[str, Any]) -> None:
    track = parse_track_gql(gql_union)
    assert isinstance(track.play_count, int)
    assert track.play_count >= 1_137_719_792


def test_parse_gql_tier1_only_fields(gql_union: dict[str, Any]) -> None:
    track = parse_track_gql(gql_union)
    assert track.track_number == 1
    assert track.album is not None
    assert track.album.id == "6N9PS4QXF1D0OWPk0Sxtb4"
    assert track.album.name == "Whenever You Need Somebody"
    assert track.share_url is not None
    assert track.share_url.startswith("https://open.spotify.com/track/")


def test_parse_gql_images_from_cover_art(gql_union: dict[str, Any]) -> None:
    track = parse_track_gql(gql_union)
    assert len(track.images) == 3
    assert {(i.width, i.height) for i in track.images} == {(300, 300), (64, 64), (640, 640)}


def test_parse_gql_release_date(gql_union: dict[str, Any]) -> None:
    assert parse_track_gql(gql_union).release_date == EXPECTED_RELEASE


def test_parse_gql_not_explicit_and_playable(gql_union: dict[str, Any]) -> None:
    track = parse_track_gql(gql_union)
    assert track.explicit is False
    assert track.playable is True


def test_parse_gql_lacks_preview(gql_union: dict[str, Any]) -> None:
    assert parse_track_gql(gql_union).preview_url is None


def test_parse_gql_explicit_label(gql_union: dict[str, Any]) -> None:
    gql_union["contentRating"] = {"label": "EXPLICIT"}
    assert parse_track_gql(gql_union).explicit is True


def test_parse_embed_core_fields(embed_entity: dict[str, Any]) -> None:
    track = parse_track_embed(embed_entity)
    assert track.id == EXPECTED_ID
    assert track.uri == EXPECTED_URI
    assert track.name == EXPECTED_NAME
    assert track.duration_ms == EXPECTED_DURATION_MS


def test_parse_embed_preview_url(embed_entity: dict[str, Any]) -> None:
    track = parse_track_embed(embed_entity)
    assert track.preview_url is not None
    assert track.preview_url.startswith("https://p.scdn.co/")


def test_parse_embed_artist(embed_entity: dict[str, Any]) -> None:
    track = parse_track_embed(embed_entity)
    assert track.artists == (
        ArtistRef(name="Rick Astley", uri="spotify:artist:0gxyHStUsqpMadRV0Di1Qt"),
    )


def test_parse_embed_images_from_visual_identity(embed_entity: dict[str, Any]) -> None:
    track = parse_track_embed(embed_entity)
    assert len(track.images) == 3
    assert {(i.width, i.height) for i in track.images} == {(300, 300), (64, 64), (640, 640)}


def test_parse_embed_release_date(embed_entity: dict[str, Any]) -> None:
    assert parse_track_embed(embed_entity).release_date == EXPECTED_RELEASE


def test_parse_embed_lacks_tier1_fields(embed_entity: dict[str, Any]) -> None:
    track = parse_track_embed(embed_entity)
    assert track.album is None
    assert track.track_number is None
    assert track.play_count is None
    assert track.share_url is None


def test_merge_prefers_gql_and_takes_embed_preview(
    gql_union: dict[str, Any], embed_entity: dict[str, Any]
) -> None:
    gql = parse_track_gql(gql_union)
    embed = parse_track_embed(embed_entity)
    merged = _merge_tracks(gql, embed)
    assert merged.preview_url == embed.preview_url
    assert merged.preview_url is not None
    assert merged.play_count == gql.play_count
    assert merged.album == gql.album
    assert merged.track_number == gql.track_number
    assert merged.images == gql.images


def test_merge_takes_embed_release_date_when_gql_missing(embed_entity: dict[str, Any]) -> None:
    embed = parse_track_embed(embed_entity)
    gql = Track(
        id=EXPECTED_ID,
        uri=EXPECTED_URI,
        name=EXPECTED_NAME,
        duration_ms=EXPECTED_DURATION_MS,
        explicit=False,
        playable=True,
        preview_url=None,
        artists=(),
        images=(),
        release_date=None,
    )
    merged = _merge_tracks(gql, embed)
    assert merged.release_date == EXPECTED_RELEASE
    assert merged.preview_url == embed.preview_url


def test_merge_keeps_gql_release_date_when_present(
    gql_union: dict[str, Any], embed_entity: dict[str, Any]
) -> None:
    gql = parse_track_gql(gql_union)
    embed = parse_track_embed(embed_entity)
    merged = _merge_tracks(gql, embed)
    assert merged.release_date == gql.release_date


def test_parse_gql_truncated_missing_id_raises() -> None:
    with pytest.raises(ParsingError, match=r"trackUnion\.id"):
        parse_track_gql({"uri": EXPECTED_URI, "name": EXPECTED_NAME})


def test_parse_gql_truncated_missing_duration_raises() -> None:
    with pytest.raises(ParsingError, match="duration"):
        parse_track_gql(
            {"id": EXPECTED_ID, "uri": EXPECTED_URI, "name": EXPECTED_NAME, "playability": {}}
        )


def test_parse_embed_truncated_missing_id_raises() -> None:
    with pytest.raises(ParsingError, match=r"entity\.id"):
        parse_track_embed({"uri": EXPECTED_URI, "name": EXPECTED_NAME, "duration": 1})


def test_parse_embed_truncated_missing_name_raises() -> None:
    with pytest.raises(ParsingError, match="name"):
        parse_track_embed({"id": EXPECTED_ID, "uri": EXPECTED_URI, "duration": 1})


def test_parse_embed_truncated_missing_duration_raises() -> None:
    with pytest.raises(ParsingError, match="duration"):
        parse_track_embed({"id": EXPECTED_ID, "uri": EXPECTED_URI, "name": EXPECTED_NAME})
