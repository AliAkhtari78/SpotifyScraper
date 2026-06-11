"""Podcast show model."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import Image
from spotify_scraper.models.episode import Episode
from spotify_scraper.urls import entity_url


@dataclass(frozen=True, slots=True)
class Show(ModelBase):
    """A podcast show.

    Tier-1-only fields (``publisher``, ``media_type``, ``total_episodes``,
    ``rating``, ``share_url``) are ``None`` when the show was built from an
    embed payload.
    """

    id: str
    uri: str
    name: str
    description: str = ""
    publisher: str | None = None
    media_type: str | None = None
    images: tuple[Image, ...] = ()
    total_episodes: int | None = None
    episodes: tuple[Episode, ...] = ()
    topics: tuple[str, ...] = ()
    rating: float | None = None
    share_url: str | None = None

    @property
    def url(self) -> str:
        """Canonical ``open.spotify.com`` URL for this show."""
        return entity_url("show", self.id)
