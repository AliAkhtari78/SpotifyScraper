"""Lyrics extractor module for SpotifyScraper.

This module provides functionality for extracting lyrics from Spotify tracks.
Lyrics are typically only available with authentication and may not be available
for all tracks.
"""

import logging
import re
from typing import Optional, Dict, Any

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import URLError, ExtractionError, AuthenticationError
from spotify_scraper.utils.url import extract_id, validate_url

logger = logging.getLogger(__name__)


class LyricsExtractor:
    """Extractor for Spotify track lyrics.

    This class handles the extraction of lyrics from Spotify's web interface.
    Note that lyrics typically require authentication to access and are provided
    by third-party services like Musixmatch.

    Attributes:
        browser: Browser instance for fetching web pages.
        authenticated: Whether the browser session is authenticated.
    """

    def __init__(self, browser: Browser):
        """Initialize the LyricsExtractor.

        Args:
            browser: Browser instance for web interactions.
        """
        self.browser = browser
        # Check if browser has authentication
        self.authenticated = hasattr(browser, "_session") and browser._session.cookies
        logger.debug("Initialized LyricsExtractor (authenticated: %s)", self.authenticated)

    def extract(self, url: str, require_auth: bool = True) -> Optional[str]:
        """Extract lyrics for a Spotify track.

        Args:
            url: Spotify track URL in any supported format.
            require_auth: Whether to require authentication for lyrics access.
                If True and not authenticated, raises AuthenticationError.
                If False, attempts extraction anyway (may return None).

        Returns:
            Optional[str]: The complete lyrics text with line breaks,
                or None if lyrics are not available.

        Raises:
            URLError: If the URL is not a valid Spotify track URL.
            AuthenticationError: If require_auth is True and not authenticated.
            ExtractionError: If there's an error extracting the lyrics.
        """
        # Validate URL
        validate_url(url, expected_type="track")
        track_id = extract_id(url)

        logger.debug("Extracting lyrics for track ID: %s", track_id)

        # Check authentication
        if require_auth and not self.authenticated:
            raise AuthenticationError(
                "Lyrics extraction requires authentication. "
                "Please provide cookies via SpotifyClient initialization."
            )

        try:
            # Note: Spotify's lyrics API requires OAuth authentication
            # Cookie-based authentication is not sufficient for lyrics access

            # Check if we have an access token (OAuth)
            access_token = None
            if hasattr(self.browser, "_session") and hasattr(self.browser._session, "headers"):
                auth_header = self.browser._session.headers.get("Authorization", "")
                if auth_header.startswith("Bearer "):
                    access_token = auth_header.replace("Bearer ", "")

            if not access_token and require_auth:
                logger.warning(
                    "Lyrics extraction requires OAuth access token. "
                    "Cookie authentication alone is not sufficient. "
                    "Consider using Spotify Web API with proper OAuth flow."
                )
                return None

            # Method 2: Try to extract from the track page
            track_url = f"https://open.spotify.com/track/{track_id}"
            page_content = self.browser.get_page_content(track_url)

            # Look for lyrics in various possible locations
            lyrics = self._extract_lyrics_from_page(page_content)
            if lyrics:
                return lyrics

            # Method 3: Try the web API with authentication token
            if self.authenticated:
                lyrics = self._try_web_api_lyrics(track_id)
                if lyrics:
                    return lyrics

            logger.debug("No lyrics found for track %s", track_id)
            return None

        except Exception as e:
            logger.error("Error extracting lyrics for track %s: %s", track_id, e)
            if require_auth:
                raise ExtractionError(f"Failed to extract lyrics: {str(e)}")
            return None

    def _parse_lyrics_response(self, data: Dict[str, Any]) -> Optional[str]:
        """Parse lyrics from API response.

        Args:
            data: JSON response from lyrics API.

        Returns:
            Optional[str]: Parsed lyrics text or None.
        """
        try:
            # Check if lyrics are available
            if not data.get("lyrics") or not data["lyrics"].get("lines"):
                return None

            # Extract lyrics lines
            lines = []
            for line in data["lyrics"]["lines"]:
                if "words" in line:
                    lines.append(line["words"])

            return "\n".join(lines) if lines else None

        except Exception as e:
            logger.debug("Error parsing lyrics response: %s", e)
            return None

    def _extract_lyrics_from_page(self, page_content: str) -> Optional[str]:
        """Extract lyrics from track page HTML.

        Args:
            page_content: HTML content of the track page.

        Returns:
            Optional[str]: Extracted lyrics or None.
        """
        # Look for lyrics container in various formats
        patterns = [
            # Look for lyrics in data attributes
            r'data-lyrics="([^"]+)"',
            # Look for lyrics in JSON data
            r'"lyrics":\s*{[^}]*"text":\s*"([^"]+)"',
            # Look for lyrics container
            r'<div[^>]*class="[^"]*lyrics[^"]*"[^>]*>(.*?)</div>',
            # Look for lyrics in script tags
            r'<script[^>]*>.*?"lyrics":\s*"([^"]+)".*?</script>',
        ]

        for pattern in patterns:
            match = re.search(pattern, page_content, re.DOTALL | re.IGNORECASE)
            if match:
                lyrics = match.group(1)
                # Unescape common HTML entities
                lyrics = lyrics.replace("\\n", "\n")
                lyrics = lyrics.replace('\\"', '"')
                lyrics = lyrics.replace("\\'", "'")
                lyrics = lyrics.replace("&amp;", "&")
                lyrics = lyrics.replace("&lt;", "<")
                lyrics = lyrics.replace("&gt;", ">")
                return lyrics.strip()

        return None

    def _try_web_api_lyrics(self, track_id: str) -> Optional[str]:
        """Try to get lyrics using the web API endpoints.

        Args:
            track_id: Spotify track ID.

        Returns:
            Optional[str]: Lyrics text or None.
        """
        try:
            # Try the color-lyrics endpoint with proper authentication
            api_url = f"https://api.spotify.com/v1/tracks/{track_id}"

            # This would require proper OAuth token which we might not have
            # For now, return None as this requires more complex auth
            return None

        except Exception as e:
            logger.debug("Web API lyrics attempt failed: %s", e)
            return None

