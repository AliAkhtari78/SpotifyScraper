"""SpotifyScraper - Modern Spotify Web Scraper.

A fast, modern Python library for extracting data from Spotify's web player.
Supports tracks, albums, artists, playlists, and lyrics with both requests and 
Selenium backends.

This package provides a high-level interface for extracting metadata from Spotify's
web player without requiring API authentication. It parses Spotify's React-based
web interface to extract structured data.

Key Features:
    - Extract metadata for tracks, albums, artists, and playlists
    - Download preview audio clips and cover images
    - Support for both lightweight (requests) and full (Selenium) browsers
    - No API key required - works with public Spotify web pages
    - Type-safe data structures using TypedDict
    - Comprehensive error handling with specific exception types

Typical usage example:
    from spotify_scraper import SpotifyClient
    
    # Create a client
    client = SpotifyClient()
    
    # Extract track information
    track_data = client.get_track_info("https://open.spotify.com/track/...")
    print(f"Track: {track_data['name']} by {track_data['artists'][0]['name']}")
    
    # Download preview and cover
    client.download_preview_mp3(track_url, path="downloads/")
    client.download_cover(track_url, path="covers/")

For authenticated features (e.g., lyrics), provide cookies:
    client = SpotifyClient(cookie_file="cookies.txt")
    track_with_lyrics = client.get_track_info_with_lyrics(track_url)

Note:
    This library is designed for educational and personal use. Always respect
    Spotify's Terms of Service and robots.txt when using this library.
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
