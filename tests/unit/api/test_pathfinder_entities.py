"""Tests for the album/artist/playlist/episode/show pathfinder operations.

Covers the OPERATIONS table entries, ``build_url`` per kind, and the
``variable_overrides`` merge used for offset/limit pagination.
"""

from __future__ import annotations

import json
from urllib.parse import parse_qs, urlsplit

from spotify_scraper.api.pathfinder import OPERATIONS, build_url

EID = "6N9PS4QXF1D0OWPk0Sxtb4"

EXPECTED: dict[str, tuple[str, str, dict[str, object]]] = {
    "album": (
        "getAlbum",
        "b9bfabef66ed756e5e13f68a942deb60bd4125ec1f1be8cc42769dc0259b4b10",
        {"uri": f"spotify:album:{EID}", "locale": "", "offset": 0, "limit": 50},
    ),
    "artist": (
        "queryArtistOverview",
        "ae0e2958a4ab645b35ca19ac04d0495ae12d9c5d7b7286217674801a9aab281a",
        {"uri": f"spotify:artist:{EID}", "locale": "", "includePrerelease": False},
    ),
    "playlist": (
        "fetchPlaylist",
        "a65e12194ed5fc443a1cdebed5fabe33ca5b07b987185d63c72483867ad13cb4",
        {
            "uri": f"spotify:playlist:{EID}",
            "offset": 0,
            "limit": 100,
            "enableWatchFeedEntrypoint": False,
        },
    ),
    "episode": (
        "getEpisodeOrChapter",
        "3416929067571ac4b79db16716be3c6ea5f6265f7975a0ee94b1fc5ee1dc1e9d",
        {"uri": f"spotify:episode:{EID}"},
    ),
    "show": (
        "queryShowMetadataV2",
        "aaad798a17a43c0f443c45d630a83df39d2ca1062a090c2e4fb045d6b00ab360",
        {"uri": f"spotify:show:{EID}"},
    ),
}


def _query(url: str) -> dict[str, str]:
    return {key: values[0] for key, values in parse_qs(urlsplit(url).query).items()}


def test_operation_table_has_all_entity_kinds() -> None:
    for kind in EXPECTED:
        assert kind in OPERATIONS


def test_operation_names_and_hashes() -> None:
    for kind, (name, sha, _variables) in EXPECTED.items():
        operation = OPERATIONS[kind]
        assert operation.name == name
        assert operation.sha256 == sha


def test_operation_variable_builders() -> None:
    for kind, (_name, _sha, variables) in EXPECTED.items():
        assert OPERATIONS[kind].build_variables(EID) == variables


def test_build_url_operation_name_per_kind() -> None:
    for kind, (name, _sha, _variables) in EXPECTED.items():
        assert _query(build_url(kind, EID))["operationName"] == name


def test_build_url_variables_per_kind() -> None:
    for kind, (_name, _sha, variables) in EXPECTED.items():
        assert json.loads(_query(build_url(kind, EID))["variables"]) == variables


def test_build_url_extensions_carry_hash_per_kind() -> None:
    for kind, (_name, sha, _variables) in EXPECTED.items():
        extensions = json.loads(_query(build_url(kind, EID))["extensions"])
        assert extensions == {"persistedQuery": {"version": 1, "sha256Hash": sha}}


def test_playlist_disables_watch_feed_entrypoint() -> None:
    variables = json.loads(_query(build_url("playlist", EID))["variables"])
    assert variables["enableWatchFeedEntrypoint"] is False


def test_variable_overrides_merge_offset_and_limit() -> None:
    url = build_url("album", EID, variable_overrides={"offset": 50, "limit": 25})
    variables = json.loads(_query(url)["variables"])
    assert variables["offset"] == 50
    assert variables["limit"] == 25
    assert variables["uri"] == f"spotify:album:{EID}"
    assert variables["locale"] == ""


def test_variable_overrides_can_add_new_keys() -> None:
    url = build_url("episode", EID, variable_overrides={"market": "US"})
    variables = json.loads(_query(url)["variables"])
    assert variables == {"uri": f"spotify:episode:{EID}", "market": "US"}


def test_variable_overrides_none_keeps_defaults() -> None:
    without = json.loads(_query(build_url("playlist", EID))["variables"])
    with_none = json.loads(_query(build_url("playlist", EID, variable_overrides=None))["variables"])
    assert without == with_none


def test_variable_overrides_does_not_mutate_operation_defaults() -> None:
    build_url("playlist", EID, variable_overrides={"offset": 200})
    fresh = json.loads(_query(build_url("playlist", EID))["variables"])
    assert fresh["offset"] == 0
