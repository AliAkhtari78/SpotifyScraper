# SpotifyClient

The `SpotifyClient` class is the main interface for interacting with Spotify's web player. It provides methods for extracting data from tracks, albums, artists, and playlists, as well as downloading media files.

## Constructor

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

### Parameters

- **cookie_file** (*Optional[str]*): Path to a Netscape-format cookies.txt file containing Spotify authentication cookies. Used for accessing protected content like lyrics.
- **cookies** (*Optional[Dict[str, str]]*): Dictionary of cookies to use instead of cookie_file. Keys should be cookie names, values should be cookie values.
- **headers** (*Optional[Dict[str, str]]*): Custom HTTP headers to include in all requests.
- **proxy** (*Optional[Dict[str, str]]*): Proxy server configuration for all requests.
- **browser_type** (*str*): Backend browser implementation to use:
  - `"requests"`: Lightweight, fast, no JavaScript support (default)
  - `"selenium"`: Full browser, slower, full JavaScript support
  - `"auto"`: Automatically choose based on requirements
- **log_level** (*str*): Logging verbosity level. Options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
- **log_file** (*Optional[str]*): Path to write log messages to. If None, logs to console only.

### Example

```python
from spotify_scraper import SpotifyClient

# Basic client
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

## Methods

### get_track_info

Extract comprehensive metadata for a single track.

```python
get_track_info(url: str) -> Dict[str, Any]
```

#### Parameters

- **url** (*str*): Spotify track URL in any supported format

#### Returns

Dictionary containing track information with the following structure:

```python
{
    "id": str,              # Spotify track ID
    "name": str,            # Track title
    "uri": str,             # Spotify URI (spotify:track:...)
    "type": "track",        # Entity type
    "duration_ms": int,     # Duration in milliseconds
    "explicit": bool,       # Explicit content flag
    "artists": List[Dict],  # List of artist objects
    "album": Dict,          # Album object with images
    "preview_url": str,     # 30-second preview MP3 URL
    "popularity": int,      # Popularity score (0-100)
    "track_number": int,    # Position in album
    "disc_number": int,     # Disc number in album
    "external_urls": Dict,  # External URLs
    "is_playable": bool,    # Playability status
}
```

#### Example

```python
track = client.get_track_info("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
print(f"{track.get('name', 'Unknown')} - {track.get('duration_ms', 0) / 1000:.1f}s")
```

### get_track_lyrics

**Note: This method currently returns None. Spotify's lyrics API requires OAuth Bearer tokens, which are not available through cookie authentication.**

```python
get_track_lyrics(url: str, require_auth: bool = True) -> Optional[str]
```

#### Parameters

- **url** (*str*): Spotify track URL
- **require_auth** (*bool*): Whether to require authentication (currently non-functional)

#### Returns

Always returns None. Lyrics require OAuth authentication through Spotify's official Web API.

#### Example

```python
client = SpotifyClient(cookie_file="spotify_cookies.txt")
lyrics = client.get_track_lyrics("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
# lyrics will always be None - OAuth required
if lyrics:
    print(lyrics)  # This will never execute
```

### get_track_info_with_lyrics

Get track information with an attempt to fetch lyrics (currently non-functional).

**Note: The `lyrics` field will always be None. Spotify's lyrics API requires OAuth Bearer tokens.**

```python
get_track_info_with_lyrics(
    url: str, 
    require_lyrics_auth: bool = True
) -> Dict[str, Any]
```

#### Parameters

- **url** (*str*): Spotify track URL
- **require_lyrics_auth** (*bool*): Whether to require authentication (currently non-functional)

#### Returns

Track info dictionary with additional `lyrics` field (always None).

### get_album_info

Extract comprehensive album information.

```python
get_album_info(url: str) -> Dict[str, Any]
```

#### Parameters

- **url** (*str*): Spotify album URL

#### Returns

Dictionary containing:

```python
{
    "id": str,                    # Spotify album ID
    "name": str,                  # Album name
    "uri": str,                   # Spotify URI
    "type": "album",              # Entity type
    "artists": List[Dict],        # List of artists
    "release_date": str,          # Release date (YYYY-MM-DD)
    "release_date_precision": str,# Date precision
    "label": str,                 # Record label
    "total_tracks": int,          # Number of tracks
    "duration_ms": int,           # Total album duration
    "popularity": int,            # Popularity score
    "images": List[Dict],         # Cover art in various sizes
    "tracks": List[Dict],         # Track listing
    "copyrights": List[Dict],     # Copyright information
    "external_urls": Dict,        # External URLs
}
```

### get_artist_info

Extract comprehensive artist information.

```python
get_artist_info(url: str) -> Dict[str, Any]
```

#### Parameters

- **url** (*str*): Spotify artist URL

#### Returns

Dictionary containing:

```python
{
    "id": str,                    # Spotify artist ID
    "name": str,                  # Artist name
    "uri": str,                   # Spotify URI
    "type": "artist",             # Entity type
    "genres": List[str],          # Associated genres
    "popularity": int,            # Popularity score
    "followers": Dict[str, int],  # Follower count
    "images": List[Dict],         # Artist images
    "top_tracks": List[Dict],     # Popular tracks
    "albums": List[Dict],         # Recent albums
    "singles": List[Dict],        # Recent singles
    "compilations": List[Dict],   # Compilation albums
    "appears_on": List[Dict],     # Albums artist appears on
    "related_artists": List[Dict],# Similar artists
    "bio": str,                   # Artist biography
    "monthly_listeners": int,     # Monthly listener count
    "verified": bool,             # Verified artist status
    "external_urls": Dict,        # External URLs
}
```

### get_playlist_info

Extract comprehensive playlist information.

```python
get_playlist_info(url: str) -> Dict[str, Any]
```

#### Parameters

- **url** (*str*): Spotify playlist URL

#### Returns

Dictionary containing:

```python
{
    "id": str,                    # Spotify playlist ID
    "name": str,                  # Playlist name
    "uri": str,                   # Spotify URI
    "type": "playlist",           # Entity type
    "description": str,           # Playlist description
    "owner": Dict[str, Any],      # Playlist owner information
    "collaborative": bool,        # Is collaborative playlist
    "public": bool,               # Is public playlist
    "followers": Dict[str, int],  # Follower count
    "images": List[Dict],         # Playlist cover images
    "tracks": {                   # Track information
        "total": int,             # Total number of tracks
        "items": List[Dict]       # List of track objects
    },
    "duration_ms": int,           # Total playlist duration
    "snapshot_id": str,           # Playlist version identifier
    "external_urls": Dict,        # External URLs
}
```

### get_all_info

Automatically detect URL type and extract appropriate information.

```python
get_all_info(url: str) -> Dict[str, Any]
```

#### Parameters

- **url** (*str*): Any valid Spotify URL

#### Returns

Appropriate data based on URL type.

### download_cover

Download cover image from any Spotify entity.

```python
download_cover(
    url: str,
    path: Union[str, Path] = "",
    filename: Optional[str] = None,
    quality_preference: Optional[List[str]] = None
) -> Optional[str]
```

#### Parameters

- **url** (*str*): Spotify URL of any supported type
- **path** (*Union[str, Path]*): Directory path where the image should be saved
- **filename** (*Optional[str]*): Custom filename for the image (without extension)
- **quality_preference** (*Optional[List[str]]*): List of size preferences in order

#### Returns

Full path to the downloaded image file, or None if download failed.

### download_preview_mp3

Download 30-second preview MP3 from a track.

```python
download_preview_mp3(
    url: str, 
    path: str = "", 
    with_cover: bool = False
) -> str
```

#### Parameters

- **url** (*str*): Spotify track URL
- **path** (*str*): Directory path where the MP3 should be saved
- **with_cover** (*bool*): Whether to embed the album cover art in the MP3 metadata

#### Returns

Full path to the downloaded MP3 file.

### close

Close the client and release all resources.

```python
close() -> None
```

## Error Handling

SpotifyScraper provides specific exception types for different error scenarios:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.core.exceptions import (
    URLError,
    ScrapingError,
    AuthenticationError,
    MediaError
)

client = SpotifyClient()

try:
    track = client.get_track_info("invalid_url")
except URLError as e:
    print(f"Invalid URL: {e}")
except ScrapingError as e:
    print(f"Extraction failed: {e}")
except AuthenticationError as e:
    print(f"Authentication required: {e}")
except MediaError as e:
    print(f"Media download failed: {e}")
```

## Best Practices

### 1. Resource Management

Always close the client when done:

```python
client = SpotifyClient()
try:
    # Use the client
    track = client.get_track_info(track_url)
finally:
    client.close()
```

### 2. Batch Processing

Reuse the same client instance for multiple requests:

```python
client = SpotifyClient()
urls = [...]  # List of URLs

for url in urls:
    try:
        info = client.get_track_info(url)
        # Process info
    except Exception as e:
        print(f"Failed to process {url}: {e}")
        
client.close()
```

### 3. Rate Limiting

Add delays between requests to avoid rate limiting:

```python
import time

for url in urls:
    info = client.get_track_info(url)
    time.sleep(1)  # Wait 1 second between requests
```

### 4. Authentication

For features requiring authentication (like lyrics), export cookies from your browser:

1. Install a browser extension like "cookies.txt"
2. Log in to Spotify Web Player
3. Export cookies to a file
4. Use with SpotifyClient

```python
client = SpotifyClient(cookie_file="spotify_cookies.txt")
```

## See Also

- [Exceptions](exceptions.md) - Error types and handling
- [Extractors](extractors.md) - Data extraction components
- [Media](media.md) - Media download handlers
- [Utils](utils.md) - Utility functions
- [Examples](../examples/index.md) - Practical examples