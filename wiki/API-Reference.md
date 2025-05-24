# API Reference

Complete API documentation for SpotifyScraper v2.0.0.

## 📋 Table of Contents

- [SpotifyClient](#spotifyclient)
- [Configuration](#configuration)
- [Data Types](#data-types)
- [Exceptions](#exceptions)
- [Utility Functions](#utility-functions)

## SpotifyClient

The main client class for interacting with Spotify.

### Constructor

```python
SpotifyClient(
    cookie_file: Optional[str] = None,
    cookies: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    proxy: Optional[Dict[str, str]] = None,
    browser_type: str = "requests",
    log_level: str = "INFO",
    log_file: Optional[str] = None
)
```

#### Parameters

- `cookie_file` (str, optional): Path to Netscape-format cookies.txt file for authentication
- `cookies` (Dict[str, str], optional): Dictionary of cookies to use instead of cookie_file
- `headers` (Dict[str, str], optional): Custom HTTP headers to include in all requests
- `proxy` (Dict[str, str], optional): Proxy server configuration (e.g., {"http": "http://proxy:8080"})
- `browser_type` (str): Backend browser implementation ("requests", "selenium", or "auto")
- `log_level` (str): Logging verbosity level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
- `log_file` (str, optional): Path to write log messages to

### Methods

#### get_track_info

```python
get_track_info(url: str) -> Dict[str, Any]
```

Extract track metadata.

**Parameters:**
- `url` (str): Spotify track URL

**Returns:**
- Dict containing track metadata

**Example:**
```python
track = client.get_track_info("https://open.spotify.com/track/...")
```

#### get_track_lyrics

```python
get_track_lyrics(url: str) -> Optional[Dict[str, Any]]
```

Extract track lyrics (requires authentication).

**Parameters:**
- `url` (str): Spotify track URL

**Returns:**
- Dict containing lyrics data or None

#### get_track_info_with_lyrics

```python
get_track_info_with_lyrics(url: str) -> Dict[str, Any]
```

Extract track metadata with lyrics.

**Parameters:**
- `url` (str): Spotify track URL

**Returns:**
- Dict containing track metadata and lyrics

#### get_album_info

```python
get_album_info(url: str) -> Dict[str, Any]
```

Extract album metadata.

**Parameters:**
- `url` (str): Spotify album URL

**Returns:**
- Dict containing album metadata

#### get_artist_info

```python
get_artist_info(
    url: str,
    top_tracks_limit: int = 10,
    albums_limit: Optional[int] = None
) -> Dict[str, Any]
```

Extract artist metadata.

**Parameters:**
- `url` (str): Spotify artist URL
- `top_tracks_limit` (int): Number of top tracks (default: 10)
- `albums_limit` (int, optional): Maximum number of albums

**Returns:**
- Dict containing artist metadata

#### get_playlist_info

```python
get_playlist_info(
    url: str,
    tracks_limit: Optional[int] = None
) -> Dict[str, Any]
```

Extract playlist metadata.

**Parameters:**
- `url` (str): Spotify playlist URL
- `tracks_limit` (int, optional): Maximum number of tracks

**Returns:**
- Dict containing playlist metadata

#### get_all_info

```python
get_all_info(url: str) -> Dict[str, Any]
```

Extract metadata for any Spotify URL type.

**Parameters:**
- `url` (str): Any Spotify URL

**Returns:**
- Dict containing appropriate metadata

#### download_cover

```python
download_cover(
    url: str,
    path: str = "covers/",
    filename: Optional[str] = None,
    size: int = 640
) -> Optional[str]
```

Download cover art.

**Parameters:**
- `url` (str): Spotify URL
- `path` (str): Download directory (default: "covers/")
- `filename` (str, optional): Custom filename
- `size` (int): Image size (default: 640)

**Returns:**
- Path to downloaded file or None

#### download_preview_mp3

```python
download_preview_mp3(
    url: str,
    path: str = "previews/",
    filename: Optional[str] = None,
    with_cover: bool = True
) -> Optional[str]
```

Download 30-second preview.

**Parameters:**
- `url` (str): Spotify track URL
- `path` (str): Download directory (default: "previews/")
- `filename` (str, optional): Custom filename
- `with_cover` (bool): Embed cover art (default: True)

**Returns:**
- Path to downloaded file or None

#### close

```python
close() -> None
```

Close the client and clean up resources.

## Configuration

### Config Class

```python
from spotify_scraper import Config

config = Config(
    cache_enabled=True,
    cache_dir=".cache",
    max_retries=3,
    timeout=30,
    proxy=None,
    user_agent="Mozilla/5.0...",
    rate_limit=1.0
)
```

### Configuration File

Create `spotify_scraper.json`:

```json
{
  "cache": {
    "enabled": true,
    "directory": ".cache",
    "ttl": 3600
  },
  "network": {
    "timeout": 30,
    "max_retries": 3,
    "proxy": null
  },
  "browser": {
    "user_agent": "Mozilla/5.0..."
  }
}
```

## Data Types

### Track Object

```python
{
    "id": str,
    "name": str,
    "artists": List[Artist],
    "album": Album,
    "duration_ms": int,
    "explicit": bool,
    "popularity": int,
    "preview_url": Optional[str],
    "external_urls": Dict[str, str],
    "is_playable": bool,
    "lyrics": Optional[Lyrics]  # If requested
}
```

### Album Object

```python
{
    "id": str,
    "name": str,
    "artists": List[Artist],
    "release_date": str,
    "total_tracks": int,
    "tracks": List[Track],
    "images": List[Image],
    "external_urls": Dict[str, str],
    "label": Optional[str],
    "copyrights": List[Copyright]
}
```

### Artist Object

```python
{
    "id": str,
    "name": str,
    "followers": int,
    "monthly_listeners": int,
    "genres": List[str],
    "images": List[Image],
    "external_urls": Dict[str, str],
    "top_tracks": List[Track],
    "albums": List[Album]
}
```

### Playlist Object

```python
{
    "id": str,
    "name": str,
    "description": str,
    "owner": Owner,
    "followers": int,
    "total_tracks": int,
    "tracks": List[Track],
    "images": List[Image],
    "external_urls": Dict[str, str],
    "public": bool,
    "collaborative": bool
}
```

## Exceptions

### SpotifyScraperError

Base exception class for all errors.

```python
from spotify_scraper import SpotifyScraperError
```

### URLError

Invalid or unsupported URL.

```python
from spotify_scraper import URLError

try:
    client.get_track_info("invalid_url")
except URLError as e:
    print(f"Invalid URL: {e}")
```

### NetworkError

Network-related errors.

```python
from spotify_scraper import NetworkError

try:
    client.get_track_info(url)
except NetworkError as e:
    print(f"Network error: {e}")
```

### AuthenticationError

Authentication required or failed.

```python
from spotify_scraper import AuthenticationError

try:
    client.get_track_lyrics(url)
except AuthenticationError as e:
    print(f"Authentication required: {e}")
```

### ExtractionError

Failed to extract data.

```python
from spotify_scraper import ExtractionError

try:
    data = client.get_track_info(url)
except ExtractionError as e:
    print(f"Extraction failed: {e}")
```

## Utility Functions

### URL Utilities

```python
from spotify_scraper import is_spotify_url, extract_id, get_url_type

# Check if URL is valid
if is_spotify_url(url):
    print("Valid Spotify URL")

# Extract ID from URL
track_id = extract_id("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
# Returns: "6rqhFgbbKwnb9MLmUQDhG6"

# Get URL type
url_type = get_url_type("https://open.spotify.com/track/...")
# Returns: "track"
```

### Format Utilities

```python
from spotify_scraper.utils import format_duration, format_number

# Format duration
duration_str = format_duration(210000)  # "3:30"

# Format numbers
followers_str = format_number(1234567)  # "1,234,567"
```

## 📚 Complete Example

```python
from spotify_scraper import SpotifyClient, URLError, NetworkError
import json

# Initialize client with all options
client = SpotifyClient(
    cookie_file="cookies.txt",
    cache_enabled=True,
    cache_dir=".spotify_cache",
    max_retries=5,
    timeout=60,
    proxy="http://proxy.example.com:8080"
)

try:
    # Get track with lyrics
    track = client.get_track_info_with_lyrics(
        "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
    )
    
    # Save to JSON
    with open("track_data.json", "w") as f:
        json.dump(track, f, indent=2)
    
    # Download media
    preview = client.download_preview_mp3(track['external_urls']['spotify'])
    cover = client.download_cover(track['external_urls']['spotify'])
    
    print(f"Track: {track['name']}")
    print(f"Preview: {preview}")
    print(f"Cover: {cover}")
    
except URLError as e:
    print(f"Invalid URL: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
finally:
    client.close()
```