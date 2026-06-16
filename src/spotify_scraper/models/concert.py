"""Artist concert/event model."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import ArtistRef


@dataclass(frozen=True, slots=True)
class Concert(ModelBase):
    """An upcoming live event for an artist.

    Returned by :meth:`SpotifyClient.get_artist_events`. ``start_date`` is the raw
    ISO-8601 start time exactly as Spotify provides it (kept as a string for
    cross-version stability); ``artists`` are the acts on the bill.
    """

    id: str
    uri: str
    title: str
    start_date: str | None = None
    city: str | None = None
    artists: tuple[ArtistRef, ...] = ()
