"""
Main client interface for SpotifyScraper.

This module provides the main client interface for SpotifyScraper,
offering a high-level API for extracting data from Spotify.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, cast

from spotify_scraper.auth.session import Session
from spotify_scraper.browsers import create_browser
from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.config import Config
from spotify_scraper.core.types import (
    TrackData,
    AlbumData,
    ArtistData,
    PlaylistData,
    SearchResults,
    LyricsData,
)
from spotify_scraper.core.exceptions import (
    SpotifyScraperError,
    URLError,
    AuthenticationRequiredError,
)
from spotify_scraper.extractors.track import TrackExtractor
from spotify_scraper.media.image import ImageDownloader
from spotify_scraper.media.audio import AudioDownloader
from spotify_scraper.utils.url import (
    validate_url,
    get_url_type,
    extract_id,
)
from spotify_scraper.utils.logger import configure_logging

logger = logging.getLogger(__name__)


class SpotifyClient:
    """
    High-level client for extracting data from Spotify.
    
    This class provides a simplified interface for extracting information
    from Spotify and downloading related media, with automatic handling of
    authentication, browser selection, and error recovery.
    
    Attributes:
        session: Authentication session
        browser: Browser instance for web interactions
        config: Configuration manager
    """
    
    def __init__(
        self,
        cookie_file: Optional[str] = None,
        auth_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        browser_type: str = "auto",
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        config_file: Optional[str] = None,
        proxy: Optional[Dict[str, str]] = None,
        user_agent: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        download_dir: Optional[str] = None,
    ):
        """
        Initialize the SpotifyClient.
        
        Args:
            cookie_file: Path to cookies file (optional)
            auth_token: OAuth token (optional)
            refresh_token: OAuth refresh token (optional)
            client_id: Spotify API client ID (optional)
            client_secret: Spotify API client secret (optional)
            browser_type: Type of browser to use ('requests', 'selenium', or 'auto')
            log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
            log_file: Path to log file (optional)
            config_file: Path to configuration file (optional)
            proxy: Proxy configuration (optional)
            user_agent: Custom user agent (optional)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            download_dir: Directory to save downloads (default: ~/Downloads)
        """
        # Configure logging
        configure_logging(level=log_level, log_file=log_file)
        
        # Load configuration
        self.config = Config(
            config_file=config_file,
            config_dict={
                "timeout": timeout,
                "retries": max_retries,
                "proxy": proxy,
                "user_agent": user_agent,
                "browser_type": browser_type,
                "log_level": log_level,
                "log_file": log_file,
                "auth_token": auth_token,
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret,
                "cookie_file": cookie_file,
                "download_dir": download_dir or os.path.expanduser("~/Downloads"),
            },
        )
        
        # Create session
        self.session = Session(
            cookie_file=cookie_file,
            auth_token=auth_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            proxy=proxy,
            user_agent=user_agent,
        )
        
        # Create browser
        self.browser = create_browser(
            browser_type=browser_type,
            session=self.session.request(),
            timeout=timeout,
            max_retries=max_retries,
        )
        
        # Create extractors and downloaders as needed
        self._track_extractor = None
        self._album_extractor = None
        self._artist_extractor = None
        self._playlist_extractor = None
        self._image_downloader = None
        self._audio_downloader = None
        
        logger.debug("SpotifyClient initialized")
    
    def _get_track_extractor(self) -> TrackExtractor:
        """
        Get or create the track extractor.
        
        Returns:
            TrackExtractor instance
        """
        if not self._track_extractor:
            self._track_extractor = TrackExtractor(browser=self.browser)
        return self._track_extractor
    
    def _get_image_downloader(self) -> ImageDownloader:
        """
        Get or create the image downloader.
        
        Returns:
            ImageDownloader instance
        """
        if not self._image_downloader:
            from spotify_scraper.media.image import ImageDownloader
            self._image_downloader = ImageDownloader(browser=self.browser)
        return self._image_downloader
    
    def _get_audio_downloader(self) -> AudioDownloader:
        """
        Get or create the audio downloader.
        
        Returns:
            AudioDownloader instance
        """
        if not self._audio_downloader:
            from spotify_scraper.media.audio import AudioDownloader
            self._audio_downloader = AudioDownloader(browser=self.browser)
        return self._audio_downloader
    
    def get_track(self, url_or_id: str) -> TrackData:
        """
        Get track information from a Spotify track URL or ID.
        
        Args:
            url_or_id: Spotify track URL or ID
            
        Returns:
            Track data as a dictionary
            
        Raises:
            URLError: If the URL is invalid
            ScrapingError: If extraction fails
        """
        # Check if input is a URL or ID
        if url_or_id.startswith("http"):
            # It's a URL
            url = url_or_id
            
            # Validate URL
            try:
                validate_url(url, expected_type="track")
            except URLError as e:
                logger.error(f"Invalid track URL: {e}")
                raise
        else:
            # It's an ID
            url = f"https://open.spotify.com/track/{url_or_id}"
        
        # Get track extractor
        track_extractor = self._get_track_extractor()
        
        # Extract track information
        return track_extractor.extract(url)
    
    def get_track_by_id(self, track_id: str) -> TrackData:
        """
        Get track information by ID.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Track data as a dictionary
        """
        return self.get_track(track_id)
    
    def download_preview(
        self,
        url_or_id: str,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        with_cover: bool = True,
    ) -> str:
        """
        Download preview MP3 from a Spotify track URL or ID.
        
        Args:
            url_or_id: Spotify track URL or ID
            filename: Custom filename (optional)
            path: Directory to save the file (optional)
            with_cover: Whether to embed the cover image (default: True)
            
        Returns:
            Path to the downloaded file
            
        Raises:
            DownloadError: If download fails
        """
        # Get track data first
        track_data = self.get_track(url_or_id)
        
        # Check if preview URL is available
        if not track_data.get("preview_url"):
            raise SpotifyScraperError("No preview URL available for this track")
        
        # Get audio downloader
        audio_downloader = self._get_audio_downloader()
        
        # Download the preview
        return audio_downloader.download_preview(
            track_data=track_data,
            filename=filename,
            path=path or self.config.get("download_dir"),
            with_cover=with_cover,
        )
    
    def download_cover(
        self,
        url_or_id: str,
        filename: Optional[str] = None,
        path: Optional[str] = None,
        size: str = "large",
    ) -> str:
        """
        Download cover image from a Spotify URL or ID.
        
        Args:
            url_or_id: Spotify URL or ID
            filename: Custom filename (optional)
            path: Directory to save the image (optional)
            size: Image size ('small', 'medium', 'large')
            
        Returns:
            Path to the downloaded image
            
        Raises:
            DownloadError: If download fails
        """
        # Determine the type of URL or ID
        if url_or_id.startswith("http"):
            # It's a URL
            url = url_or_id
            url_type = get_url_type(url)
        else:
            # It's an ID, assume it's a track ID if not specified
            url = f"https://open.spotify.com/track/{url_or_id}"
            url_type = "track"
        
        # Get the appropriate data based on URL type
        if url_type == "track":
            entity_data = self.get_track(url)
        # Add other entity types as implemented
        else:
            raise URLError(f"Unsupported URL type for cover download: {url_type}")
        
        # Get image downloader
        image_downloader = self._get_image_downloader()
        
        # Download the cover
        return image_downloader.download_cover(
            entity_data=entity_data,
            filename=filename,
            path=path or self.config.get("download_dir"),
            size=size,
        )
    
    def is_authenticated(self) -> bool:
        """
        Check if the client is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        return self.session.is_authenticated()
    
    def refresh_token(self) -> bool:
        """
        Refresh the OAuth token.
        
        Returns:
            True if token was refreshed successfully, False otherwise
        """
        return self.session.refresh_auth_token()
    
    def logout(self) -> None:
        """
        Log out by clearing authentication data.
        """
        self.session.logout()
    
    def close(self) -> None:
        """
        Close the client and release resources.
        """
        logger.debug("Closing SpotifyClient")
        self.browser.close()
