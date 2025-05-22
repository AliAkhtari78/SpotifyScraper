#!/usr/bin/env python
"""
Track extractor module for SpotifyScraper.

This module provides functionality for extracting track information
from Spotify track pages, with support for both regular and embed URLs.
"""

import json
import logging
import re
from typing import Dict, Optional, Any, Union, List, cast
from urllib.parse import urlparse

# Simplified browser interface
class Browser:
    def get(self, url: str) -> str:
        """Get page content from URL."""
        pass

# Type definitions
class ImageData(Dict[str, Any]):
    pass

class ArtistData(Dict[str, Any]):
    pass

class AlbumData(Dict[str, Any]):
    pass

class LyricsLineData(Dict[str, Any]):
    pass

class LyricsData(Dict[str, Any]):
    pass

class TrackData(Dict[str, Any]):
    pass

# Constants
NEXT_DATA_SELECTOR = "script#__NEXT_DATA__"
TRACK_JSON_PATH = "props.pageProps.state.data.entity"

# Simplified exceptions
class ScrapingError(Exception):
    """Error during scraping."""
    pass

class URLError(Exception):
    """Error with URL."""
    pass

class ParsingError(Exception):
    """Error parsing data."""
    pass

# Simplified URL utilities
def validate_url(url: str, expected_type: Optional[str] = None) -> bool:
    """Validate a Spotify URL."""
    if not url.startswith("https://open.spotify.com"):
        raise URLError(f"Not a valid Spotify URL: {url}")
    
    if expected_type and expected_type not in url:
        raise URLError(f"URL is not a Spotify {expected_type} URL: {url}")
    
    return True

def extract_id(url: str) -> str:
    """Extract ID from Spotify URL."""
    parts = url.split("/")
    if len(parts) < 5:
        raise URLError(f"Invalid URL format: {url}")
    
    id_part = parts[-1]
    if "?" in id_part:
        id_part = id_part.split("?")[0]
    
    return id_part

def convert_to_embed_url(url: str) -> str:
    """Convert regular Spotify URL to embed URL."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    
    if path.startswith("embed/"):
        return url
    
    parts = path.split("/")
    if len(parts) < 2:
        raise URLError(f"Invalid URL path: {parsed.path}")
    
    url_type, id_value = parts[0], parts[1]
    embed_path = f"/embed/{url_type}/{id_value}"
    
    return f"https://open.spotify.com{embed_path}"

def get_url_type(url: str) -> str:
    """Get the type of Spotify URL."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    
    if path.startswith("embed/"):
        path = path[6:]  # Remove 'embed/'
    
    parts = path.split("/")
    if not parts:
        return "unknown"
    
    return parts[0]

# Extract JSON from HTML
def extract_json_from_html(html_content: str, selector: str) -> Dict[str, Any]:
    """Extract JSON data from a script tag in HTML."""
    selector_parts = selector.split('#')
    if len(selector_parts) != 2:
        raise ParsingError(f"Invalid selector format: {selector}")
    
    tag_name, id_value = selector_parts[0] or 'script', selector_parts[1]
    
    # Use a more precise pattern
    pattern = rf'<{tag_name}\s+id="{id_value}"[^>]*>(.*?)</{tag_name}>'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if not match:
        # Try with single quotes
        pattern = rf"<{tag_name}\s+id='{id_value}'[^>]*>(.*?)</{tag_name}>"
        match = re.search(pattern, html_content, re.DOTALL)
    
    if not match:
        # Try a more relaxed pattern
        pattern = rf'<{tag_name}[^>]*id=["\']{id_value}["\'][^>]*>(.*?)</{tag_name}>'
        match = re.search(pattern, html_content, re.DOTALL)
    
    if not match:
        # Dump a snippet of the HTML to help with debugging
        snippet = html_content[:500] + "..." if len(html_content) > 500 else html_content
        raise ParsingError(f"No script tag found with selector: {selector}\nHTML snippet: {snippet}")
    
    script_content = match.group(1).strip()
    
    try:
        return json.loads(script_content)
    except json.JSONDecodeError as e:
        raise ParsingError(f"Failed to parse JSON from script tag: {e}")

def extract_json_from_next_data(html_content: str) -> Dict[str, Any]:
    """Extract JSON data from Spotify's __NEXT_DATA__ script tag."""
    return extract_json_from_html(html_content, NEXT_DATA_SELECTOR)

