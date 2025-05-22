"""
Core client implementation for SpotifyScraper.

This module provides the main SpotifyClient class that serves as the primary
interface for users of the library. Think of this as the command center that
coordinates all the different extraction capabilities.
"""

from typing import Optional, Dict, Any, Union
import logging

from spotify_scraper.core.exceptions import SpotifyScraperError, URLError
from spotify_scraper.core.types import TrackData, AlbumData, ArtistData, PlaylistData
from spotify_scraper.browsers.base import Browser
from spotify_scraper.extractors.track import TrackExtractor

logger = logging.getLogger(__name__)


class SpotifyClient:
    """
    Main client class for SpotifyScraper.
    
    This class provides a high-level interface for extracting data from Spotify.
    It coordinates between different extractors and handles browser management.
    
    Think of this class as your main entry point - instead of having to understand
    all the individual extractor classes, you can just use this client to get
    whatever data you need from Spotify.
    """
    
    def __init__(self, browser: Optional[Browser] = None):
        """
        Initialize the Spotify client.
        
        Args:
            browser: Browser instance to use for web requests. If None, a default
                    requests-based browser will be created.
        """
        # For now, we'll accept the browser parameter but won't create a default
        # This allows the client to be instantiated without breaking, but full
        # functionality will require a proper browser implementation
        self.browser = browser
        
        # Initialize extractors - but only if we have a browser
        if self.browser:
            self.track_extractor = TrackExtractor(self.browser)
        else:
            self.track_extractor = None
            
        logger.debug("Initialized SpotifyClient")
    
    def get_track(self, url: str) -> TrackData:
        """
        Extract track information from a Spotify track URL.
        
        This is the main method users will call to get track data. It handles
        all the complexity of URL validation, browser management, and data extraction.
        
        Args:
            url: Spotify track URL (regular or embed format)
            
        Returns:
            Dictionary containing track information including metadata and lyrics
            
        Raises:
            SpotifyScraperError: If extraction fails
            URLError: If the URL is invalid
        """
        if not self.track_extractor:
            raise SpotifyScraperError("No browser available for extraction")
            
        return self.track_extractor.extract(url)
    
    def get_album(self, url: str) -> AlbumData:
        """
        Extract album information from a Spotify album URL.
        
        Args:
            url: Spotify album URL
            
        Returns:
            Dictionary containing album information
            
        Raises:
            SpotifyScraperError: If extraction fails or album extractor not implemented
        """
        # Placeholder for album extraction - to be implemented
        raise NotImplementedError("Album extraction not yet implemented")
    
    def get_artist(self, url: str) -> ArtistData:
        """
        Extract artist information from a Spotify artist URL.
        
        Args:
            url: Spotify artist URL
            
        Returns:
            Dictionary containing artist information
            
        Raises:
            SpotifyScraperError: If extraction fails or artist extractor not implemented
        """
        # Placeholder for artist extraction - to be implemented
        raise NotImplementedError("Artist extraction not yet implemented")
    
    def get_playlist(self, url: str) -> PlaylistData:
        """
        Extract playlist information from a Spotify playlist URL.
        
        Args:
            url: Spotify playlist URL
            
        Returns:
            Dictionary containing playlist information
            
        Raises:
            SpotifyScraperError: If extraction fails or playlist extractor not implemented
        """
        # Placeholder for playlist extraction - to be implemented
        raise NotImplementedError("Playlist extraction not yet implemented")
    
    def close(self) -> None:
        """
        Close the client and release any resources.
        
        This method should be called when you're done using the client,
        especially if you're using a browser that needs cleanup (like Selenium).
        """
        if self.browser:
            self.browser.close()
        logger.debug("Closed SpotifyClient")
