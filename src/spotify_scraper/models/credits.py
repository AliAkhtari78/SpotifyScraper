"""Track-credits models (performers, writers, producers)."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.base import ModelBase


@dataclass(frozen=True, slots=True)
class CreditArtist(ModelBase):
    """A person credited on a track, with their sub-roles."""

    name: str
    uri: str = ""
    image_url: str | None = None
    subroles: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CreditRole(ModelBase):
    """A credit role (e.g. ``"Performers"``, ``"Writers"``, ``"Producers"``)."""

    title: str
    artists: tuple[CreditArtist, ...] = ()


@dataclass(frozen=True, slots=True)
class Credits(ModelBase):
    """A track's credits, grouped by role.

    Returned by :meth:`SpotifyClient.get_credits` (an authenticated feature).
    """

    track_uri: str
    track_title: str
    roles: tuple[CreditRole, ...] = ()
    source_names: tuple[str, ...] = ()
