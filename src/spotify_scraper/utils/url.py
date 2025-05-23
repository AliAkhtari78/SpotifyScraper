"""URL manipulation utilities for SpotifyScraper.

This module provides comprehensive utilities for working with Spotify URLs,
including validation, parsing, conversion between formats, and ID extraction.
It supports all Spotify URL formats including regular web URLs, embed URLs,
and Spotify URIs.

The module handles URLs for all Spotify entity types:
    - Tracks: /track/{id}
    - Albums: /album/{id}
    - Artists: /artist/{id}
    - Playlists: /playlist/{id}

Example:
    >>> from spotify_scraper.utils.url import is_spotify_url, extract_id, convert_to_embed_url
    >>> 
    >>> url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
    >>> if is_spotify_url(url):
    ...     track_id = extract_id(url)
    ...     embed_url = convert_to_embed_url(url)
    ...     print(f"Track ID: {track_id}")
    ...     print(f"Embed URL: {embed_url}")
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
    """Check if a URL is a valid Spotify URL.
    
    Validates whether the provided URL belongs to Spotify's domains.
    Supports all known Spotify domains including regular, embed, and legacy.
    
    Args:
        url: URL string to validate. Can be any string.
    
    Returns:
        bool: True if the URL is from a Spotify domain, False otherwise.
    
    Example:
        >>> is_spotify_url("https://open.spotify.com/track/123")
        True
        >>> is_spotify_url("https://open.spotify.com/embed/track/123")
        True
        >>> is_spotify_url("https://example.com/track/123")
        False
        >>> is_spotify_url("not a url")
        False
    
    Note:
        This function only checks the domain, not whether the URL
        structure is valid or the resource exists.
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc in ["open.spotify.com", "play.spotify.com", "embed.spotify.com"]


def get_url_type(url: str) -> URLType:
    """Determine the type of Spotify entity from a URL.
    
    Analyzes the URL path to determine what type of Spotify entity
    it references. Handles both regular and embed URL formats.
    
    Args:
        url: Spotify URL to analyze. Must be a valid Spotify URL.
    
    Returns:
        URLType: The entity type as a string literal:
            - "track": Track URL
            - "album": Album URL  
            - "artist": Artist URL
            - "playlist": Playlist URL
            - "search": Search results URL
            - "unknown": Valid Spotify URL but unknown type
    
    Raises:
        URLError: If the URL is not from a Spotify domain.
    
    Example:
        >>> get_url_type("https://open.spotify.com/track/123")
        'track'
        >>> get_url_type("https://open.spotify.com/embed/album/456")
        'album'
        >>> get_url_type("https://open.spotify.com/search/queen")
        'search'
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
    """Extract the Spotify entity ID from a URL.
    
    Parses the URL and extracts the 22-character alphanumeric ID that
    uniquely identifies the Spotify entity (track, album, artist, or playlist).
    
    Args:
        url: Spotify URL containing an entity ID. Supports:
            - Regular: https://open.spotify.com/track/{id}
            - Embed: https://open.spotify.com/embed/track/{id}
            - With params: https://open.spotify.com/track/{id}?si=...
    
    Returns:
        str: The 22-character Spotify ID.
            Example: "6rqhFgbbKwnb9MLmUQDhG6"
    
    Raises:
        URLError: If the URL is not a valid Spotify URL or if no ID
            can be extracted (e.g., homepage, search page).
    
    Example:
        >>> extract_id("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
        '6rqhFgbbKwnb9MLmUQDhG6'
        >>> extract_id("https://open.spotify.com/embed/album/1DFixLWuPkv3KT3TnV35m3")
        '1DFixLWuPkv3KT3TnV35m3'
        >>> extract_id("https://open.spotify.com/track/123?si=abcd&utm_source=copy")
        '123'
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
    """Convert any Spotify URL to embed format.
    
    Converts regular Spotify URLs to their embed equivalents. Embed URLs
    are useful because they don't require authentication for basic metadata
    and have a more consistent structure for parsing.
    
    Args:
        url: Any Spotify entity URL. If already an embed URL, returns unchanged.
            Supports tracks, albums, artists, and playlists.
    
    Returns:
        str: Embed URL format: https://open.spotify.com/embed/{type}/{id}
    
    Raises:
        URLError: If the URL is not a valid Spotify URL, has an unknown type,
            or doesn't contain an extractable ID.
    
    Example:
        >>> convert_to_embed_url("https://open.spotify.com/track/123")
        'https://open.spotify.com/embed/track/123'
        >>> convert_to_embed_url("spotify:album:456")
        'https://open.spotify.com/embed/album/456'
        >>> # Already embed URL - returns unchanged
        >>> convert_to_embed_url("https://open.spotify.com/embed/track/123") 
        'https://open.spotify.com/embed/track/123'
    
    Note:
        Search URLs and other non-entity URLs cannot be converted to embed format.
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
    """Validate a Spotify URL and optionally check its type.
    
    Performs validation on a Spotify URL to ensure it's from a valid domain
    and optionally verifies it matches an expected entity type. This is useful
    for input validation in functions that expect specific URL types.
    
    Args:
        url: URL to validate. Must be a complete URL with protocol.
        expected_type: If provided, validates the URL is of this specific type.
            Options: "track", "album", "artist", "playlist", "search"
    
    Returns:
        bool: Always returns True if validation passes.
    
    Raises:
        URLError: If validation fails with a descriptive error message:
            - "Not a valid Spotify URL" if domain is wrong
            - "URL is not a Spotify {type} URL" if type doesn't match
    
    Example:
        >>> # Basic validation
        >>> validate_url("https://open.spotify.com/track/123")
        True
        
        >>> # Type-specific validation  
        >>> validate_url("https://open.spotify.com/track/123", expected_type="track")
        True
        
        >>> # Type mismatch
        >>> validate_url("https://open.spotify.com/album/123", expected_type="track")
        Traceback (most recent call last):
        URLError: URL is not a Spotify track URL: https://open.spotify.com/album/123
    
    Note:
        This function is designed to be used with exception handling for
        validation flow control.
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
    """Construct a Spotify URL from components.
    
    Builds a properly formatted Spotify URL given the entity type and ID.
    Useful for programmatically creating URLs when you have the components.
    
    Args:
        resource_type: Type of Spotify entity. Must be one of:
            "track", "album", "artist", "playlist"
        resource_id: The 22-character Spotify ID for the entity.
            Example: "6rqhFgbbKwnb9MLmUQDhG6"
        embed: If True, creates an embed URL (/embed/...).
            If False (default), creates a regular URL.
        query_params: Optional query parameters to append to the URL.
            Example: {"si": "abc123", "utm_source": "copy-link"}
    
    Returns:
        str: Complete Spotify URL with the specified components.
            Examples:
            - Regular: "https://open.spotify.com/track/123"
            - Embed: "https://open.spotify.com/embed/track/123"
            - With params: "https://open.spotify.com/track/123?si=abc"
    
    Raises:
        URLError: If resource_type is "unknown" or "search", or if
            resource_id is empty.
    
    Example:
        >>> build_url("track", "6rqhFgbbKwnb9MLmUQDhG6")
        'https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6'
        
        >>> build_url("album", "123", embed=True)
        'https://open.spotify.com/embed/album/123'
        
        >>> build_url("track", "456", query_params={"si": "abc"})
        'https://open.spotify.com/track/456?si=abc'
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
