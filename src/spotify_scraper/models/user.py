"""Public Spotify user-profile model."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.base import ModelBase
from spotify_scraper.models.common import ArtistRef, Image
from spotify_scraper.models.playlist import Playlist


@dataclass(frozen=True, slots=True)
class UserProfile(ModelBase):
    """A public Spotify user profile.

    Returned by :meth:`SpotifyClient.get_user` (an authenticated feature). Every
    count and listing reflects only what the user has made public;
    ``recently_played_artists`` is populated for some accounts and empty for
    others (e.g. the official ``spotify`` account exposes none).
    """

    id: str
    uri: str
    name: str
    images: tuple[Image, ...] = ()
    followers_count: int | None = None
    following_count: int | None = None
    public_playlists: tuple[Playlist, ...] = ()
    public_playlists_total: int | None = None
    recently_played_artists: tuple[ArtistRef, ...] = ()
    is_verified: bool | None = None
