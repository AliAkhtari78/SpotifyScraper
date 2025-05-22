"""
Image downloading and processing module for SpotifyScraper.

This module provides functionality for downloading and processing
cover images and other image assets from Spotify.
"""

import os
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import DownloadError
from spotify_scraper.core.types import TrackData, AlbumData, ArtistData, PlaylistData

logger = logging.getLogger(__name__)


class ImageDownloader:
    """
    Download and process images from Spotify.
    
    This class handles downloading of cover images and other image assets,
    with support for different sizes, formats, and caching.
    
    Attributes:
        browser: Browser instance for web interactions
    """
    
    def __init__(self, browser: Browser):
        """
        Initialize the ImageDownloader.
        
        Args:
            browser: Browser instance for web interactions
        """
        self.browser = browser
        logger.debug("Initialized ImageDownloader")
    
    def download_cover(
        self,
        entity_data: Union[TrackData, AlbumData, ArtistData, PlaylistData],
        filename: Optional[str] = None,
        path: str = "",
        size: str = "large",
    ) -> str:
        """
        Download cover image for a Spotify entity.
        
        Args:
            entity_data: Entity data from an extractor
            filename: Custom filename (optional)
            path: Directory to save the image (default: current directory)
            size: Image size ('small', 'medium', 'large')
            
        Returns:
            Path to the downloaded image
            
        Raises:
            DownloadError: If download fails
        """
        # Get cover URL based on entity type
        cover_url = self._get_cover_url(entity_data, size)
        if not cover_url:
            raise DownloadError("No cover image available")
        
        # Generate filename if not provided
        if not filename:
            # Get entity name and type
            entity_name = entity_data.get("name", "unknown")
            entity_type = entity_data.get("type", "track")
            
            # Create a valid filename
            filename = f"{entity_name.replace(' ', '_')}_{entity_type}_cover"
        
        # Clean filename to be safe for filesystem
        filename = "".join(x for x in filename if x.isalnum() or x in "_-.")
        
        # Add extension if not present
        if not filename.endswith((".jpg", ".jpeg", ".png")):
            filename += ".jpg"
        
        # Create full path
        if path:
            # Ensure path exists
            os.makedirs(path, exist_ok=True)
            file_path = os.path.join(path, filename)
        else:
            file_path = filename
        
        # Download the image
        try:
            logger.debug(f"Downloading cover image from {cover_url}")
            response = requests.get(cover_url, stream=True)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.debug(f"Cover image saved to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to download cover image: {e}")
            raise DownloadError(f"Failed to download cover image: {e}", url=cover_url, file_path=file_path)
    
    def _get_cover_url(
        self,
        entity_data: Union[TrackData, AlbumData, ArtistData, PlaylistData],
        size: str = "large",
    ) -> Optional[str]:
        """
        Get cover image URL from entity data.
        
        Args:
            entity_data: Entity data
            size: Image size ('small', 'medium', 'large')
            
        Returns:
            Cover image URL, or None if not available
        """
        # Handle track entities
        if "album" in entity_data and "images" in entity_data["album"]:
            images = entity_data["album"]["images"]
        # Handle album entities
        elif "images" in entity_data:
            images = entity_data["images"]
        # Handle visual identity (from embed data)
        elif "visualIdentity" in entity_data and "image" in entity_data["visualIdentity"]:
            images = entity_data["visualIdentity"]["image"]
        else:
            return None
        
        # Sort images by size
        sorted_images = sorted(images, key=lambda x: x.get("width", 0) if isinstance(x.get("width"), int) else 0)
        
        # Get image based on requested size
        if size == "small" and len(sorted_images) > 0:
            return sorted_images[0].get("url")
        elif size == "medium" and len(sorted_images) > 1:
            return sorted_images[len(sorted_images) // 2].get("url")
        elif len(sorted_images) > 0:
            return sorted_images[-1].get("url")
        
        return None
