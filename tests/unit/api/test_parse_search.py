"""Tests for search-results parsing from a real ``searchDesktop`` fixture."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.api.parse_entities import parse_search_results
from spotify_scraper.errors import ParsingError
from spotify_scraper.models.common import AlbumRef, ShowRef
from spotify_scraper.models.episode import Episode
from spotify_scraper.models.search import SearchResults

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"

QUERY = "daft punk"


def _load(relative: str) -> dict[str, Any]:
    with (FIXTURES / relative).open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
        return data


@pytest.fixture
def union() -> dict[str, Any]:
    section: dict[str, Any] = _load("pathfinder/search.json")["data"]["searchV2"]
    return section


def test_query_echoed(union: dict[str, Any]) -> None:
    assert parse_search_results(union, query=QUERY).query == QUERY


def test_per_type_counts(union: dict[str, Any]) -> None:
    results = parse_search_results(union, query=QUERY)
    assert len(results.tracks) == 3
    assert len(results.artists) == 3
    assert len(results.albums) == 3
    assert len(results.playlists) == 3
    assert len(results.shows) == 3
    assert len(results.episodes) == 3


def test_track_fields(union: dict[str, Any]) -> None:
    track = parse_search_results(union, query=QUERY).tracks[0]
    assert track.name == "One More Time"
    assert track.id == "0DiWol3AO6WpXZgp0goxAV"
    assert track.uri == "spotify:track:0DiWol3AO6WpXZgp0goxAV"
    assert track.artists[0].name == "Daft Punk"
    assert track.album is not None
    assert track.album.name == "Discovery"
    assert len(track.images) == 3
    # Sparse hit: tier-1-only fields the search payload omits stay None.
    assert track.play_count is None
    assert track.share_url is None
    assert track.preview_url is None


def test_artist_fields(union: dict[str, Any]) -> None:
    artist = parse_search_results(union, query=QUERY).artists[0]
    assert artist.name == "Daft Punk"
    # No id in the payload: it is derived from the uri.
    assert artist.id == "4tZwfgrHOc3mvqYlEYSvVi"
    assert artist.uri == "spotify:artist:4tZwfgrHOc3mvqYlEYSvVi"
    assert len(artist.images) == 3


def test_album_is_lightweight_ref(union: dict[str, Any]) -> None:
    album = parse_search_results(union, query=QUERY).albums[0]
    assert isinstance(album, AlbumRef)
    assert album.name == "Random Access Memories"
    assert album.id == "4m2880jivSbbyEGAKfITCa"
    assert len(album.images) == 3


def test_playlist_fields(union: dict[str, Any]) -> None:
    playlist = parse_search_results(union, query=QUERY).playlists[0]
    assert playlist.name == "Daft Punk Greatest Hits"
    assert playlist.owner is not None
    assert playlist.owner.name == "Red Franzen"
    assert playlist.description != ""


def test_show_is_lightweight_ref(union: dict[str, Any]) -> None:
    show = parse_search_results(union, query=QUERY).shows[0]
    assert isinstance(show, ShowRef)
    assert show.publisher == "Amazon Originals"
    assert show.id == "54WLkpC52fstLCptFS72qS"
    assert len(show.images) == 3


def test_episode_fields(union: dict[str, Any]) -> None:
    episode = parse_search_results(union, query=QUERY).episodes[0]
    assert isinstance(episode, Episode)
    assert episode.duration_ms > 0
    assert episode.description != ""
    assert episode.id == "4q6WrMpLrvsm03PoXgAS3A"


def test_total_from_tracks_section(union: dict[str, Any]) -> None:
    assert parse_search_results(union, query=QUERY).total == 1000


def test_empty_union_yields_empty_results() -> None:
    results = parse_search_results({}, query="no hits at all")
    assert results == SearchResults(query="no hits at all")
    assert results.tracks == ()
    assert results.artists == ()
    assert results.albums == ()
    assert results.playlists == ()
    assert results.shows == ()
    assert results.episodes == ()
    assert results.total is None


def test_empty_sections_yield_empty_tuples() -> None:
    union = {"tracksV2": {"items": [], "totalCount": 0}, "artists": {"items": []}}
    results = parse_search_results(union, query=QUERY)
    assert results.tracks == ()
    assert results.artists == ()
    assert results.total == 0


def test_items_missing_uri_are_skipped() -> None:
    union = {"tracksV2": {"items": [{"item": {"data": {"name": "no uri"}}}]}}
    assert parse_search_results(union, query=QUERY).tracks == ()


def test_track_with_partial_album_does_not_abort_search() -> None:
    # A track hit whose albumOfTrack is present but missing its name must NOT
    # raise (which would abort the entire result set) — the track is kept with
    # album=None, honouring the skip-don't-raise contract.
    union = {
        "tracksV2": {
            "items": [
                {
                    "item": {
                        "data": {
                            "uri": "spotify:track:abc",
                            "name": "Song",
                            "albumOfTrack": {"uri": "spotify:album:xyz"},  # no name
                        }
                    }
                }
            ]
        }
    }
    results = parse_search_results(union, query=QUERY)
    assert len(results.tracks) == 1
    assert results.tracks[0].name == "Song"
    assert results.tracks[0].album is None


def test_non_mapping_section_is_ignored() -> None:
    union = {"tracksV2": "broken", "artists": None}
    results = parse_search_results(union, query=QUERY)
    assert results.tracks == ()
    assert results.artists == ()


def test_non_mapping_union_raises() -> None:
    with pytest.raises(ParsingError, match="searchV2"):
        parse_search_results("not a mapping", query=QUERY)  # type: ignore[arg-type]


def test_to_dict_round_trip(union: dict[str, Any]) -> None:
    results = parse_search_results(union, query=QUERY)
    restored = SearchResults.from_dict(results.to_dict())
    assert restored == results
