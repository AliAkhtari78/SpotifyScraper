"""Round-trip tests for ModelBase serialization via the common value models."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import AlbumRef, ArtistRef, Image, ShowRef, UserRef


@dataclass(frozen=True, slots=True)
class _Stamped(ModelBase):
    name: str
    released: datetime | None = None


IMAGES = (
    Image(url="https://i.scdn.co/image/ab67616d00001e02", width=300, height=300),
    Image(url="https://i.scdn.co/image/ab67616d00004851", width=64, height=64),
)

FULL_INSTANCES = [
    Image(url="https://i.scdn.co/image/abc", width=640, height=640),
    ArtistRef(
        name="Daft Punk", uri="spotify:artist:4tZwfgrHOc3mvqYlEYSvVi", id="4tZwfgrHOc3mvqYlEYSvVi"
    ),
    AlbumRef(
        id="4m2880jivSbbyEGAKfITCa",
        uri="spotify:album:4m2880jivSbbyEGAKfITCa",
        name="Random Access Memories",
        images=IMAGES,
    ),
    ShowRef(
        id="4rOoJ6Egrf8K2IrywzwOMk",
        uri="spotify:show:4rOoJ6Egrf8K2IrywzwOMk",
        name="The Joe Rogan Experience",
        publisher="Joe Rogan",
        images=IMAGES,
    ),
    UserRef(name="Spotify", uri="spotify:user:spotify"),
    _Stamped(name="stamped", released=datetime(2013, 5, 17, 0, 0, tzinfo=timezone.utc)),
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


def test_nested_tuple_serializes_to_list_of_dicts() -> None:
    album = AlbumRef(id="a" * 22, uri="spotify:album:" + "a" * 22, name="Nested", images=IMAGES)
    data = album.to_dict()
    assert data["images"] == [
        {"url": IMAGES[0].url, "width": 300, "height": 300},
        {"url": IMAGES[1].url, "width": 64, "height": 64},
    ]


def test_nested_tuple_rebuilds_as_tuple_of_models() -> None:
    album = AlbumRef(id="a" * 22, uri="spotify:album:" + "a" * 22, name="Nested", images=IMAGES)
    rebuilt = AlbumRef.from_dict(album.to_dict())
    assert isinstance(rebuilt.images, tuple)
    assert all(isinstance(image, Image) for image in rebuilt.images)
    assert rebuilt == album


def test_empty_tuple_round_trip() -> None:
    album = AlbumRef(id="b" * 22, uri="spotify:album:" + "b" * 22, name="Bare")
    data = album.to_dict()
    assert data["images"] == []
    assert AlbumRef.from_dict(data).images == ()


def test_none_fields_round_trip() -> None:
    image = Image(url="https://i.scdn.co/image/xyz")
    data = image.to_dict()
    assert data == {"url": "https://i.scdn.co/image/xyz", "width": None, "height": None}
    assert Image.from_dict(data) == image


def test_optional_model_field_none_round_trip() -> None:
    show = ShowRef(id="c" * 22, uri="spotify:show:" + "c" * 22, name="Quiet")
    data = show.to_dict()
    assert data["publisher"] is None
    rebuilt = ShowRef.from_dict(data)
    assert rebuilt.publisher is None
    assert rebuilt == show


def test_from_dict_missing_keys_use_defaults() -> None:
    artist = ArtistRef.from_dict({"name": "Underworld"})
    assert artist == ArtistRef(name="Underworld", uri="", id="")
    user = UserRef.from_dict({"name": "listener"})
    assert user.uri == ""


def test_datetime_serializes_to_isoformat_string() -> None:
    released = datetime(2013, 5, 17, 12, 30, 45, tzinfo=timezone.utc)
    stamped = _Stamped(name="rt", released=released)
    data = stamped.to_dict()
    assert data["released"] == released.isoformat()
    assert _Stamped.from_dict(data) == stamped


def test_datetime_none_round_trip() -> None:
    stamped = _Stamped(name="no-date")
    data = stamped.to_dict()
    assert data["released"] is None
    assert _Stamped.from_dict(data) == stamped
