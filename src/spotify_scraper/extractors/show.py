"""Show extractor module for SpotifyScraper.

This module provides specialized functionality for extracting podcast show information
from Spotify's web interface. It handles parsing of Spotify's React-based pages
to extract structured show metadata, including episodes list, ratings, and categories.

The extractor intelligently converts regular Spotify URLs to embed format for
better reliability and to avoid authentication requirements for basic metadata.

Example:
    >>> from spotify_scraper.browsers import create_browser
    >>> from spotify_scraper.extractors.show import ShowExtractor
    >>>
    >>> browser = create_browser("requests")
    >>> extractor = ShowExtractor(browser)
    >>> show_data = extractor.extract("https://open.spotify.com/show/...")
    >>> print(f"{show_data['name']} - {show_data['publisher']}")
"""

import logging
import re
from typing import Any, Dict, List, Optional

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import URLError
from spotify_scraper.core.types import ShowData
from spotify_scraper.utils.url import (
    convert_to_embed_url,
    extract_id,
    validate_url,
)

logger = logging.getLogger(__name__)


class ShowExtractor:
    """Extractor for Spotify podcast show information.

    This class specializes in extracting show metadata from Spotify's web pages.
    It handles the complexity of parsing Spotify's React-based interface and
    provides clean, structured data output including episodes list.

    The extractor automatically converts regular Spotify URLs to embed format
    (/embed/show/...) which provides several advantages:
        - No authentication required for basic metadata
        - More consistent page structure
        - Faster page loads
        - Same data availability as regular pages

    Attributes:
        browser: Browser instance for fetching web pages and handling requests.

    Example:
        >>> browser = create_browser("requests")
        >>> extractor = ShowExtractor(browser)
        >>>
        >>> # Extract by URL
        >>> show = extractor.extract("https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk")
        >>> print(show['name'])  # "The Joe Rogan Experience"
        >>>
        >>> # Extract by ID
        >>> show = extractor.extract_by_id("4rOoJ6Egrf8K2IrywzwOMk")
        >>>
        >>> # Get episodes list
        >>> episodes = show.get('episodes', [])
        >>> print(f"Found {len(episodes)} episodes")

    Note:
        The embed page typically shows only recent episodes. For complete episode
        listings, pagination or API access would be required.
    """

    def __init__(self, browser: Browser):
        """Initialize the ShowExtractor.

        Args:
            browser: Browser instance for web interactions. Can be either
                RequestsBrowser for lightweight operations or SeleniumBrowser
                for JavaScript-heavy pages.

        Example:
            >>> from spotify_scraper.browsers import create_browser
            >>> browser = create_browser("requests")
            >>> extractor = ShowExtractor(browser)
        """
        self.browser = browser
        logger.debug("Initialized ShowExtractor")

    def extract(self, url: str) -> ShowData:
        """Extract show information from a Spotify show URL.

        This method accepts any valid Spotify show URL format and automatically
        converts it to an embed URL for extraction. This approach bypasses
        authentication requirements while still providing complete metadata.

        Args:
            url: Spotify show URL in any format:
                - Regular: https://open.spotify.com/show/{id}
                - Embed: https://open.spotify.com/embed/show/{id}
                - URI: spotify:show:{id}
                - With query params: https://open.spotify.com/show/{id}?si=...

        Returns:
            ShowData: Dictionary containing show information with fields:
                - id (str): Spotify show ID
                - name (str): Show title
                - uri (str): Spotify URI
                - type (str): Always "show"
                - description (str): Show description
                - publisher (str): Publisher name
                - categories (List[str]): Show categories/genres
                - total_episodes (int): Total number of episodes
                - images (List[Dict]): Cover art in various sizes
                - episodes (List[Dict]): Recent episodes with metadata
                - rating (Dict): Rating information if available
                - explicit (bool): Explicit content flag
                - media_type (str): Type of media (usually "audio" or "video")
                - ERROR (str): Error message if extraction failed

        Raises:
            URLError: If the URL is not a valid Spotify show URL
            ExtractionError: If the page structure is unexpected

        Example:
            >>> show = extractor.extract("https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk")
            >>> print(f"{show['name']} by {show['publisher']}")
            The Joe Rogan Experience by Joe Rogan
            >>> print(f"Episodes: {show['total_episodes']}")
        """
        # Validate URL
        logger.debug("Extracting data from show URL: %s", url)
        try:
            validate_url(url, expected_type="show")
        except URLError as e:
            logger.error("Invalid show URL: %s", e)
            return {
                "ERROR": str(e),
                "id": "",
                "name": "",
                "uri": "",
                "type": "show",
            }

        # Extract show ID for logging
        try:
            show_id = extract_id(url)
            logger.debug("Extracted show ID: %s", show_id)
        except URLError:
            show_id = "unknown"

        # Always use embed URL, which doesn't require authentication
        try:
            # Convert any show URL to embed format
            embed_url = convert_to_embed_url(url)
            logger.debug("Using embed URL: %s", embed_url)

            # Get page content from embed URL
            page_content = self.browser.get_page_content(embed_url)

            # Parse show information
            show_data = self._extract_show_data_from_embed(page_content)

            # If we got valid data, return it
            if show_data and not show_data.get("ERROR"):
                logger.debug(
                    f"Successfully extracted data for show: {show_data.get('name', show_id)}"
                )
                return show_data

            # If extraction failed, log the error and return the error data
            error_msg = show_data.get("ERROR", "Unknown error")
            logger.warning("Failed to extract show data from embed URL: %s", error_msg)
            return show_data

        except Exception as e:
            logger.error("Failed to extract show data: %s", e)
            return {
                "ERROR": str(e),
                "id": show_id,
                "name": "",
                "uri": "",
                "type": "show",
            }

    def _extract_show_data_from_embed(self, page_content: str) -> ShowData:
        """Extract show data from embed page HTML content.

        Args:
            page_content: HTML content of the embed page

        Returns:
            ShowData: Extracted show information
        """
        try:
            # Find the __NEXT_DATA__ script tag which contains all the data
            match = re.search(
                r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>',
                page_content,
            )
            if not match:
                return {
                    "ERROR": "Could not find show data in page",
                    "id": "",
                    "name": "",
                    "uri": "",
                    "type": "show",
                }

            import json

            data = json.loads(match.group(1))

            # Navigate to the show entity data
            show_entity = (
                data.get("props", {})
                .get("pageProps", {})
                .get("state", {})
                .get("data", {})
                .get("entity", {})
            )

            if not show_entity:
                return {
                    "ERROR": "Could not find show entity in data",
                    "id": "",
                    "name": "",
                    "uri": "",
                    "type": "show",
                }

            # Check if we got episode data instead of show data
            if show_entity.get("type") == "episode":
                logger.warning(
                    "Embed URL returned episode data instead of show data, "
                    "attempting to extract show info from episode"
                )
                show_data = self._extract_show_data_from_episode(show_entity, data)

                # Try to enrich the data from the regular page
                if show_data and not show_data.get("ERROR"):
                    show_data = self._enrich_show_data_from_regular_page(show_data)

                return show_data

            # Extract all available show information
            show_data = {
                "id": show_entity.get("id", ""),
                "name": show_entity.get("name", ""),
                "uri": show_entity.get("uri", ""),
                "type": "show",
                "title": show_entity.get("title", show_entity.get("name", "")),
                "subtitle": show_entity.get("subtitle", ""),
                "publisher": (
                    show_entity.get("publisher", {}).get("name", "")
                    if isinstance(show_entity.get("publisher"), dict)
                    else show_entity.get("publisher", "")
                ),
                "media_type": show_entity.get("mediaType", ""),
                "is_externally_hosted": show_entity.get("isExternallyHosted", False),
                "explicit": (show_entity.get("htmlDescription", "").lower().find("explicit") != -1),
            }

            # Extract description
            html_desc = show_entity.get("htmlDescription", "")
            if html_desc:
                # Simple HTML tag removal
                show_data["description"] = re.sub(r"<[^>]+>", "", html_desc)

            # Extract images
            if "visualIdentity" in show_entity and "image" in show_entity["visualIdentity"]:
                show_data["images"] = show_entity["visualIdentity"]["image"]
            elif "coverArt" in show_entity:
                show_data["images"] = show_entity.get("coverArt", [])

            # Extract visual identity (colors)
            visual_identity = show_entity.get("visualIdentity", {})
            if visual_identity:
                show_data["visual_identity"] = {
                    "background_color": visual_identity.get("backgroundBase"),
                    "text_color": visual_identity.get("textBase"),
                }

            # Extract rating if available
            if "podcastV2" in show_entity:
                podcast_v2 = show_entity["podcastV2"]
                if "ratings" in podcast_v2:
                    ratings = podcast_v2["ratings"]
                    show_data["rating"] = {
                        "average": ratings.get("averageRating", 0),
                        "count": ratings.get("totalRatings", 0),
                    }

            # Extract episodes from the page
            episodes_data = []
            episodes_entity = (
                data.get("props", {})
                .get("pageProps", {})
                .get("state", {})
                .get("data", {})
                .get("episodeList", {})
            )

            if episodes_entity and "items" in episodes_entity:
                for episode in episodes_entity["items"]:
                    episode_info = {
                        "id": episode.get("id", ""),
                        "name": episode.get("name", ""),
                        "uri": episode.get("uri", ""),
                        "duration_ms": episode.get("duration", 0),
                        "release_date": (
                            episode.get("releaseDate", {}).get("isoString", "")
                            if isinstance(episode.get("releaseDate"), dict)
                            else episode.get("releaseDate", "")
                        ),
                        "explicit": episode.get("isExplicit", False),
                        "is_playable": episode.get("isPlayable", True),
                        "has_video": episode.get("hasVideo", False),
                        "is_trailer": episode.get("isTrailer", False),
                    }

                    # Extract audio preview if available
                    if "audioPreview" in episode:
                        episode_info["audio_preview_url"] = episode["audioPreview"].get("url", "")

                    # Extract video preview if available
                    if "videoPreview" in episode:
                        episode_info["video_preview_url"] = episode["videoPreview"].get("url", "")

                    episodes_data.append(episode_info)

            show_data["episodes"] = episodes_data
            show_data["total_episodes"] = (
                episodes_entity.get("totalCount", len(episodes_data))
                if episodes_entity
                else len(episodes_data)
            )

            # Extract categories/topics if available
            topics = show_entity.get("topics", [])
            if topics:
                show_data["categories"] = [
                    topic.get("title", "") for topic in topics if topic.get("title")
                ]

            return show_data

        except Exception as e:
            logger.error("Error parsing show data: %s", e)
            return {
                "ERROR": f"Failed to parse show data: {str(e)}",
                "id": "",
                "name": "",
                "uri": "",
                "type": "show",
            }

    def _extract_show_data_from_episode(
        self, episode_entity: Dict[str, Any], full_data: Dict[str, Any]
    ) -> ShowData:
        """Extract show data from episode data when embed returns episode instead of show.

        Args:
            episode_entity: Episode entity data from the embed page
            full_data: Full data structure from __NEXT_DATA__

        Returns:
            ShowData: Extracted show information (limited)
        """
        try:
            # Extract show ID from related entity URI
            related_uri = episode_entity.get("relatedEntityUri", "")
            show_id = ""
            if related_uri and related_uri.startswith("spotify:show:"):
                show_id = related_uri.replace("spotify:show:", "")

            # Extract show name from subtitle (usually contains show name)
            show_name = episode_entity.get("subtitle", "")

            # Get cover art from related entity
            cover_art = episode_entity.get("relatedEntityCoverArt", [])

            # Extract episodes from the full data if available
            episodes_data = []
            episodes_entity = (
                full_data.get("props", {})
                .get("pageProps", {})
                .get("state", {})
                .get("data", {})
                .get("episodeList", {})
            )

            if episodes_entity and "items" in episodes_entity:
                for episode in episodes_entity["items"]:
                    episode_info = {
                        "id": episode.get("id", ""),
                        "name": episode.get("name", ""),
                        "uri": episode.get("uri", ""),
                        "duration_ms": episode.get("duration", 0),
                        "release_date": (
                            episode.get("releaseDate", {}).get("isoString", "")
                            if isinstance(episode.get("releaseDate"), dict)
                            else episode.get("releaseDate", "")
                        ),
                        "explicit": episode.get("isExplicit", False),
                        "is_playable": episode.get("isPlayable", True),
                        "has_video": episode.get("hasVideo", False),
                        "is_trailer": episode.get("isTrailer", False),
                    }

                    # Extract audio preview if available
                    if "audioPreview" in episode:
                        episode_info["audio_preview_url"] = episode["audioPreview"].get("url", "")

                    episodes_data.append(episode_info)

            # Create basic show data structure
            show_data = {
                "id": show_id,
                "name": show_name,
                "uri": related_uri,
                "type": "show",
                "title": show_name,
                "images": cover_art,
                "description": f"Podcast show: {show_name}",
                "publisher": "",  # Not available in episode data
                "media_type": "audio",  # Assume audio for now
                "is_externally_hosted": False,
                "explicit": episode_entity.get("isExplicit", False),
                "episodes": episodes_data,
                "total_episodes": (
                    episodes_entity.get("totalCount", len(episodes_data))
                    if episodes_entity
                    else len(episodes_data)
                ),
                "_extracted_from_episode": True,  # Flag to indicate limited data
                "_latest_episode": {
                    "id": episode_entity.get("id", ""),
                    "name": episode_entity.get("name", ""),
                    "uri": episode_entity.get("uri", ""),
                    "release_date": (
                        episode_entity.get("releaseDate", {}).get("isoString", "")
                        if isinstance(episode_entity.get("releaseDate"), dict)
                        else episode_entity.get("releaseDate", "")
                    ),
                    "duration_ms": episode_entity.get("duration", 0),
                    "explicit": episode_entity.get("isExplicit", False),
                    "has_video": episode_entity.get("hasVideo", False),
                },
            }

            # Extract visual identity if available
            if "visualIdentity" in episode_entity:
                visual_identity = episode_entity["visualIdentity"]
                show_data["visual_identity"] = {
                    "background_color": visual_identity.get("backgroundBase"),
                    "text_color": visual_identity.get("textBase"),
                }

            # Try to get the embedded entity URI for potential fallback
            embedded_uri = (
                full_data.get("props", {})
                .get("pageProps", {})
                .get("state", {})
                .get("data", {})
                .get("embeded_entity_uri", "")
            )
            if embedded_uri and embedded_uri.startswith("spotify:show:"):
                # This confirms we're dealing with a show embed that returned episode data
                show_data["_embedded_uri"] = embedded_uri

            logger.info(
                f"Extracted limited show data from episode for show: {show_name} (ID: {show_id})"
            )

            return show_data

        except Exception as e:
            logger.error("Error extracting show data from episode: %s", e)
            return {
                "ERROR": f"Failed to extract show data from episode: {str(e)}",
                "id": "",
                "name": "",
                "uri": "",
                "type": "show",
            }

    def _enrich_show_data_from_regular_page(self, show_data: ShowData) -> ShowData:
        """Try to enrich show data by fetching additional info from regular page.

        Args:
            show_data: Basic show data to enrich

        Returns:
            ShowData: Enriched show data
        """
        try:
            # Only try this if we have a show ID
            if not show_data.get("id"):
                return show_data

            # Try to get the regular page
            regular_url = f"https://open.spotify.com/show/{show_data['id']}"
            page_content = self.browser.get_page_content(regular_url)

            # Look for JSON-LD data which often has publisher info
            jsonld_match = re.search(
                r'<script type="application/ld\+json">([^<]+)</script>', page_content
            )
            if jsonld_match:
                import json

                jsonld_data = json.loads(jsonld_match.group(1))

                # Extract publisher if available
                if "publisher" in jsonld_data and not show_data.get("publisher"):
                    publisher = jsonld_data["publisher"]
                    if isinstance(publisher, dict) and "name" in publisher:
                        show_data["publisher"] = publisher["name"]
                    elif isinstance(publisher, str):
                        show_data["publisher"] = publisher

                # Extract description if better than what we have
                if "description" in jsonld_data and show_data.get("description", "").startswith(
                    "Podcast show:"
                ):
                    # Clean up the description
                    desc = jsonld_data["description"]
                    desc = desc.replace("Listen to ", "").replace(" on Spotify.", ".")
                    show_data["description"] = desc

            # Look for meta tags
            desc_match = re.search(
                r'<meta property="og:description" content="([^"]+)"', page_content
            )
            if desc_match and show_data.get("description", "").startswith("Podcast show:"):
                # Parse the meta description format: "Podcast · Publisher · Description"
                parts = desc_match.group(1).split(" · ")
                if len(parts) >= 3:
                    show_data["publisher"] = (
                        parts[1] if not show_data.get("publisher") else show_data["publisher"]
                    )
                    show_data["description"] = parts[2]

        except Exception as e:
            logger.debug(f"Could not enrich show data from regular page: {e}")

        return show_data

    def extract_by_id(self, show_id: str) -> ShowData:
        """Extract show information using only the Spotify show ID.

        Convenience method that constructs an embed URL from the show ID
        and extracts the data. Useful when you have show IDs from other
        sources (e.g., Spotify API, episode data, etc.).

        Args:
            show_id: Spotify show ID (22-character alphanumeric string).
                Example: "4rOoJ6Egrf8K2IrywzwOMk"

        Returns:
            ShowData: Same structure as extract() method

        Example:
            >>> show = extractor.extract_by_id("4rOoJ6Egrf8K2IrywzwOMk")
            >>> print(show['name'])
            The Joe Rogan Experience

        Note:
            This method always uses the embed URL format for consistency
            and to avoid authentication requirements.
        """
        # Directly create an embed URL for best results
        url = f"https://open.spotify.com/embed/show/{show_id}"
        return self.extract(url)

    def get_show_info(self, url: str) -> Dict[str, Any]:
        """Get show information from a Spotify show URL.

        This is an alias for the extract() method, provided to maintain
        compatibility with the SpotifyClient interface and for semantic clarity.

        Args:
            url: Spotify show URL in any supported format

        Returns:
            Dict[str, Any]: Show information (same as extract() method)

        See Also:
            extract(): The main extraction method with full documentation
        """
        return self.extract(url)

    def extract_cover_url(self, url: str) -> Optional[str]:
        """Extract show cover image URL.

        Convenience method that extracts just the show's cover URL without
        returning full show metadata. Returns the highest quality image
        available.

        Args:
            url: Spotify show URL in any supported format

        Returns:
            Optional[str]: Direct URL to the show cover image (usually JPEG),
                or None if no cover image is available

        Example:
            >>> cover_url = extractor.extract_cover_url(
            ...     "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"
            ... )
            >>> if cover_url:
            ...     print(f"Cover image: {cover_url}")
            ...     # Can be used to download: requests.get(cover_url)

        Note:
            - The URL returned is typically for the highest resolution available
            - Image URLs are CDN links that may expire after some time
        """
        show_data = self.extract(url)

        # Check if show has images
        if "images" in show_data and show_data["images"]:
            images = show_data["images"]
            if images and len(images) > 0:
                return images[0].get("url")

        # Check visual identity as fallback
        if "visual_identity" in show_data and "image" in show_data["visual_identity"]:
            images = show_data["visual_identity"]["image"]
            if images and len(images) > 0:
                return images[0].get("url")

        return None

    def extract_episodes_list(self, url: str) -> List[Dict[str, Any]]:
        """Extract just the episodes list from a show.

        Convenience method that extracts only the episodes list without
        returning full show metadata. Useful when you only need episode
        information.

        Args:
            url: Spotify show URL in any supported format

        Returns:
            List[Dict[str, Any]]: List of episode dictionaries with basic info

        Example:
            >>> episodes = extractor.extract_episodes_list(
            ...     "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"
            ... )
            >>> for ep in episodes[:5]:  # First 5 episodes
            ...     print(f"{ep['name']} - {ep['duration_ms'] / 1000 / 60:.1f} min")

        Note:
            The embed page typically only includes recent episodes, not the
            complete show history.
        """
        show_data = self.extract(url)
        return show_data.get("episodes", [])
