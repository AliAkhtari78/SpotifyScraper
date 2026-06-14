"""SpotifyScraper: extract public Spotify data without the official API.

The public surface is the two client facades, the HTTP configuration objects,
the typed entity models, and the exception hierarchy. Everything else is an
implementation detail.
"""

from __future__ import annotations

from spotify_scraper._async import AsyncSpotifyClient
from spotify_scraper._sync import SpotifyClient
from spotify_scraper.batch import BatchItem
from spotify_scraper.errors import (
    AuthenticationError,
    MediaError,
    NetworkError,
    NotFoundError,
    ParsingError,
    RateLimitedError,
    SpotifyScraperError,
    TokenError,
    URLError,
)
from spotify_scraper.http import RateLimit, RetryPolicy
from spotify_scraper.models import (
    Album,
    AlbumRef,
    Artist,
    ArtistRef,
    Episode,
    Image,
    Lyrics,
    LyricsLine,
    Playlist,
    PlaylistTrack,
    Show,
    ShowRef,
    Track,
    UserRef,
)

__version__ = "3.2.0"

__all__ = [
    "Album",
    "AlbumRef",
    "Artist",
    "ArtistRef",
    "AsyncSpotifyClient",
    "AuthenticationError",
    "BatchItem",
    "Episode",
    "Image",
    "Lyrics",
    "LyricsLine",
    "MediaError",
    "NetworkError",
    "NotFoundError",
    "ParsingError",
    "Playlist",
    "PlaylistTrack",
    "RateLimit",
    "RateLimitedError",
    "RetryPolicy",
    "Show",
    "ShowRef",
    "SpotifyClient",
    "SpotifyScraperError",
    "TokenError",
    "Track",
    "URLError",
    "UserRef",
    "__version__",
]
