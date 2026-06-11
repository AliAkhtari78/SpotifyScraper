"""Contract and round-trip tests for Episode, Show, and Lyrics models."""

from __future__ import annotations

import dataclasses
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import Image, ShowRef
from spotify_scraper.models.episode import Episode
from spotify_scraper.models.lyrics import Lyrics, LyricsLine
from spotify_scraper.models.show import Show

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def _load(path: str) -> dict[str, Any]:
    raw: dict[str, Any] = json.loads((FIXTURES / path).read_text())
    return raw


def _iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _episode_from_fixtures() -> Episode:
    payload = _load("pathfinder/episode.json")["data"]["episodeUnionV2"]
    embed = _load("embed/episode.json")["props"]["pageProps"]["state"]["data"]["entity"]
    show = payload["podcastV2"]["data"]
    return Episode(
        id=payload["id"],
        uri=payload["uri"],
        name=payload["name"],
        duration_ms=payload["duration"]["totalMilliseconds"],
        description=payload["description"],
        explicit=payload["contentRating"]["label"] == "EXPLICIT",
        playable=payload["playability"]["playable"],
        release_date=_iso(payload["releaseDate"]["isoString"]),
        images=tuple(
            Image(url=img["url"], width=img["maxWidth"], height=img["maxHeight"])
            for img in embed["visualIdentity"]["image"]
        ),
        preview_url=payload["previewPlayback"]["audioPreview"]["cdnUrl"],
        show=ShowRef(id=show["uri"].rsplit(":", 1)[-1], uri=show["uri"], name=show["name"]),
        share_url=payload["sharingInfo"]["shareUrl"],
    )


def _show_from_fixtures() -> Show:
    payload = _load("pathfinder/show.json")["data"]["podcastUnionV2"]
    return Show(
        id=payload["id"],
        uri=payload["uri"],
        name=payload["name"],
        description=payload["description"],
        publisher=payload["publisher"]["name"],
        media_type=payload["mediaType"],
        images=tuple(
            Image(url=img["url"], width=img["width"], height=img["height"])
            for img in payload["coverArt"]["sources"]
        ),
        total_episodes=len(payload["episodesV2"]["items"]),
        episodes=(_episode_from_fixtures(),),
        topics=tuple(topic["title"] for topic in payload["topics"]["items"]),
        rating=payload["rating"]["averageRating"]["average"],
        share_url=payload["sharingInfo"]["shareUrl"],
    )


def _lyrics_full() -> Lyrics:
    return Lyrics(
        lines=(
            LyricsLine(start_ms=0, text="Like the legend of the phoenix"),
            LyricsLine(start_ms=12450, text="All ends with beginnings"),
        ),
        sync_type="LINE_SYNCED",
        provider="MusixMatch",
        language="en",
    )


FULL_INSTANCES = [
    _episode_from_fixtures(),
    _show_from_fixtures(),
    _lyrics_full(),
    LyricsLine(start_ms=3070, text="What keeps the planet spinning"),
]


def _assert_json_primitives(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            assert isinstance(key, str)
            _assert_json_primitives(item)
    elif isinstance(value, list):
        for item in value:
            _assert_json_primitives(item)
    else:
        assert value is None or isinstance(value, (str, int, float, bool))


@pytest.mark.parametrize("instance", FULL_INSTANCES, ids=lambda m: type(m).__name__)
def test_round_trip_equality(instance: ModelBase) -> None:
    assert type(instance).from_dict(instance.to_dict()) == instance


@pytest.mark.parametrize("instance", FULL_INSTANCES, ids=lambda m: type(m).__name__)
def test_to_dict_is_json_safe(instance: ModelBase) -> None:
    data = instance.to_dict()
    _assert_json_primitives(data)
    json.dumps(data)


@pytest.mark.parametrize("instance", FULL_INSTANCES, ids=lambda m: type(m).__name__)
def test_models_are_frozen(instance: ModelBase) -> None:
    field_name = dataclasses.fields(instance)[0].name  # type: ignore[arg-type]
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(instance, field_name, "mutated")


def test_episode_embed_only_construction() -> None:
    embed = _load("embed/episode.json")["props"]["pageProps"]["state"]["data"]["entity"]
    episode = Episode(
        id=embed["id"],
        uri=embed["uri"],
        name=embed["name"],
        duration_ms=embed["duration"],
        explicit=embed["isExplicit"],
        playable=embed["isPlayable"],
        release_date=_iso(embed["releaseDate"]["isoString"]),
        preview_url=embed["audioPreview"]["url"],
    )
    assert episode.description == ""
    assert episode.images == ()
    assert episode.show is None
    assert episode.share_url is None


def test_show_minimal_construction_defaults() -> None:
    show = Show(id="4rOoJ6Egrf8K2IrywzwOMk", uri="spotify:show:4rOoJ6Egrf8K2IrywzwOMk", name="JRE")
    assert show.description == ""
    assert show.publisher is None
    assert show.media_type is None
    assert show.images == ()
    assert show.total_episodes is None
    assert show.episodes == ()
    assert show.topics == ()
    assert show.rating is None
    assert show.share_url is None


def test_episode_url_property() -> None:
    episode = _episode_from_fixtures()
    assert episode.url == f"https://open.spotify.com/episode/{episode.id}"
    assert "url" not in episode.to_dict()


def test_show_url_property() -> None:
    show = _show_from_fixtures()
    assert show.url == f"https://open.spotify.com/show/{show.id}"
    assert "url" not in show.to_dict()


def test_show_nested_episodes_rebuild_as_models() -> None:
    show = _show_from_fixtures()
    rebuilt = Show.from_dict(show.to_dict())
    assert isinstance(rebuilt.episodes, tuple)
    assert all(isinstance(episode, Episode) for episode in rebuilt.episodes)
    assert all(isinstance(episode.show, ShowRef) for episode in rebuilt.episodes)
    assert isinstance(rebuilt.topics, tuple)
    assert rebuilt == show


def test_episode_release_date_serializes_to_isoformat() -> None:
    episode = _episode_from_fixtures()
    data = episode.to_dict()
    assert episode.release_date is not None
    assert data["release_date"] == episode.release_date.isoformat()
    assert Episode.from_dict(data).release_date == episode.release_date


def test_lyrics_defaults() -> None:
    lyrics = Lyrics(lines=(LyricsLine(start_ms=0, text="Instrumental"),))
    assert lyrics.sync_type == "UNSYNCED"
    assert lyrics.provider is None
    assert lyrics.language is None


def test_lyrics_lines_rebuild_as_models() -> None:
    lyrics = _lyrics_full()
    rebuilt = Lyrics.from_dict(lyrics.to_dict())
    assert isinstance(rebuilt.lines, tuple)
    assert all(isinstance(line, LyricsLine) for line in rebuilt.lines)
    assert rebuilt == lyrics


def test_lyrics_empty_lines_round_trip() -> None:
    lyrics = Lyrics(lines=())
    data = lyrics.to_dict()
    assert data["lines"] == []
    assert Lyrics.from_dict(data) == lyrics
