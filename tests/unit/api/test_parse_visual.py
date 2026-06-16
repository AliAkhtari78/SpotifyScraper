"""Parser tests for Colors and Canvas (the visual primitives)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.api.parse_entities import parse_canvas, parse_colors
from spotify_scraper.errors import ParsingError
from spotify_scraper.models.canvas import Canvas
from spotify_scraper.models.colors import Colors

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "pathfinder"
COLORS_BODY: dict[str, Any] = json.loads((FIXTURES / "colors.json").read_text(encoding="utf-8"))
CANVAS_BODY: dict[str, Any] = json.loads((FIXTURES / "canvas.json").read_text(encoding="utf-8"))
CANVAS_ABSENT: dict[str, Any] = json.loads(
    (FIXTURES / "canvas_absent.json").read_text(encoding="utf-8")
)


def test_parse_colors_from_fixture() -> None:
    colors = parse_colors(COLORS_BODY["data"]["extractedColors"])
    assert isinstance(colors, Colors)
    for value in (colors.raw, colors.dark, colors.light):
        assert value.startswith("#") and len(value) == 7
    assert isinstance(colors.is_fallback, bool)
    # JSON round-trip stays lossless.
    assert Colors.from_dict(colors.to_dict()) == colors


def test_parse_colors_empty_raises() -> None:
    with pytest.raises(ParsingError):
        parse_colors([])


def test_parse_colors_missing_hex_raises() -> None:
    with pytest.raises(ParsingError):
        parse_colors([{"colorRaw": {}, "colorDark": {}, "colorLight": {}}])


def test_parse_canvas_present() -> None:
    canvas = parse_canvas(CANVAS_BODY["data"]["trackUnion"]["canvas"])
    assert isinstance(canvas, Canvas)
    assert canvas.url.startswith("https://")
    assert canvas.uri.startswith("spotify:canvas:")
    assert canvas.id == canvas.uri.rsplit(":", 1)[-1]
    assert canvas.canvas_type
    assert Canvas.from_dict(canvas.to_dict()) == canvas


def test_parse_canvas_absent_returns_none() -> None:
    assert parse_canvas(CANVAS_ABSENT["data"]["trackUnion"]["canvas"]) is None
    assert parse_canvas(None) is None


def test_parse_canvas_without_url_returns_none() -> None:
    assert parse_canvas({"uri": "spotify:canvas:x", "type": "VIDEO_LOOPING"}) is None
