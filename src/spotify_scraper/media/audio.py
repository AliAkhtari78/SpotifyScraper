"""Audio downloading and processing module for SpotifyScraper.

This module handles the downloading of audio preview clips from Spotify tracks.
It provides functionality to download 30-second MP3 previews and optionally
embed metadata and cover art into the downloaded files.

The module uses the requests library for downloading and optionally eyeD3
for embedding metadata and cover art into MP3 files.

Example:
    >>> from spotify_scraper.browsers import create_browser
    >>> from spotify_scraper.media.audio import AudioDownloader
    >>> from spotify_scraper.extractors.track import TrackExtractor
    >>> 
    >>> browser = create_browser("requests")
    >>> downloader = AudioDownloader(browser)
    >>> extractor = TrackExtractor(browser)
    >>> 
    >>> track_data = extractor.extract("https://open.spotify.com/track/...")
    >>> mp3_path = downloader.download_preview(track_data, with_cover=True)
    >>> print(f"Downloaded to: {mp3_path}")
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
    """Download and process audio previews from Spotify.
    
    This class specializes in downloading 30-second preview clips that Spotify
    provides for most tracks. It handles the complete download process including
    file naming, metadata embedding, and cover art integration.
    
    Key features:
        - Downloads 30-second MP3 preview clips
        - Automatic filename generation from track metadata
        - Optional cover art embedding (requires eyeD3)
        - Metadata tagging (title, artist, album)
        - Safe filename generation for all platforms
    
    Attributes:
        browser: Browser instance for web interactions (though primarily uses
            direct requests for audio downloads).
        _image_downloader: Lazy-loaded ImageDownloader instance for cover art.
    
    Example:
        >>> downloader = AudioDownloader(browser)
        >>> # Download with automatic filename
        >>> path = downloader.download_preview(track_data)
        >>> 
        >>> # Download with custom settings
        >>> path = downloader.download_preview(
        ...     track_data,
        ...     filename="my_preview",
        ...     path="downloads/",
        ...     with_cover=True
        ... )
    
    Note:
        Not all Spotify tracks have preview URLs available. This is typically
        due to licensing restrictions or regional availability.
    """
    
    def __init__(self, browser: Browser):
        """Initialize the AudioDownloader.
        
        Args:
            browser: Browser instance for web interactions. While the browser
                is not directly used for downloading audio (uses requests),
                it's maintained for consistency with other components and
                potential future use.
        
        Example:
            >>> from spotify_scraper.browsers import create_browser
            >>> browser = create_browser("requests")
            >>> downloader = AudioDownloader(browser)
        """
        self.browser = browser
        self._image_downloader = None
        logger.debug("Initialized AudioDownloader")
    
    def _get_image_downloader(self) -> ImageDownloader:
        """Get or create the image downloader instance.
        
        Lazy-loads the ImageDownloader to avoid unnecessary initialization
        if cover art embedding is not used.
        
        Returns:
            ImageDownloader: Cached instance for downloading cover art
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
        """Download preview MP3 for a track.
        
        Downloads the 30-second preview clip from Spotify and saves it as an MP3 file.
        Optionally embeds cover art and metadata tags into the file.
        
        Args:
            track_data: Track information dictionary from TrackExtractor.extract().
                Must contain at least 'preview_url' or 'audioPreview.url'.
                Should also contain 'name', 'artists', and 'album' for proper
                filename generation and metadata tagging.
            filename: Custom filename for the MP3 (without extension).
                If None, generates filename as: "{track_name}_by_{artist_name}.mp3"
                Special characters are sanitized for filesystem compatibility.
            path: Directory path where the MP3 should be saved.
                Defaults to current directory. Directory will be created if needed.
            with_cover: Whether to embed album cover art in the MP3 metadata.
                Requires eyeD3 library. If eyeD3 is not installed, this option
                is silently ignored with a warning logged.
            
        Returns:
            str: Full path to the downloaded MP3 file.
                Example: "/downloads/Bohemian_Rhapsody_by_Queen.mp3"
            
        Raises:
            DownloadError: If no preview URL is available or download fails.
                Includes the URL and file path in the error for debugging.
            MediaError: If there's an error processing metadata (rare).
        
        Example:
            >>> # Basic download
            >>> track_data = track_extractor.extract(track_url)
            >>> mp3_path = downloader.download_preview(track_data)
            >>> print(f"Downloaded: {mp3_path}")
            
            >>> # Custom filename and path with cover
            >>> mp3_path = downloader.download_preview(
            ...     track_data,
            ...     filename="my_favorite_song",
            ...     path="music/previews/",
            ...     with_cover=True
            ... )
        
        Note:
            - Preview clips are typically 96-128 kbps MP3 files
            - Not all tracks have previews (regional/licensing restrictions)
            - Cover embedding will fail silently if eyeD3 is not installed
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
        """Embed cover image and metadata in an MP3 file.
        
        Uses eyeD3 library to embed album cover art and metadata tags
        (title, artist, album) into the MP3 file. This enriches the file
        with visual and textual information for better media player support.
        
        Args:
            file_path: Full path to the MP3 file to modify
            track_data: Track information containing metadata and cover image URL
            
        Raises:
            MediaError: If critical errors occur during embedding (currently
                suppressed - failures are logged as warnings instead)
        
        Note:
            - Requires eyeD3 library: pip install eyeD3
            - Downloads cover to temporary file, embeds it, then cleans up
            - Failures are non-critical and logged as warnings
            - Sets ID3v2.3 tags for maximum compatibility
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
