"""
JSON parser module for SpotifyScraper.

This module provides specialized functionality for parsing JSON data
from Spotify web pages, with support for different page structures
and data formats.
"""

import json
import logging
from typing import Any, Callable, Dict, Optional, TypeVar

from bs4 import BeautifulSoup

from spotify_scraper.core.constants import (
    AUTH_TOKEN_JSON_PATH,
    NEXT_DATA_SELECTOR,
    RESOURCE_SELECTOR,
    TRACK_JSON_PATH,
)
from spotify_scraper.core.exceptions import ParsingError
from spotify_scraper.core.types import (
    AlbumData,
    ArtistData,
    LyricsData,
    LyricsLineData,
    PlaylistData,
    TrackData,
)

logger = logging.getLogger(__name__)

# Type variable for generic functions
T = TypeVar("T")


def extract_json_from_html(html_content: str, selector: str) -> Dict[str, Any]:
    """
    Extract JSON data from an HTML document using a CSS selector.

    Args:
        html_content: HTML content
        selector: CSS selector for the script tag containing JSON

    Returns:
        Parsed JSON data as a dictionary

    Raises:
        ParsingError: If JSON extraction or parsing fails
    """
    try:
        # Parse HTML content
        soup = BeautifulSoup(html_content, "html.parser")

        # Find script tag with the given selector
        script_tag = soup.select_one(selector)
        if not script_tag or not script_tag.string:
            raise ParsingError(f"No JSON data found with selector: {selector}")

        # Extract and parse JSON data
        json_data = json.loads(script_tag.string)

        return json_data
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON data: %s", e)
        raise ParsingError(f"Failed to parse JSON data: {e}", data_type="JSON") from e
    except Exception as e:
        logger.error("Failed to extract JSON data: %s", e)
        raise ParsingError(f"Failed to extract JSON data: {e}") from e


