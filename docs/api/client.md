# SpotifyClient API Reference

The `SpotifyClient` class is the main interface for interacting with SpotifyScraper. It provides high-level methods for extracting data from Spotify URLs.

## Class: SpotifyClient

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()
```

### Constructor

#### `__init__(cookie_file=None, cookies=None, headers=None, proxy=None, browser_type="requests", log_level="INFO", log_file=None)`

Initialize a new SpotifyClient instance.

**Parameters:**
- `cookie_file` (Optional[str]): Path to a Netscape-format cookies.txt file for authentication
- `cookies` (Optional[Dict[str, str]]): Dictionary of cookies to use instead of cookie_file
- `headers` (Optional[Dict[str, str]]): Custom HTTP headers to include in all requests
- `proxy` (Optional[Dict[str, str]]): Proxy server configuration
- `browser_type` (str): Backend browser implementation ("requests", "selenium", or "auto")
- `log_level` (str): Logging verbosity level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
- `log_file` (Optional[str]): Path to write log messages to

**Example:**
```python
from spotify_scraper import SpotifyClient

# Simple client with default settings
client = SpotifyClient()

# Client with authentication
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Client with custom configuration
client = SpotifyClient(
    browser_type="selenium",
    proxy={"https": "https://proxy.example.com:8080"},
    log_level="DEBUG",
    log_file="scraper.log"
)
```

### Methods

#### `get_track_info(url: str) -> Dict[str, Any]`

Extract track information from a Spotify track URL.

**Parameters:**
- `url` (str): Spotify track URL (regular or embed format)

**Returns:**
- `Dict[str, Any]`: Dictionary containing track information

**Raises:**
- `SpotifyScraperError`: If extraction fails
- `URLError`: If the URL is invalid

**Example:**
```python
# Regular track URL
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track_data = client.get_track_info(track_url)

# Embed track URL
embed_url = "https://open.spotify.com/embed/track/6rqhFgbbKwnb9MLmUQDhG6"
track_data = client.get_track_info(embed_url)

# Access track information
print(f"Track: {track_data['name']}")
print(f"Artist: {track_data['artists'][0]['name']}")
# Note: Album name may be empty due to embed URL limitations
print(f"Album: {track_data.get('album', {}).get('name', 'N/A')}")
print(f"Duration: {track_data['duration_ms']} ms")
print(f"Preview URL: {track_data.get('preview_url')}")
```

**Track Data Structure:**
```python
{
    'id': str,                    # Spotify track ID
    'name': str,                  # Track name
    'uri': str,                   # Spotify URI
    'type': 'track',              # Entity type
    'duration_ms': int,           # Duration in milliseconds
    'artists': [                  # List of artists
        {
            'id': str,
            'name': str,
            'uri': str,
            'type': 'artist'
        }
    ],
    'album': {                    # Album information
        'id': str,
        'name': str,
        'uri': str,
        'type': 'album',
        'images': [               # Album cover images
            {
                'url': str,
                'width': int,
                'height': int
            }
        ],
        'release_date': str,      # Release date
        'total_tracks': int       # Total tracks in album
    },
    'preview_url': str,           # 30-second preview URL (optional)
    'is_playable': bool,          # Whether track is playable
    'is_explicit': bool,          # Explicit content flag
    'track_number': int,          # Position in album
    'disc_number': int,           # Disc number
    'lyrics': {                   # Lyrics (requires auth, optional)
        'sync_type': str,
        'lines': [
            {
                'start_time_ms': int,
                'words': str,
                'end_time_ms': int
            }
        ],
        'provider': str,
        'language': str
    }
}
```

#### `get_album_info(url: str) -> Dict[str, Any]`

Extract album information from a Spotify album URL.

**Parameters:**
- `url` (str): Spotify album URL

**Returns:**
- `Dict[str, Any]`: Dictionary containing album information

**Raises:**
- `SpotifyScraperError`: If extraction fails
- `URLError`: If the URL is invalid

**Example:**
```python
album_url = "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"
album_data = client.get_album_info(album_url)

print(f"Album: {album_data['name']}")
print(f"Artist: {album_data['artists'][0]['name']}")
print(f"Release Date: {album_data.get('release_date', 'N/A')}")
print(f"Total Tracks: {album_data['total_tracks']}")

# List all tracks
for track in album_data['tracks']:
    print(f"  {track['track_number']}. {track['name']}")
```

#### `get_artist_info(url: str) -> Dict[str, Any]`

Extract artist information from a Spotify artist URL.

**Parameters:**
- `url` (str): Spotify artist URL

**Returns:**
- `Dict[str, Any]`: Dictionary containing artist information

**Raises:**
- `SpotifyScraperError`: If extraction fails
- `URLError`: If the URL is invalid

**Example:**
```python
artist_url = "https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb"
artist_data = client.get_artist_info(artist_url)

