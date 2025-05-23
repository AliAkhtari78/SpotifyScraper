"""Image downloading and processing module for SpotifyScraper.

This module handles the downloading of cover images from Spotify entities
including tracks (album covers), albums, artists, and playlists. It provides
functionality to download images in various sizes with automatic filename
generation and path management.

The module supports all Spotify entity types and intelligently extracts
the appropriate image URL from the entity data structure.

Example:
    >>> from spotify_scraper.browsers import create_browser
    >>> from spotify_scraper.media.image import ImageDownloader
    >>> from spotify_scraper.extractors.track import TrackExtractor
    >>> 
    >>> browser = create_browser("requests")
    >>> downloader = ImageDownloader(browser)
    >>> extractor = TrackExtractor(browser)
    >>> 
    >>> track_data = extractor.extract("https://open.spotify.com/track/...")
    >>> cover_path = downloader.download_cover(track_data, size="large")
    >>> print(f"Cover saved to: {cover_path}")
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
    """Download and process cover images from Spotify.
    
    This class specializes in downloading cover art images from various Spotify
    entities. It handles the complete download process including URL extraction,
    size selection, filename generation, and file saving.
    
    The downloader supports:
        - Track album covers
        - Album covers
        - Artist images
        - Playlist covers
        - Multiple image sizes (small, medium, large)
        - Automatic filename sanitization
        - Custom paths and filenames
    
    Attributes:
        browser: Browser instance for web interactions (though primarily uses
            direct requests for image downloads).
    
    Example:
        >>> downloader = ImageDownloader(browser)
        >>> # Download track's album cover
        >>> track_data = track_extractor.extract(track_url)
        >>> cover_path = downloader.download_cover(track_data)
        >>> 
        >>> # Download with custom settings
        >>> cover_path = downloader.download_cover(
        ...     album_data,
        ...     filename="my_album_cover",
        ...     path="covers/",
        ...     size="small"
        ... )
    
    Note:
        Image quality and available sizes depend on what Spotify provides.
        Not all entities have images in all sizes.
    """
    
    def __init__(self, browser: Browser):
        """Initialize the ImageDownloader.
        
        Args:
            browser: Browser instance for web interactions. While the browser
                is not directly used for downloading images (uses requests),
                it's maintained for consistency with other components.
        
        Example:
            >>> from spotify_scraper.browsers import create_browser
            >>> browser = create_browser("requests")
            >>> downloader = ImageDownloader(browser)
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
        """Download cover image for a Spotify entity.
        
        Downloads the cover art/image associated with any Spotify entity.
        Automatically detects the entity type and extracts the appropriate
        image URL. Images are saved as JPEG files.
        
        Args:
            entity_data: Entity information dictionary from any extractor
                (TrackExtractor, AlbumExtractor, ArtistExtractor, or
                PlaylistExtractor). Must contain image data in one of
                these locations:
                - entity_data['album']['images'] (for tracks)
                - entity_data['images'] (for albums/artists/playlists)
                - entity_data['visualIdentity']['image'] (embed format)
            filename: Custom filename for the image (without extension).
                If None, generates filename as: "{name}_{type}_cover.jpg"
                Special characters are sanitized for filesystem compatibility.
            path: Directory path where the image should be saved.
                Defaults to current directory. Directory will be created
                if it doesn't exist.
            size: Preferred image size to download.
                - "small": Smallest available (typically 64x64)
                - "medium": Medium size (typically 300x300)
                - "large": Largest available (typically 640x640)
                Actual dimensions depend on what Spotify provides.
            
        Returns:
            str: Full path to the downloaded image file.
                Example: "/covers/Bohemian_Rhapsody_track_cover.jpg"
            
        Raises:
            DownloadError: If no cover image is available or download fails.
                Includes the URL and file path in the error for debugging.
        
        Example:
            >>> # Download album cover
            >>> album_data = album_extractor.extract(album_url)
            >>> cover_path = downloader.download_cover(album_data)
            >>> 
            >>> # Download artist image with custom settings
            >>> artist_data = artist_extractor.extract(artist_url)
            >>> cover_path = downloader.download_cover(
            ...     artist_data,
            ...     filename="queen_band",
            ...     path="artist_images/",
            ...     size="medium"
            ... )
        
        Note:
            - Tracks use their album's cover (no track-specific covers)
            - Image files are always saved as JPEG regardless of source format
            - Existing files are overwritten without warning
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
        """Extract cover image URL from entity data.
        
        Intelligently searches for image URLs in the entity data structure,
        handling different formats and entity types. Selects the appropriate
        image size based on the requested preference.
        
        Args:
            entity_data: Entity information dictionary containing image data
            size: Preferred image size ("small", "medium", or "large")
            
        Returns:
            Optional[str]: Direct URL to the image, or None if no images
                are available in the entity data
        
        Note:
            The method checks multiple possible locations for images:
            1. entity_data['album']['images'] - for track entities
            2. entity_data['images'] - for album/artist/playlist entities
            3. entity_data['visualIdentity']['image'] - for embed format
            
            Images are sorted by width to ensure consistent size selection.
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
