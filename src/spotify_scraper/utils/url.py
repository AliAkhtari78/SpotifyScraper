"""
URL manipulation utilities for SpotifyScraper.

This module provides functions for manipulating and validating Spotify URLs,
including conversion between regular and embed URLs, ID extraction, and type detection.
"""

import re
from typing import Dict, Optional, Tuple, Literal, Union
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from spotify_scraper.core.constants import (
    SPOTIFY_BASE_URL,
    SPOTIFY_EMBED_URL,
    TRACK_URL_PATTERN,
    ALBUM_URL_PATTERN,
    ARTIST_URL_PATTERN,
    PLAYLIST_URL_PATTERN,
)
from spotify_scraper.core.exceptions import URLError

# URL type definitions
URLType = Literal["track", "album", "artist", "playlist", "search", "unknown"]


def is_spotify_url(url: str) -> bool:
    """
    Check if a URL is a valid Spotify URL.
    
    Args:
        url: URL to check
        
    Returns:
        True if the URL is a valid Spotify URL, False otherwise
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc in ["open.spotify.com", "play.spotify.com", "embed.spotify.com"]


def get_url_type(url: str) -> URLType:
    """
    Get the type of Spotify URL.
    
    Args:
        url: Spotify URL
        
    Returns:
        URL type ("track", "album", "artist", "playlist", "search", or "unknown")
    """
    if not is_spotify_url(url):
        raise URLError(f"Not a valid Spotify URL: {url}")
    
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    
    if len(path_parts) < 1:
        return "unknown"
    
    resource_type = path_parts[0]
    if resource_type == "embed" and len(path_parts) >= 2:
        resource_type = path_parts[1]
    
    if resource_type == "track":
        return "track"
    elif resource_type == "album":
        return "album"
    elif resource_type == "artist":
        return "artist"
    elif resource_type == "playlist":
        return "playlist"
    elif resource_type == "search":
        return "search"
    else:
        return "unknown"


def extract_id(url: str) -> str:
    """
    Extract the Spotify ID from a URL.
    
    Args:
        url: Spotify URL
        
    Returns:
        Spotify ID
        
    Raises:
        URLError: If the URL is invalid or the ID cannot be extracted
    """
    if not is_spotify_url(url):
        raise URLError(f"Not a valid Spotify URL: {url}")
    
    # Parse the URL
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    
    # Handle embed URLs
    if path_parts[0] == "embed" and len(path_parts) >= 3:
        return path_parts[2]
    
    # Handle regular URLs
    if len(path_parts) >= 2:
        # Extract ID and remove any query parameters
        id_part = path_parts[1].split("?")[0]
        return id_part
    
    raise URLError(f"Could not extract ID from URL: {url}")


def clean_url(url: str) -> str:
    """
    Clean a Spotify URL by removing query parameters.
    
    Args:
        url: Spotify URL
        
    Returns:
        Cleaned URL
    """
    if not is_spotify_url(url):
        raise URLError(f"Not a valid Spotify URL: {url}")
    
    parsed_url = urlparse(url)
    clean_parsed = parsed_url._replace(query="", fragment="")
    return urlunparse(clean_parsed)


def convert_to_embed_url(url: str) -> str:
    """
    Convert a regular Spotify URL to an embed URL.
    
    Args:
        url: Regular Spotify URL
        
    Returns:
        Equivalent embed URL
        
    Raises:
        URLError: If the URL is invalid or cannot be converted
    """
    if not is_spotify_url(url):
        raise URLError(f"Not a valid Spotify URL: {url}")
    
    # If it's already an embed URL, return it
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    
    if path_parts[0] == "embed":
        return url
    
    # Get the URL type and ID
    url_type = get_url_type(url)
    if url_type == "unknown":
        raise URLError(f"Cannot convert URL of unknown type to embed URL: {url}")
    
    try:
        id_value = extract_id(url)
    except URLError:
        raise URLError(f"Could not extract ID for embed URL conversion: {url}")
    
    # Construct embed URL
    embed_path = f"/embed/{url_type}/{id_value}"
    embed_parsed = parsed_url._replace(path=embed_path)
    return urlunparse(embed_parsed)


def convert_to_regular_url(url: str) -> str:
    """
    Convert an embed Spotify URL to a regular URL.
    
    Args:
        url: Embed Spotify URL
        
    Returns:
        Equivalent regular URL
        
    Raises:
        URLError: If the URL is invalid or cannot be converted
    """
    if not is_spotify_url(url):
        raise URLError(f"Not a valid Spotify URL: {url}")
    
    # If it's already a regular URL, return it
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    
    if path_parts[0] != "embed":
        return url
    
    # Remove the "embed" part from the path
    if len(path_parts) >= 3:
        resource_type = path_parts[1]
        resource_id = path_parts[2]
        
        regular_path = f"/{resource_type}/{resource_id}"
        regular_parsed = parsed_url._replace(path=regular_path)
        return urlunparse(regular_parsed)
    
    raise URLError(f"Invalid embed URL format: {url}")


def convert_spotify_uri_to_url(uri: str) -> str:
    """
    Convert a Spotify URI to a regular URL.
    
    Args:
        uri: Spotify URI (e.g., "spotify:track:6rqhFgbbKwnb9MLmUQDhG6")
        
    Returns:
        Equivalent regular URL
        
    Raises:
        URLError: If the URI is invalid or cannot be converted
    """
    # Check if it's a valid Spotify URI
    uri_pattern = r"^spotify:([a-z]+):([a-zA-Z0-9]+)$"
    match = re.match(uri_pattern, uri)
    
    if not match:
        raise URLError(f"Invalid Spotify URI format: {uri}")
    
    resource_type = match.group(1)
    resource_id = match.group(2)
    
    # Validate resource type
    valid_types = ["track", "album", "artist", "playlist", "show", "episode"]
    if resource_type not in valid_types:
        raise URLError(f"Unsupported Spotify URI resource type: {resource_type}")
    
    # Construct URL
    return f"{SPOTIFY_BASE_URL}/{resource_type}/{resource_id}"


def convert_url_to_spotify_uri(url: str) -> str:
    """
    Convert a Spotify URL to a URI.
    
    Args:
        url: Spotify URL
        
    Returns:
        Equivalent Spotify URI
        
    Raises:
        URLError: If the URL is invalid or cannot be converted
    """
    if not is_spotify_url(url):
        raise URLError(f"Not a valid Spotify URL: {url}")
    
    url_type = get_url_type(url)
    if url_type == "unknown":
        raise URLError(f"Cannot convert URL of unknown type to URI: {url}")
    
    try:
        id_value = extract_id(url)
    except URLError:
        raise URLError(f"Could not extract ID for URI conversion: {url}")
    
    return f"spotify:{url_type}:{id_value}"


def validate_url(url: str, expected_type: Optional[URLType] = None) -> bool:
    """
    Validate a Spotify URL.
    
    Args:
        url: URL to validate
        expected_type: Expected URL type (optional)
        
    Returns:
        True if valid
        
    Raises:
        URLError: If the URL is invalid
    """
    if not is_spotify_url(url):
        raise URLError(f"Not a valid Spotify URL: {url}")
    
    if expected_type is not None:
        url_type = get_url_type(url)
        if url_type != expected_type:
            raise URLError(f"URL is not a Spotify {expected_type} URL: {url}")
    
    return True


def build_url(
    resource_type: URLType,
    resource_id: str,
    embed: bool = False,
    query_params: Optional[Dict[str, str]] = None,
) -> str:
    """
    Build a Spotify URL for a given resource.
    
    Args:
        resource_type: Resource type ("track", "album", "artist", "playlist")
        resource_id: Resource ID
        embed: Whether to create an embed URL (default: False)
        query_params: Query parameters to include (optional)
        
    Returns:
        Constructed URL
        
    Raises:
        URLError: If the parameters are invalid
    """
    if resource_type == "unknown":
        raise URLError("Cannot build URL for resource type 'unknown'")
    
    if not resource_id:
        raise URLError("Resource ID cannot be empty")
    
    # Construct base URL
    base_url = SPOTIFY_EMBED_URL if embed else SPOTIFY_BASE_URL
    
    # Construct path
    if embed:
        path = f"/embed/{resource_type}/{resource_id}"
    else:
        path = f"/{resource_type}/{resource_id}"
    
    # Construct query string
    query = urlencode(query_params) if query_params else ""
    
    # Construct URL
    parsed = urlparse(base_url)
    parsed = parsed._replace(path=path, query=query)
    
    return urlunparse(parsed)


def extract_url_components(url: str) -> Tuple[URLType, str, Dict[str, str]]:
    """
    Extract components from a Spotify URL.
    
    Args:
        url: Spotify URL
        
    Returns:
        Tuple of (resource_type, resource_id, query_params)
        
    Raises:
        URLError: If the URL is invalid or components cannot be extracted
    """
    if not is_spotify_url(url):
        raise URLError(f"Not a valid Spotify URL: {url}")
    
    # Get resource type
    resource_type = get_url_type(url)
    if resource_type == "unknown":
        raise URLError(f"Unknown resource type in URL: {url}")
    
    # Get resource ID
    try:
        resource_id = extract_id(url)
    except URLError:
        raise URLError(f"Could not extract resource ID from URL: {url}")
    
    # Get query parameters
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Convert query params from lists to single values
    query_dict = {k: v[0] if v and len(v) == 1 else v for k, v in query_params.items()}
    
    return resource_type, resource_id, query_dict
