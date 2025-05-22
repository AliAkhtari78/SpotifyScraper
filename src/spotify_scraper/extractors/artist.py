"""
Artist extractor module for SpotifyScraper.

This module provides functionality for extracting artist information
from Spotify artist pages, with support for both regular and embed URLs.
"""

import logging
from typing import Dict, Optional, Any, Union, List, cast

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import ScrapingError, URLError, ParsingError
from spotify_scraper.core.types import ArtistData, AlbumData, TrackData
from spotify_scraper.parsers.json_parser import (
    extract_json_from_next_data, 
    extract_json_from_resource,
    get_nested_value,
)
from spotify_scraper.utils.url import (
    convert_to_embed_url,
    validate_url,
    extract_id,
    get_url_type,
)
from spotify_scraper.core.constants import ARTIST_JSON_PATH

logger = logging.getLogger(__name__)


class ArtistExtractor:
    """
    Extractor for Spotify artist information.
    
    This class provides functionality to extract information from
    Spotify artist pages, with support for different page structures and
    automatic conversion between regular and embed URLs.
    
    Attributes:
        browser: Browser instance for web interactions
    """
    
    def __init__(self, browser: Browser):
        """
        Initialize the ArtistExtractor.
        
        Args:
            browser: Browser instance for web interactions
        """
        self.browser = browser
        logger.debug("Initialized ArtistExtractor")
    
    def extract(self, url: str) -> ArtistData:
        """
        Extract artist information from a Spotify artist URL.
        
        Args:
            url: Spotify artist URL
            
        Returns:
            Artist data as a dictionary
            
        Raises:
            URLError: If the URL is invalid
            ScrapingError: If extraction fails
        """
        # Validate URL
        logger.debug(f"Extracting data from artist URL: {url}")
        try:
            validate_url(url, expected_type="artist")
        except URLError as e:
            logger.error(f"Invalid artist URL: {e}")
            return {"ERROR": str(e), "id": "", "name": "", "uri": "", "type": "artist"}
        
        # Extract artist ID for logging
        try:
            artist_id = extract_id(url)
            logger.debug(f"Extracted artist ID: {artist_id}")
        except URLError:
            artist_id = "unknown"
        
        try:
            # Convert any artist URL to embed format
            embed_url = convert_to_embed_url(url)
            logger.debug(f"Using embed URL: {embed_url}")
            
            # Get page content from embed URL
            page_content = self.browser.get_page_content(embed_url)
            
            # Parse artist information
            artist_data = self.extract_artist_data_from_page(page_content)
            
            # If we got valid data, return it
            if artist_data and not artist_data.get("ERROR"):
                logger.debug(f"Successfully extracted data for artist: {artist_data.get('name', artist_id)}")
                return artist_data
            
            # If extraction failed, log the error and return the error data
            error_msg = artist_data.get("ERROR", "Unknown error")
            logger.warning(f"Failed to extract artist data from embed URL: {error_msg}")
            return artist_data
            
        except Exception as e:
            logger.error(f"Failed to extract artist data: {e}")
            return {"ERROR": str(e), "id": artist_id, "name": "", "uri": "", "type": "artist"}
    
    def extract_by_id(self, artist_id: str) -> ArtistData:
        """
        Extract artist information by ID.
        
        This method constructs an embed URL from the artist ID and extracts the data.
        
        Args:
            artist_id: Spotify artist ID
            
        Returns:
            Artist data as a dictionary
        """
        # Directly create an embed URL for best results
        url = f"https://open.spotify.com/embed/artist/{artist_id}"
        return self.extract(url)
    
    def extract_artist_data_from_page(self, html_content: str) -> ArtistData:
        """
        Extract artist data from a Spotify page.
        
        This function tries multiple methods to extract artist data,
        falling back to alternative methods if the preferred method fails.
        
        Args:
            html_content: HTML content of the Spotify page
            
        Returns:
            Structured artist data
            
        Raises:
            ParsingError: If all extraction methods fail
        """
        # Try using __NEXT_DATA__ first (modern approach)
        try:
            json_data = extract_json_from_next_data(html_content)
            return self.extract_artist_data(json_data, ARTIST_JSON_PATH)
        except ParsingError as e:
            logger.warning(f"Failed to extract artist data using __NEXT_DATA__: {e}")
        
        # Fallback to resource script tag (legacy approach)
        try:
            json_data = extract_json_from_resource(html_content)
            # For resource script tag, the data is directly in the root
            return self.extract_artist_data(json_data, "")
        except ParsingError as e:
            logger.warning(f"Failed to extract artist data using resource script: {e}")
        
        # If all methods fail, raise a more specific error
        raise ParsingError("Failed to extract artist data from page using any method")
    
    def extract_artist_data(self, json_data: Dict[str, Any], path: str) -> ArtistData:
        """
        Extract artist data from Spotify JSON data.
        
        Args:
            json_data: Parsed JSON data
            path: JSON path to artist data
            
        Returns:
            Structured artist data
            
        Raises:
            ParsingError: If artist data extraction fails
        """
        try:
            # Get artist data from specified path
            artist_data = get_nested_value(json_data, path)
            if not artist_data:
                raise ParsingError(f"No artist data found at path: {path}")
            
            # Create a standardized artist data object
            result: ArtistData = {
                "id": artist_data.get("id", ""),
                "name": artist_data.get("name", ""),
                "uri": artist_data.get("uri", ""),
                "type": "artist",
            }
            
            # Extract verified status
            if "is_verified" in artist_data:
                result["is_verified"] = artist_data["is_verified"]
            elif "isVerified" in artist_data:
                result["is_verified"] = artist_data["isVerified"]
            
            # Extract biography
            if "bio" in artist_data:
                result["bio"] = artist_data["bio"]
            elif "biography" in artist_data:
                result["bio"] = artist_data["biography"]
            
            # Extract images
            if "images" in artist_data:
                result["images"] = []
                for image in artist_data["images"]:
                    image_data = {
                        "url": image.get("url", ""),
                        "height": image.get("height", 0),
                        "width": image.get("width", 0),
                    }
                    result["images"].append(image_data)
            
            # Extract visual identity data if available
            if "visualIdentity" in artist_data and "image" in artist_data["visualIdentity"]:
                if "images" not in result:
                    result["images"] = []
                
                for image in artist_data["visualIdentity"]["image"]:
                    image_data = {
                        "url": image.get("url", ""),
                        "height": image.get("maxHeight", 0),
                        "width": image.get("maxWidth", 0),
                    }
                    result["images"].append(image_data)
            
            # Extract statistics
            if "stats" in artist_data:
                result["stats"] = artist_data["stats"]
            
            # Extract popular releases
            if "popular_releases" in artist_data:
                result["popular_releases"] = artist_data["popular_releases"]
            elif "popularReleases" in artist_data:
                result["popular_releases"] = artist_data["popularReleases"]
            
            # Extract discography statistics
            if "discography_stats" in artist_data:
                result["discography_stats"] = artist_data["discography_stats"]
            elif "discographyStats" in artist_data:
                result["discography_stats"] = artist_data["discographyStats"]
            
            # Extract top tracks
            if "top_tracks" in artist_data:
                result["top_tracks"] = artist_data["top_tracks"]
            elif "topTracks" in artist_data and "tracks" in artist_data["topTracks"]:
                result["top_tracks"] = artist_data["topTracks"]["tracks"]
            
            # Extract social links (if available)
            if "social" in artist_data:
                result["social"] = artist_data["social"]
            
            # Extract followers count
            if "followers" in artist_data and "total" in artist_data["followers"]:
                result["followers"] = artist_data["followers"]["total"]
            
            # Extract monthly listeners
            if "monthly_listeners" in artist_data:
                result["monthly_listeners"] = artist_data["monthly_listeners"]
            elif "monthlyListeners" in artist_data:
                result["monthly_listeners"] = artist_data["monthlyListeners"]
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract artist data: {e}")
            # Return a minimal artist data object with error information
            return {"ERROR": str(e), "id": "", "name": "", "uri": "", "type": "artist"}
    
    def extract_image_url(self, url: str, size: str = "large") -> Optional[str]:
        """
        Extract profile image URL from an artist.
        
        Args:
            url: Spotify artist URL
            size: Desired image size ('small', 'medium', or 'large')
            
        Returns:
            Image URL, or None if not available
        """
        artist_data = self.extract(url)
        
        # Check if artist has images
        if "images" in artist_data and artist_data["images"]:
            images = artist_data["images"]
            
            # Sort images by size
            sorted_images = sorted(images, key=lambda img: img.get("height", 0))
            
            if size == "small" and len(sorted_images) > 0:
                return sorted_images[0].get("url")
            elif size == "medium" and len(sorted_images) > 1:
                return sorted_images[len(sorted_images) // 2].get("url")
            elif len(sorted_images) > 0:
                return sorted_images[-1].get("url")
        
        return None
    
    def extract_top_tracks(self, url: str) -> List[TrackData]:
        """
        Extract top tracks from an artist.
        
        Args:
            url: Spotify artist URL
            
        Returns:
            List of track data dictionaries
        """
        artist_data = self.extract(url)
        
        if "top_tracks" in artist_data:
            return artist_data["top_tracks"]
        
        return []
    
    def extract_discography(self, url: str) -> List[AlbumData]:
        """
        Extract discography from an artist.
        
        Args:
            url: Spotify artist URL
            
        Returns:
            List of album data dictionaries
        """
        artist_data = self.extract(url)
        
        if "popular_releases" in artist_data:
            return artist_data["popular_releases"]
        
        return []
