"""
SpotifyScraper 2.0 - Modern Spotify Web Scraper

A fast, modern Python library for extracting data from Spotify's web player.
Supports tracks, albums, artists, playlists, and lyrics with both requests and Selenium backends.
"""

__version__ = "2.0.0"
__author__ = "Ali Akhtari"
__email__ = "aliakhtari78@hotmail.com"
__license__ = "MIT"
__url__ = "https://github.com/AliAkhtari78/SpotifyScraper"

# Core imports for easy access
from spotify_scraper.client import SpotifyClient
from spotify_scraper.core.exceptions import (
    SpotifyScraperError,
    URLError,
    ParsingError,
    ExtractionError,
    NetworkError,
    AuthenticationError,
    BrowserError,
    MediaError,
)

# Utility functions
from spotify_scraper.utils.url import (
    is_spotify_url,
    extract_id,
    convert_to_embed_url,
)

# No backward compatibility needed

__all__ = [
    "SpotifyClient",
    "is_spotify_url",
    "extract_id", 
    "convert_to_embed_url",
    "SpotifyScraperError",
    "URLError",
    "ParsingError",
    "ExtractionError",
    "NetworkError",
    "AuthenticationError",
    "BrowserError",
    "MediaError",
]

# Package metadata
__title__ = "spotifyscraper"
__description__ = "A modern Python library for extracting data from Spotify's web interface"
__version_info__ = tuple(int(part) for part in __version__.split('.'))