def get_nested_value(
    data: Dict[str, Any],
    path: str,
    default: Optional[Any] = None,
) -> Any:
    """
    Get a nested value from a dictionary using a dot-separated path.

    Args:
        data: Dictionary to search
        path: Dot-separated path to the value (e.g., "props.pageProps.state.data")
        default: Default value to return if the path is not found

    Returns:
        Value at the specified path, or default if not found
    """
    current = data
    for key in path.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def extract_track_data(json_data: Dict[str, Any], path: str = TRACK_JSON_PATH) -> TrackData:
    """
    Extract track data from Spotify JSON data.

    Args:
        json_data: Parsed JSON data
        path: JSON path to track data (default: from constants)

    Returns:
        Structured track data

    Raises:
        ParsingError: If track data extraction fails
    """
    try:
        # Get track data from specified path
        track_data = get_nested_value(json_data, path)
        if not track_data:
            raise ParsingError(f"No track data found at path: {path}")

        # Create a standardized track data object
        # This handles variations in the Spotify data structure
        result: TrackData = {
            "id": track_data.get("id", ""),
            "name": track_data.get("name", ""),
            "title": track_data.get("title", track_data.get("name", "")),
            "uri": track_data.get("uri", ""),
            "type": "track",
        }

        # Extract duration - handle both string and numeric representations
        if "duration" in track_data:
            if (
                isinstance(track_data["duration"], dict)
                and "totalMilliseconds" in track_data["duration"]
            ):
                result["duration_ms"] = track_data["duration"]["totalMilliseconds"]
            else:
                result["duration"] = track_data["duration"]

        if "duration_ms" in track_data:
            result["duration_ms"] = track_data["duration_ms"]
        elif "duration" in track_data and isinstance(track_data["duration"], int):
            result["duration_ms"] = track_data["duration"]

        # Extract artists - handle both direct array and nested items structure
        artists_list = []
        if "artists" in track_data:
            if isinstance(track_data["artists"], dict) and "items" in track_data["artists"]:
                # Handle nested structure from test fixtures
                for artist in track_data["artists"]["items"]:
                    artist_name = ""
                    artist_uri = artist.get("uri", "")

                    # Extract name from profile if present
                    if "profile" in artist and "name" in artist["profile"]:
                        artist_name = artist["profile"]["name"]
                    else:
                        artist_name = artist.get("name", "")

                    artist_data: ArtistData = {
                        "name": artist_name,
                        "uri": artist_uri,
                    }

                    if artist_uri:
                        artist_data["id"] = artist_uri.split(":")[-1]

                    artists_list.append(artist_data)
            elif isinstance(track_data["artists"], list):
                # Handle direct array structure
                for artist in track_data["artists"]:
                    artist_data: ArtistData = {
                        "name": artist.get("name", ""),
                        "uri": artist.get("uri", ""),
                    }

                    if "uri" in artist and artist["uri"]:
                        uri_parts = artist["uri"].split(":")
                        if len(uri_parts) > 0:
                            artist_data["id"] = uri_parts[-1]

                    artists_list.append(artist_data)

        # Also check for single artist field
        elif "artist" in track_data:
            artist = track_data["artist"]
            artist_name = ""
            if "profile" in artist and "name" in artist["profile"]:
                artist_name = artist["profile"]["name"]
            else:
                artist_name = artist.get("name", "")

            artists_list.append(
                {
                    "name": artist_name,
                    "uri": artist.get("uri", ""),
                }
            )

        if artists_list:
            result["artists"] = artists_list

        # Extract audio preview - handle both audioPreview object and direct preview_url
        if "audioPreview" in track_data:
            if isinstance(track_data["audioPreview"], dict) and "url" in track_data["audioPreview"]:
                result["preview_url"] = track_data["audioPreview"]["url"]
            elif isinstance(track_data["audioPreview"], str):
                result["preview_url"] = track_data["audioPreview"]
        elif "preview_url" in track_data:
            result["preview_url"] = track_data["preview_url"]

        # Extract explicit flag
        if "isExplicit" in track_data:
            result["is_explicit"] = track_data["isExplicit"]
        elif "contentRating" in track_data and isinstance(track_data["contentRating"], dict):
            result["is_explicit"] = track_data["contentRating"].get("label", "NONE") != "NONE"
        elif "explicit" in track_data:
            result["is_explicit"] = track_data["explicit"]
        else:
            result["is_explicit"] = False  # Default to not explicit

        # Extract playable flag
        if "isPlayable" in track_data:
            result["is_playable"] = track_data["isPlayable"]
        elif "playable" in track_data:
            result["is_playable"] = track_data["playable"]
        else:
            result["is_playable"] = True  # Default to playable

        # Extract album - handle both "album" and "albumOfTrack" fields
        album_data = track_data.get("album") or track_data.get("albumOfTrack")
        if album_data:
            album: AlbumData = {
                "name": album_data.get("name", ""),
                "type": "album",
            }

            if "uri" in album_data and album_data["uri"]:
                album["uri"] = album_data["uri"]
                uri_parts = album_data["uri"].split(":")
                if len(uri_parts) > 0:
                    album["id"] = uri_parts[-1]

            # Extract images from various possible locations
            if "images" in album_data:
                album["images"] = album_data["images"]
            elif "coverArt" in album_data and "sources" in album_data["coverArt"]:
                # Convert coverArt sources to images format
                album["images"] = []
                for source in album_data["coverArt"]["sources"]:
                    album["images"].append(
                        {
                            "url": source.get("url", ""),
                            "width": source.get("width", 0),
                            "height": source.get("height", 0),
                        }
                    )

            # Extract release date if available
            if "releaseDate" in album_data:
                if isinstance(album_data["releaseDate"], dict):
                    # Handle structured date format
                    date_obj = album_data["releaseDate"]
                    year = date_obj.get("year", "")
                    month = str(date_obj.get("month", "")).zfill(2)
                    day = str(date_obj.get("day", "")).zfill(2)
                    if year and month and day:
                        album["release_date"] = f"{year}-{month}-{day}"
                else:
                    album["release_date"] = album_data["releaseDate"]
            elif "release_date" in album_data:
                album["release_date"] = album_data["release_date"]
            elif "date" in album_data:
                # Handle the "date" field format used in some responses
                if isinstance(album_data["date"], dict):
                    date_obj = album_data["date"]
                    year = date_obj.get("year", "")
                    month = str(date_obj.get("month", "")).zfill(2) if date_obj.get("month") else ""
                    day = str(date_obj.get("day", "")).zfill(2) if date_obj.get("day") else ""
                    if year and month and day:
                        album["release_date"] = f"{year}-{month}-{day}"
                    elif year and month:
                        album["release_date"] = f"{year}-{month}"
                    elif year:
                        album["release_date"] = str(year)
                else:
                    album["release_date"] = album_data["date"]

            result["album"] = album
        else:
            # For embed URLs, construct album from visualIdentity if available
            if "visualIdentity" in track_data and "image" in track_data["visualIdentity"]:
                album: AlbumData = {
                    "name": "",  # Album name not available in embed
                    "type": "album",
                    "images": [],
                }

                # Convert visualIdentity images to album images
                for img in track_data["visualIdentity"]["image"]:
                    album["images"].append(
                        {
                            "url": img.get("url", ""),
                            "width": img.get("maxWidth", 0),
                            "height": img.get("maxHeight", 0),
                        }
                    )

                result["album"] = album

        # Extract visual identity data if available (only for album images)
        if "visualIdentity" in track_data:
            visual_identity = track_data["visualIdentity"]

            # Extract cover images - format may vary
            if "image" in visual_identity:
                images = []
                for img in visual_identity["image"]:
                    images.append(
                        {
                            "url": img.get("url", ""),
                            "width": img.get("maxWidth", 0),
                            "height": img.get("maxHeight", 0),
                        }
                    )

                # If we have album data, add images to it
                if "album" in result and "images" not in result["album"]:
                    result["album"]["images"] = images

        # Extract release date if available
        release_date = None
        if "release_date" in track_data:
            release_date = track_data["release_date"]
        elif "releaseDate" in track_data:
            if isinstance(track_data["releaseDate"], dict):
                # Handle structured date format
                date_obj = track_data["releaseDate"]
                if "isoString" in date_obj:
                    release_date = date_obj["isoString"][:10]  # Extract YYYY-MM-DD
                elif "year" in date_obj:
                    year = date_obj.get("year", "")
                    month = str(date_obj.get("month", "")).zfill(2)
                    day = str(date_obj.get("day", "")).zfill(2)
                    if year and month and day:
                        release_date = f"{year}-{month}-{day}"
            else:
                release_date = track_data["releaseDate"]

        if release_date:
            result["release_date"] = release_date

        # Extract lyrics if available
        if "lyrics" in track_data:
            lyrics_data = track_data["lyrics"]
            # Handle different sync type field names
            sync_type = lyrics_data.get("syncType") or lyrics_data.get("sync_type", "UNSYNCED")
            lyrics: LyricsData = {"sync_type": sync_type, "lines": []}

            # Add provider and language if available
            if "provider" in lyrics_data:
                lyrics["provider"] = lyrics_data["provider"]
            elif sync_type:  # If syncType is available but no provider, assume Spotify
                lyrics["provider"] = "SPOTIFY"

            if "language" in lyrics_data:
                lyrics["language"] = lyrics_data["language"]

            # Extract lyrics lines - handle both field naming conventions
            if "lines" in lyrics_data:
                for line in lyrics_data["lines"]:
                    # Handle both camelCase and snake_case field names
                    start_time = line.get("startTimeMs") or line.get("start_time_ms", 0)
                    end_time = line.get("endTimeMs") or line.get("end_time_ms", 0)

                    line_data: LyricsLineData = {
                        "start_time_ms": start_time,
                        "words": line.get("words", ""),
                        "end_time_ms": end_time,
                    }
                    lyrics["lines"].append(line_data)

            result["lyrics"] = lyrics

        return result
    except Exception as e:
        logger.error("Failed to extract track data: %s", e)
        # Return a minimal track data object with error information
        return {"ERROR": str(e), "id": "", "name": "", "uri": "", "type": "track"}


