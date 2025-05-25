# API Reference

Complete reference for the SpotifyScraper API.

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

- **cookie_file** (*str, optional*): Path to cookies.txt file for authentication
- **cookies** (*dict, optional*): Cookie dictionary for authentication
- **headers** (*dict, optional*): Custom HTTP headers
- **proxy** (*dict, optional*): Proxy configuration
- **browser_type** (*str*): Browser backend - "requests", "selenium", or "auto"
- **log_level** (*str*): Logging level - "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
- **log_file** (*str, optional*): Path to log file

#### Example

```python
# Basic client
client = SpotifyClient()

# With authentication
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# With custom configuration
client = SpotifyClient(
    browser_type="selenium",
    proxy={"https": "https://proxy.example.com:8080"},
    log_level="DEBUG"
)
```

### Methods

#### get_track_info

Extract information from a Spotify track URL.

```python
get_track_info(url: str) -> Dict[str, Any]
```

**Parameters:**
- **url** (*str*): Spotify track URL

**Returns:** Dictionary containing:
- `id`: Spotify track ID
- `name`: Track title
- `artists`: List of artist objects
- `album`: Album object with images
- `duration_ms`: Duration in milliseconds
- `explicit`: Explicit content flag
- `preview_url`: 30-second preview URL
- `popularity`: Popularity score (0-100)

**Example:**
```python
track = client.get_track_info("https://open.spotify.com/track/...")
print(f"{track['name']} - {track['duration_ms'] / 1000:.1f}s")
```

#### get_track_lyrics

Get lyrics for a Spotify track (requires authentication).

```python
get_track_lyrics(url: str, require_auth: bool = True) -> Optional[str]
```

**Parameters:**
- **url** (*str*): Spotify track URL
- **require_auth** (*bool*): Whether to require authentication

**Returns:** Lyrics text or None if unavailable

**Example:**
```python
lyrics = client.get_track_lyrics(track_url)
if lyrics:
    print(lyrics)
```

#### get_track_info_with_lyrics

Get track information and lyrics in one call.

```python
get_track_info_with_lyrics(
    url: str, 
    require_lyrics_auth: bool = True
) -> Dict[str, Any]
```

**Parameters:**
- **url** (*str*): Spotify track URL
- **require_lyrics_auth** (*bool*): Whether to require auth for lyrics

**Returns:** Track info dictionary with additional `lyrics` field

#### get_album_info

Extract information from a Spotify album URL.

```python
get_album_info(url: str) -> Dict[str, Any]
```

**Parameters:**
- **url** (*str*): Spotify album URL

**Returns:** Dictionary containing:
- `id`: Spotify album ID
- `name`: Album name
- `artists`: List of artist objects
- `release_date`: Release date (YYYY-MM-DD)
- `total_tracks`: Number of tracks
- `tracks`: Track listing
- `images`: Cover art in various sizes
- `label`: Record label

**Example:**
```python
album = client.get_album_info("https://open.spotify.com/album/...")
print(f"{album['name']} ({album['total_tracks']} tracks)")
```

#### get_artist_info

Extract information from a Spotify artist URL.

```python
get_artist_info(url: str) -> Dict[str, Any]
```

**Parameters:**
- **url** (*str*): Spotify artist URL

**Returns:** Dictionary containing:
- `id`: Spotify artist ID
- `name`: Artist name
- `genres`: List of genres
- `popularity`: Popularity score
- `followers`: Follower count
- `images`: Artist images
- `top_tracks`: Popular tracks
- `related_artists`: Similar artists

**Example:**
```python
artist = client.get_artist_info("https://open.spotify.com/artist/...")
print(f"{artist['name']} - {artist['followers']['total']:,} followers")
```

#### get_playlist_info

Extract information from a Spotify playlist URL.

```python
get_playlist_info(url: str) -> Dict[str, Any]
```

**Parameters:**
- **url** (*str*): Spotify playlist URL

**Returns:** Dictionary containing:
- `id`: Spotify playlist ID
- `name`: Playlist name
- `description`: Playlist description
- `owner`: Owner information
- `tracks`: Track listing with total count
- `public`: Public status
- `collaborative`: Collaborative status

**Example:**
```python
playlist = client.get_playlist_info("https://open.spotify.com/playlist/...")
print(f"{playlist['name']} by {playlist['owner']['display_name']}")
```

#### get_all_info

Automatically detect URL type and extract information.

```python
get_all_info(url: str) -> Dict[str, Any]
```

**Parameters:**
- **url** (*str*): Any Spotify URL

**Returns:** Appropriate data based on URL type

**Example:**
```python
# Works with any URL type
info = client.get_all_info(spotify_url)
print(f"{info['type']}: {info['name']}")
```

#### download_cover

Download cover image from any Spotify entity.

```python
download_cover(
    url: str,
    path: Union[str, Path] = "",
    filename: Optional[str] = None,
    quality_preference: Optional[List[str]] = None
) -> Optional[str]
```

