"""Tests for :func:`spotify_scraper.api.parse_entities.parse_lyrics`."""

from __future__ import annotations

from typing import Any

import pytest

from spotify_scraper.api.parse_entities import parse_lyrics
from spotify_scraper.errors import ParsingError


def _payload(**overrides: Any) -> dict[str, Any]:
    lyrics: dict[str, Any] = {
        "syncType": "LINE_SYNCED",
        "provider": "MusixMatch",
        "language": "en",
        "lines": [
            {"startTimeMs": "19630", "words": "We're no strangers to love"},
            {"startTimeMs": "23400", "words": "You know the rules and so do I"},
        ],
    }
    lyrics.update(overrides)
    return {"lyrics": lyrics}


def test_parses_synced_lines() -> None:
    lyrics = parse_lyrics(_payload())
    assert lyrics.sync_type == "LINE_SYNCED"
    assert lyrics.provider == "MusixMatch"
    assert lyrics.language == "en"
    assert len(lyrics.lines) == 2
    assert lyrics.lines[0].start_ms == 19630
    assert lyrics.lines[0].text == "We're no strangers to love"


def test_start_ms_is_non_negative_int() -> None:
    lyrics = parse_lyrics(_payload())
    assert all(isinstance(line.start_ms, int) and line.start_ms >= 0 for line in lyrics.lines)


def test_empty_words_lines_are_dropped() -> None:
    lyrics = parse_lyrics(
        _payload(
            lines=[
                {"startTimeMs": "0", "words": ""},
                {"startTimeMs": "1000", "words": "real line"},
                {"startTimeMs": "2000"},
            ]
        )
    )
    assert len(lyrics.lines) == 1
    assert lyrics.lines[0].text == "real line"


def test_integer_start_time_is_accepted() -> None:
    lyrics = parse_lyrics(_payload(lines=[{"startTimeMs": 5000, "words": "hi"}]))
    assert lyrics.lines[0].start_ms == 5000


def test_unparsable_start_time_falls_back_to_zero() -> None:
    lyrics = parse_lyrics(_payload(lines=[{"startTimeMs": "abc", "words": "hi"}]))
    assert lyrics.lines[0].start_ms == 0


def test_defaults_when_metadata_absent() -> None:
    lyrics = parse_lyrics({"lyrics": {"lines": [{"startTimeMs": "0", "words": "x"}]}})
    assert lyrics.sync_type == "UNSYNCED"
    assert lyrics.provider is None
    assert lyrics.language is None


def test_missing_lyrics_object_raises() -> None:
    with pytest.raises(ParsingError):
        parse_lyrics({})


def test_missing_lines_raises() -> None:
    with pytest.raises(ParsingError):
        parse_lyrics({"lyrics": {"syncType": "UNSYNCED"}})
