"""
Extractors package for SpotifyScraper.

This package provides classes for extracting data from Spotify web pages.
"""

from spotify_scraper.extractors.track import TrackExtractor
from spotify_scraper.extractors.album import AlbumExtractor
from spotify_scraper.extractors.artist import ArtistExtractor
from spotify_scraper.extractors.playlist import PlaylistExtractor

__all__ = [
    "TrackExtractor",
    "AlbumExtractor",
    "ArtistExtractor",
    "PlaylistExtractor",
]
