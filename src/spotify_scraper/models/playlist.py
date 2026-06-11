"""Playlist entity model and its track wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import Image, UserRef
from spotify_scraper.models.track import Track
from spotify_scraper.urls import entity_url


@dataclass(frozen=True, slots=True)
class PlaylistTrack(ModelBase):
    """A track entry in a playlist, with playlist-specific metadata."""

    track: Track
    added_at: datetime | None = None
    added_by: UserRef | None = None


@dataclass(frozen=True, slots=True)
class Playlist(ModelBase):
    """A Spotify playlist."""

    id: str
    uri: str
    name: str
    description: str = ""
    owner: UserRef | None = None
    followers: int | None = None
    images: tuple[Image, ...] = ()
    total_tracks: int | None = None
    tracks: tuple[PlaylistTrack, ...] = ()
    share_url: str | None = None

    @property
    def url(self) -> str:
        """Canonical ``open.spotify.com`` URL for this playlist."""
        return entity_url("playlist", self.id)
