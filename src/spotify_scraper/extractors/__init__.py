"""
Extractors package for SpotifyScraper.

This package provides classes for extracting data from Spotify web pages.
"""

from spotify_scraper.extractors.album import AlbumExtractor
from spotify_scraper.extractors.artist import ArtistExtractor
from spotify_scraper.extractors.episode import EpisodeExtractor
from spotify_scraper.extractors.lyrics import LyricsExtractor
from spotify_scraper.extractors.playlist import PlaylistExtractor
from spotify_scraper.extractors.show import ShowExtractor
from spotify_scraper.extractors.track import TrackExtractor

__all__ = [
    "TrackExtractor",
    "AlbumExtractor",
    "ArtistExtractor",
    "PlaylistExtractor",
    "EpisodeExtractor",
    "ShowExtractor",
    "LyricsExtractor",
]
