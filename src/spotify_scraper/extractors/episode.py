"""Episode extractor module for SpotifyScraper.

This module provides specialized functionality for extracting podcast episode information
from Spotify's web interface. It handles parsing of Spotify's React-based pages
to extract structured episode metadata, including basic information, audio previews,
and optionally full episode URLs (with authentication).

The extractor intelligently converts regular Spotify URLs to embed format for
better reliability and to avoid authentication requirements for basic metadata.

Example:
    >>> from spotify_scraper.browsers import create_browser
    >>> from spotify_scraper.extractors.episode import EpisodeExtractor
    >>>
    >>> browser = create_browser("requests")
    >>> extractor = EpisodeExtractor(browser)
    >>> episode_data = extractor.extract("https://open.spotify.com/episode/...")
    >>> print(f"{episode_data['name']} - {episode_data['show']['name']}")
"""

import logging
import re
from typing import Any, Dict, List, Optional

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import URLError
from spotify_scraper.core.types import EpisodeData
from spotify_scraper.utils.url import (
    convert_to_embed_url,
    extract_id,
    validate_url,
)

logger = logging.getLogger(__name__)


class EpisodeExtractor:
    """Extractor for Spotify podcast episode information.

    This class specializes in extracting episode metadata from Spotify's web pages.
    It handles the complexity of parsing Spotify's React-based interface and
    provides clean, structured data output.

    The extractor automatically converts regular Spotify URLs to embed format
    (/embed/episode/...) which provides several advantages:
        - No authentication required for basic metadata
        - More consistent page structure
        - Faster page loads
        - Same data availability as regular pages

    Attributes:
        browser: Browser instance for fetching web pages and handling requests.

    Example:
        >>> browser = create_browser("requests")
        >>> extractor = EpisodeExtractor(browser)
        >>>
        >>> # Extract by URL
        >>> episode = extractor.extract("https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G")
        >>> print(episode['name'])  # "#2333 - Protect Our Parks 15"
        >>>
        >>> # Extract by ID
        >>> episode = extractor.extract_by_id("5Q2dkZHfnGb2Y4BzzoBu2G")
        >>>
        >>> # Get preview URL
        >>> preview_url = extractor.extract_preview_url(episode_url)
        >>> print(f"Preview: {preview_url}")

    Note:
        While this extractor can parse full episode URLs when available in the page data,
        official Spotify full episodes typically require Premium authentication to access.
        Use the SpotifyClient with proper authentication for reliable full episode access.
    """

    def __init__(self, browser: Browser):
        """Initialize the EpisodeExtractor.

        Args:
            browser: Browser instance for web interactions. Can be either
                RequestsBrowser for lightweight operations or SeleniumBrowser
                for JavaScript-heavy pages.

        Example:
            >>> from spotify_scraper.browsers import create_browser
            >>> browser = create_browser("requests")
            >>> extractor = EpisodeExtractor(browser)
        """
        self.browser = browser
        logger.debug("Initialized EpisodeExtractor")

    def extract(self, url: str) -> EpisodeData:
        """Extract episode information from a Spotify episode URL.

        This method accepts any valid Spotify episode URL format and automatically
        converts it to an embed URL for extraction. This approach bypasses
        authentication requirements while still providing complete metadata.

        Args:
            url: Spotify episode URL in any format:
                - Regular: https://open.spotify.com/episode/{id}
                - Embed: https://open.spotify.com/embed/episode/{id}
                - URI: spotify:episode:{id}
                - With query params: https://open.spotify.com/episode/{id}?si=...

        Returns:
            EpisodeData: Dictionary containing episode information with fields:
                - id (str): Spotify episode ID
                - name (str): Episode title
                - uri (str): Spotify URI
                - type (str): Always "episode"
                - duration_ms (int): Duration in milliseconds
                - explicit (bool): Explicit content flag
                - show (Dict): Show information
                - audio_preview_url (str): Preview clip URL
                - video_preview_url (str): Video preview URL (if available)
                - release_date (str): Release date ISO string
                - description (str): Episode description
                - is_playable (bool): Playability status
                - is_trailer (bool): Whether it's a trailer
                - has_video (bool): Whether episode has video
                - ERROR (str): Error message if extraction failed

        Raises:
            URLError: If the URL is not a valid Spotify episode URL
            ExtractionError: If the page structure is unexpected

        Example:
            >>> episode = extractor.extract(
            ...     "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
            ... )
            >>> duration_min = episode['duration_ms'] / 1000 / 60
            >>> print(f"{episode['name']} - Duration: {duration_min:.1f} minutes")
            #2333 - Protect Our Parks 15 - Duration: 191.3 minutes
        """
        # Validate URL
        logger.debug("Extracting data from episode URL: %s", url)
        try:
            validate_url(url, expected_type="episode")
        except URLError as e:
            logger.error("Invalid episode URL: %s", e)
            return {
                "ERROR": str(e),
                "id": "",
                "name": "",
                "uri": "",
                "type": "episode",
            }

        # Extract episode ID for logging
        try:
            episode_id = extract_id(url)
            logger.debug("Extracted episode ID: %s", episode_id)
        except URLError:
            episode_id = "unknown"

        # Always use embed URL, which doesn't require authentication
        try:
            # Convert any episode URL to embed format
            embed_url = convert_to_embed_url(url)
            logger.debug("Using embed URL: %s", embed_url)

            # Get page content from embed URL
            page_content = self.browser.get_page_content(embed_url)

            # Parse episode information
            episode_data = self._extract_episode_data_from_embed(page_content)

            # If we got valid data, return it
            if episode_data and not episode_data.get("ERROR"):
                logger.debug(
                    "Successfully extracted data for episode: %s",
                    episode_data.get("name", episode_id),
                )
                return episode_data

            # If extraction failed, log the error and return the error data
            error_msg = episode_data.get("ERROR", "Unknown error")
            logger.warning("Failed to extract episode data from embed URL: %s", error_msg)
            return episode_data

        except Exception as e:
            logger.error("Failed to extract episode data: %s", e)
            return {
                "ERROR": str(e),
                "id": episode_id,
                "name": "",
                "uri": "",
                "type": "episode",
            }

    def _extract_episode_data_from_embed(self, page_content: str) -> EpisodeData:
        """Extract episode data from embed page HTML content.

        Args:
            page_content: HTML content of the embed page

        Returns:
            EpisodeData: Extracted episode information
        """
        try:
            # Find the __NEXT_DATA__ script tag which contains all the data
            match = re.search(
                r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>',
                page_content,
            )
            if not match:
                return {
                    "ERROR": "Could not find episode data in page",
                    "id": "",
                    "name": "",
                    "uri": "",
                    "type": "episode",
                }

            import json

            data = json.loads(match.group(1))

            # Navigate to the episode entity data
            episode_entity = (
                data.get("props", {})
                .get("pageProps", {})
                .get("state", {})
                .get("data", {})
                .get("entity", {})
            )

            if not episode_entity:
                return {
                    "ERROR": "Could not find episode entity in data",
                    "id": "",
                    "name": "",
                    "uri": "",
                    "type": "episode",
                }

            # Extract all available episode information
            episode_data = {
                "id": episode_entity.get("id", ""),
                "name": episode_entity.get("name", ""),
                "uri": episode_entity.get("uri", ""),
                "type": "episode",
                "duration_ms": episode_entity.get("duration", 0),
                "explicit": episode_entity.get("isExplicit", False),
                "is_playable": episode_entity.get("isPlayable", True),
                "is_trailer": episode_entity.get("isTrailer", False),
                "is_audiobook": episode_entity.get("isAudiobook", False),
                "has_video": episode_entity.get("hasVideo", False),
                "release_date": episode_entity.get("releaseDate", {}).get("isoString", ""),
                "subtitle": episode_entity.get("subtitle", ""),
                "title": episode_entity.get("title", episode_entity.get("name", "")),
            }

            # Extract audio preview URL
            audio_preview = episode_entity.get("audioPreview", {})
            if audio_preview:
                episode_data["audio_preview_url"] = audio_preview.get("url", "")

            # Extract video preview URL (if available)
            video_preview = episode_entity.get("videoPreview", {})
            if video_preview:
                episode_data["video_preview_url"] = video_preview.get("url", "")

            # Extract video thumbnail images
            video_thumbnails = episode_entity.get("videoThumbnailImage", [])
            if video_thumbnails:
                episode_data["video_thumbnails"] = video_thumbnails

            # Extract show information
            related_entity_uri = episode_entity.get("relatedEntityUri", "")
            if related_entity_uri:
                show_id = related_entity_uri.split(":")[-1] if ":" in related_entity_uri else ""
                episode_data["show"] = {
                    "id": show_id,
                    "uri": related_entity_uri,
                    "name": episode_entity.get("subtitle", ""),
                    "images": episode_entity.get("relatedEntityCoverArt", []),
                }

            # Extract visual identity (colors and images)
            visual_identity = episode_entity.get("visualIdentity", {})
            if visual_identity:
                episode_data["visual_identity"] = visual_identity
                # Also use visual identity images as episode images if available
                if "image" in visual_identity:
                    episode_data["images"] = visual_identity["image"]

            # Extract full audio file information (requires authentication)
            default_audio = (
                data.get("props", {})
                .get("pageProps", {})
                .get("state", {})
                .get("data", {})
                .get("defaultAudioFileObject", {})
            )
            if default_audio and default_audio.get("url"):
                episode_data["full_audio_urls"] = default_audio.get("url", [])
                episode_data["audio_format"] = default_audio.get("format", "")
                episode_data["file_id"] = default_audio.get("fileId", "")
                # Note if DRM is required
                if default_audio.get("video"):
                    video_info = default_audio["video"][0] if default_audio["video"] else {}
                    episode_data["requires_drm"] = video_info.get("requiresDRM", False)

            return episode_data

        except Exception as e:
            logger.error("Error parsing episode data: %s", e)
            return {
                "ERROR": f"Failed to parse episode data: {str(e)}",
                "id": "",
                "name": "",
                "uri": "",
                "type": "episode",
            }

    def extract_by_id(self, episode_id: str) -> EpisodeData:
        """Extract episode information using only the Spotify episode ID.

        Convenience method that constructs an embed URL from the episode ID
        and extracts the data. Useful when you have episode IDs from other
        sources (e.g., Spotify API, playlists, etc.).

        Args:
            episode_id: Spotify episode ID (22-character alphanumeric string).
                Example: "5Q2dkZHfnGb2Y4BzzoBu2G"

        Returns:
            EpisodeData: Same structure as extract() method

        Example:
            >>> episode = extractor.extract_by_id("5Q2dkZHfnGb2Y4BzzoBu2G")
            >>> print(episode['name'])
            #2333 - Protect Our Parks 15

        Note:
            This method always uses the embed URL format for consistency
            and to avoid authentication requirements.
        """
        # Directly create an embed URL for best results
        url = f"https://open.spotify.com/embed/episode/{episode_id}"
        return self.extract(url)

    def extract_preview_url(self, url: str) -> Optional[str]:
        """Extract only the preview audio URL from an episode.

        Convenience method that extracts just the preview URL (typically 1-2 minutes)
        without returning the full episode metadata. Useful when you only
        need the preview audio.

        Args:
            url: Spotify episode URL in any supported format

        Returns:
            Optional[str]: Direct URL to the preview MP3,
                or None if no preview is available for this episode

        Example:
            >>> preview_url = extractor.extract_preview_url(
            ...     "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
            ... )
            >>> if preview_url:
            ...     print(f"Preview available: {preview_url}")
            ... else:
            ...     print("No preview available")

        Note:
            Not all episodes have preview URLs. This is typically due to
            licensing restrictions or regional availability.
        """
        episode_data = self.extract(url)
        return episode_data.get("audio_preview_url")

    def get_episode_info(self, url: str) -> Dict[str, Any]:
        """Get episode information from a Spotify episode URL.

        This is an alias for the extract() method, provided to maintain
        compatibility with the SpotifyClient interface and for semantic clarity.

        Args:
            url: Spotify episode URL in any supported format

        Returns:
            Dict[str, Any]: Episode information (same as extract() method)

        See Also:
            extract(): The main extraction method with full documentation
        """
        return self.extract(url)

    def extract_cover_url(self, url: str) -> Optional[str]:
        """Extract show cover image URL from an episode.

        Convenience method that extracts just the show's cover URL without
        returning full episode metadata. Returns the highest quality image
        available.

        Args:
            url: Spotify episode URL in any supported format

        Returns:
            Optional[str]: Direct URL to the show cover image (usually JPEG),
                or None if no cover image is available

        Example:
            >>> cover_url = extractor.extract_cover_url(
            ...     "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
            ... )
            >>> if cover_url:
            ...     print(f"Cover image: {cover_url}")
            ...     # Can be used to download: requests.get(cover_url)

        Note:
            - Episodes use their show's cover image (no episode-specific covers)
            - The URL returned is typically for the highest resolution available
            - Image URLs are CDN links that may expire after some time
        """
        episode_data = self.extract(url)

        # First check if episode has its own images
        if "images" in episode_data and episode_data["images"]:
            images = episode_data["images"]
            if images and len(images) > 0:
                return images[0].get("url")

        # Then check show cover art
        if "show" in episode_data and "images" in episode_data["show"]:
            images = episode_data["show"]["images"]
            if images and len(images) > 0:
                return images[0].get("url")

        # Check visual identity as fallback
        if "visual_identity" in episode_data and "image" in episode_data["visual_identity"]:
            images = episode_data["visual_identity"]["image"]
            if images and len(images) > 0:
                return images[0].get("url")

        return None

    def extract_full_audio_url(self, url: str, require_auth: bool = True) -> Optional[List[str]]:
        """Extract full episode audio URLs (requires Premium authentication).

        Attempts to extract the full episode audio URLs from the page data.
        Note that these URLs require Premium authentication and have
        expiration timestamps.

        Args:
            url: Spotify episode URL in any supported format
            require_auth: Whether to require authentication for full audio access.
                If True (default), returns None if URLs are found but may not work
                without proper auth. If False, returns URLs anyway.

        Returns:
            Optional[List[str]]: List of full episode audio URLs with tokens,
                or None if full audio URLs are not available or accessible

        Example:
            >>> # With Premium authentication
            >>> full_urls = extractor.extract_full_audio_url(episode_url)
            >>> if full_urls:
            ...     print(f"Full episode URL: {full_urls[0]}")
            ... else:
            ...     print("Full episode requires Premium account")

        Note:
            - Full episode URLs require active Premium authentication
            - URLs include expiration timestamps and authentication tokens
            - For reliable full episode access, use SpotifyClient with Premium cookies
        """
        episode_data = self.extract(url)

        full_urls = episode_data.get("full_audio_urls")

        if full_urls and require_auth:
            logger.warning(
                "Full episode URLs found but require Premium authentication. "
                "Use SpotifyClient with Premium cookies for reliable access."
            )

        return full_urls if full_urls else None