**Parameters:**
- **url** (*str*): Spotify URL
- **path** (*str/Path*): Directory to save image
- **filename** (*str, optional*): Custom filename (without extension)
- **quality_preference** (*list, optional*): Size preferences ["large", "medium", "small"]

**Returns:** Path to downloaded file or None

**Example:**
```python
cover_path = client.download_cover(
    album_url,
    path="covers/",
    filename="album_cover"
)
```

#### download_preview_mp3

Download 30-second preview MP3 from a track.

```python
download_preview_mp3(
    url: str, 
    path: str = "", 
    with_cover: bool = False
) -> str
```

**Parameters:**
- **url** (*str*): Spotify track URL
- **path** (*str*): Directory to save MP3
- **with_cover** (*bool*): Embed cover art in MP3

**Returns:** Path to downloaded MP3 file

**Example:**
```python
mp3_path = client.download_preview_mp3(
    track_url,
    path="previews/",
    with_cover=True
)
```

#### close

Close the client and release resources.

```python
close() -> None
```

**Example:**
```python
client.close()
```

## Utility Functions

### URL Validation and Parsing

```python
from spotify_scraper import is_spotify_url, extract_id, get_url_type

# Check if URL is valid
is_spotify_url("https://open.spotify.com/track/...")  # True

# Extract Spotify ID
extract_id("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")  # "6rqhFgbbKwnb9MLmUQDhG6"

# Get URL type
get_url_type("https://open.spotify.com/album/...")  # "album"
```

## Exceptions

### URLError

Raised when an invalid Spotify URL is provided.

```python
from spotify_scraper.core.exceptions import URLError

try:
    client.get_track_info("invalid_url")
except URLError as e:
    print(f"Invalid URL: {e}")
```

### ScrapingError

Raised when data extraction fails.

```python
from spotify_scraper.core.exceptions import ScrapingError

try:
    client.get_track_info(url)
except ScrapingError as e:
    print(f"Extraction failed: {e}")
```

### AuthenticationError

Raised when authentication is required but not provided.

```python
from spotify_scraper.core.exceptions import AuthenticationError

try:
    client.get_track_lyrics(url)
except AuthenticationError as e:
    print(f"Authentication required: {e}")
```

### MediaError

Raised when media download fails.

```python
from spotify_scraper.core.exceptions import MediaError

try:
    client.download_preview_mp3(url)
except MediaError as e:
    print(f"Download failed: {e}")
```

## Authentication

### Getting Spotify Cookies

1. Install a browser extension like "cookies.txt"
2. Log in to Spotify Web Player
3. Export cookies to a file
4. Use with SpotifyClient:

```python
client = SpotifyClient(cookie_file="spotify_cookies.txt")
```

### Cookie Format

The cookies.txt file should be in Netscape format:
```
# Netscape HTTP Cookie File
.spotify.com    TRUE    /    TRUE    1234567890    sp_t    auth_token_value
```

## Browser Backends

### requests (Default)

- Lightweight and fast
- No JavaScript support
- Suitable for most use cases

```python
client = SpotifyClient(browser_type="requests")
```

### selenium

- Full browser with JavaScript support
- Slower but more reliable for dynamic content
- Requires WebDriver installation

```python
client = SpotifyClient(browser_type="selenium")
```

### auto

- Automatically selects appropriate backend
- Starts with requests, falls back to selenium if needed

```python
client = SpotifyClient(browser_type="auto")
```

## Response Format

### Common Fields

All entity types include:
- `id`: Spotify ID
- `name`: Entity name
- `type`: Entity type (track, album, artist, playlist)
- `uri`: Spotify URI
- `external_urls`: External URLs including Spotify

### Track Object

```json
{
    "id": "6rqhFgbbKwnb9MLmUQDhG6",
    "name": "Bohemian Rhapsody",
    "artists": [
        {
            "id": "1dfeR4HaWDbWqFHLkxsg1d",
            "name": "Queen"
        }
    ],
    "album": {
        "id": "4LH4d3cOWNNsVw41Gqt2kv",
        "name": "A Night at the Opera",
        "images": [...]
    },
    "duration_ms": 354947,
    "preview_url": "https://p.scdn.co/mp3-preview/...",
    "explicit": false,
    "popularity": 89
}
```

### Album Object

```json
{
    "id": "4LH4d3cOWNNsVw41Gqt2kv",
    "name": "A Night at the Opera",
    "artists": [...],
    "release_date": "1975-11-21",
    "total_tracks": 12,
    "tracks": {
        "items": [...]
    },
    "images": [...],
    "label": "EMI"
}
```

## Rate Limiting

SpotifyScraper doesn't enforce rate limits, but be considerate:

```python
import time

urls = [...]  # List of URLs
for url in urls:
    info = client.get_track_info(url)
    time.sleep(1)  # Add delay between requests
```

## Logging

Configure logging for debugging:

```python
# Set log level
client = SpotifyClient(log_level="DEBUG")

# Log to file
client = SpotifyClient(
    log_level="INFO",
    log_file="spotify_scraper.log"
)

# Custom logging
import logging
logging.getLogger("spotify_scraper").setLevel(logging.DEBUG)
```