def extract_json_from_next_data(html_content: str) -> Dict[str, Any]:
    """
    Extract JSON data from Spotify's __NEXT_DATA__ script tag.

    This is the modern way that Spotify embeds data in its web pages.

    Args:
        html_content: HTML content of the Spotify page

    Returns:
        Parsed JSON data

    Raises:
        ParsingError: If extraction fails
    """
    return extract_json_from_html(html_content, NEXT_DATA_SELECTOR)


def extract_json_from_resource(html_content: str) -> Dict[str, Any]:
    """
    Extract JSON data from Spotify's resource script tag.

    This is the legacy way that Spotify used to embed data in its web pages.

    Args:
        html_content: HTML content of the Spotify page

    Returns:
        Parsed JSON data

    Raises:
        ParsingError: If extraction fails
    """
    return extract_json_from_html(html_content, RESOURCE_SELECTOR)


def extract_track_data_from_page(html_content: str) -> TrackData:
    """
    Extract track data from a Spotify page.

    This function tries multiple methods to extract track data,
    falling back to alternative methods if the preferred method fails.

    Args:
        html_content: HTML content of the Spotify page

    Returns:
        Structured track data

    Raises:
        ParsingError: If all extraction methods fail
    """
    # Try using __NEXT_DATA__ first (modern approach)
    try:
        json_data = extract_json_from_next_data(html_content)
        track_data = extract_track_data(json_data, TRACK_JSON_PATH)

        # Check if album data is missing and try to fetch it from JSON-LD
        if "album" not in track_data and not track_data.get("ERROR"):
            try:
                # Try to extract album data from JSON-LD
                album_data = extract_album_data_from_jsonld(html_content)
                if album_data:
                    track_data["album"] = album_data
            except Exception as e:
                logger.warning("Failed to extract album data from JSON-LD: %s", e)

        return track_data
    except ParsingError as e:
        logger.warning("Failed to extract track data using __NEXT_DATA__: %s", e)

    # Fallback to resource script tag (legacy approach)
    try:
        json_data = extract_json_from_resource(html_content)
        # For resource script tag, the data is directly in the root
        track_data = extract_track_data(json_data, "")

        # Check if album data is missing and try to fetch it from JSON-LD
        if "album" not in track_data and not track_data.get("ERROR"):
            try:
                # Try to extract album data from JSON-LD
                album_data = extract_album_data_from_jsonld(html_content)
                if album_data:
                    track_data["album"] = album_data
            except Exception as e:
                logger.warning("Failed to extract album data from JSON-LD: %s", e)

        return track_data
    except ParsingError as e:
        logger.warning("Failed to extract track data using resource script: %s", e)

    # If all methods fail, raise a more specific error
    raise ParsingError("Failed to extract track data from page using any method")


