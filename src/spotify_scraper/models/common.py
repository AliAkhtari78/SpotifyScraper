"""Shared value objects embedded in entity models."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.base import ModelBase


@dataclass(frozen=True, slots=True)
class Image(ModelBase):
    """An image source with optional pixel dimensions."""

    url: str
    width: int | None = None
    height: int | None = None


@dataclass(frozen=True, slots=True)
class ArtistRef(ModelBase):
    """Lightweight reference to an artist.

    Embed payloads provide ``name`` (and sometimes ``uri``); pathfinder
    payloads provide all fields.
    """

    name: str
    uri: str = ""
    id: str = ""


@dataclass(frozen=True, slots=True)
class AlbumRef(ModelBase):
    """Lightweight reference to an album."""

    id: str
    uri: str
    name: str
    images: tuple[Image, ...] = ()


@dataclass(frozen=True, slots=True)
class ShowRef(ModelBase):
    """Lightweight reference to a podcast show."""

    id: str
    uri: str
    name: str
    publisher: str | None = None
    images: tuple[Image, ...] = ()


@dataclass(frozen=True, slots=True)
class UserRef(ModelBase):
    """Lightweight reference to a Spotify user."""

    name: str
    uri: str = ""
