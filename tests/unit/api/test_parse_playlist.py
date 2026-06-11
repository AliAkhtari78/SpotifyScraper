"""Tests for playlist parsing from real pathfinder and embed fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.api.parse_entities import (
    parse_playlist_embed,
    parse_playlist_gql,
    parse_playlist_tracks_page,
)
from spotify_scraper.errors import ParsingError

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"

# The playlist name uses a curly apostrophe (U+2019, RIGHT SINGLE QUOTATION MARK).
EXPECTED_NAME = "Today’s Top Hits"  # noqa: RUF001
EXPECTED_ID = "37i9dQZF1DXcBWIGoYBM5M"
EXPECTED_URI = "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"


def _load(relative: str) -> dict[str, Any]:
    with (FIXTURES / relative).open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
        return data


@pytest.fixture
def gql_union() -> dict[str, Any]:
    union: dict[str, Any] = _load("pathfinder/playlist.json")["data"]["playlistV2"]
    return union


@pytest.fixture
def embed_entity() -> dict[str, Any]:
    entity: dict[str, Any] = _load("embed/playlist.json")["props"]["pageProps"]["state"]["data"][
        "entity"
    ]
    return entity


def test_parse_gql_core_fields(gql_union: dict[str, Any]) -> None:
    playlist = parse_playlist_gql(gql_union)
    assert playlist.id == EXPECTED_ID
    assert playlist.uri == EXPECTED_URI
    assert playlist.name == EXPECTED_NAME
    assert playlist.description


def test_parse_gql_owner_name_present(gql_union: dict[str, Any]) -> None:
    playlist = parse_playlist_gql(gql_union)
    assert playlist.owner is not None
    assert playlist.owner.name == "Spotify"
    assert playlist.owner.uri == "spotify:user:spotify"


def test_parse_gql_total_tracks_positive(gql_union: dict[str, Any]) -> None:
    playlist = parse_playlist_gql(gql_union)
    assert isinstance(playlist.total_tracks, int)
    assert playlist.total_tracks > 0
    assert isinstance(playlist.followers, int)
    assert playlist.followers > 0


def test_parse_gql_tracks_from_page(gql_union: dict[str, Any]) -> None:
    playlist = parse_playlist_gql(gql_union)
    assert len(playlist.tracks) > 0
    first = playlist.tracks[0]
    assert first.added_at is not None
    track = first.track
    assert track.name == "hate that i made you love me"
    assert track.uri == "spotify:track:20jbSiX29FDX4oQxBXyUEi"
    assert track.id == "20jbSiX29FDX4oQxBXyUEi"
    assert track.duration_ms == 197949
    assert isinstance(track.play_count, int)
    assert track.play_count > 0
    assert track.album is not None
    assert track.album.name == "hate that i made you love me"
    assert len(track.images) >= 1
    assert [a.name for a in track.artists] == ["Ariana Grande"]


def test_parse_gql_total_tracks_independent_of_page(gql_union: dict[str, Any]) -> None:
    playlist = parse_playlist_gql(gql_union)
    # The page holds fewer items than the playlist's full size.
    assert playlist.total_tracks is not None
    assert len(playlist.tracks) <= playlist.total_tracks


def test_parse_gql_max_tracks_caps_page(gql_union: dict[str, Any]) -> None:
    playlist = parse_playlist_gql(gql_union, max_tracks=5)
    assert len(playlist.tracks) == 5
    assert playlist.total_tracks == 50


def test_parse_gql_share_url(gql_union: dict[str, Any]) -> None:
    playlist = parse_playlist_gql(gql_union)
    assert playlist.share_url is not None
    assert playlist.share_url.startswith("https://open.spotify.com/playlist/")


def test_parse_playlist_tracks_page_skips_local_file() -> None:
    union = {
        "content": {
            "items": [
                {
                    "addedAt": {"isoString": "2024-01-01T00:00:00Z"},
                    "itemV2": {
                        "__typename": "LocalTrackResponseWrapper",
                        "data": {
                            "__typename": "LocalTrack",
                            "name": "A Local File",
                            "uri": "spotify:local:::A+Local+File:200",
                        },
                    },
                },
                {
                    "addedAt": {"isoString": "2024-01-02T00:00:00Z"},
                    "itemV2": {
                        "__typename": "TrackResponseWrapper",
                        "data": {
                            "__typename": "Track",
                            "name": "A Real Track",
                            "uri": "spotify:track:1111111111111111111111",
                            "trackDuration": {"totalMilliseconds": 100000},
                            "playability": {"playable": True},
                            "artists": {"items": [{"profile": {"name": "Someone"}}]},
                        },
                    },
                },
            ]
        }
    }
    tracks = parse_playlist_tracks_page(union)
    assert len(tracks) == 1
    assert tracks[0].track.name == "A Real Track"
    assert tracks[0].track.id == "1111111111111111111111"


def test_parse_playlist_tracks_page_missing_content_returns_empty() -> None:
    assert parse_playlist_tracks_page({"uri": EXPECTED_URI}) == ()


def test_parse_embed_core_fields(embed_entity: dict[str, Any]) -> None:
    playlist = parse_playlist_embed(embed_entity)
    assert playlist.id == EXPECTED_ID
    assert playlist.uri == EXPECTED_URI
    assert playlist.name == EXPECTED_NAME


def test_parse_embed_owner_from_subtitle(embed_entity: dict[str, Any]) -> None:
    playlist = parse_playlist_embed(embed_entity)
    assert playlist.owner is not None
    assert playlist.owner.name == "Spotify"


def test_parse_embed_tracks_have_no_added_at(embed_entity: dict[str, Any]) -> None:
    playlist = parse_playlist_embed(embed_entity)
    assert len(playlist.tracks) > 0
    assert all(entry.added_at is None for entry in playlist.tracks)
    assert playlist.tracks[0].track.name == "hate that i made you love me"


def test_parse_embed_lacks_tier1_fields(embed_entity: dict[str, Any]) -> None:
    playlist = parse_playlist_embed(embed_entity)
    assert playlist.total_tracks is None
    assert playlist.followers is None
    assert playlist.share_url is None


def test_parse_gql_truncated_missing_uri_raises() -> None:
    with pytest.raises(ParsingError, match=r"playlistV2\.uri"):
        parse_playlist_gql({"name": EXPECTED_NAME})


def test_parse_gql_truncated_missing_name_raises() -> None:
    with pytest.raises(ParsingError, match=r"playlistV2\.name"):
        parse_playlist_gql({"uri": EXPECTED_URI})
