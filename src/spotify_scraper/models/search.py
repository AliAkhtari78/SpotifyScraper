"""Aggregate search results model."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.artist import Artist
from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import AlbumRef, ShowRef
from spotify_scraper.models.episode import Episode
from spotify_scraper.models.playlist import Playlist
from spotify_scraper.models.track import Track


@dataclass(frozen=True, slots=True)
class SearchResults(ModelBase):
    """The results of an aggregate Spotify search.

    Each tuple holds the hits for one entity type, reusing the existing entity
    and reference models. Search hits are sparse: tier-1-only fields absent from
    the search payload stay ``None``/``()``. Albums and shows are returned as the
    lightweight :class:`AlbumRef`/:class:`ShowRef` (search returns no
    tracklist/discography for them).
    """

    query: str
    tracks: tuple[Track, ...] = ()
    artists: tuple[Artist, ...] = ()
    albums: tuple[AlbumRef, ...] = ()
    playlists: tuple[Playlist, ...] = ()
    shows: tuple[ShowRef, ...] = ()
    episodes: tuple[Episode, ...] = ()
    total: int | None = None
