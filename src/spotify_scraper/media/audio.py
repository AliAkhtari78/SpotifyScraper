"""
Audio downloading and processing module for SpotifyScraper.

This module provides functionality for downloading and processing
audio previews and other audio assets from Spotify.
"""

import os
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import DownloadError, MediaError
from spotify_scraper.core.types import TrackData
from spotify_scraper.media.image import ImageDownloader

logger = logging.getLogger(__name__)


class AudioDownloader:
    """
    Download and process audio from Spotify.
    
    This class handles downloading of preview audio files,
    with support for various formats, quality levels, and metadata.
    
    Attributes:
        browser: Browser instance for web interactions
    """
    
    def __init__(self, browser: Browser):
        """
        Initialize the AudioDownloader.
        
        Args:
            browser: Browser instance for web interactions
        """
        self.browser = browser
        self._image_downloader = None
        logger.debug("Initialized AudioDownloader")
    
    def _get_image_downloader(self) -> ImageDownloader:
        """
        Get or create the image downloader.
        
        Returns:
            ImageDownloader instance
        """
        if not self._image_downloader:
            self._image_downloader = ImageDownloader(browser=self.browser)
        return self._image_downloader
    
    def download_preview(
        self,
        track_data: TrackData,
        filename: Optional[str] = None,
        path: str = "",
        with_cover: bool = True,
    ) -> str:
        """
        Download preview MP3 for a track.
        
        Args:
            track_data: Track data from TrackExtractor
            filename: Custom filename (optional)
            path: Directory to save the audio (default: current directory)
            with_cover: Whether to embed the cover image (default: True)
            
        Returns:
            Path to the downloaded audio file
            
        Raises:
            DownloadError: If download fails
            MediaError: If metadata processing fails
        """
        # Get preview URL
        preview_url = track_data.get("preview_url")
        if not preview_url and "audioPreview" in track_data and "url" in track_data["audioPreview"]:
            preview_url = track_data["audioPreview"]["url"]
        
        if not preview_url:
            raise DownloadError("No preview URL available for this track")
        
        # Generate filename if not provided
        if not filename:
            # Get track name and artist
            track_name = track_data.get("name", "unknown")
            artist_name = "unknown"
            if "artists" in track_data and track_data["artists"]:
                artist_name = track_data["artists"][0].get("name", "unknown")
            
            # Create a valid filename
            filename = f"{track_name.replace(' ', '_')}_by_{artist_name.replace(' ', '_')}"
        
        # Clean filename to be safe for filesystem
        filename = "".join(x for x in filename if x.isalnum() or x in "_-.")
        
        # Add extension if not present
        if not filename.endswith(".mp3"):
            filename += ".mp3"
        
        # Create full path
        if path:
            # Ensure path exists
            os.makedirs(path, exist_ok=True)
            file_path = os.path.join(path, filename)
        else:
            file_path = filename
        
        # Download the audio
        try:
            logger.debug(f"Downloading preview audio from {preview_url}")
            response = requests.get(preview_url, stream=True)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.debug(f"Preview audio saved to {file_path}")
            
            # Embed cover image if requested
            if with_cover:
                self._embed_cover(file_path, track_data)
            
            return file_path
        except Exception as e:
            logger.error(f"Failed to download preview audio: {e}")
            raise DownloadError(f"Failed to download preview audio: {e}", url=preview_url, file_path=file_path)
    
    def _embed_cover(self, file_path: str, track_data: TrackData) -> None:
        """
        Embed cover image in an audio file.
        
        Args:
            file_path: Path to the audio file
            track_data: Track data
            
        Raises:
            MediaError: If embedding fails
        """
        try:
            # Try to import eyed3
            try:
                import eyed3
            except ImportError:
                logger.warning("eyeD3 library not available, skipping cover embedding")
                return
            
            # Get or download cover image
            image_downloader = self._get_image_downloader()
            temp_cover_path = os.path.join(os.path.dirname(file_path), "_temp_cover.jpg")
            
            try:
                # Download cover to temporary file
                image_downloader.download_cover(
                    entity_data=track_data,
                    filename="_temp_cover.jpg",
                    path=os.path.dirname(file_path),
                )
                
                # Load audio file
                audio_file = eyed3.load(file_path)
                if audio_file.tag is None:
                    audio_file.initTag()
                
                # Set metadata
                audio_file.tag.title = track_data.get("name", "")
                if "artists" in track_data and track_data["artists"]:
                    audio_file.tag.artist = track_data["artists"][0].get("name", "")
                if "album" in track_data:
                    audio_file.tag.album = track_data["album"].get("name", "")
                
                # Embed cover image
                with open(temp_cover_path, "rb") as f:
                    audio_file.tag.images.set(3, f.read(), "image/jpeg")
                
                # Save changes
                audio_file.tag.save()
                logger.debug(f"Embedded cover image in {file_path}")
            finally:
                # Clean up temporary files
                if os.path.exists(temp_cover_path):
                    os.remove(temp_cover_path)
        except Exception as e:
            logger.warning(f"Failed to embed cover image: {e}")
            # This is not a critical error, so we don't raise an exception
