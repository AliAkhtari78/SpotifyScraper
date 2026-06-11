"""Podcast episode model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import Image, ShowRef
from spotify_scraper.urls import entity_url


@dataclass(frozen=True, slots=True)
class Episode(ModelBase):
    """A podcast episode.

    Tier-1-only fields (``show``, ``share_url``) are ``None`` when the
    episode was built from an embed payload.
    """

    id: str
    uri: str
    name: str
    duration_ms: int
    description: str = ""
    explicit: bool = False
    playable: bool = True
    release_date: datetime | None = None
    images: tuple[Image, ...] = ()
    preview_url: str | None = None
    show: ShowRef | None = None
    share_url: str | None = None

    @property
    def url(self) -> str:
        """Canonical ``open.spotify.com`` URL for this episode."""
        return entity_url("episode", self.id)
