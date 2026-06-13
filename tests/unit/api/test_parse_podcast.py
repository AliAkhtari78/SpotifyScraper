"""Tests for episode and show parsing from real pathfinder and embed fixtures.

Fixture note: ``pathfinder/show.json`` is a ``queryShowMetadataV2`` response,
which carries no ``episodesV2.totalCount`` and only a uri-only episode stub, so
``parse_show_gql`` alone leaves ``total_episodes`` ``None``. The full listing
comes from the separate ``queryPodcastEpisodes`` operation, captured in
``pathfinder/show_episodes.json`` and parsed by ``parse_show_episodes_page`` /
``show_episodes_total`` (tested at the bottom of this file).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.api.parse_entities import (
    parse_episode_embed,
    parse_episode_gql,
    parse_show_embed,
    parse_show_episodes_page,
    parse_show_gql,
    show_episodes_total,
)
from spotify_scraper.errors import ParsingError

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"

EPISODE_NAME = "#2512 - Joey Diaz"
EPISODE_ID = "07gKzPFkbvGF0cHoeG7ARS"
EPISODE_URI = "spotify:episode:07gKzPFkbvGF0cHoeG7ARS"
SHOW_NAME = "The Joe Rogan Experience"
SHOW_ID = "4rOoJ6Egrf8K2IrywzwOMk"
SHOW_URI = "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"


def _load(relative: str) -> dict[str, Any]:
    with (FIXTURES / relative).open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
        return data


@pytest.fixture
def episode_union() -> dict[str, Any]:
    union: dict[str, Any] = _load("pathfinder/episode.json")["data"]["episodeUnionV2"]
    return union


@pytest.fixture
def show_union() -> dict[str, Any]:
    union: dict[str, Any] = _load("pathfinder/show.json")["data"]["podcastUnionV2"]
    return union


@pytest.fixture
def episode_embed_entity() -> dict[str, Any]:
    entity: dict[str, Any] = _load("embed/episode.json")["props"]["pageProps"]["state"]["data"][
        "entity"
    ]
    return entity


@pytest.fixture
def show_embed_entity() -> dict[str, Any]:
    entity: dict[str, Any] = _load("embed/show.json")["props"]["pageProps"]["state"]["data"][
        "entity"
    ]
    return entity


# --------------------------------------------------------------------------- #
# Episode
# --------------------------------------------------------------------------- #


def test_parse_episode_gql_core_fields(episode_union: dict[str, Any]) -> None:
    episode = parse_episode_gql(episode_union)
    assert episode.id == EPISODE_ID
    assert episode.uri == EPISODE_URI
    assert episode.name == EPISODE_NAME
    assert episode.duration_ms > 0
    assert episode.explicit is True
    assert episode.playable is True
    assert episode.description


def test_parse_episode_gql_release_and_images(episode_union: dict[str, Any]) -> None:
    episode = parse_episode_gql(episode_union)
    assert episode.release_date == datetime(2026, 6, 10, 17, 0, tzinfo=timezone.utc)
    assert len(episode.images) >= 1


def test_parse_episode_gql_has_preview(episode_union: dict[str, Any]) -> None:
    episode = parse_episode_gql(episode_union)
    assert episode.preview_url is not None
    assert episode.preview_url.startswith("https://p.scdn.co/")


def test_parse_episode_gql_show_ref(episode_union: dict[str, Any]) -> None:
    episode = parse_episode_gql(episode_union)
    assert episode.show is not None
    assert episode.show.name == SHOW_NAME
    assert episode.show.id == SHOW_ID
    assert episode.show.uri == SHOW_URI
    assert len(episode.show.images) >= 1
    assert episode.share_url is not None
    assert episode.share_url.startswith("https://open.spotify.com/episode/")


def test_parse_episode_embed_core_fields(episode_embed_entity: dict[str, Any]) -> None:
    episode = parse_episode_embed(episode_embed_entity)
    assert episode.id == EPISODE_ID
    assert episode.uri == EPISODE_URI
    assert episode.name == EPISODE_NAME
    assert episode.duration_ms > 0
    assert episode.explicit is True
    assert episode.preview_url is not None


def test_parse_episode_embed_show_ref(episode_embed_entity: dict[str, Any]) -> None:
    episode = parse_episode_embed(episode_embed_entity)
    assert episode.show is not None
    assert episode.show.name == SHOW_NAME
    assert episode.show.id == SHOW_ID
    assert episode.show.uri == SHOW_URI


def test_parse_episode_embed_lacks_tier1_fields(episode_embed_entity: dict[str, Any]) -> None:
    episode = parse_episode_embed(episode_embed_entity)
    assert episode.share_url is None
    assert episode.show is not None
    assert episode.show.publisher is None


# --------------------------------------------------------------------------- #
# Show
# --------------------------------------------------------------------------- #


def test_parse_show_gql_core_fields(show_union: dict[str, Any]) -> None:
    show = parse_show_gql(show_union)
    assert show.id == SHOW_ID
    assert show.uri == SHOW_URI
    assert show.name == SHOW_NAME
    assert show.description


def test_parse_show_gql_publisher_present(show_union: dict[str, Any]) -> None:
    show = parse_show_gql(show_union)
    assert show.publisher is not None
    assert show.publisher == "Joe Rogan"
    assert show.media_type == "MIXED"


def test_parse_show_gql_omits_metadata_episode_stub(show_union: dict[str, Any]) -> None:
    # queryShowMetadataV2 carries only a uri-only episode stub; parse_show_gql
    # must NOT emit a phantom episode from it. The real listing comes from the
    # separate queryPodcastEpisodes operation.
    show = parse_show_gql(show_union)
    assert show.episodes == ()


def test_parse_show_gql_rating_and_topics(show_union: dict[str, Any]) -> None:
    show = parse_show_gql(show_union)
    assert show.rating is not None
    assert 0 < show.rating <= 5
    assert show.topics == ("Comedy",)
    assert show.share_url is not None
    assert show.share_url.startswith("https://open.spotify.com/show/")


def test_parse_show_gql_total_episodes_from_count(show_union: dict[str, Any]) -> None:
    # The captured queryShowMetadataV2 payload omits episodesV2.totalCount.
    assert show_union["episodesV2"].get("totalCount") is None
    assert parse_show_gql(show_union).total_episodes is None
    # When a totalCount is present (the rich listing case), it is surfaced.
    show_union["episodesV2"]["totalCount"] = 2512
    assert parse_show_gql(show_union).total_episodes == 2512


def test_parse_show_embed_core_fields(show_embed_entity: dict[str, Any]) -> None:
    show = parse_show_embed(show_embed_entity)
    assert show.id == SHOW_ID
    assert show.uri == SHOW_URI
    assert show.name == SHOW_NAME
    assert len(show.images) >= 1


def test_parse_show_embed_lacks_listing(show_embed_entity: dict[str, Any]) -> None:
    show = parse_show_embed(show_embed_entity)
    assert show.episodes == ()
    assert show.total_episodes is None
    assert show.publisher is None


# --------------------------------------------------------------------------- #
# Degradation
# --------------------------------------------------------------------------- #


def test_parse_episode_gql_truncated_missing_uri_raises() -> None:
    with pytest.raises(ParsingError, match=r"episodeUnionV2\.uri"):
        parse_episode_gql({"name": EPISODE_NAME, "duration": {"totalMilliseconds": 1}})


def test_parse_episode_gql_truncated_missing_duration_raises() -> None:
    with pytest.raises(ParsingError, match="duration"):
        parse_episode_gql({"uri": EPISODE_URI, "name": EPISODE_NAME})


def test_parse_show_gql_truncated_missing_name_raises() -> None:
    with pytest.raises(ParsingError, match=r"podcastUnionV2\.name"):
        parse_show_gql({"uri": SHOW_URI})


@pytest.fixture
def show_episodes_union() -> dict[str, Any]:
    union: dict[str, Any] = _load("pathfinder/show_episodes.json")["data"]["podcastUnionV2"]
    return union


def test_show_episodes_total(show_episodes_union: dict[str, Any]) -> None:
    assert show_episodes_total(show_episodes_union) == 2707


def test_parse_show_episodes_page(show_episodes_union: dict[str, Any]) -> None:
    episodes = parse_show_episodes_page(show_episodes_union)
    assert len(episodes) == 10
    assert all(ep.name for ep in episodes)
    assert all(ep.duration_ms > 0 for ep in episodes)


def test_parse_show_episodes_page_empty_is_safe() -> None:
    assert parse_show_episodes_page({}) == ()
    assert show_episodes_total({}) is None