def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """Get a nested value from a dictionary using a dot-separated path."""
    if not path:
        return data
    
    parts = path.split(".")
    result = data
    
    for part in parts:
        if not isinstance(result, dict) or part not in result:
            return None
        result = result[part]
    
    return result

# Extract track data from JSON
def extract_track_data(json_data: Dict[str, Any], path: str = TRACK_JSON_PATH) -> TrackData:
    """Extract track data from Spotify JSON data."""
    try:
        # Get track data from specified path
        track_data = get_nested_value(json_data, path)
        if not track_data:
            raise ParsingError(f"No track data found at path: {path}")
        
        # Create a standardized track data object
        result: TrackData = {
            "id": track_data.get("id", ""),
            "name": track_data.get("name", ""),
            "title": track_data.get("title", track_data.get("name", "")),
            "uri": track_data.get("uri", ""),
            "type": "track",
        }
        
        # Extract duration
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
            result["is_playable"] = track_data["isPlayable"]
        
        if "isExplicit" in track_data:
            result["is_explicit"] = track_data["isExplicit"]
        
        # Extract album
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
        
        # Extract release date
        if "release_date" in track_data:
            result["release_date"] = track_data["release_date"]
        elif "releaseDate" in track_data:
            result["release_date"] = track_data["releaseDate"]
            
            # If album exists, add release date to it
            if "album" in result:
                result["album"]["release_date"] = track_data["releaseDate"]
        
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
        # Return a minimal track data object with error information
        return {"ERROR": str(e), "id": "", "name": "", "uri": "", "type": "track"}

def extract_track_data_from_html(html_content: str) -> TrackData:
    """Extract track data from HTML content."""
    try:
        # Find the __NEXT_DATA__ script tag
        pattern = r'<script id="__NEXT_DATA__" type="application/json">\s*(.*?)\s*</script>'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            return {"ERROR": "No __NEXT_DATA__ script found", "id": "", "name": "", "uri": "", "type": "track"}
        
        # Parse the JSON data
        json_data = json.loads(match.group(1))
        
        # Extract track data
        entity = json_data.get("props", {}).get("pageProps", {}).get("state", {}).get("data", {}).get("entity", {})
        
        # Create track data object
        result: TrackData = {
            "id": entity.get("id", ""),
            "name": entity.get("name", ""),
            "title": entity.get("name", ""),
            "uri": entity.get("uri", ""),
            "type": "track",
        }
        
        # Extract duration
        if "duration_ms" in entity:
            result["duration_ms"] = entity["duration_ms"]
        elif "duration" in entity:
            if isinstance(entity["duration"], dict) and "totalMilliseconds" in entity["duration"]:
                result["duration_ms"] = entity["duration"]["totalMilliseconds"]
            elif isinstance(entity["duration"], int):
                result["duration_ms"] = entity["duration"]
        
        # Extract artists
        artists = []
        if "artists" in entity:
            for artist in entity.get("artists", {}).get("items", []):
                artist_data = {
                    "name": artist.get("profile", {}).get("name", ""),
                    "uri": artist.get("uri", ""),
                    "id": artist.get("uri", "").split(":")[-1] if artist.get("uri") else "",
                }
                artists.append(artist_data)
        result["artists"] = artists
        
        # Extract album
        album_data = entity.get("albumOfTrack", {})
        album = {
            "name": album_data.get("name", ""),
            "uri": album_data.get("uri", ""),
            "id": album_data.get("uri", "").split(":")[-1] if album_data.get("uri") else "",
        }
        
        # Extract album images
        if "coverArt" in album_data:
            images = []
            for image in album_data.get("coverArt", {}).get("sources", []):
                img = {
                    "url": image.get("url", ""),
                    "width": image.get("width", 0),
                    "height": image.get("height", 0),
                }
                images.append(img)
            album["images"] = images
        
        # Add release date
        if "date" in album_data:
            date_obj = album_data["date"]
            if "year" in date_obj and "month" in date_obj and "day" in date_obj:
                release_date = f"{date_obj['year']}-{date_obj['month']:02d}-{date_obj['day']:02d}"
                album["release_date"] = release_date
        
        result["album"] = album
        
        # Extract playability
        result["is_playable"] = entity.get("playability", {}).get("playable", True)
        
        # Extract preview URL
        if "audioPreview" in entity and "url" in entity["audioPreview"]:
            result["preview_url"] = entity["audioPreview"]["url"]
        elif "previews" in entity and entity["previews"] and "url" in entity["previews"][0]:
            result["preview_url"] = entity["previews"][0]["url"]
        
        # Extract explicit flag
        result["is_explicit"] = entity.get("contentRating", {}).get("label", "") == "EXPLICIT"
        
        # Extract lyrics
        if "lyrics" in entity:
            lyrics_data = entity["lyrics"]
            lyrics = {
                "sync_type": lyrics_data.get("syncType", "LINE_SYNCED"),
                "provider": lyrics_data.get("provider", "SPOTIFY"),
                "language": lyrics_data.get("language", "en"),
                "lines": []
            }
            
            # Extract lyrics lines
            for line in lyrics_data.get("lines", []):
                lyrics_line = {
                    "start_time_ms": line.get("startTimeMs", 0),
                    "words": line.get("words", ""),
                    "end_time_ms": line.get("endTimeMs", 0),
                }
                lyrics["lines"].append(lyrics_line)
            
            result["lyrics"] = lyrics
        
        return result
        
    except Exception as e:
        return {"ERROR": str(e), "id": "", "name": "", "uri": "", "type": "track"}

