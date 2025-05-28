# API Reference

Comprehensive reference for all SpotifyScraper classes and methods.

## Table of Contents

- [SpotifyClient](#spotifyclient)
- [Configuration](#configuration)
- [Bulk Operations](#bulk-operations)
- [Data Models](#data-models)
- [Exceptions](#exceptions)
- [Utility Functions](#utility-functions)

## SpotifyClient

The main interface for interacting with Spotify's web player.

### Initialization

```python
from spotify_scraper import SpotifyClient

# Basic initialization
client = SpotifyClient()

# With custom configuration
from spotify_scraper.core.config import Config

config = Config(
    browser_type="selenium",
    headless=True,
    timeout=30
)
client = SpotifyClient(config=config)

# With authentication
client = SpotifyClient(cookie_file="cookies.txt")
```

### Methods

#### `get_track_info(url: str) -> Dict[str, Any]`

Extract track metadata.

```python
track = client.get_track_info("https://open.spotify.com/track/...")

# Returns:
{
    "id": "track_id",
    "name": "Track Name",
    "artists": [{"name": "Artist", "id": "artist_id"}],
    "album": {"name": "Album", "id": "album_id"},
    "duration_ms": 240000,
    "popularity": 75,
    "preview_url": "https://...",
    "explicit": False
}
```

#### `get_album_info(url: str) -> Dict[str, Any]`

Extract album metadata with all tracks.

```python
album = client.get_album_info("https://open.spotify.com/album/...")

# Returns:
{
    "id": "album_id",
    "name": "Album Name",
    "artists": [{"name": "Artist", "id": "artist_id"}],
    "release_date": "2023-01-01",
    "total_tracks": 12,
    "tracks": {"items": [...]},
    "images": [{"url": "...", "height": 640, "width": 640}]
}
```

#### `get_artist_info(url: str) -> Dict[str, Any]`

Extract artist metadata.

```python
artist = client.get_artist_info("https://open.spotify.com/artist/...")

# Returns:
{
    "id": "artist_id",
    "name": "Artist Name",
    "genres": ["genre1", "genre2"],
    "followers": {"total": 1000000},
    "popularity": 80,
    "images": [{"url": "...", "height": 640, "width": 640}],
    "top_tracks": [...]
}
```

#### `get_playlist_info(url: str) -> Dict[str, Any]`

Extract playlist metadata with all tracks.

```python
playlist = client.get_playlist_info("https://open.spotify.com/playlist/...")

# Returns:
{
    "id": "playlist_id",
    "name": "Playlist Name",
    "owner": {"display_name": "Owner Name"},
    "tracks": {"total": 50, "items": [...]},
    "public": True,
    "collaborative": False,
    "description": "Playlist description"
}
```

#### `download_preview_mp3(url: str, output_dir: str = ".") -> Optional[str]`

Download 30-second preview clip.

```python
# Download with automatic naming
path = client.download_preview_mp3(track_url)

# Download to specific directory
path = client.download_preview_mp3(track_url, output_dir="previews/")

# Download with custom filename
path = client.download_preview_mp3(
    track_url, 
    output_dir="previews/",
    filename="my_track"
)
```

#### `download_cover(url: str, output_dir: str = ".") -> Optional[str]`

Download album cover art.

```python
# Download cover
path = client.download_cover(track_url, output_dir="covers/")

# Specify image size preference
path = client.download_cover(
    track_url,
    output_dir="covers/",
    size_preference="large"  # "small", "medium", "large"
)
```

#### `get_track_lyrics(url: str) -> Optional[str]`

Get track lyrics (requires authentication).

```python
# Requires cookie authentication
client = SpotifyClient(cookie_file="cookies.txt")
lyrics = client.get_track_lyrics(track_url)
```

## Configuration

### Config Class

```python
from spotify_scraper.core.config import Config

config = Config(
    # Browser settings
    browser_type="requests",  # "requests" or "selenium"
    headless=True,           # For Selenium only
    
    # Request settings
    timeout=20,              # Request timeout in seconds
    max_retries=3,           # Number of retry attempts
    retry_delay=1.0,         # Delay between retries
    
    # User agent
    user_agent="custom-agent",  # Custom user agent string
    
    # Proxy settings
    proxy="http://proxy:8080",  # Proxy URL
    
    # Cookie file
    cookie_file="cookies.txt"   # Path to Netscape cookie file
)
```

## Bulk Operations

### SpotifyBulkOperations Class

```python
from spotify_scraper.utils.common import SpotifyBulkOperations

bulk = SpotifyBulkOperations(client=None)  # Creates new client if None
```

#### `process_urls(urls: List[str], operation: str = "info") -> Dict[str, Any]`

Process multiple URLs efficiently.

```python
urls = [
    "https://open.spotify.com/track/...",
    "https://open.spotify.com/album/...",
    "https://open.spotify.com/playlist/..."
]

# Get information
results = bulk.process_urls(urls, operation="info")

# Download media
results = bulk.process_urls(urls, operation="download", output_dir="media/")

# Both info and downloads
results = bulk.process_urls(urls, operation="both", output_dir="output/")
```

#### `export_to_json(data: Dict, output_file: str) -> Path`

Export results to JSON.

```python
path = bulk.export_to_json(results, "output.json")
```

#### `export_to_csv(data: Dict, output_file: str) -> Path`

Export results to CSV.

```python
path = bulk.export_to_csv(results, "output.csv")
```

#### `batch_download(urls: List[str], output_dir: str) -> Dict[str, Any]`

Batch download media files.

```python
results = bulk.batch_download(
    urls,
    output_dir="downloads/",
    media_types=["audio", "cover"],
    skip_errors=True
)
```

## Data Models

### Track Data

```python
TrackData = {
    "id": str,
    "name": str,
    "uri": str,
    "duration_ms": int,
    "popularity": int,
    "preview_url": Optional[str],
    "explicit": bool,
    "is_playable": bool,
    "artists": List[ArtistData],
    "album": AlbumData,
    "lyrics": Optional[str]  # If requested
}
```

### Album Data

```python
AlbumData = {
    "id": str,
    "name": str,
    "uri": str,
    "release_date": str,
    "total_tracks": int,
    "album_type": str,
    "artists": List[ArtistData],
    "images": List[ImageData],
    "tracks": {"items": List[TrackData]}
}
```

### Artist Data

```python
ArtistData = {
    "id": str,
    "name": str,
    "uri": str,
    "genres": List[str],
    "popularity": int,
    "followers": {"total": int},
    "images": List[ImageData],
    "top_tracks": List[TrackData]  # If available
}
```

### Playlist Data

```python
PlaylistData = {
    "id": str,
    "name": str,
    "uri": str,
    "public": bool,
    "collaborative": bool,
    "description": str,
    "owner": {"display_name": str},
    "followers": {"total": int},
    "images": List[ImageData],
    "tracks": {
        "total": int,
        "items": List[{"track": TrackData}]
    }
}
```

## Exceptions

All exceptions inherit from `SpotifyScraperError`.

```python
from spotify_scraper.core.exceptions import (
    SpotifyScraperError,    # Base exception
    URLError,               # Invalid URL format
    NetworkError,           # Network/connection issues
    ParsingError,           # HTML/JSON parsing failed
    ExtractionError,        # Data extraction failed
    AuthenticationError,    # Cookie/auth issues
    BrowserError,           # Browser-specific errors
    MediaError,             # Download failures
    ConfigurationError      # Invalid configuration
)
```

### Exception Handling

```python
try:
    track = client.get_track_info(url)
except URLError as e:
    print(f"Invalid URL: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except SpotifyScraperError as e:
    print(f"General error: {e}")
```

## Utility Functions

### URL Utilities

```python
from spotify_scraper.utils.url import (
    is_spotify_url,
    extract_id,
    get_url_type,
    convert_to_embed_url
)

# Validate URL
if is_spotify_url(url):
    # Extract ID
    item_id = extract_id(url)
    
    # Get type
    url_type = get_url_type(url)  # "track", "album", etc.
    
    # Convert to embed URL
    embed_url = convert_to_embed_url(url)
```

### Data Analysis

```python
from spotify_scraper.utils.common import SpotifyDataAnalyzer

analyzer = SpotifyDataAnalyzer()

# Analyze playlist
analysis = analyzer.analyze_playlist(playlist_data)

# Compare playlists
comparison = analyzer.compare_playlists(playlist1, playlist2)
```

### Data Formatting

```python
from spotify_scraper.utils.common import SpotifyDataFormatter

formatter = SpotifyDataFormatter()

# Format as text
summary = formatter.format_track_summary(track_data)

# Format as markdown
markdown = formatter.format_playlist_markdown(playlist_data)

# Export to M3U
formatter.export_to_m3u(tracks, "playlist.m3u")
```

## Advanced Usage

### Custom Headers

```python
config = Config()
config.headers = {
    "Accept-Language": "en-US,en;q=0.9",
    "Custom-Header": "value"
}
client = SpotifyClient(config=config)
```

### Session Management

```python
# Reuse session across requests
client = SpotifyClient()

# Process multiple items
for url in urls:
    data = client.get_track_info(url)
    # Session is reused

# Always close when done
client.close()
```

### Context Manager

```python
from spotify_scraper import SpotifyClient

# Automatic cleanup with context manager
with SpotifyClient() as client:
    track = client.get_track_info(url)
    # Client closes automatically
```

## Performance Tips

1. **Reuse clients** - Create once, use multiple times
2. **Use bulk operations** - Process multiple URLs together
3. **Enable caching** - Avoid redundant requests
4. **Choose appropriate browser** - Use requests when possible
5. **Handle errors gracefully** - Implement retry logic

## See Also

- [Examples](Examples.md) - More code examples
- [FAQ](FAQ.md) - Common questions
- [GitHub Repository](https://github.com/AliAkhtari78/SpotifyScraper)