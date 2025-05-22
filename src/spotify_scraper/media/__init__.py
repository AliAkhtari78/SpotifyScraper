"""
Media handling package for SpotifyScraper.

This package provides functionality for downloading and processing
media files from Spotify, including images and audio.
"""

from spotify_scraper.media.image import ImageDownloader
from spotify_scraper.media.audio import AudioDownloader

__all__ = [
    "ImageDownloader",
    "AudioDownloader",
]
