# API Reference

Complete API documentation for all SpotifyScraper classes, methods, and utilities.

## Overview

SpotifyScraper provides a clean, intuitive API organized into logical components:

```python
from spotify_scraper import SpotifyClient

# Main client for all operations
client = SpotifyClient()

# Extract data
track = client.get_track_info(url)
album = client.get_album_info(url)
artist = client.get_artist_info(url)
playlist = client.get_playlist_info(url)

# Download media
preview = client.download_preview_mp3(url)
cover = client.download_cover(url)
```

---

## Core Components

### 🎯 Main Client
- [**SpotifyClient**](client.md) - Primary interface for all operations
  - Data extraction methods (`get_track_info`, `get_album_info`, etc.)
  - Media download capabilities (`download_preview_mp3`, `download_cover`)
  - Authentication handling (cookie-based for lyrics)
  - Resource management (automatic cleanup)

### 🔍 Data Extractors
- [**TrackExtractor**](extractors.md#trackextractor) - Extract track metadata
- [**AlbumExtractor**](extractors.md#albumextractor) - Extract album information
- [**ArtistExtractor**](extractors.md#artistextractor) - Extract artist profiles
- [**PlaylistExtractor**](extractors.md#playlistextractor) - Extract playlist data

### 📥 Media Handlers
- [**AudioDownloader**](media.md#audiodownloader) - Download audio previews
- [**ImageDownloader**](media.md#imagedownloader) - Download cover art

### 🛠️ Utilities
- [**URL Utilities**](utils.md#url-utilities) - URL validation and manipulation
- [**Common Utilities**](utils.md#common-utilities) - Helper functions
- [**SpotifyBulkOperations**](utils.md#spotifybulkoperations) - Batch operations
- [**SpotifyDataAnalyzer**](utils.md#spotifydataanalyzer) - Data analysis
- [**Logger**](utils.md#logger) - Logging configuration

### ⚠️ Exceptions
- [**Exception Hierarchy**](exceptions.md) - All error types
  - `SpotifyScraperError` - Base exception
  - `URLError` - Invalid URL errors
  - `NetworkError` - Connection issues
  - `ExtractionError` - Parsing failures
  - `AuthenticationError` - Auth problems
  - `MediaError` - Download errors

---

## Quick Reference

### SpotifyClient Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `get_track_info(url)` | Extract track metadata | `Dict[str, Any]` |
| `get_track_info_with_lyrics(url)` | Track with lyrics (auth required) | `Dict[str, Any]` |
| `get_album_info(url)` | Extract album data | `Dict[str, Any]` |
| `get_artist_info(url)` | Extract artist profile | `Dict[str, Any]` |
| `get_playlist_info(url)` | Extract playlist | `Dict[str, Any]` |
| `get_track_lyrics(url)` | Get lyrics only | `Optional[str]` |
| `download_preview_mp3(url, **kwargs)` | Download preview | `str` |
| `download_cover(url, **kwargs)` | Download cover art | `str` |
| `get_all_info(url)` | Auto-detect and extract | `Dict[str, Any]` |
| `close()` | Clean up resources | `None` |

### Data Structures

#### Track Data
```python
{
    'id': str,                    # Spotify track ID
    'name': str,                  # Track title
    'uri': str,                   # Spotify URI
    'type': 'track',              # Entity type
    'duration_ms': int,           # Duration in milliseconds
    'artists': List[Dict],        # Artist information
    'album': Dict,                # Album information
    'preview_url': Optional[str], # 30-second preview URL
    'is_explicit': bool,          # Explicit content flag
    'release_date': str,          # Release date
    'track_number': int,          # Position in album
    'lyrics': Optional[str]       # Lyrics (if available)
}
```

#### Album Data
```python
{
    'id': str,                    # Spotify album ID
    'name': str,                  # Album title
    'uri': str,                   # Spotify URI
    'type': 'album',              # Entity type
    'artists': List[Dict],        # Album artists
    'images': List[Dict],         # Cover art URLs
    'release_date': str,          # Release date
    'total_tracks': int,          # Number of tracks
    'tracks': List[Dict]          # Track listings
}
```

#### Artist Data
```python
{
    'id': str,                    # Spotify artist ID
    'name': str,                  # Artist name
    'uri': str,                   # Spotify URI
    'type': 'artist',             # Entity type
    'images': List[Dict],         # Artist images
    'genres': List[str],          # Music genres
    'popularity': int,            # Popularity score
    'followers': int,             # Follower count
    'bio': Optional[str],         # Artist biography
    'top_tracks': List[Dict],     # Popular tracks
    'stats': Dict                 # Statistics
}
```

#### Playlist Data
```python
{
    'id': str,                    # Spotify playlist ID
    'name': str,                  # Playlist name
    'uri': str,                   # Spotify URI
    'type': 'playlist',           # Entity type
    'owner': Dict,                # Playlist owner
    'images': List[Dict],         # Cover images
    'description': str,           # Playlist description
    'track_count': int,           # Number of tracks
    'tracks': List[Dict],         # Track listings
    'duration_ms': int            # Total duration
}
```

---

## Usage Examples

### Basic Usage
```python
from spotify_scraper import SpotifyClient

# Initialize client
client = SpotifyClient()

# Extract track information
track = client.get_track_info("https://open.spotify.com/track/...")
print(f"Track: {track.get('name', 'Unknown')} by {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")

# Download preview
preview_path = client.download_preview_mp3(track_url, path="previews/")
```

### With Authentication
```python
# Use cookies for authenticated features
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Now you can access lyrics
track = client.get_track_info_with_lyrics(track_url)
if track.get('lyrics'):
    print(track['lyrics'])
```

### Error Handling
```python
from spotify_scraper import (
    SpotifyClient,
    URLError,
    NetworkError,
    ExtractionError
)

client = SpotifyClient()

try:
    data = client.get_track_info(url)
except URLError:
    print("Invalid Spotify URL")
except NetworkError:
    print("Connection failed")
except ExtractionError:
    print("Could not extract data")
```

### Resource Management
```python
# Always close when using Selenium
client = SpotifyClient(browser_type="selenium")
try:
    # Your code here
    data = client.get_track_info(url)
finally:
    client.close()
```

---

## Type Hints

SpotifyScraper is fully typed for better IDE support:

```python
from typing import Dict, Any, Optional, List
from spotify_scraper import SpotifyClient

def analyze_track(url: str) -> Dict[str, Any]:
    """Analyze a Spotify track."""
    client: SpotifyClient = SpotifyClient()
    track_data: Dict[str, Any] = client.get_track_info(url)
    
    return {
        'title': track_data.get('name', 'Unknown'),
        'artist': track_data['artists'][0]['name'],
        'duration_seconds': track_data['duration_ms'] / 1000
    }
```

---

## Best Practices

### 1. Reuse Client Instances
```python
# Good - reuse client
client = SpotifyClient()
for url in urls:
    data = client.get_track_info(url)
    
# Don't forget to close if using Selenium
if client.browser_type == "selenium":
    client.close()

# Bad - creating new client each time
for url in urls:
    client = SpotifyClient()
    data = client.get_track_info(url)
```

### 2. Handle Errors Gracefully
```python
def safe_extract(url: str) -> Optional[Dict[str, Any]]:
    """Safely extract data with error handling."""
    try:
        client = SpotifyClient()
        return client.get_track_info(url)
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return None
```

### 3. Use Type Hints
```python
from typing import List, Dict, Any
from spotify_scraper import SpotifyClient

def get_playlist_tracks(url: str) -> List[Dict[str, Any]]:
    """Get all tracks from a playlist."""
    client = SpotifyClient()
    playlist = client.get_playlist_info(url)
    return playlist.get('tracks', [])
```

### 4. Close Resources
```python
# When using Selenium
client = SpotifyClient(browser_type="selenium")
try:
    # Your operations
    track = client.get_track_info(url)
    album = client.get_album_info(album_url)
finally:
    client.close()
    
# Requests backend doesn't require explicit cleanup
client = SpotifyClient(browser_type="requests")
track = client.get_track_info(url)  # No close() needed
```

---

## Advanced Topics

- [Performance Optimization](../advanced/performance.md)
- [Custom Extractors](../advanced/custom-extractors.md)
- [Scaling Guide](../advanced/scaling.md)
- [Architecture Overview](../advanced/architecture.md)

---

## See Also

- [Installation Guide](../getting-started/installation.md)
- [Basic Usage Guide](../guide/basic-usage.md)
- [Examples](../examples/index.md)
- [Troubleshooting](../troubleshooting.md)
- [FAQ](../faq.md)