"""Album entity model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from spotify_scraper import urls
from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import ArtistRef, Image
from spotify_scraper.models.track import Track


@dataclass(frozen=True, slots=True)
class Album(ModelBase):
    """A Spotify album.

    ``album_type`` is the lowercased release kind (``"album"``, ``"single"``,
    or ``"compilation"``). Tier-1-only fields default to ``None`` or empty.
    """

    id: str
    uri: str
    name: str
    album_type: str
    images: tuple[Image, ...]
    release_date: datetime | None
    artists: tuple[ArtistRef, ...]
    label: str | None = None
    total_tracks: int | None = None
    tracks: tuple[Track, ...] = ()
    copyrights: tuple[str, ...] = ()
    share_url: str | None = None

    @property
    def url(self) -> str:
        """Canonical ``open.spotify.com`` URL for this album."""
        return urls.entity_url("album", self.id)
