"""Construction, immutability, and serialization tests for Track and Album.

Instances are built from the real captured payloads in ``tests/fixtures/``:
fully-populated ones from pathfinder (tier 1) data, minimal ones from embed
(tier 2) data.
"""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.models.album import Album
from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import AlbumRef, ArtistRef, Image
from spotify_scraper.models.track import Track

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def _fixture(name: str) -> dict[str, Any]:
    with (FIXTURES / name).open(encoding="utf-8") as handle:
        data: dict[str, Any] = json.load(handle)
        return data


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _pathfinder_images(sources: list[dict[str, Any]]) -> tuple[Image, ...]:
    return tuple(Image(url=s["url"], width=s["width"], height=s["height"]) for s in sources)


def _embed_images(sources: list[dict[str, Any]]) -> tuple[Image, ...]:
    return tuple(Image(url=s["url"], width=s["maxWidth"], height=s["maxHeight"]) for s in sources)


@pytest.fixture(scope="module")
def full_track() -> Track:
    data = _fixture("pathfinder/track.json")["data"]["trackUnion"]
    album = data["albumOfTrack"]
    artist = data["firstArtist"]["items"][0]
    embed = _fixture("embed/track.json")["props"]["pageProps"]["state"]["data"]["entity"]
    images = _pathfinder_images(album["coverArt"]["sources"])
    return Track(
        id=data["id"],
        uri=data["uri"],
        name=data["name"],
        duration_ms=data["duration"]["totalMilliseconds"],
        explicit=data["contentRating"]["label"] == "EXPLICIT",
        playable=data["playability"]["playable"],
        preview_url=embed["audioPreview"]["url"],
        artists=(ArtistRef(name=artist["profile"]["name"], uri=artist["uri"], id=artist["id"]),),
        images=images,
        release_date=_parse_iso(album["date"]["isoString"]),
        album=AlbumRef(id=album["id"], uri=album["uri"], name=album["name"], images=images),
        track_number=data["trackNumber"],
        play_count=int(data["playcount"]),
        share_url=data["sharingInfo"]["shareUrl"],
    )


@pytest.fixture(scope="module")
def embed_track() -> Track:
    entity = _fixture("embed/track.json")["props"]["pageProps"]["state"]["data"]["entity"]
    return Track(
        id=entity["id"],
        uri=entity["uri"],
        name=entity["name"],
        duration_ms=entity["duration"],
        explicit=entity["isExplicit"],
        playable=entity["isPlayable"],
        preview_url=entity["audioPreview"]["url"],
        artists=tuple(ArtistRef(name=a["name"], uri=a["uri"]) for a in entity["artists"]),
        images=_embed_images(entity["visualIdentity"]["image"]),
        release_date=_parse_iso(entity["releaseDate"]["isoString"]),
    )


@pytest.fixture(scope="module")
def full_album() -> Album:
    data = _fixture("pathfinder/album.json")["data"]["albumUnion"]
    album_id = data["uri"].rsplit(":", maxsplit=1)[-1]
    tracks = tuple(
        Track(
            id=item["track"]["uri"].rsplit(":", maxsplit=1)[-1],
            uri=item["track"]["uri"],
            name=item["track"]["name"],
            duration_ms=item["track"]["duration"]["totalMilliseconds"],
            explicit=item["track"]["contentRating"]["label"] == "EXPLICIT",
            playable=item["track"]["playability"]["playable"],
            preview_url=None,
            artists=tuple(
                ArtistRef(name=a["profile"]["name"], uri=a["uri"])
                for a in item["track"]["artists"]["items"]
            ),
            images=(),
            release_date=None,
            track_number=item["track"]["trackNumber"],
            play_count=int(item["track"]["playcount"]),
        )
        for item in data["tracksV2"]["items"][:2]
    )
    return Album(
        id=album_id,
        uri=data["uri"],
        name=data["name"],
        album_type=data["type"].lower(),
        images=_pathfinder_images(data["coverArt"]["sources"]),
        release_date=_parse_iso(data["date"]["isoString"]),
        artists=tuple(
            ArtistRef(name=a["profile"]["name"], uri=a["uri"], id=a["id"])
            for a in data["artists"]["items"]
        ),
        label=data["label"],
        total_tracks=data["tracksV2"]["totalCount"],
        tracks=tracks,
        copyrights=tuple(item["text"] for item in data["copyright"]["items"]),
        share_url=data["sharingInfo"]["shareUrl"],
    )


