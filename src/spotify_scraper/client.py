"""
Client module for the SpotifyScraper package.

This module provides a high-level client interface for interacting 
with the Spotify web player and extracting data.
"""

from typing import Dict, List, Optional, Union, Any
import logging
from pathlib import Path

from spotify_scraper.auth.session import Session
from spotify_scraper.core.scraper import Scraper
from spotify_scraper.browsers import create_browser
from spotify_scraper.extractors.track import TrackExtractor
from spotify_scraper.media.image import ImageDownloader
from spotify_scraper.media.audio import AudioDownloader
from spotify_scraper.utils.logger import configure_logging
from spotify_scraper.exceptions import AuthenticationRequiredError

logger = logging.getLogger(__name__)


class SpotifyClient:
    """
    High-level client for interacting with Spotify web player.
    
    This class provides a simplified interface for extracting information
    from Spotify web player and downloading related media.
    
    Attributes:
        session: The authentication session.
        scraper: The underlying scraper instance.
        browser: The browser instance used for web interactions.
        track_extractor: Extractor for track data and lyrics.
    """
    
    def __init__(
        self,
        cookie_file: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        proxy: Optional[Dict[str, str]] = None,
        browser_type: str = "requests",
        log_level: str = "INFO",
        log_file: Optional[str] = None,
    ):
        """
        Initialize the SpotifyClient.
        
        Args:
            cookie_file: Path to a cookies.txt file (optional).
            cookies: A dictionary of cookies to use (optional).
            headers: Custom headers for requests (optional).
            proxy: Proxy configuration (optional).
            browser_type: Type of browser to use ('requests', 'selenium', or 'auto').
            log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
            log_file: Path to log file (optional).
        """
        # Configure logging
        configure_logging(level=log_level.upper(), log_file=log_file)

        # Create session
        self.session = Session(cookie_file=cookie_file, cookies=cookies, headers=headers, proxy=proxy)

        # Create browser
        self.browser = create_browser(browser_type=browser_type, session=self.session.get_requests_session())

        # Create scraper instance
        self.scraper = Scraper(browser=self.browser, log_level=log_level)

        # Create extractors
        self.track_extractor = TrackExtractor(browser=self.browser, scraper_instance=self.scraper)

        # Create downloaders
        self._image_downloader = ImageDownloader(browser=self.browser)
        self._audio_downloader = AudioDownloader(browser=self.browser)
        
        logger.info(f"SpotifyClient initialized. Authenticated: {self.session.is_authenticated()}")

    def get_track_info(self, url: str) -> Dict[str, Any]:
        """
        Get track information from a Spotify track URL using the embed page.

        Args:
            url: Spotify track URL.

        Returns:
            Dictionary containing track information.
        """
        logger.info(f"Getting track info for {url}")
        return self.track_extractor.get_track_info(url)

    def get_track_lyrics(self, url: str, require_auth: bool = True) -> Optional[str]:
        """
        Get lyrics for a Spotify track. Requires authentication by default.

        Args:
            url: Spotify track URL.
            require_auth: If True (default), an error is raised if the session is not authenticated.
                          If False, it attempts to fetch lyrics without ensuring authentication.

        Returns:
            A string containing the lyrics, or None if not found or an error occurs.

        Raises:
            AuthenticationRequiredError: If require_auth is True and session is not authenticated.
        """
        logger.info(f"Getting lyrics for track {url}")
        if require_auth and not self.session.is_authenticated():
            raise AuthenticationRequiredError(
                "Fetching official Spotify lyrics requires an authenticated session. "
                "Please provide cookies via 'cookie_file' or 'cookies' parameter during client initialization."
            )
        return self.track_extractor.get_lyrics(url, require_auth=require_auth)

    def get_track_info_with_lyrics(self, url: str, require_lyrics_auth: bool = True) -> Dict[str, Any]:
        """
        Get track information and lyrics for a Spotify track URL.

        Args:
            url: Spotify track URL.
            require_lyrics_auth: If True (default), an error is raised for lyrics fetching
                                 if the session is not authenticated.

        Returns:
            Dictionary containing track information, with an added 'lyrics' key.
        """
        logger.info(f"Getting track info and lyrics for {url}")
        track_info = self.get_track_info(url)
        try:
            lyrics = self.get_track_lyrics(url, require_auth=require_lyrics_auth)
            track_info["lyrics"] = lyrics
        except AuthenticationRequiredError as e:
            logger.warning(f"Could not fetch lyrics for {url} due to authentication: {e}")
            track_info["lyrics"] = None
        except Exception as e:
            logger.error(f"An error occurred while fetching lyrics for {url}: {e}")
            track_info["lyrics"] = None

        return track_info

    def download_cover(self, url: str, path: Union[str, Path] = "", filename: Optional[str] = None, quality_preference: Optional[List[str]] = None) -> Optional[str]:
        """
        Download cover image from a Spotify URL (track, album, playlist, artist).

        Args:
            url: Spotify URL (track, album, playlist, artist).
            path: Directory to save the image (optional, defaults to current dir).
            filename: Desired filename (without extension). If None, a default is generated.
            quality_preference: List of preferred image quality keys.
        Returns:
            Path to the downloaded image
        """
        logger.info(f"Downloading cover for {url}")
        return self._image_downloader.download(url, path)

    def download_preview_mp3(self, url: str, path: str = "", with_cover: bool = False) -> str:
        """
        Download preview MP3 from a Spotify track URL.

        Args:
            url: Spotify track URL
            path: Directory to save the MP3 (optional)
            with_cover: Whether to embed the cover in the MP3 (optional)

        Returns:
            Path to the downloaded MP3
        """
        logger.info(f"Downloading preview MP3 for {url}")
        return self._audio_downloader.download(url, path, with_cover)

    def close(self) -> None:
        """
        Close the client and release resources.
        """
        logger.debug("Closing SpotifyClient")
        self.browser.close()
