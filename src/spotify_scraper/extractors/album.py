"""
Album extractor module for SpotifyScraper.

This module provides functionality for extracting album information
from Spotify album pages, with support for both regular and embed URLs.
"""

import logging
from typing import Any, Dict, List, Optional

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.constants import ALBUM_JSON_PATH
from spotify_scraper.core.exceptions import ParsingError, ScrapingError, URLError
from spotify_scraper.core.types import AlbumData, TrackData
from spotify_scraper.parsers.json_parser import (
    extract_json_from_next_data,
    extract_json_from_resource,
    get_nested_value,
)
from spotify_scraper.utils.url import (
    convert_to_embed_url,
    extract_id,
    validate_url,
)

logger = logging.getLogger(__name__)


class AlbumExtractor:
    """
    Extractor for Spotify album information.

    This class provides functionality to extract information from
    Spotify album pages, with support for different page structures and
    automatic conversion between regular and embed URLs.

    Attributes:
        browser: Browser instance for web interactions

    Note:
        This extractor prioritizes using Spotify embed URLs (/embed/album/...)
        over regular URLs because embed endpoints do not require authentication
        and provide comprehensive album metadata.
    """

    def __init__(self, browser: Browser):
        """
        Initialize the AlbumExtractor.

        Args:
            browser: Browser instance for web interactions
        """
        self.browser = browser
        logger.debug("Initialized AlbumExtractor")

    def extract(self, url: str) -> AlbumData:
        """
        Extract album information from a Spotify album URL.

        This method takes any Spotify album URL and converts it to an
        embed URL format for extraction. Embed URLs don't require Spotify
        login/authentication but still provide full album metadata.

        Args:
            url: Spotify album URL (will be converted to embed format)

        Returns:
            Album data as a dictionary

        Raises:
            URLError: If the URL is invalid
            ScrapingError: If extraction fails
        """
        # Validate URL
        logger.debug("Extracting data from album URL: %s", url)
        try:
            validate_url(url, expected_type="album")
        except URLError as e:
            logger.error("Invalid album URL: %s", e)
            raise

        # Extract album ID for logging
        try:
            album_id = extract_id(url)
            logger.debug("Extracted album ID: %s", album_id)
        except URLError:
            album_id = "unknown"

        # Always use embed URL, which doesn't require authentication
        try:
            # Convert any album URL to embed format
            embed_url = convert_to_embed_url(url)
            logger.debug("Using embed URL: %s", embed_url)

            # Get page content from embed URL
            page_content = self.browser.get_page_content(embed_url)

            # Parse album information
            album_data = self.extract_album_data_from_page(page_content)

            # If we got valid data, return it
            if album_data and not album_data.get("ERROR"):
                logger.debug(
                    f"Successfully extracted data for album: {album_data.get('name', album_id)}"
                )
                return album_data

            # If extraction failed, raise an error
            error_msg = album_data.get("ERROR", "Unknown error")
            logger.warning("Failed to extract album data from embed URL: %s", error_msg)
            raise ScrapingError(f"Failed to extract album data: {error_msg}")

        except URLError:
            # Re-raise URLError as-is
            raise
        except ScrapingError:
            # Re-raise ScrapingError as-is
            raise
        except Exception as e:
            logger.error("Failed to extract album data: %s", e)
            raise ScrapingError(f"Failed to extract album data: {str(e)}") from e

    def extract_by_id(self, album_id: str) -> AlbumData:
        """
        Extract album information by ID.

        This method constructs an embed URL from the album ID and extracts the data.

        Args:
            album_id: Spotify album ID

        Returns:
            Album data as a dictionary
        """
        # Directly create an embed URL for best results
        url = f"https://open.spotify.com/embed/album/{album_id}"
        return self.extract(url)

    def extract_album_data_from_page(self, html_content: str) -> AlbumData:
        """
        Extract album data from a Spotify page.

        This function tries multiple methods to extract album data,
        falling back to alternative methods if the preferred method fails.

        Args:
            html_content: HTML content of the Spotify page

        Returns:
            Structured album data

        Raises:
            ParsingError: If all extraction methods fail
        """
        # Try using __NEXT_DATA__ first (modern approach)
        try:
            json_data = extract_json_from_next_data(html_content)
            return self.extract_album_data(json_data, ALBUM_JSON_PATH)
        except ParsingError as e:
            logger.warning("Failed to extract album data using __NEXT_DATA__: %s", e)

        # Fallback to resource script tag (legacy approach)
        try:
            json_data = extract_json_from_resource(html_content)
            # For resource script tag, the data is directly in the root
            return self.extract_album_data(json_data, "")
        except ParsingError as e:
            logger.warning("Failed to extract album data using resource script: %s", e)

        # If all methods fail, raise a more specific error
        raise ParsingError("Failed to extract album data from page using any method")

    def extract_album_data(self, json_data: Dict[str, Any], path: str) -> AlbumData:
        """
        Extract album data from Spotify JSON data.

        Args:
            json_data: Parsed JSON data
            path: JSON path to album data (default: from constants)

        Returns:
            Structured album data

        Raises:
            ParsingError: If album data extraction fails
        """
        try:
            # Get album data from specified path
            album_data = get_nested_value(json_data, path)
            if not album_data:
                raise ParsingError(f"No album data found at path: {path}")

            # Create a standardized album data object
            # This handles variations in the Spotify data structure
            result: AlbumData = {
                "id": album_data.get("id", ""),
                "name": album_data.get("name", ""),
                "uri": album_data.get("uri", ""),
                "type": "album",
            }

            # Extract release date
            release_date = None
            if "release_date" in album_data:
                release_date = album_data["release_date"]
            elif "releaseDate" in album_data:
                if isinstance(album_data["releaseDate"], dict):
                    # Handle structured date format
                    date_obj = album_data["releaseDate"]
                    if "isoString" in date_obj:
                        release_date = date_obj["isoString"][:10]  # Extract YYYY-MM-DD
                    elif "year" in date_obj:
                        year = date_obj.get("year", "")
                        month = (
                            str(date_obj.get("month", "")).zfill(2)
                            if date_obj.get("month")
                            else "01"
                        )
                        day = str(date_obj.get("day", "")).zfill(2) if date_obj.get("day") else "01"
                        if year:
                            release_date = f"{year}-{month}-{day}"
                else:
                    release_date = album_data["releaseDate"]
            elif "date" in album_data:
                if isinstance(album_data["date"], dict):
                    date_obj = album_data["date"]
                    year = date_obj.get("year", "")
                    month = (
                        str(date_obj.get("month", "")).zfill(2) if date_obj.get("month") else "01"
                    )
                    day = str(date_obj.get("day", "")).zfill(2) if date_obj.get("day") else "01"
                    if year:
                        release_date = f"{year}-{month}-{day}"
                else:
                    release_date = album_data["date"]

            if release_date:
                result["release_date"] = release_date

            # Extract total tracks
            if "total_tracks" in album_data:
                result["total_tracks"] = album_data["total_tracks"]
            elif "totalTracks" in album_data:
                result["total_tracks"] = album_data["totalTracks"]

            # Extract artists
            if "artists" in album_data:
                result["artists"] = []
                for artist in album_data["artists"]:
                    artist_data = {
                        "id": artist.get("id", ""),
                        "name": artist.get("name", ""),
                        "uri": artist.get("uri", ""),
                        "type": "artist",
                    }

                    # If we don't have an ID but do have a URI, extract ID from URI
                    if not artist_data["id"] and "uri" in artist:
                        artist_data["id"] = artist["uri"].split(":")[-1]

                    result["artists"].append(artist_data)
            elif "subtitle" in album_data:
                # For embed URLs, subtitle contains artist name
                result["artists"] = [
                    {"id": "", "name": album_data["subtitle"], "uri": "", "type": "artist"}
                ]

            # Extract images
            if "images" in album_data:
                result["images"] = []
                for image in album_data["images"]:
                    image_data = {
                        "url": image.get("url", ""),
                        "height": image.get("height", 0),
                        "width": image.get("width", 0),
                    }
                    result["images"].append(image_data)

            # Extract visual identity data if available (modern format)
            if "visualIdentity" in album_data and "image" in album_data["visualIdentity"]:
                if "images" not in result:
                    result["images"] = []

                for image in album_data["visualIdentity"]["image"]:
                    image_data = {
                        "url": image.get("url", ""),
                        "height": image.get("maxHeight", 0),
                        "width": image.get("maxWidth", 0),
                    }
                    result["images"].append(image_data)

            # Extract tracks if available
            if "tracks" in album_data and "items" in album_data["tracks"]:
                result["tracks"] = []
                for track in album_data["tracks"]["items"]:
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

                    # Extract track number
                    if "track_number" in track:
                        track_data["track_number"] = track["track_number"]

                    # Extract disc number
                    if "disc_number" in track:
                        track_data["disc_number"] = track["disc_number"]

                    # Extract preview URL if available
                    if "preview_url" in track:
                        track_data["preview_url"] = track["preview_url"]

                    # Extract explicit flag if available
                    if "explicit" in track:
                        track_data["is_explicit"] = track["explicit"]
                    elif "isExplicit" in track:
                        track_data["is_explicit"] = track["isExplicit"]

                    result["tracks"].append(track_data)
            elif "trackList" in album_data:
                # For embed URLs, trackList is a simple list
                result["tracks"] = []
                if isinstance(album_data["trackList"], list):
                    for idx, track_item in enumerate(album_data["trackList"]):
                        # Embed trackList items have limited info
                        track_data: TrackData = {
                            "id": track_item.get("id", ""),
                            "name": track_item.get("title", track_item.get("name", "")),
                            "uri": track_item.get("uri", ""),
                            "type": "track",
                            "track_number": idx + 1,
                        }

                        if "duration" in track_item:
                            track_data["duration_ms"] = track_item["duration"]

                        if "artists" in track_item:
                            track_data["artists"] = track_item["artists"]

                        result["tracks"].append(track_data)

                result["total_tracks"] = len(result.get("tracks", []))

            # Extract album type
            if "album_type" in album_data:
                result["album_type"] = album_data["album_type"]
            elif "albumType" in album_data:
                result["album_type"] = album_data["albumType"]

            # Extract copyright information
            if "copyrights" in album_data:
                result["copyrights"] = album_data["copyrights"]

            # Extract label information
            if "label" in album_data:
                result["label"] = album_data["label"]

            # Extract popularity score
            if "popularity" in album_data:
                result["popularity"] = album_data["popularity"]

            # Ensure total_tracks is set
            if "total_tracks" not in result:
                if "tracks" in result:
                    result["total_tracks"] = len(result["tracks"])
                else:
                    # Default to 0 if we can't determine track count
                    result["total_tracks"] = 0

            return result

        except Exception as e:
            logger.error("Failed to extract album data: %s", e)
            # Raise error instead of returning error dict
            raise ParsingError(f"Failed to extract album data: {str(e)}") from e

    def extract_cover_url(self, url: str, size: str = "large") -> Optional[str]:
        """
        Extract cover URL from an album.

        Args:
            url: Spotify album URL
            size: Desired image size ('small', 'medium', or 'large')

        Returns:
            Cover URL, or None if not available
        """
        album_data = self.extract(url)

        # Check if album has images
        if "images" in album_data and album_data["images"]:
            images = album_data["images"]

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
        Extract tracks from an album.

        Args:
            url: Spotify album URL

        Returns:
            List of track data dictionaries
        """
        album_data = self.extract(url)

        if "tracks" in album_data:
            return album_data["tracks"]

        return []