class TrackExtractor:
    """
    Extractor for Spotify track information.
    
    This class provides functionality to extract information from
    Spotify track pages, with support for different page structures and
    automatic conversion between regular and embed URLs.
    
    Attributes:
        browser: Browser instance for web interactions
    
    Note:
        This extractor prioritizes using Spotify embed URLs (/embed/track/...)
        over regular URLs because embed endpoints do not require authentication
        and provide the same track metadata including lyrics.
    """
    
    def __init__(self, browser: Browser):
        """
        Initialize the TrackExtractor.
        
        Args:
            browser: Browser instance for web interactions
        """
        self.browser = browser
    
    def extract(self, url: str) -> TrackData:
        """
        Extract track information from a Spotify track URL.
        
        This method takes any Spotify track URL and converts it to an
        embed URL format for extraction. Embed URLs don't require Spotify
        login/authentication but still provide full track metadata.
        
        Args:
            url: Spotify track URL (will be converted to embed format)
            
        Returns:
            Track data as a dictionary
            
        Raises:
            URLError: If the URL is invalid
            ScrapingError: If extraction fails
        """
        # Validate URL
        try:
            validate_url(url, expected_type="track")
        except URLError as e:
            return {"ERROR": str(e), "id": "", "name": "", "uri": "", "type": "track"}
        
        # Extract track ID for logging
        try:
            track_id = extract_id(url)
        except URLError:
            track_id = "unknown"
        
        # Always use embed URL, which doesn't require authentication
        try:
            # Convert any track URL to embed format
            embed_url = convert_to_embed_url(url)
            
            # Get page content from embed URL
            page_content = self.browser.get(embed_url)
            
            # Parse track information
            track_data = extract_track_data_from_html(page_content)
            
            # If we got valid data, return it
            if track_data and not track_data.get("ERROR"):
                return track_data
            
            # If extraction failed, return the error data
            return track_data
            
        except Exception as e:
            return {"ERROR": str(e), "id": track_id, "name": "", "uri": "", "type": "track"}
    
    def extract_by_id(self, track_id: str) -> TrackData:
        """
        Extract track information by ID.
        
        This method constructs an embed URL from the track ID and extracts the data.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Track data as a dictionary
        """
        # Directly create an embed URL for best results
        url = f"https://open.spotify.com/embed/track/{track_id}"
        return self.extract(url)
    
    def extract_preview_url(self, url: str) -> Optional[str]:
        """
        Extract preview URL from a track.
        
        Args:
            url: Spotify track URL
            
        Returns:
            Preview URL, or None if not available
        """
        track_data = self.extract(url)
        return track_data.get("preview_url")
    
    def extract_cover_url(self, url: str) -> Optional[str]:
        """
        Extract cover URL from a track.
        
        Args:
            url: Spotify track URL
            
        Returns:
            Cover URL, or None if not available
        """
        track_data = self.extract(url)
        
        # Check if album is available and has images
        if "album" in track_data and "images" in track_data["album"]:
            images = track_data["album"]["images"]
            if images and len(images) > 0:
                return images[0].get("url")
        
        return None