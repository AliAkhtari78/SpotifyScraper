"""Artist entity model."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import AlbumRef, Image
from spotify_scraper.models.track import Track
from spotify_scraper.urls import entity_url


@dataclass(frozen=True, slots=True)
class Artist(ModelBase):
    """A Spotify artist.

    Tier-1-only fields (``biography``, ``followers``, ``monthly_listeners``,
    ``world_rank``, ``share_url``) default to ``None``; discography
    collections default to empty tuples.
    """

    id: str
    uri: str
    name: str
    images: tuple[Image, ...]
    biography: str | None = None
    followers: int | None = None
    monthly_listeners: int | None = None
    world_rank: int | None = None
    top_tracks: tuple[Track, ...] = ()
    albums: tuple[AlbumRef, ...] = ()
    singles: tuple[AlbumRef, ...] = ()
    external_links: tuple[str, ...] = ()
    share_url: str | None = None

    @property
    def url(self) -> str:
        """Canonical ``open.spotify.com`` URL for this artist."""
        return entity_url("artist", self.id)