@pytest.fixture(scope="module")
def embed_album() -> Album:
    entity = _fixture("embed/album.json")["props"]["pageProps"]["state"]["data"]["entity"]
    return Album(
        id=entity["id"],
        uri=entity["uri"],
        name=entity["name"],
        album_type=entity["type"],
        images=_embed_images(entity["visualIdentity"]["image"]),
        release_date=None,
        artists=(),
    )


ALL_MODELS = ["full_track", "embed_track", "full_album", "embed_album"]


def test_full_track_field_values(full_track: Track) -> None:
    assert full_track.id == "4uLU6hMCjMI75M1A2tKUQC"
    assert full_track.name == "Never Gonna Give You Up"
    assert full_track.duration_ms == 213573
    assert full_track.explicit is False
    assert full_track.playable is True
    assert full_track.play_count == 1137719792
    assert full_track.track_number == 1
    assert full_track.album is not None
    assert full_track.album.name == "Whenever You Need Somebody"
    assert full_track.release_date == datetime(1987, 11, 12, tzinfo=timezone.utc)
    assert full_track.share_url is not None
    assert full_track.share_url.startswith("https://open.spotify.com/track/")


def test_embed_track_tier1_fields_default_none(embed_track: Track) -> None:
    assert embed_track.album is None
    assert embed_track.track_number is None
    assert embed_track.play_count is None
    assert embed_track.share_url is None
    assert embed_track.preview_url is not None
    assert embed_track.artists == (
        ArtistRef(name="Rick Astley", uri="spotify:artist:0gxyHStUsqpMadRV0Di1Qt"),
    )
    assert len(embed_track.images) == 3


def test_full_album_field_values(full_album: Album) -> None:
    assert full_album.id == "6N9PS4QXF1D0OWPk0Sxtb4"
    assert full_album.album_type == "album"
    assert full_album.label == "Sony Music CG"
    assert full_album.total_tracks == 10
    assert len(full_album.tracks) == 2
    assert full_album.tracks[0].explicit is False
    assert full_album.copyrights == (
        "(P) 1987 Sony Music Entertainment UK Limited under exclusive license to "
        "BMG Rights Management (UK) Limited",
    )
    assert full_album.release_date == datetime(1987, 11, 12, tzinfo=timezone.utc)


def test_embed_album_tier1_fields_default(embed_album: Album) -> None:
    assert embed_album.label is None
    assert embed_album.total_tracks is None
    assert embed_album.tracks == ()
    assert embed_album.copyrights == ()
    assert embed_album.share_url is None


def test_track_is_frozen(embed_track: Track) -> None:
    with pytest.raises(FrozenInstanceError):
        embed_track.name = "mutated"  # type: ignore[misc]


def test_album_is_frozen(embed_album: Album) -> None:
    with pytest.raises(FrozenInstanceError):
        embed_album.label = "mutated"  # type: ignore[misc]


def test_track_url_derived_and_not_serialized(full_track: Track) -> None:
    assert full_track.url == "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
    assert "url" not in full_track.to_dict()


def test_album_url_derived_and_not_serialized(full_album: Album) -> None:
    assert full_album.url == "https://open.spotify.com/album/6N9PS4QXF1D0OWPk0Sxtb4"
    assert "url" not in full_album.to_dict()


@pytest.mark.parametrize("name", ALL_MODELS)
def test_round_trip_equality(name: str, request: pytest.FixtureRequest) -> None:
    model: ModelBase = request.getfixturevalue(name)
    assert type(model).from_dict(model.to_dict()) == model


@pytest.mark.parametrize("name", ALL_MODELS)
def test_to_dict_is_json_safe(name: str, request: pytest.FixtureRequest) -> None:
    model: ModelBase = request.getfixturevalue(name)
    json.dumps(model.to_dict())


def test_round_trip_rebuilds_nested_models(full_album: Album) -> None:
    rebuilt = Album.from_dict(full_album.to_dict())
    assert isinstance(rebuilt.tracks, tuple)
    assert all(isinstance(track, Track) for track in rebuilt.tracks)
    assert all(isinstance(artist, ArtistRef) for artist in rebuilt.tracks[0].artists)
    assert isinstance(rebuilt.release_date, datetime)
