"""Typed, immutable models for public Spotify entities."""

from __future__ import annotations

from spotify_scraper.models.account import Account
from spotify_scraper.models.album import Album
from spotify_scraper.models.artist import Artist
from spotify_scraper.models.common import AlbumRef, ArtistRef, Image, ShowRef, UserRef
from spotify_scraper.models.episode import Episode
from spotify_scraper.models.lyrics import Lyrics, LyricsLine
from spotify_scraper.models.playlist import Playlist, PlaylistTrack
from spotify_scraper.models.show import Show
from spotify_scraper.models.track import Track
from spotify_scraper.models.transcript import Transcript, TranscriptLine

__all__ = [
    "Account",
    "Album",
    "AlbumRef",
    "Artist",
    "ArtistRef",
    "Episode",
    "Image",
    "Lyrics",
    "LyricsLine",
    "Playlist",
    "PlaylistTrack",
    "Show",
    "ShowRef",
    "Track",
    "Transcript",
    "TranscriptLine",
    "UserRef",
]
