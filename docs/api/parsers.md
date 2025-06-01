# Parsers Module

The `parsers` module provides specialized classes and functions for parsing data from Spotify web pages, handling JSON extraction, and data structure normalization.

## Table of Contents
- [Overview](#overview)
- [JSON Parser](#json-parser)
- [Data Extraction Functions](#data-extraction-functions)
- [Data Type Parsers](#data-type-parsers)
- [Utility Functions](#utility-functions)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Overview

The parsers module is responsible for:

- **JSON Extraction**: Extract structured data from Spotify HTML pages
- **Data Normalization**: Convert raw Spotify data into consistent formats
- **Type Safety**: Ensure parsed data matches expected TypedDict structures
- **Error Handling**: Graceful handling of malformed or missing data

### Import Statement

```python
from spotify_scraper.parsers import (
    extract_json_from_html,
    get_nested_value,
    extract_track_data,
    extract_album_data,
    extract_artist_data,
    extract_playlist_data,
    extract_lyrics_data
)
```

---

## JSON Parser

### extract_json_from_html

Extract JSON data from HTML documents using CSS selectors.

```python
def extract_json_from_html(html_content: str, selector: str) -> Dict[str, Any]
```

**Parameters:**
- `html_content` (str): HTML content from Spotify page
- `selector` (str): CSS selector for script tag containing JSON

**Returns:**
- `Dict[str, Any]`: Parsed JSON data

**Raises:**
- `ParsingError`: If JSON extraction or parsing fails

**Example:**
```python
from spotify_scraper.parsers import extract_json_from_html

# Extract JSON from Spotify page
html_content = "<html>...</html>"  # HTML from Spotify
json_data = extract_json_from_html(html_content, "#__NEXT_DATA__")

print(json_data.keys())
# Output: dict_keys(['props', 'page', 'query', 'buildId'])
```

### Common Selectors

```python
# Built-in selectors for different page types
NEXT_DATA_SELECTOR = "#__NEXT_DATA__"
RESOURCE_SELECTOR = "script[data-testid='resource']"

# Usage examples
next_data = extract_json_from_html(html, NEXT_DATA_SELECTOR)
resource_data = extract_json_from_html(html, RESOURCE_SELECTOR)
```

---

## Data Extraction Functions

### get_nested_value

Safely extract nested values from dictionaries using dot notation.

```python
def get_nested_value(
    data: Dict[str, Any],
    path: str,
    default: Optional[Any] = None,
) -> Any
```

**Parameters:**
- `data` (Dict): Dictionary to search
- `path` (str): Dot-separated path (e.g., "props.pageProps.state.data")
- `default` (Optional): Default value if path not found

**Returns:**
- Value at specified path or default

**Example:**
```python
from spotify_scraper.parsers import get_nested_value

data = {
    "props": {
        "pageProps": {
            "state": {
                "data": {"track": {"name": "Song Title"}}
            }
        }
    }
}

# Extract nested value
track_name = get_nested_value(data, "props.pageProps.state.data.track.name")
print(track_name)  # Output: "Song Title"

# With default value
artist_name = get_nested_value(data, "props.pageProps.state.data.track.artist", "Unknown")
print(artist_name)  # Output: "Unknown"
```

---

## Data Type Parsers

### extract_track_data

Extract and normalize track data from Spotify JSON.

```python
def extract_track_data(json_data: Dict[str, Any], path: str = TRACK_JSON_PATH) -> TrackData
```

**Parameters:**
- `json_data` (Dict): Raw JSON data from Spotify
- `path` (str): JSON path to track data (optional)

**Returns:**
- `TrackData`: Normalized track information

**Example:**
```python
from spotify_scraper.parsers import extract_track_data

# Extract from Next.js data
json_data = extract_json_from_html(html_content, "#__NEXT_DATA__")
track_data = extract_track_data(json_data)

print(track_data)
# Output: {
#     'id': 'track_id',
#     'name': 'Track Name',
#     'artists': [{'name': 'Artist Name', 'uri': 'spotify:artist:...'}],
#     'album': {'name': 'Album Name', 'images': [...]},
#     'duration_ms': 210000,
#     'preview_url': 'https://...',
#     'is_explicit': False,
#     'is_playable': True,
#     'uri': 'spotify:track:...'
# }
```

### extract_album_data

Extract and normalize album data from Spotify JSON.

```python
def extract_album_data(json_data: Dict[str, Any], path: str = ALBUM_JSON_PATH) -> AlbumData
```

**Example:**
```python
from spotify_scraper.parsers import extract_album_data

album_data = extract_album_data(json_data)
print(album_data)
# Output: {
#     'id': 'album_id',
#     'name': 'Album Name',
#     'artists': [{'name': 'Artist Name', 'uri': 'spotify:artist:...'}],
#     'release_date': '2023-01-01',
#     'total_tracks': 12,
#     'images': [{'url': '...', 'width': 640, 'height': 640}],
#     'uri': 'spotify:album:...'
# }
```

### extract_artist_data

Extract and normalize artist data from Spotify JSON.

```python
def extract_artist_data(json_data: Dict[str, Any], path: str = ARTIST_JSON_PATH) -> ArtistData
```

**Example:**
```python
from spotify_scraper.parsers import extract_artist_data

artist_data = extract_artist_data(json_data)
print(artist_data)
# Output: {
#     'id': 'artist_id',
#     'name': 'Artist Name',
#     'genres': ['pop', 'dance pop'],
#     'followers': 1000000,
#     'images': [{'url': '...', 'width': 640, 'height': 640}],
#     'uri': 'spotify:artist:...'
# }
```

### extract_playlist_data

Extract and normalize playlist data from Spotify JSON.

```python
def extract_playlist_data(json_data: Dict[str, Any], path: str = PLAYLIST_JSON_PATH) -> PlaylistData
```

**Example:**
```python
from spotify_scraper.parsers import extract_playlist_data

playlist_data = extract_playlist_data(json_data)
print(playlist_data)
# Output: {
#     'id': 'playlist_id',
#     'name': 'Playlist Name',
#     'description': 'Playlist description',
#     'owner': {'display_name': 'Owner Name', 'id': 'user_id'},
#     'tracks': {'total': 50, 'items': [...]},
#     'images': [{'url': '...', 'width': 640, 'height': 640}],
#     'uri': 'spotify:playlist:...'
# }
```

### extract_lyrics_data

Extract and normalize lyrics data from Spotify JSON.

```python
def extract_lyrics_data(json_data: Dict[str, Any]) -> LyricsData
```

**Example:**
```python
from spotify_scraper.parsers import extract_lyrics_data

lyrics_data = extract_lyrics_data(json_data)
print(lyrics_data)
# Output: {
#     'lyrics': {
#         'syncType': 'LINE_SYNCED',
#         'lines': [
#             {'startTimeMs': 0, 'words': 'First line of lyrics'},
#             {'startTimeMs': 5000, 'words': 'Second line of lyrics'}
#         ]
#     },
#     'colors': {'background': '#000000', 'text': '#ffffff'},
#     'hasVocalRemoval': False
# }
```

---

## Utility Functions

### Data Validation

```python
def validate_track_data(track_data: Dict[str, Any]) -> bool:
    """Validate track data structure."""
    required_fields = ['id', 'name', 'artists', 'uri']
    return all(field in track_data for field in required_fields)

def validate_album_data(album_data: Dict[str, Any]) -> bool:
    """Validate album data structure."""
    required_fields = ['id', 'name', 'artists', 'uri']
    return all(field in album_data for field in required_fields)
```

### Data Normalization

```python
def normalize_duration(duration_ms: int) -> str:
    """Convert duration from milliseconds to MM:SS format."""
    total_seconds = duration_ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"

def normalize_image_url(images: List[Dict[str, Any]], size: str = "medium") -> str:
    """Get image URL for specified size."""
    if not images:
        return ""
    
    size_preferences = {
        "small": (64, 300),
        "medium": (300, 640),
        "large": (640, float('inf'))
    }
    
    min_size, max_size = size_preferences.get(size, (300, 640))
    
    # Find best matching image
    for image in sorted(images, key=lambda x: x.get('width', 0)):
        width = image.get('width', 0)
        if min_size <= width <= max_size:
            return image.get('url', '')
    
    # Return largest if no match
    return images[-1].get('url', '') if images else ""
```

### Date Parsing

```python
def parse_release_date(date_data: Union[str, Dict[str, Any]]) -> str:
    """Parse release date from various formats."""
    if isinstance(date_data, str):
        return date_data
    
    if isinstance(date_data, dict):
        year = date_data.get('year', '')
        month = str(date_data.get('month', '')).zfill(2) if date_data.get('month') else ''
        day = str(date_data.get('day', '')).zfill(2) if date_data.get('day') else ''
        
        if year and month and day:
            return f"{year}-{month}-{day}"
        elif year and month:
            return f"{year}-{month}"
        elif year:
            return str(year)
    
    return ""
```

---

## Error Handling

### Custom Exceptions

```python
from spotify_scraper.core.exceptions import ParsingError

try:
    track_data = extract_track_data(json_data)
except ParsingError as e:
    print(f"Parsing failed: {e}")
    print(f"Data type: {e.data_type}")
    print(f"Details: {e.details}")
```

### Safe Parsing

```python
def safe_extract_track(json_data: Dict[str, Any]) -> Optional[TrackData]:
    """Safely extract track data with error handling."""
    try:
        return extract_track_data(json_data)
    except ParsingError as e:
        logger.warning(f"Failed to parse track data: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during parsing: {e}")
        return None

# Usage
track_data = safe_extract_track(json_data)
if track_data:
    print(f"Track: {track_data.get('name', 'Unknown')}")
else:
    print("Failed to extract track data")
```

### Error Recovery

```python
def extract_with_fallback(
    json_data: Dict[str, Any],
    primary_path: str,
    fallback_paths: List[str]
) -> Any:
    """Extract data with multiple fallback paths."""
    
    # Try primary path first
    result = get_nested_value(json_data, primary_path)
    if result is not None:
        return result
    
    # Try fallback paths
    for fallback_path in fallback_paths:
        result = get_nested_value(json_data, fallback_path)
        if result is not None:
            logger.info(f"Using fallback path: {fallback_path}")
            return result
    
    return None

# Usage
track_name = extract_with_fallback(
    json_data,
    "props.pageProps.state.data.entity.name",
    [
        "props.pageProps.state.data.track.name",
        "props.pageProps.state.data.title",
        "track.name"
    ]
)
```

---

## Examples

### Complete Track Parsing

```python
from spotify_scraper.parsers import (
    extract_json_from_html,
    extract_track_data,
    NEXT_DATA_SELECTOR
)

def parse_track_page(html_content: str) -> Optional[TrackData]:
    """Parse a complete track page."""
    try:
        # Extract JSON data
        json_data = extract_json_from_html(html_content, NEXT_DATA_SELECTOR)
        
        # Extract track data
        track_data = extract_track_data(json_data)
        
        # Validate required fields
        if not all(field in track_data for field in ['id', 'name', 'artists']):
            raise ParsingError("Missing required track fields")
        
        return track_data
        
    except ParsingError as e:
        logger.error(f"Failed to parse track page: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
```

### Batch Data Processing

```python
def process_multiple_tracks(html_pages: List[str]) -> List[TrackData]:
    """Process multiple track pages efficiently."""
    tracks = []
    
    for i, html_content in enumerate(html_pages):
        try:
            track_data = parse_track_page(html_content)
            if track_data:
                tracks.append(track_data)
            else:
                logger.warning(f"Failed to parse track {i}")
        except Exception as e:
            logger.error(f"Error processing track {i}: {e}")
            continue
    
    return tracks
```

### Custom Data Extraction

```python
def extract_custom_metadata(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract custom metadata not covered by standard parsers."""
    
    custom_data = {}
    
    # Extract additional track features
    audio_features = get_nested_value(json_data, "track.audioFeatures")
    if audio_features:
        custom_data.update({
            'energy': audio_features.get('energy'),
            'danceability': audio_features.get('danceability'),
            'valence': audio_features.get('valence'),
            'tempo': audio_features.get('tempo')
        })
    
    # Extract chart information
    chart_data = get_nested_value(json_data, "track.chartData")
    if chart_data:
        custom_data.update({
            'chart_position': chart_data.get('position'),
            'chart_country': chart_data.get('country'),
            'chart_date': chart_data.get('date')
        })
    
    # Extract social metrics
    social_data = get_nested_value(json_data, "track.socialMetrics")
    if social_data:
        custom_data.update({
            'play_count': social_data.get('playCount'),
            'like_count': social_data.get('likeCount'),
            'share_count': social_data.get('shareCount')
        })
    
    return custom_data
```

---

## Advanced Usage

### Custom Parser Classes

```python
from typing import Protocol
from spotify_scraper.core.types import TrackData

class DataParser(Protocol):
    """Protocol for custom data parsers."""
    
    def parse(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON data and return structured data."""
        ...

class CustomTrackParser:
    """Custom track parser with enhanced features."""
    
    def __init__(self, include_audio_features: bool = False):
        self.include_audio_features = include_audio_features
    
    def parse(self, json_data: Dict[str, Any]) -> TrackData:
        """Parse track data with custom enhancements."""
        
        # Use standard parser as base
        track_data = extract_track_data(json_data)
        
        # Add custom features if requested
        if self.include_audio_features:
            audio_features = self._extract_audio_features(json_data)
            track_data.update(audio_features)
        
        return track_data
    
    def _extract_audio_features(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract audio feature data."""
        features = {}
        
        audio_analysis = get_nested_value(json_data, "track.audioAnalysis")
        if audio_analysis:
            features.update({
                'key': audio_analysis.get('key'),
                'mode': audio_analysis.get('mode'),
                'time_signature': audio_analysis.get('time_signature'),
                'acousticness': audio_analysis.get('acousticness'),
                'instrumentalness': audio_analysis.get('instrumentalness'),
                'liveness': audio_analysis.get('liveness'),
                'speechiness': audio_analysis.get('speechiness')
            })
        
        return features
```

### Performance Optimization

```python
import functools
from typing import LRU_CACHE_SIZE = 128

@functools.lru_cache(maxsize=LRU_CACHE_SIZE)
def cached_extract_json(html_content: str, selector: str) -> Dict[str, Any]:
    """Cached version of JSON extraction for repeated requests."""
    return extract_json_from_html(html_content, selector)

def batch_parse_with_cache(html_pages: List[str]) -> List[TrackData]:
    """Batch parse with caching for performance."""
    tracks = []
    
    for html_content in html_pages:
        try:
            # Use cached extraction
            json_data = cached_extract_json(html_content, NEXT_DATA_SELECTOR)
            track_data = extract_track_data(json_data)
            tracks.append(track_data)
        except Exception as e:
            logger.warning(f"Failed to parse track: {e}")
            continue
    
    return tracks
```

---

## Type Definitions

The parsers module uses TypedDict classes for type safety:

```python
from spotify_scraper.core.types import (
    TrackData,
    AlbumData,
    ArtistData,
    PlaylistData,
    LyricsData,
    LyricsLineData
)

# TrackData structure
track: TrackData = {
    'id': 'track_id',
    'name': 'Track Name',
    'artists': [{'name': 'Artist', 'uri': 'spotify:artist:...'}],
    'album': {'name': 'Album', 'type': 'album'},
    'duration_ms': 210000,
    'preview_url': 'https://...',
    'is_explicit': False,
    'is_playable': True,
    'uri': 'spotify:track:...'
}
```

---

## Best Practices

### Error Handling

1. **Always handle ParsingError**: Expected when data structure changes
2. **Use safe extraction**: Prefer `get_nested_value` over direct dictionary access
3. **Validate parsed data**: Check for required fields before using data
4. **Log parsing failures**: Help with debugging and monitoring

### Performance

1. **Cache repeated extractions**: Use `@lru_cache` for repeated HTML parsing
2. **Batch process when possible**: Process multiple items together
3. **Use appropriate selectors**: Choose the most specific selector available
4. **Validate early**: Check data structure before expensive operations

### Maintainability

1. **Use constants for paths**: Define JSON paths as constants
2. **Create custom parsers**: Extend functionality with custom parser classes
3. **Document data structures**: Use TypedDict for clear interfaces
4. **Test edge cases**: Handle missing or malformed data gracefully

---

## Next Steps

Now that you understand the parsers module:

1. 🔍 Explore [extractors module](extractors.md) for higher-level data extraction
2. 🛠️ Learn about [error handling](../guide/error-handling.md) patterns
3. ⚡ Check [performance optimization](../advanced/performance.md) techniques
4. 🧪 Write [custom extractors](../advanced/custom-extractors.md)

---

## Getting Help

If you need help with parsing:

1. 📖 Check the [API reference](index.md) for complete documentation
2. 🔧 Review [troubleshooting guide](../troubleshooting.md)
3. 💬 Ask on [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
4. 🐛 Report parsing issues on [GitHub Issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)