print(f"Artist: {artist_data['name']}")
print(f"Verified: {artist_data.get('is_verified', False)}")
print(f"Biography: {artist_data.get('bio', 'No biography available')}")

# Top tracks
for track in artist_data.get('top_tracks', []):
    print(f"  - {track['name']}")
```

#### `get_playlist_info(url: str) -> Dict[str, Any]`

Extract playlist information from a Spotify playlist URL.

**Parameters:**
- `url` (str): Spotify playlist URL

**Returns:**
- `Dict[str, Any]`: Dictionary containing playlist information

**Raises:**
- `SpotifyScraperError`: If extraction fails
- `URLError`: If the URL is invalid

**Example:**
```python
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
playlist_data = client.get_playlist_info(playlist_url)

print(f"Playlist: {playlist_data['name']}")
print(f"Owner: {playlist_data['owner']['name']}")
print(f"Description: {playlist_data.get('description', '')}")
print(f"Track Count: {playlist_data['track_count']}")

# List first 10 tracks
for i, track in enumerate(playlist_data['tracks'][:10]):
    print(f"{i+1}. {track['name']} - {track['artists'][0]['name']}")
```

#### `download_preview_mp3(url: str, path: str = "", with_cover: bool = False) -> str`

Download 30-second preview MP3 from a Spotify track.

**Parameters:**
- `url` (str): Spotify track URL
- `path` (str): Directory path where the MP3 should be saved (default: current directory)
- `with_cover` (bool): Whether to embed album cover art in the MP3 metadata

**Returns:**
- `str`: Full path to the downloaded MP3 file

**Raises:**
- `MediaError`: If download fails or no preview is available

**Example:**
```python
# Basic download
mp3_path = client.download_preview_mp3(
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
)
print(f"Downloaded to: {mp3_path}")

# Download with cover art to specific directory
mp3_path = client.download_preview_mp3(
    track_url,
    path="downloads/",
    with_cover=True
)
```

#### `download_cover(url: str, filename: Optional[str] = None, path: str = "", quality_preference: Optional[List[str]] = None) -> str`

Download cover art from any Spotify URL (track, album, playlist, artist).

**Parameters:**
- `url` (str): Spotify URL
- `filename` (Optional[str]): Custom filename (without extension)
- `path` (str): Directory path where the image should be saved
- `quality_preference` (Optional[List[str]]): List of size preferences ["large", "medium", "small"]

**Returns:**
- `str`: Full path to the downloaded image file

**Raises:**
- `MediaError`: If download fails

**Example:**
```python
# Download album cover
cover_path = client.download_cover(
    "https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3"
)

# Download with custom filename and size preference
cover_path = client.download_cover(
    album_url,
    filename="my_album_cover",
    path="covers/",
    quality_preference=["large"]
)
```

#### `get_track_lyrics(url: str, require_auth: bool = True) -> Optional[str]`

Get lyrics for a Spotify track (requires authentication).

**Parameters:**
- `url` (str): Spotify track URL
- `require_auth` (bool): Whether to require authentication

**Returns:**
- `Optional[str]`: Lyrics text or None if not available

**Example:**
```python
lyrics = client.get_track_lyrics(track_url)
if lyrics:
    print(lyrics)
```

#### `close()`

Close the client and release any resources.

**Example:**
```python
client = SpotifyClient(browser_type="selenium")
try:
    # Use the client
    track_data = client.get_track_info(url)
finally:
    # Always close when using Selenium
    client.close()
```

## Authentication

To access additional features like lyrics, you can use cookie-based authentication:

```python
from spotify_scraper import SpotifyClient

# Load cookies from file
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Get track with lyrics (if available)
track_data = client.get_track_info_with_lyrics(track_url)
if track_data.get('lyrics'):
    print(track_data['lyrics'])
```

## Error Handling

```python
from spotify_scraper import (
    SpotifyClient,
    SpotifyScraperError,
    URLError,
    NetworkError,
    ExtractionError
)

client = SpotifyClient()

try:
    track_data = client.get_track_info(url)
except URLError as e:
    print(f"Invalid URL: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except ExtractionError as e:
    print(f"Failed to extract data: {e}")
except SpotifyScraperError as e:
    print(f"General error: {e}")
```

## Performance Tips

1. **Reuse Client Instances**: Create one client and reuse it for multiple requests
2. **Use RequestsBrowser**: Unless you need JavaScript rendering, RequestsBrowser is faster
3. **Batch Operations**: Extract multiple items in sequence using the same client
4. **Handle Rate Limits**: Add delays between requests to avoid rate limiting

```python
import time
from spotify_scraper import SpotifyClient

client = SpotifyClient()

urls = [
    "https://open.spotify.com/track/...",
    "https://open.spotify.com/track/...",
    # ... more URLs
]

results = []
for url in urls:
    try:
        data = client.get_track(url)
        results.append(data)
        time.sleep(0.5)  # Be respectful to Spotify's servers
    except Exception as e:
        print(f"Failed to extract {url}: {e}")
```