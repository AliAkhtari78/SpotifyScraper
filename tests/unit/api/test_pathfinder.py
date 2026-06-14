"""Tests for pathfinder URL building, auth headers, and response classification."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest

from spotify_scraper.api.pathfinder import (
    OPERATIONS,
    PATHFINDER_URL,
    SEARCH_OPERATION,
    auth_headers,
    build_search_url,
    build_url,
    classify_response,
)
from spotify_scraper.errors import NotFoundError, ParsingError, TokenError

TRACK_ID = "4uLU6hMCjMI75M1A2tKUQC"
TRACK_HASH = "612585ae06ba435ad26369870deaae23b5c8800a256cd8a57e08eddc25a37294"
SEARCH_HASH = "eff59fa0a3d026b88b56fddbcf4bdfa16a186b8175a5c1a358c072e053c2e5b0"


def _query(url: str) -> dict[str, str]:
    return {key: values[0] for key, values in parse_qs(urlsplit(url).query).items()}


def test_build_url_targets_pathfinder_endpoint() -> None:
    url = build_url("track", TRACK_ID)
    split = urlsplit(url)
    assert f"{split.scheme}://{split.netloc}{split.path}" == PATHFINDER_URL


def test_build_url_operation_name() -> None:
    assert _query(build_url("track", TRACK_ID))["operationName"] == "getTrack"


def test_build_url_variables_encode_uri() -> None:
    variables = json.loads(_query(build_url("track", TRACK_ID))["variables"])
    assert variables == {"uri": f"spotify:track:{TRACK_ID}"}


def test_build_url_extensions_carry_persisted_query_hash() -> None:
    extensions = json.loads(_query(build_url("track", TRACK_ID))["extensions"])
    assert extensions == {"persistedQuery": {"version": 1, "sha256Hash": TRACK_HASH}}


def test_build_url_unknown_kind_raises() -> None:
    with pytest.raises(KeyError):
        build_url("nonexistent", TRACK_ID)


def test_track_operation_table_entry() -> None:
    operation = OPERATIONS["track"]
    assert operation.name == "getTrack"
    assert operation.sha256 == TRACK_HASH
    assert operation.build_variables(TRACK_ID) == {"uri": f"spotify:track:{TRACK_ID}"}


def test_build_search_url_targets_pathfinder_endpoint() -> None:
    url = build_search_url("daft punk")
    split = urlsplit(url)
    assert f"{split.scheme}://{split.netloc}{split.path}" == PATHFINDER_URL


def test_build_search_url_operation_name() -> None:
    assert _query(build_search_url("daft punk"))["operationName"] == "searchDesktop"


def test_build_search_url_variables_encode_query() -> None:
    variables = json.loads(_query(build_search_url("daft punk"))["variables"])
    assert variables["searchTerm"] == "daft punk"
    assert variables["limit"] == 10


def test_build_search_url_extensions_carry_persisted_query_hash() -> None:
    extensions = json.loads(_query(build_search_url("daft punk"))["extensions"])
    assert extensions == {"persistedQuery": {"version": 1, "sha256Hash": SEARCH_HASH}}


def test_build_search_url_overrides_win() -> None:
    variables = json.loads(
        _query(build_search_url("x", variable_overrides={"limit": 5}))["variables"]
    )
    assert variables["limit"] == 5
    assert variables["searchTerm"] == "x"


def test_search_operation_entry() -> None:
    assert SEARCH_OPERATION.name == "searchDesktop"
    assert SEARCH_OPERATION.sha256 == SEARCH_HASH
    assert SEARCH_OPERATION.build_variables("x")["searchTerm"] == "x"


def test_auth_headers() -> None:
    assert auth_headers("tok-123") == {
        "Authorization": "Bearer tok-123",
        "app-platform": "WebPlayer",
    }


def test_classify_response_ok_returns_data() -> None:
    body: dict[str, Any] = {"data": {"trackUnion": {"id": TRACK_ID}}}
    assert classify_response(200, body) == {"trackUnion": {"id": TRACK_ID}}


def test_classify_response_persisted_query_not_found() -> None:
    body = {"errors": [{"message": "PersistedQueryNotFound"}]}
    with pytest.raises(ParsingError, match="PersistedQueryNotFound"):
        classify_response(200, body)


def test_classify_response_persisted_query_advises_update() -> None:
    body = {"errors": [{"message": "PersistedQueryNotFound"}]}
    with pytest.raises(ParsingError, match="library update"):
        classify_response(200, body)


def test_classify_response_null_union_is_not_found() -> None:
    with pytest.raises(NotFoundError):
        classify_response(200, {"data": {"trackUnion": None}})


def test_classify_response_empty_data_is_not_found() -> None:
    with pytest.raises(NotFoundError):
        classify_response(200, {"data": {}})


def test_classify_response_401_raises_token_error() -> None:
    with pytest.raises(TokenError):
        classify_response(401, None)


def test_classify_response_401_takes_precedence_over_body() -> None:
    with pytest.raises(TokenError):
        classify_response(401, {"data": {"trackUnion": {"id": TRACK_ID}}})


def test_classify_response_missing_body_raises_parsing_error() -> None:
    with pytest.raises(ParsingError):
        classify_response(200, None)


def test_classify_response_missing_data_key_raises_parsing_error() -> None:
    with pytest.raises(ParsingError, match="data"):
        classify_response(200, {"extensions": {}})
