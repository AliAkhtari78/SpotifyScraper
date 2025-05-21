"""
SpotifyScraper 2.0 - Modern Spotify Web Scraper

A fast, modern Python library for extracting data from Spotify's web player.
Supports tracks, albums, artists, playlists, and lyrics with both requests and Selenium backends.
"""

__version__ = "2.0.0"
__author__ = "Ali Akhtari"
__email__ = "aliakhtari78@hotmail.com"

# Core imports for easy access
from spotify_scraper.core.client import SpotifyClient
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

# Backward compatibility imports
from spotify_scraper.compat import Scraper, Request

__all__ = [
    "SpotifyClient",
    "Scraper",
    "Request",
    "SpotifyScraperError",
    "URLError",
    "ParsingError",
    "ExtractionError",
    "NetworkError",
    "AuthenticationError",
    "BrowserError",
    "MediaError",
]
