"""
Track extractor module for SpotifyScraper.

This module provides functionality for extracting track information
from Spotify track pages, with support for both regular and embed URLs.
"""

import logging
from typing import Dict, Optional, Any, Union, List, cast

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import ScrapingError, URLError
from spotify_scraper.core.types import TrackData
from spotify_scraper.parsers.json_parser import extract_track_data_from_page
from spotify_scraper.utils.url import (
    convert_to_embed_url,
    validate_url,
    extract_id,
    get_url_type,
)

logger = logging.getLogger(__name__)


class TrackExtractor:
    """
    Extractor for Spotify track information.
    
    This class provides functionality to extract information from
    Spotify track pages, with support for different page structures and
    automatic conversion between regular and embed URLs.
    
    Attributes:
        browser: Browser instance for web interactions
        
    Note:
        This extractor prioritizes using Spotify embed URLs (/embed/track/...)
        over regular URLs because embed endpoints do not require authentication
        and provide the same track metadata including lyrics.
    """
    
    def __init__(self, browser: Browser):
        """
        Initialize the TrackExtractor.
        
        Args:
            browser: Browser instance for web interactions
        """
        self.browser = browser
        logger.debug("Initialized TrackExtractor")
    
    def extract(self, url: str) -> TrackData:
        """
        Extract track information from a Spotify track URL.
        
        This method takes any Spotify track URL and converts it to an
        embed URL format for extraction. Embed URLs don't require Spotify
        login/authentication but still provide full track metadata.
        
        Args:
            url: Spotify track URL (will be converted to embed format)
            
        Returns:
            Track data as a dictionary
            
        Raises:
            URLError: If the URL is invalid
            ScrapingError: If extraction fails
        """
        # Validate URL
        logger.debug(f"Extracting data from track URL: {url}")
        try:
            validate_url(url, expected_type="track")
        except URLError as e:
            logger.error(f"Invalid track URL: {e}")
            return {"ERROR": str(e), "id": "", "name": "", "uri": "", "type": "track"}
        
        # Extract track ID for logging
        try:
            track_id = extract_id(url)
            logger.debug(f"Extracted track ID: {track_id}")
        except URLError:
            track_id = "unknown"
        
        # Always use embed URL, which doesn't require authentication
        try:
            # Convert any track URL to embed format
            embed_url = convert_to_embed_url(url)
            logger.debug(f"Using embed URL: {embed_url}")
            
            # Get page content from embed URL
            page_content = self.browser.get(embed_url)
            
            # Parse track information
            track_data = extract_track_data_from_page(page_content)
            
            # If we got valid data, return it
            if track_data and not track_data.get("ERROR"):
                logger.debug(f"Successfully extracted data for track: {track_data.get('name', track_id)}")
                return track_data
            
            # If extraction failed, log the error and return the error data
            error_msg = track_data.get("ERROR", "Unknown error")
            logger.warning(f"Failed to extract track data from embed URL: {error_msg}")
            return track_data
            
        except Exception as e:
            logger.error(f"Failed to extract track data: {e}")
            return {"ERROR": str(e), "id": track_id, "name": "", "uri": "", "type": "track"}
    
    def extract_by_id(self, track_id: str) -> TrackData:
        """
        Extract track information by ID.
        
        This method constructs an embed URL from the track ID and extracts the data.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Track data as a dictionary
        """
        # Directly create an embed URL for best results
        url = f"https://open.spotify.com/embed/track/{track_id}"
        return self.extract(url)
    
    def extract_preview_url(self, url: str) -> Optional[str]:
        """
        Extract preview URL from a track.
        
        Args:
            url: Spotify track URL
            
        Returns:
            Preview URL, or None if not available
        """
        track_data = self.extract(url)
        return track_data.get("preview_url")
    
    def extract_cover_url(self, url: str) -> Optional[str]:
        """
        Extract cover URL from a track.
        
        Args:
            url: Spotify track URL
            
        Returns:
            Cover URL, or None if not available
        """
        track_data = self.extract(url)
        
        # Check if album is available and has images
        if "album" in track_data and "images" in track_data["album"]:
            images = track_data["album"]["images"]
            if images and len(images) > 0:
                return images[0].get("url")
        
        # Check visual identity as fallback
        if "visualIdentity" in track_data and "image" in track_data["visualIdentity"]:
            images = track_data["visualIdentity"]["image"]
            if images and len(images) > 0:
                return images[0].get("url")
        
        return None
