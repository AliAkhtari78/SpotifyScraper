"""
JSON parser module for SpotifyScraper.

This module provides specialized functionality for parsing JSON data
from Spotify web pages, with support for different page structures
and data formats.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, cast

from bs4 import BeautifulSoup

from spotify_scraper.core.types import (
    TrackData,
    AlbumData,
    ArtistData,
    PlaylistData,
    VisualIdentityData,
)
from spotify_scraper.core.constants import (
    NEXT_DATA_SELECTOR,
    RESOURCE_SELECTOR,
    TRACK_JSON_PATH,
    ALBUM_JSON_PATH,
    ARTIST_JSON_PATH,
    PLAYLIST_JSON_PATH,
)
from spotify_scraper.core.exceptions import ParsingError

logger = logging.getLogger(__name__)

# Type variable for generic functions
T = TypeVar('T')


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
        logger.error(f"Failed to parse JSON data: {e}")
        raise ParsingError(f"Failed to parse JSON data: {e}", data_type="JSON")
    except Exception as e:
        logger.error(f"Failed to extract JSON data: {e}")
        raise ParsingError(f"Failed to extract JSON data: {e}")


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
    for key in path.split('.'):
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
            result["duration"] = track_data["duration"]
        
        if "duration_ms" in track_data:
            result["duration_ms"] = track_data["duration_ms"]
        elif "duration" in track_data and isinstance(track_data["duration"], int):
            result["duration_ms"] = track_data["duration"]
        
        # Extract artists
        if "artists" in track_data:
            result["artists"] = []
            for artist in track_data["artists"]:
                artist_data: ArtistData = {
                    "name": artist.get("name", ""),
                    "uri": artist.get("uri", ""),
                }
                
                if "uri" in artist:
                    artist_data["id"] = artist["uri"].split(":")[-1]
                
                result["artists"].append(artist_data)
        
        # Extract audio preview
        if "audioPreview" in track_data and "url" in track_data["audioPreview"]:
            result["preview_url"] = track_data["audioPreview"]["url"]
        elif "preview_url" in track_data:
            result["preview_url"] = track_data["preview_url"]
        
        # Extract playability and explicit flags
        if "isPlayable" in track_data:
            result["isPlayable"] = track_data["isPlayable"]
        
        if "isExplicit" in track_data:
            result["isExplicit"] = track_data["isExplicit"]
        
        # Extract album - this may be a nested structure or a reference
        if "album" in track_data:
            album_data = track_data["album"]
            album: AlbumData = {
                "name": album_data.get("name", ""),
            }
            
            if "uri" in album_data:
                album["uri"] = album_data["uri"]
                album["id"] = album_data["uri"].split(":")[-1]
            
            if "images" in album_data:
                album["images"] = album_data["images"]
            
            result["album"] = album
        
        # Extract visual identity data if available
        if "visualIdentity" in track_data:
            visual_identity = track_data["visualIdentity"]
            
            # Extract cover images - format may vary
            if "image" in visual_identity:
                images = []
                for img in visual_identity["image"]:
                    images.append({
                        "url": img.get("url", ""),
                        "width": img.get("maxWidth", 0),
                        "height": img.get("maxHeight", 0),
                    })
                
                # If we have album data, add images to it
                if "album" in result:
                    result["album"]["images"] = images
            
            # Include the full visual identity data
            result["visualIdentity"] = cast(VisualIdentityData, visual_identity)
        
        # Extract release date
        if "release_date" in track_data:
            result["release_date"] = track_data["release_date"]
        elif "releaseDate" in track_data:
            result["release_date"] = track_data["releaseDate"]
        
        # Extract hasVideo flag
        if "hasVideo" in track_data:
            result["hasVideo"] = track_data["hasVideo"]
        
        # Extract related entity URI
        if "relatedEntityUri" in track_data:
            result["relatedEntityUri"] = track_data["relatedEntityUri"]
        
        # Extract lyrics if available
        if "lyrics" in track_data:
            lyrics_data = track_data["lyrics"]
            lyrics: LyricsData = {
                "sync_type": lyrics_data.get("syncType", "UNSYNCED"),
                "lines": []
            }
            
            # Add provider and language if available
            if "provider" in lyrics_data:
                lyrics["provider"] = lyrics_data["provider"]
            elif "syncType" in lyrics_data:  # If syncType is available but no provider, assume Spotify
                lyrics["provider"] = "SPOTIFY"
            
            if "language" in lyrics_data:
                lyrics["language"] = lyrics_data["language"]
            
            # Extract lyrics lines
            if "lines" in lyrics_data:
                for line in lyrics_data["lines"]:
                    line_data: LyricsLineData = {
                        "start_time_ms": line.get("startTimeMs", 0),
                        "words": line.get("words", ""),
                        "end_time_ms": line.get("endTimeMs", 0)
                    }
                    lyrics["lines"].append(line_data)
            
            result["lyrics"] = lyrics
        
        return result
    except Exception as e:
        logger.error(f"Failed to extract track data: {e}")
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
        return extract_track_data(json_data, TRACK_JSON_PATH)
    except ParsingError as e:
        logger.warning(f"Failed to extract track data using __NEXT_DATA__: {e}")
    
    # Fallback to resource script tag (legacy approach)
    try:
        json_data = extract_json_from_resource(html_content)
        # For resource script tag, the data is directly in the root
        return extract_track_data(json_data, "")
    except ParsingError as e:
        logger.warning(f"Failed to extract track data using resource script: {e}")
    
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
        logger.warning(f"Failed to extract auth token: {e}")
        return None


def with_fallback(
    primary_func: Callable[..., T],
    fallback_func: Callable[..., T],
    *args: Any,
    **kwargs: Any
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
        logger.warning(f"Primary function failed: {primary_error}")
        try:
            return fallback_func(*args, **kwargs)
        except Exception as fallback_error:
            logger.error(f"Fallback function also failed: {fallback_error}")
            raise Exception(f"Both primary and fallback functions failed: {primary_error} / {fallback_error}")
