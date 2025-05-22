"""
Playlist extractor module for SpotifyScraper.

This module provides functionality for extracting playlist information
from Spotify playlist pages, with support for both regular and embed URLs.
"""

import logging
from typing import Dict, Optional, Any, Union, List, cast

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import ScrapingError, URLError, ParsingError
from spotify_scraper.core.types import PlaylistData, TrackData
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
from spotify_scraper.core.constants import PLAYLIST_JSON_PATH

logger = logging.getLogger(__name__)


class PlaylistExtractor:
    """
    Extractor for Spotify playlist information.
    
    This class provides functionality to extract information from
    Spotify playlist pages, with support for different page structures and
    automatic conversion between regular and embed URLs.
    
    Attributes:
        browser: Browser instance for web interactions
    """
    
    def __init__(self, browser: Browser):
        """
        Initialize the PlaylistExtractor.
        
        Args:
            browser: Browser instance for web interactions
        """
        self.browser = browser
        logger.debug("Initialized PlaylistExtractor")
    
    def extract(self, url: str) -> PlaylistData:
        """
        Extract playlist information from a Spotify playlist URL.
        
        Args:
            url: Spotify playlist URL
            
        Returns:
            Playlist data as a dictionary
            
        Raises:
            URLError: If the URL is invalid
            ScrapingError: If extraction fails
        """
        # Validate URL
        logger.debug(f"Extracting data from playlist URL: {url}")
        try:
            validate_url(url, expected_type="playlist")
        except URLError as e:
            logger.error(f"Invalid playlist URL: {e}")
            return {"ERROR": str(e), "id": "", "name": "", "uri": "", "type": "playlist"}
        
        # Extract playlist ID for logging
        try:
            playlist_id = extract_id(url)
            logger.debug(f"Extracted playlist ID: {playlist_id}")
        except URLError:
            playlist_id = "unknown"
        
        try:
            # Convert any playlist URL to embed format
            embed_url = convert_to_embed_url(url)
            logger.debug(f"Using embed URL: {embed_url}")
            
            # Get page content from embed URL
            page_content = self.browser.get_page_content(embed_url)
            
            # Parse playlist information
            playlist_data = self.extract_playlist_data_from_page(page_content)
            
            # If we got valid data, return it
            if playlist_data and not playlist_data.get("ERROR"):
                logger.debug(f"Successfully extracted data for playlist: {playlist_data.get('name', playlist_id)}")
                return playlist_data
            
            # If extraction failed, log the error and return the error data
            error_msg = playlist_data.get("ERROR", "Unknown error")
            logger.warning(f"Failed to extract playlist data from embed URL: {error_msg}")
            return playlist_data
            
        except Exception as e:
            logger.error(f"Failed to extract playlist data: {e}")
            return {"ERROR": str(e), "id": playlist_id, "name": "", "uri": "", "type": "playlist"}
    
    def extract_by_id(self, playlist_id: str) -> PlaylistData:
        """
        Extract playlist information by ID.
        
        This method constructs an embed URL from the playlist ID and extracts the data.
        
        Args:
            playlist_id: Spotify playlist ID
            
        Returns:
            Playlist data as a dictionary
        """
        # Directly create an embed URL for best results
        url = f"https://open.spotify.com/embed/playlist/{playlist_id}"
        return self.extract(url)
    
    def extract_playlist_data_from_page(self, html_content: str) -> PlaylistData:
        """
        Extract playlist data from a Spotify page.
        
        This function tries multiple methods to extract playlist data,
        falling back to alternative methods if the preferred method fails.
        
        Args:
            html_content: HTML content of the Spotify page
            
        Returns:
            Structured playlist data
            
        Raises:
            ParsingError: If all extraction methods fail
        """
        # Try using __NEXT_DATA__ first (modern approach)
        try:
            json_data = extract_json_from_next_data(html_content)
            return self.extract_playlist_data(json_data, PLAYLIST_JSON_PATH)
        except ParsingError as e:
            logger.warning(f"Failed to extract playlist data using __NEXT_DATA__: {e}")
        
        # Fallback to resource script tag (legacy approach)
        try:
            json_data = extract_json_from_resource(html_content)
            # For resource script tag, the data is directly in the root
            return self.extract_playlist_data(json_data, "")
        except ParsingError as e:
            logger.warning(f"Failed to extract playlist data using resource script: {e}")
        
        # If all methods fail, raise a more specific error
        raise ParsingError("Failed to extract playlist data from page using any method")
    
    def extract_playlist_data(self, json_data: Dict[str, Any], path: str) -> PlaylistData:
        """
        Extract playlist data from Spotify JSON data.
        
        Args:
            json_data: Parsed JSON data
            path: JSON path to playlist data
            
        Returns:
            Structured playlist data
            
        Raises:
            ParsingError: If playlist data extraction fails
        """
        try:
            # Get playlist data from specified path
            playlist_data = get_nested_value(json_data, path)
            if not playlist_data:
                raise ParsingError(f"No playlist data found at path: {path}")
            
            # Create a standardized playlist data object
            result: PlaylistData = {
                "id": playlist_data.get("id", ""),
                "name": playlist_data.get("name", ""),
                "uri": playlist_data.get("uri", ""),
                "type": "playlist",
            }
            
            # Extract description
            if "description" in playlist_data:
                result["description"] = playlist_data["description"]
            
            # Extract owner
            if "owner" in playlist_data:
                owner_data = playlist_data["owner"]
                result["owner"] = {
                    "id": owner_data.get("id", ""),
                    "name": owner_data.get("display_name", owner_data.get("name", "")),
                    "uri": owner_data.get("uri", ""),
                }
            
            # Extract images
            if "images" in playlist_data:
                result["images"] = []
                for image in playlist_data["images"]:
                    image_data = {
                        "url": image.get("url", ""),
                        "height": image.get("height", 0),
                        "width": image.get("width", 0),
                    }
                    result["images"].append(image_data)
            
            # Extract visual identity data if available
            if "visualIdentity" in playlist_data and "image" in playlist_data["visualIdentity"]:
                if "images" not in result:
                    result["images"] = []
                
                for image in playlist_data["visualIdentity"]["image"]:
                    image_data = {
                        "url": image.get("url", ""),
                        "height": image.get("maxHeight", 0),
                        "width": image.get("maxWidth", 0),
                    }
                    result["images"].append(image_data)
            
            # Extract track count
            if "tracks" in playlist_data and "total" in playlist_data["tracks"]:
                result["track_count"] = playlist_data["tracks"]["total"]
            elif "track_count" in playlist_data:
                result["track_count"] = playlist_data["track_count"]
            elif "trackCount" in playlist_data:
                result["track_count"] = playlist_data["trackCount"]
            
            # Extract tracks if available
            if "tracks" in playlist_data and "items" in playlist_data["tracks"]:
                result["tracks"] = []
                for item in playlist_data["tracks"]["items"]:
                    # Some APIs return track in a nested 'track' field
                    track = item.get("track", item)
                    
                    track_data: TrackData = {
                        "id": track.get("id", ""),
                        "name": track.get("name", ""),
                        "uri": track.get("uri", ""),
                        "type": "track",
                    }
                    
                    # Extract track duration
                    if "duration_ms" in track:
                        track_data["duration_ms"] = track["duration_ms"]
                    elif "duration" in track:
                        track_data["duration_ms"] = track["duration"]
                    
                    # Extract artists
                    if "artists" in track:
                        track_data["artists"] = []
                        for artist in track["artists"]:
                            artist_data = {
                                "id": artist.get("id", ""),
                                "name": artist.get("name", ""),
                                "uri": artist.get("uri", ""),
                                "type": "artist",
                            }
                            track_data["artists"].append(artist_data)
                    
                    # Extract album
                    if "album" in track:
                        album = track["album"]
                        album_data = {
                            "id": album.get("id", ""),
                            "name": album.get("name", ""),
                            "uri": album.get("uri", ""),
                            "type": "album",
                        }
                        
                        # Extract album images
                        if "images" in album:
                            album_data["images"] = album["images"]
                        
                        track_data["album"] = album_data
                    
                    # Extract added_at if available
                    if "added_at" in item:
                        track_data["added_at"] = item["added_at"]
                    
                    # Extract added_by if available
                    if "added_by" in item:
                        track_data["added_by"] = item["added_by"]
                    
                    # Extract preview URL if available
                    if "preview_url" in track:
                        track_data["preview_url"] = track["preview_url"]
                    
                    # Extract explicit flag if available
                    if "explicit" in track:
                        track_data["is_explicit"] = track["explicit"]
                    elif "isExplicit" in track:
                        track_data["is_explicit"] = track["isExplicit"]
                    
                    result["tracks"].append(track_data)
            
            # Extract collaborative flag
            if "collaborative" in playlist_data:
                result["collaborative"] = playlist_data["collaborative"]
            
            # Extract public flag
            if "public" in playlist_data:
                result["public"] = playlist_data["public"]
            
            # Extract followers count
            if "followers" in playlist_data and "total" in playlist_data["followers"]:
                result["followers"] = playlist_data["followers"]["total"]
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract playlist data: {e}")
            # Return a minimal playlist data object with error information
            return {"ERROR": str(e), "id": "", "name": "", "uri": "", "type": "playlist"}
    
    def extract_cover_url(self, url: str, size: str = "large") -> Optional[str]:
        """
        Extract cover URL from a playlist.
        
        Args:
            url: Spotify playlist URL
            size: Desired image size ('small', 'medium', or 'large')
            
        Returns:
            Cover URL, or None if not available
        """
        playlist_data = self.extract(url)
        
        # Check if playlist has images
        if "images" in playlist_data and playlist_data["images"]:
            images = playlist_data["images"]
            
            # Sort images by size
            sorted_images = sorted(images, key=lambda img: img.get("height", 0))
            
            if size == "small" and len(sorted_images) > 0:
                return sorted_images[0].get("url")
            elif size == "medium" and len(sorted_images) > 1:
                return sorted_images[len(sorted_images) // 2].get("url")
            elif len(sorted_images) > 0:
                return sorted_images[-1].get("url")
        
        return None
    
    def extract_tracks(self, url: str) -> List[TrackData]:
        """
        Extract tracks from a playlist.
        
        Args:
            url: Spotify playlist URL
            
        Returns:
            List of track data dictionaries
        """
        playlist_data = self.extract(url)
        
        if "tracks" in playlist_data:
            return playlist_data["tracks"]
        
        return []
