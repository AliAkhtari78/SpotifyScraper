"""
Core scraper module for SpotifyScraper.

This module provides the base Scraper class that handles the low-level
scraping functionality.
"""

from typing import Dict, Optional, Any, Union
import logging
import json
from urllib.parse import urlparse, urljoin

from spotify_scraper.exceptions import ScrapingError, URLError
from spotify_scraper.browsers.base import Browser
from spotify_scraper.constants import SPOTIFY_BASE_URL, SPOTIFY_EMBED_URL

logger = logging.getLogger(__name__)


class Scraper:
    """
    Base scraper class for extracting data from Spotify web player.
    
    This class provides common scraping functionality used by various extractors.
    """
    
    def __init__(self, browser: Browser, log_level: str = "INFO"):
        """
        Initialize the Scraper.
        
        Args:
            browser: Browser instance for web interactions
            log_level: Logging level string (e.g., "DEBUG", "INFO")
        """
        self.browser = browser

        # Configure logger for this instance based on log_level
        try:
            logger.setLevel(getattr(logging, log_level.upper()))
        except AttributeError:
            logger.setLevel(logging.INFO) # Default to INFO if invalid level is provided
            logger.warning(f"Invalid log_level '{log_level}'. Defaulting to INFO.")

        logger.debug("Initialized Scraper")
    
    @staticmethod
    def _script_data_to_json(script_content: str) -> Dict[str, Any]:
        """
        Convert the content of a <script id="__NEXT_DATA__"> tag to a JSON object.

        Args:
            script_content: The string content of the script tag.

        Returns:
            Dict containing parsed JSON data.

        Raises:
            ScrapingError: If JSON parsing fails.
        """
        try:
            # The content is typically directly JSON.
            return json.loads(script_content)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing __NEXT_DATA__ JSON: {e}")
            logger.debug(f"Problematic script content: {script_content[:500]}...") # Log snippet
            raise ScrapingError(f"Error parsing __NEXT_DATA__ JSON: {e}") from e

    @staticmethod
    def _ms_to_readable(millis: int) -> str:
        """
        Convert milliseconds to a readable time format (MM:SS or HH:MM:SS).

        Args:
            millis: Time in milliseconds
            
        Returns:
            Formatted time string (e.g., "4:30" or "1:30:45")
        """
        if not isinstance(millis, int) or millis < 0:
            logger.warning(f"Invalid milliseconds value: {millis}. Returning '0:00'.")
            return "0:00"

        seconds_total = millis // 1000
        minutes_total = seconds_total // 60
        hours = minutes_total // 60

        seconds = seconds_total % 60
        minutes = minutes_total % 60

        if hours == 0:
            return f"{minutes}:{seconds:02d}"
        else:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def convert_to_embed_url(url: str) -> Optional[str]:
        """
        Convert a standard Spotify track URL to its embed equivalent.

        Args:
            url: Spotify track URL (e.g., https://open.spotify.com/track/TRACK_ID)

        Returns:
            Embed URL (e.g., https://open.spotify.com/embed/track/TRACK_ID)
            or None if the URL is not a valid track URL.
        """
        parsed_url = urlparse(url)
        if parsed_url.netloc == "open.spotify.com" and parsed_url.path.startswith("/track/"):
            track_id = parsed_url.path.split("/track/")[-1]
            if "?" in track_id: # Remove query params from track_id
                track_id = track_id.split("?")[0]
            return urljoin(SPOTIFY_EMBED_URL, f"track/{track_id}")
        logger.warning(f"Could not convert URL to embed URL: {url}")
        return None

    @staticmethod
    def get_track_id_from_url(url: str) -> Optional[str]:
        """
        Extracts the track ID from a Spotify track URL.

        Args:
            url: The Spotify track URL.

        Returns:
            The track ID if found, otherwise None.
        """
        parsed_url = urlparse(url)
        if parsed_url.netloc == "open.spotify.com":
            path_parts = parsed_url.path.strip("/").split("/")
            if len(path_parts) >= 2 and path_parts[0] in ["track", "embed"]:
                # For /track/ID or /embed/track/ID
                track_id_index = 1 if path_parts[0] == "track" else (2 if path_parts[0] == "embed" and path_parts[1] == "track" else -1)
                if track_id_index != -1 and track_id_index < len(path_parts):
                    track_id = path_parts[track_id_index]
                    return track_id.split("?")[0] # Remove query parameters
        logger.warning(f"Could not extract track ID from URL: {url}")
        return None

    def validate_spotify_url(self, url: str, expected_type: Optional[str] = None) -> bool:
        """
        Validate a Spotify URL and optionally its type.

        Args:
            url: URL to validate.
            expected_type: Expected URL type (e.g., 'track', 'playlist', 'album', 'artist', 'embed/track').

        Returns:
            True if valid.

        Raises:
            URLError: If the URL is invalid or does not match the expected type.
        """
        if not url or not isinstance(url, str):
            raise URLError("URL must be a non-empty string.")

        parsed_url = urlparse(url)
        if parsed_url.scheme not in ["http", "https"] or parsed_url.netloc != "open.spotify.com":
            raise URLError(f"Invalid Spotify URL: {url}. Must be from 'open.spotify.com'.")

        path = parsed_url.path.strip("/") # Normalize path

        if expected_type:
            # Handle embed case specifically if needed, e.g. 'embed/track'
            if expected_type.startswith("embed/"):
                if not path.startswith(expected_type):
                    raise URLError(f"URL '{url}' is not a Spotify {expected_type} URL. Path: '{path}'")
            elif not path.startswith(expected_type + "/"):
                 # Ensure it's followed by a slash for non-embed types like 'track/'
                raise URLError(f"URL '{url}' is not a Spotify {expected_type} URL. Path: '{path}'")

        logger.debug(f"Validated Spotify URL: {url} (Expected type: {expected_type})")
        return True


