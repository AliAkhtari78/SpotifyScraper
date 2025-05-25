# API Reference

Complete API documentation for SpotifyScraper v2.0.0.

## Table of Contents

- [SpotifyClient](#spotifyclient)
  - [Constructor](#constructor)
  - [Track Methods](#track-methods)
  - [Album Methods](#album-methods)
  - [Artist Methods](#artist-methods)
  - [Playlist Methods](#playlist-methods)
  - [Media Methods](#media-methods)
  - [Utility Methods](#utility-methods)
- [Data Types](#data-types)
- [Exceptions](#exceptions)
- [Utility Functions](#utility-functions)
- [Configuration](#configuration)
- [Browser Types](#browser-types)

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

- **cookie_file** (Optional[str]): Path to cookies.txt file for authentication
- **cookies** (Optional[Dict[str, str]]): Dictionary of cookies for authentication
- **headers** (Optional[Dict[str, str]]): Additional HTTP headers
- **proxy** (Optional[Dict[str, str]]): Proxy configuration (e.g., {"http": "...", "https": "..."})
- **browser_type** (str): Browser backend - "requests", "selenium", or "auto"
- **log_level** (str): Logging level - "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
- **log_file** (Optional[str]): Path to log file

### Track Methods

#### get_track_info(url: str) -> Dict[str, Any]

Extract track information.

```python
track_info = client.get_track_info("https://open.spotify.com/track/...")
```

**Returns**: Dictionary containing track metadata

#### get_track_lyrics(url: str, require_auth: bool = True) -> Optional[str]

Get track lyrics (requires authentication).

```python
lyrics = client.get_track_lyrics("https://open.spotify.com/track/...", require_auth=True)
```

**Returns**: Lyrics as string or None if not available

#### get_track_info_with_lyrics(url: str, require_lyrics_auth: bool = True) -> Dict[str, Any]

Get track information including lyrics.

```python
track_with_lyrics = client.get_track_info_with_lyrics("https://open.spotify.com/track/...")
```

**Returns**: Track info dictionary with 'lyrics' key added

### Album Methods

#### get_album_info(url: str) -> Dict[str, Any]

Extract album information.

```python
album_info = client.get_album_info("https://open.spotify.com/album/...")
```

**Returns**: Dictionary containing album metadata and tracks

### Artist Methods

#### get_artist_info(url: str) -> Dict[str, Any]

Extract artist information.

```python
artist_info = client.get_artist_info("https://open.spotify.com/artist/...")
```

**Returns**: Dictionary containing artist metadata

### Playlist Methods

#### get_playlist_info(url: str) -> Dict[str, Any]

Extract playlist information.

```python
playlist_info = client.get_playlist_info("https://open.spotify.com/playlist/...")
```

**Returns**: Dictionary containing playlist metadata and tracks

### Media Methods

#### download_cover(url: str, path: str = "", filename: Optional[str] = None, quality_preference: Optional[List[str]] = None) -> Optional[str]

Download cover image.

```python
cover_path = client.download_cover(
    "https://open.spotify.com/track/...",
    path="covers/",
    filename="cover.jpg",
    quality_preference=["large", "medium", "small"]
)
```

**Parameters**:
- **url**: Spotify URL (track, album, artist, or playlist)
- **path**: Directory to save the image
- **filename**: Custom filename (optional)
- **quality_preference**: List of preferred sizes in order

**Returns**: Path to downloaded file or None

#### download_preview_mp3(url: str, path: str = "", with_cover: bool = False) -> str

Download track preview MP3 (30 seconds).

```python
preview_path = client.download_preview_mp3(
    "https://open.spotify.com/track/...",
    path="previews/",
    with_cover=True
)
```

**Parameters**:
- **url**: Track URL
- **path**: Directory to save the MP3
- **with_cover**: Embed cover art in MP3 metadata

**Returns**: Path to downloaded file

### Utility Methods

#### get_all_info(url: str) -> Dict[str, Any]

Auto-detect URL type and extract information.

```python
info = client.get_all_info("https://open.spotify.com/...")
```

**Returns**: Appropriate data based on URL type

#### close() -> None

Close the client and release resources.

```python
client.close()
```

## Data Types

### TrackData

```python
{
    "id": str,                    # Spotify ID
    "name": str,                  # Track name
    "uri": str,                   # Spotify URI
    "type": "track",              # Entity type
    "duration_ms": int,           # Duration in milliseconds
    "artists": List[{
        "name": str,
        "uri": str,
        "id": str
    }],
    "album": {
        "name": str,
        "uri": str,
        "id": str,
        "images": List[{"url": str, "width": int, "height": int}]
    },
    "preview_url": Optional[str], # 30-second preview URL
    "is_playable": bool,          # Playability status
    "is_explicit": bool,          # Explicit content flag
    "track_number": Optional[int],
    "disc_number": Optional[int],
    "lyrics": Optional[{          # If requested with auth
        "sync_type": str,
        "lines": List[{
            "start_time_ms": int,
            "words": str,
            "end_time_ms": int
        }],
        "provider": str,
        "language": str
    }]
}
```

### AlbumData

```python
{
    "id": str,
    "name": str,
    "uri": str,
    "type": "album",
    "artists": List[{
        "name": str,
        "uri": str,
        "id": str
    }],
    "images": List[{"url": str, "width": int, "height": int}],
    "release_date": str,          # YYYY-MM-DD format
    "total_tracks": int,
    "tracks": List[TrackData]     # List of track dictionaries
}
```

### ArtistData

```python
{
    "id": str,
    "name": str,
    "uri": str,
    "type": "artist",
    "is_verified": Optional[bool],
    "bio": Optional[str],
    "images": List[{"url": str, "width": int, "height": int}],
    "stats": Optional[{
        "followers": int,
        "monthly_listeners": int
    }],
    "popular_releases": Optional[List[AlbumData]],
    "discography_stats": Optional[{
        "albums": int,
        "singles": int,
        "compilations": int
    }],
    "top_tracks": Optional[List[TrackData]]
}
```

### PlaylistData

```python
{
    "id": str,
    "name": str,
    "uri": str,
    "type": "playlist",
    "description": Optional[str],
    "owner": {
        "name": str,
        "uri": str
    },
    "images": List[{"url": str, "width": int, "height": int}],
    "track_count": int,
    "tracks": List[TrackData]     # May be limited to first 100
}
```

## Exceptions

All exceptions inherit from `SpotifyScraperError`.

```python
from spotify_scraper import (
    SpotifyScraperError,      # Base exception
    URLError,                 # Invalid or unsupported URL
    ParsingError,             # HTML/JSON parsing failed
    ExtractionError,          # Data extraction failed
    NetworkError,             # Network/HTTP errors
    AuthenticationError,      # Authentication required/failed
    TokenError,               # Token-specific errors
    BrowserError,             # Browser operation failed
    MediaError,               # Media operation failed
    DownloadError,            # Download failed
    ConfigurationError        # Configuration invalid
)
```

### Exception Hierarchy

```
SpotifyScraperError
├── URLError
├── ParsingError
├── ExtractionError
├── NetworkError
├── AuthenticationError
│   └── TokenError
├── BrowserError
├── MediaError
│   └── DownloadError
└── ConfigurationError
```

## Utility Functions

### URL Utilities (spotify_scraper.utils.url)

```python
from spotify_scraper import (
    is_spotify_url,          # Check if URL is from Spotify
    extract_id,              # Extract ID from URL
    get_url_type,            # Get entity type from URL
    convert_to_embed_url,    # Convert to embed URL
    build_url,               # Build Spotify URL from ID
)

# Examples
is_spotify_url("https://open.spotify.com/track/...")  # True
extract_id("https://open.spotify.com/track/123")      # "123"
get_url_type("https://open.spotify.com/album/...")    # "album"
```

### Data Analysis (spotify_scraper.utils.common)

```python
from spotify_scraper.utils.common import (
    SpotifyDataAnalyzer,     # Playlist analysis
    SpotifyDataFormatter,    # Format data for output
    SpotifyBulkOperations,   # Batch processing
)

# Analyzer example
analyzer = SpotifyDataAnalyzer()
stats = analyzer.analyze_playlist(playlist_url)
comparison = analyzer.compare_playlists(url1, url2)

# Formatter example
formatter = SpotifyDataFormatter()
table = formatter.format_as_table(data)
csv = formatter.format_as_csv(data)

# Bulk operations example
bulk = SpotifyBulkOperations()
results = bulk.process_urls(urls, operation="all_info")
bulk.export_to_json(results, "output.json")
```

### Duration Formatting

```python
from spotify_scraper.utils.common import format_duration

formatted = format_duration(225400)  # "3:45"
```

## Configuration

### Environment Variables

All environment variables must be prefixed with `SPOTIFY_SCRAPER_`:

```bash
export SPOTIFY_SCRAPER_LOG_LEVEL=DEBUG
export SPOTIFY_SCRAPER_BROWSER_TYPE=selenium
export SPOTIFY_SCRAPER_COOKIE_FILE=/path/to/cookies.txt
export SPOTIFY_SCRAPER_PROXY=http://proxy:8080
```

### Available Settings

- `SPOTIFY_SCRAPER_LOG_LEVEL`: Logging level
- `SPOTIFY_SCRAPER_LOG_FILE`: Log file path
- `SPOTIFY_SCRAPER_BROWSER_TYPE`: Browser backend
- `SPOTIFY_SCRAPER_COOKIE_FILE`: Cookie file path
- `SPOTIFY_SCRAPER_PROXY`: Proxy URL

## Browser Types

### RequestsBrowser (Default)

- Lightweight and fast
- No JavaScript support
- Lower memory usage
- Suitable for most use cases

### SeleniumBrowser

- Full browser automation
- JavaScript support
- Higher memory usage
- Required for some dynamic content

### Auto Mode

When `browser_type="auto"`, the client tries RequestsBrowser first and falls back to SeleniumBrowser if needed.

## Best Practices

1. **Always close the client**: Use `client.close()` or context manager
2. **Handle exceptions**: Wrap calls in try-except blocks
3. **Respect rate limits**: Add delays between requests
4. **Use appropriate browser**: RequestsBrowser for most cases
5. **Cache results**: Avoid repeated requests for same data

## Example: Complete Usage

```python
from spotify_scraper import SpotifyClient, URLError, NetworkError
import time

# Initialize with configuration
client = SpotifyClient(
    browser_type="auto",
    log_level="INFO",
    cookie_file="spotify_cookies.txt"
)

try:
    # Extract various data types
    urls = [
        "https://open.spotify.com/track/...",
        "https://open.spotify.com/album/...",
        "https://open.spotify.com/playlist/..."
    ]
    
    for url in urls:
        try:
            # Auto-detect and extract
            info = client.get_all_info(url)
            print(f"{info['type']}: {info['name']}")
            
            # Download cover
            if 'images' in info and info['images']:
                cover = client.download_cover(url, path="covers/")
                print(f"Cover saved: {cover}")
            
            # Add delay to avoid rate limiting
            time.sleep(1)
            
        except URLError as e:
            print(f"Invalid URL: {e}")
        except NetworkError as e:
            print(f"Network error: {e}")
            
finally:
    # Always clean up
    client.close()
```