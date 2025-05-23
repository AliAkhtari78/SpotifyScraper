"""Track extractor module for SpotifyScraper.

This module provides specialized functionality for extracting track information
from Spotify's web interface. It handles parsing of Spotify's React-based pages
to extract structured track metadata, including basic information, audio previews,
and optionally lyrics (with authentication).

The extractor intelligently converts regular Spotify URLs to embed format for
better reliability and to avoid authentication requirements for basic metadata.

Example:
    >>> from spotify_scraper.browsers import create_browser
    >>> from spotify_scraper.extractors.track import TrackExtractor
    >>> 
    >>> browser = create_browser("requests")
    >>> extractor = TrackExtractor(browser)
    >>> track_data = extractor.extract("https://open.spotify.com/track/...")
    >>> print(f"{track_data['name']} - {track_data['artists'][0]['name']}")
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
    """Extractor for Spotify track information.
    
    This class specializes in extracting track metadata from Spotify's web pages.
    It handles the complexity of parsing Spotify's React-based interface and
    provides clean, structured data output.
    
    The extractor automatically converts regular Spotify URLs to embed format
    (/embed/track/...) which provides several advantages:
        - No authentication required for basic metadata
        - More consistent page structure
        - Faster page loads
        - Same data availability as regular pages
    
    Attributes:
        browser: Browser instance for fetching web pages and handling requests.
    
    Example:
        >>> browser = create_browser("requests")
        >>> extractor = TrackExtractor(browser)
        >>> 
        >>> # Extract by URL
        >>> track = extractor.extract("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
        >>> print(track['name'])  # "Bohemian Rhapsody"
        >>> 
        >>> # Extract by ID
        >>> track = extractor.extract_by_id("6rqhFgbbKwnb9MLmUQDhG6")
        >>> 
        >>> # Get preview URL
        >>> preview_url = extractor.extract_preview_url(track_url)
        >>> print(f"Preview: {preview_url}")
    
    Note:
        While this extractor can parse lyrics when available in the page data,
        official Spotify lyrics typically require authentication to access.
        Use the SpotifyClient with proper authentication for reliable lyrics access.
    """
    
    def __init__(self, browser: Browser):
        """Initialize the TrackExtractor.
        
        Args:
            browser: Browser instance for web interactions. Can be either
                RequestsBrowser for lightweight operations or SeleniumBrowser
                for JavaScript-heavy pages.
        
        Example:
            >>> from spotify_scraper.browsers import create_browser
            >>> browser = create_browser("requests")
            >>> extractor = TrackExtractor(browser)
        """
        self.browser = browser
        logger.debug("Initialized TrackExtractor")
    
    def extract(self, url: str) -> TrackData:
        """Extract track information from a Spotify track URL.
        
        This method accepts any valid Spotify track URL format and automatically
        converts it to an embed URL for extraction. This approach bypasses
        authentication requirements while still providing complete metadata.
        
        Args:
            url: Spotify track URL in any format:
                - Regular: https://open.spotify.com/track/{id}
                - Embed: https://open.spotify.com/embed/track/{id}
                - URI: spotify:track:{id}
                - With query params: https://open.spotify.com/track/{id}?si=...
            
        Returns:
            TrackData: Dictionary containing track information with fields:
                - id (str): Spotify track ID
                - name (str): Track title
                - uri (str): Spotify URI
                - type (str): Always "track"
                - duration_ms (int): Duration in milliseconds
                - explicit (bool): Explicit content flag
                - artists (List[Dict]): Artist information
                - album (Dict): Album information with images
                - preview_url (str): 30-second preview URL
                - ERROR (str): Error message if extraction failed
            
        Raises:
            URLError: If the URL is not a valid Spotify track URL
            ScrapingError: If the page structure is unexpected
        
        Example:
            >>> track = extractor.extract("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
            >>> print(f"{track['name']} by {track['artists'][0]['name']}")
            Bohemian Rhapsody by Queen
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
            page_content = self.browser.get_page_content(embed_url)
            
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
        """Extract track information using only the Spotify track ID.
        
        Convenience method that constructs an embed URL from the track ID
        and extracts the data. Useful when you have track IDs from other
        sources (e.g., Spotify API, playlists, etc.).
        
        Args:
            track_id: Spotify track ID (22-character alphanumeric string).
                Example: "6rqhFgbbKwnb9MLmUQDhG6"
            
        Returns:
            TrackData: Same structure as extract() method
        
        Example:
            >>> track = extractor.extract_by_id("6rqhFgbbKwnb9MLmUQDhG6")
            >>> print(track['name'])
            Bohemian Rhapsody
        
        Note:
            This method always uses the embed URL format for consistency
            and to avoid authentication requirements.
        """
        # Directly create an embed URL for best results
        url = f"https://open.spotify.com/embed/track/{track_id}"
        return self.extract(url)
    
    def extract_preview_url(self, url: str) -> Optional[str]:
        """Extract only the preview audio URL from a track.
        
        Convenience method that extracts just the 30-second preview URL
        without returning the full track metadata. Useful when you only
        need the preview audio.
        
        Args:
            url: Spotify track URL in any supported format
            
        Returns:
            Optional[str]: Direct URL to the 30-second MP3 preview,
                or None if no preview is available for this track
        
        Example:
            >>> preview_url = extractor.extract_preview_url(
            ...     "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
            ... )
            >>> if preview_url:
            ...     print(f"Preview available: {preview_url}")
            ... else:
            ...     print("No preview available")
        
        Note:
            Not all tracks have preview URLs. This is typically due to
            licensing restrictions or regional availability.
        """
        track_data = self.extract(url)
        return track_data.get("preview_url")
    
    def get_track_info(self, url: str) -> Dict[str, Any]:
        """Get track information from a Spotify track URL.
        
        This is an alias for the extract() method, provided to maintain
        compatibility with the SpotifyClient interface and for semantic clarity.
        
        Args:
            url: Spotify track URL in any supported format
            
        Returns:
            Dict[str, Any]: Track information (same as extract() method)
        
        See Also:
            extract(): The main extraction method with full documentation
        """
        return self.extract(url)
    
    def get_lyrics(self, url: str, require_auth: bool = True) -> Optional[str]:
        """Get lyrics for a Spotify track.
        
        Attempts to extract lyrics from the track page. Note that Spotify's
        official lyrics (provided by Musixmatch) typically require authentication
        to access. This method will return None for most tracks without proper
        authentication.
        
        Args:
            url: Spotify track URL in any supported format
            require_auth: Whether to require authentication for lyrics access.
                Currently a placeholder for future implementation.
                Does not affect behavior in current version.
            
        Returns:
            Optional[str]: The complete lyrics text with line breaks,
                or None if lyrics are not available or accessible
        
        Example:
            >>> # Without auth, typically returns None
            >>> lyrics = extractor.get_lyrics(track_url)
            >>> if lyrics:
            ...     print(lyrics.split('\\n')[0])  # First line
            ... else:
            ...     print("Lyrics not available")
        
        Note:
            For reliable lyrics access, use SpotifyClient with authentication
            cookies. This method is limited without proper authentication.
        
        TODO:
            Implement proper lyrics extraction with authentication support.
        """
        track_data = self.extract(url)
        
        # Check if lyrics are available in the track data
        if "lyrics" in track_data and track_data["lyrics"]:
            return track_data["lyrics"]
        
        # For now, return None as lyrics extraction requires more complex implementation
        logger.debug(f"No lyrics found for track: {url}")
        return None
    
    def extract_cover_url(self, url: str) -> Optional[str]:
        """Extract album cover image URL from a track.
        
        Convenience method that extracts just the album cover URL without
        returning full track metadata. Returns the highest quality image
        available.
        
        Args:
            url: Spotify track URL in any supported format
            
        Returns:
            Optional[str]: Direct URL to the album cover image (usually JPEG),
                or None if no cover image is available
        
        Example:
            >>> cover_url = extractor.extract_cover_url(
            ...     "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
            ... )
            >>> if cover_url:
            ...     print(f"Cover image: {cover_url}")
            ...     # Can be used to download: requests.get(cover_url)
        
        Note:
            - Tracks use their album's cover image (no track-specific covers)
            - The URL returned is typically for the highest resolution available
            - Image URLs are CDN links that may expire after some time
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