def extract_album_data_from_page(html_content: str) -> AlbumData:
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
    # Implementation would follow a similar pattern to extract_track_data_from_page
    # For brevity, this is left as a placeholder
    raise NotImplementedError("Album data extraction not yet implemented")


def extract_artist_data_from_page(html_content: str) -> ArtistData:
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
    # Implementation would follow a similar pattern to extract_track_data_from_page
    # For brevity, this is left as a placeholder
    raise NotImplementedError("Artist data extraction not yet implemented")


def extract_playlist_data_from_page(html_content: str) -> PlaylistData:
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
    # Implementation would follow a similar pattern to extract_track_data_from_page
    # For brevity, this is left as a placeholder
    raise NotImplementedError("Playlist data extraction not yet implemented")


def extract_album_data_from_jsonld(html_content: str) -> Optional[AlbumData]:
    """
    Extract album data from JSON-LD script tags in a Spotify page.

    JSON-LD (JSON for Linked Data) is a method of encoding linked data using JSON.
    Spotify embeds album metadata in JSON-LD script tags for SEO purposes.

    Args:
        html_content: HTML content of the Spotify page

    Returns:
        AlbumData or None if no album data could be extracted
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # Look for application/ld+json script tags
        jsonld_scripts = soup.find_all("script", {"type": "application/ld+json"})

        for script in jsonld_scripts:
            script_content = getattr(script, "string", None)
            if not script_content:
                continue

            try:
                data = json.loads(script_content)

                # Check if this is album data
                if isinstance(data, dict) and data.get("@type") == "MusicRecording":
                    album_data: AlbumData = {}

                    # Extract album data
                    if "inAlbum" in data:
                        in_album = data["inAlbum"]

                        if "name" in in_album:
                            album_data["name"] = in_album["name"]

                        if "@type" in in_album:
                            album_data["type"] = "album"

                        if "@id" in in_album:
                            album_id = in_album["@id"]
                            if isinstance(album_id, str) and "album:" in album_id:
                                album_data["id"] = album_id.split("album:")[-1]
                                album_data["uri"] = f"spotify:album:{album_data['id']}"

                        # Extract image data if available
                        if "image" in data:
                            album_data["images"] = []

                            # Handle both string and array image formats
                            images = (
                                data["image"]
                                if isinstance(data["image"], list)
                                else [data["image"]]
                            )

                            for img in images:
                                if isinstance(img, str):
                                    album_data["images"].append(
                                        {"url": img, "width": 0, "height": 0}
                                    )

                    # Return if we found meaningful album data
                    if "name" in album_data:
                        return album_data

            except json.JSONDecodeError:
                continue

        return None
    except Exception as e:
        logger.warning("Failed to extract album data from JSON-LD: %s", e)
        return None


def extract_auth_token_from_page(html_content: str) -> Optional[str]:
    """
    Extract authentication token from a Spotify page.

    Args:
        html_content: HTML content of the Spotify page

    Returns:
        Authentication token, or None if not found
    """
    try:
        json_data = extract_json_from_next_data(html_content)
        return get_nested_value(json_data, AUTH_TOKEN_JSON_PATH)
    except Exception as e:
        logger.warning("Failed to extract auth token: %s", e)
        return None


def with_fallback(
    primary_func: Callable[..., T], fallback_func: Callable[..., T], *args: Any, **kwargs: Any
) -> T:
    """
    Try a primary function, falling back to a secondary function if it fails.

    Args:
        primary_func: Primary function to try
        fallback_func: Fallback function to use if primary fails
        *args: Arguments to pass to both functions
        **kwargs: Keyword arguments to pass to both functions

    Returns:
        Result of either primary_func or fallback_func

    Raises:
        Exception: If both functions fail
    """
    try:
        return primary_func(*args, **kwargs)
    except Exception as primary_error:
        logger.warning("Primary function failed: %s", primary_error)
        try:
            return fallback_func(*args, **kwargs)
        except Exception as fallback_error:
            logger.error("Fallback function also failed: %s", fallback_error)
            raise Exception(
                f"Both primary and fallback functions failed: {primary_error} / {fallback_error}"
            ) from fallback_error
