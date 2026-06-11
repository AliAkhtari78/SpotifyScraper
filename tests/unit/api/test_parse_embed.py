"""Tests for embed-page __NEXT_DATA__ parsing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.api.parse_embed import (
    EmbedSession,
    extract_next_data,
    get_entity,
    get_session,
)
from spotify_scraper.errors import NotFoundError, ParsingError

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "embed"
FIXTURE_NAMES = ["track", "album", "artist", "episode", "playlist", "show"]


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / f"{name}.json").read_text())


def wrap_next_data(next_data: dict[str, Any]) -> str:
    body = json.dumps(next_data)
    return (
        "<!DOCTYPE html><html><body>"
        f'<script id="__NEXT_DATA__" type="application/json">{body}</script>'
        "</body></html>"
    )


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_extract_next_data_from_wrapped_html(name: str) -> None:
    next_data = load_fixture(name)
    extracted = extract_next_data(wrap_next_data(next_data))
    assert extracted == next_data
    assert "state" in extracted["props"]["pageProps"]


def test_extract_next_data_no_script() -> None:
    with pytest.raises(ParsingError):
        extract_next_data("<html><body>no script here</body></html>")


def test_extract_next_data_malformed_json() -> None:
    html = '<script id="__NEXT_DATA__" type="application/json">{not json}</script>'
    with pytest.raises(ParsingError):
        extract_next_data(html)


def test_extract_next_data_not_object() -> None:
    html = '<script id="__NEXT_DATA__" type="application/json">[1, 2, 3]</script>'
    with pytest.raises(ParsingError):
        extract_next_data(html)


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_get_session_from_each_fixture(name: str) -> None:
    session = get_session(load_fixture(name))
    assert isinstance(session, EmbedSession)
    assert session.access_token == "REDACTED"  # noqa: S105
    assert session.expires_at_ms > 0
    assert session.is_anonymous is True


@pytest.mark.parametrize("name", FIXTURE_NAMES)
def test_get_entity_from_each_fixture(name: str) -> None:
    entity = get_entity(load_fixture(name))
    assert "uri" in entity
    assert "id" in entity


def test_get_entity_dead_payload_raises_not_found() -> None:
    dead = {
        "props": {
            "pageProps": {
                "status": 404,
                "forbiddenReason": "NOT_FOUND",
            }
        }
    }
    with pytest.raises(NotFoundError):
        get_entity(dead)


def test_get_entity_forbidden_only_raises_not_found() -> None:
    dead = {"props": {"pageProps": {"forbiddenReason": "GEO_RESTRICTED"}}}
    with pytest.raises(NotFoundError):
        get_entity(dead)


def test_get_entity_unexpected_shape_raises_parsing_error() -> None:
    broken = {"props": {"pageProps": {"state": {"data": {}}}}}
    with pytest.raises(ParsingError):
        get_entity(broken)


def test_get_session_missing_session_raises_parsing_error() -> None:
    broken = {"props": {"pageProps": {"state": {"settings": {}}}}}
    with pytest.raises(ParsingError):
        get_session(broken)


def test_extract_then_get_session_roundtrip() -> None:
    html = wrap_next_data(load_fixture("track"))
    session = get_session(extract_next_data(html))
    assert session.expires_at_ms == 1781122107115
