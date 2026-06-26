"""SpotifyScraper: extract public Spotify data without the official API.

The public surface is the two client facades, the HTTP configuration objects,
the typed entity models, and the exception hierarchy. Everything else is an
implementation detail.
"""

from __future__ import annotations

from spotify_scraper._async import AsyncSpotifyClient
from spotify_scraper._sync import SpotifyClient
from spotify_scraper.auth.session import SessionInfo
from spotify_scraper.batch import BatchItem
from spotify_scraper.errors import (
    AuthenticationError,
    MediaError,
    NetworkError,
    NotFoundError,
    ParsingError,
    RateLimitedError,
    SessionError,
    SpotifyScraperError,
    TokenError,
    URLError,
)
from spotify_scraper.http import (
    AsyncCachingTransport,
    CacheConfig,
    CachingTransport,
    DiskCache,
    FileCache,
    RateLimit,
    RetryPolicy,
)
from spotify_scraper.models import (
    Account,
    Album,
    AlbumRef,
    Artist,
    ArtistRef,
    Canvas,
    Colors,
    Concert,
    CreditArtist,
    CreditRole,
    Credits,
    Episode,
    Image,
    Lyrics,
    LyricsLine,
    Playlist,
    PlaylistTrack,
    SearchResults,
    Show,
    ShowRef,
    Track,
    Transcript,
    TranscriptLine,
    UserProfile,
    UserRef,
)

__version__ = "3.9.2"

__all__ = [
    "Account",
    "Album",
    "AlbumRef",
    "Artist",
    "ArtistRef",
    "AsyncCachingTransport",
    "AsyncSpotifyClient",
    "AuthenticationError",
    "BatchItem",
    "CacheConfig",
    "CachingTransport",
    "Canvas",
    "Colors",
    "Concert",
    "CreditArtist",
    "CreditRole",
    "Credits",
    "DiskCache",
    "Episode",
    "FileCache",
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
    "SearchResults",
    "SessionError",
    "SessionInfo",
    "Show",
    "ShowRef",
    "SpotifyClient",
    "SpotifyScraperError",
    "TokenError",
    "Track",
    "Transcript",
    "TranscriptLine",
    "URLError",
    "UserProfile",
    "UserRef",
    "__version__",
]
