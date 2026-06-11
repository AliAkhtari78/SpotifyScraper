"""Track entity model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from spotify_scraper import urls
from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import AlbumRef, ArtistRef, Image


@dataclass(frozen=True, slots=True)
class Track(ModelBase):
    """A Spotify track.

    Tier-1-only fields (``album``, ``track_number``, ``play_count``,
    ``share_url``) stay ``None`` when built from embed data alone.
    """

    id: str
    uri: str
    name: str
    duration_ms: int
    explicit: bool
    playable: bool
    preview_url: str | None
    artists: tuple[ArtistRef, ...]
    images: tuple[Image, ...]
    release_date: datetime | None
    album: AlbumRef | None = None
    track_number: int | None = None
    play_count: int | None = None
    share_url: str | None = None

    @property
    def url(self) -> str:
        """Canonical ``open.spotify.com`` URL for this track."""
        return urls.entity_url("track", self.id)
