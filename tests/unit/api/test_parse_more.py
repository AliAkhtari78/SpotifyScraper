"""Parser tests for credits and concerts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.api.parse_entities import parse_concerts, parse_credits
from spotify_scraper.errors import ParsingError
from spotify_scraper.models.concert import Concert
from spotify_scraper.models.credits import Credits

PF = Path(__file__).resolve().parents[2] / "fixtures" / "pathfinder"
SPC = Path(__file__).resolve().parents[2] / "fixtures" / "spclient"

CONCERTS: dict[str, Any] = json.loads((PF / "concerts.json").read_text(encoding="utf-8"))
CREDITS: dict[str, Any] = json.loads((SPC / "track_credits.json").read_text(encoding="utf-8"))


def test_parse_concerts() -> None:
    concerts = parse_concerts(CONCERTS["data"]["concerts"])
    assert len(concerts) > 0
    first = concerts[0]
    assert isinstance(first, Concert)
    assert first.uri.startswith("spotify:concert:")
    assert first.id == first.uri.rsplit(":", 1)[-1]
    assert first.title
    assert Concert.from_dict(first.to_dict()) == first


def test_parse_concerts_missing_node() -> None:
    assert parse_concerts({}) == ()


def test_parse_credits() -> None:
    credits = parse_credits(CREDITS)
    assert isinstance(credits, Credits)
    assert credits.track_uri.startswith("spotify:track:")
    assert credits.track_title
    assert len(credits.roles) > 0
    assert all(role.title for role in credits.roles)
    performers = [role for role in credits.roles if role.artists]
    assert performers and all(a.name for a in performers[0].artists)
    assert Credits.from_dict(credits.to_dict()) == credits


def test_parse_credits_missing_uri_raises() -> None:
    with pytest.raises(ParsingError):
        parse_credits({"trackTitle": "x"})
