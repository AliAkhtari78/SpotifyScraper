# Client Module

The `client` module provides the main `SpotifyClient` class for interacting with Spotify.

## SpotifyClient

```python
from spotify_scraper import SpotifyClient
```

The main client class that orchestrates all Spotify data extraction operations.

### Constructor

```python
SpotifyClient(
    browser_type: str = "requests",
    log_level: str = "INFO",
    cookie_file: Optional[str] = None
)
```

**Parameters:**
- `browser_type` (str): Browser backend to use. Options: "requests" (default) or "selenium"
- `log_level` (str): Logging level. Options: "DEBUG", "INFO" (default), "WARNING", "ERROR"
- `cookie_file` (Optional[str]): Path to cookies file for authenticated features (e.g., lyrics)

**Example:**
```python
from spotify_scraper import SpotifyClient

# Default client with requests backend
client = SpotifyClient()

# Client with Selenium backend for complex pages
client = SpotifyClient(browser_type="selenium")

# Client with authentication for lyrics
client = SpotifyClient(cookie_file="spotify_cookies.txt")
```

### Methods

#### get_track_info

```python
get_track_info(track_id_or_url: str) -> Dict[str, Any]
```

Extract track information from Spotify.

**Parameters:**
- `track_id_or_url` (str): Spotify track ID or URL (including embed URLs)

**Returns:**
- Dict containing track metadata

**Example:**
```python
track = client.get_track_info("4iV5W9uYEdYUVa79Axb7Rh")
track = client.get_track_info("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
track = client.get_track_info("https://open.spotify.com/embed/track/4iV5W9uYEdYUVa79Axb7Rh")
```

#### get_album_info

```python
get_album_info(album_id_or_url: str) -> Dict[str, Any]
```

Extract album information including all tracks.

**Parameters:**
- `album_id_or_url` (str): Spotify album ID or URL

**Returns:**
- Dict containing album metadata and track list

**Example:**
```python
album = client.get_album_info("4aawyAB9vmqN3uQ7FjRGTy")
album = client.get_album_info("https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy")
print(f"Album: {album['name']} by {album['artists'][0]['name']}")
print(f"Tracks: {len(album['tracks'])}")
```

#### get_artist_info

```python
get_artist_info(artist_id_or_url: str) -> Dict[str, Any]
```

Extract artist information.

**Parameters:**
- `artist_id_or_url` (str): Spotify artist ID or URL

**Returns:**
- Dict containing artist metadata

**Example:**
```python
artist = client.get_artist_info("0OdUWJ0sBjDrqHygGUXeCF")
artist = client.get_artist_info("https://open.spotify.com/artist/0OdUWJ0sBjDrqHygGUXeCF")
print(f"Artist: {artist['name']}")
print(f"Genres: {', '.join(artist.get('genres', []))}")
```#### get_playlist_info

```python
get_playlist_info(playlist_id_or_url: str) -> Dict[str, Any]
```

Extract playlist information including all tracks.

**Parameters:**
- `playlist_id_or_url` (str): Spotify playlist ID or URL

**Returns:**
- Dict containing playlist metadata and track list

**Example:**
```python
playlist = client.get_playlist_info("37i9dQZF1DXcBWIGoYBM5M")
playlist = client.get_playlist_info("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
print(f"Playlist: {playlist['name']}")
print(f"Owner: {playlist['owner']['display_name']}")
print(f"Tracks: {playlist['track_count']}")
```

### Additional Methods

#### get_track_info_with_lyrics

```python
get_track_info_with_lyrics(track_id_or_url: str) -> Dict[str, Any]
```

Extract track information including lyrics (requires authentication).

**Parameters:**
- `track_id_or_url` (str): Spotify track ID or URL

**Returns:**
- Dict containing track metadata with lyrics field

**Example:**
```python
client = SpotifyClient(cookie_file="spotify_cookies.txt")
track = client.get_track_info_with_lyrics("4iV5W9uYEdYUVa79Axb7Rh")
if track.get('lyrics'):
    print(track['lyrics'])
```

#### get_track_lyrics

```python
get_track_lyrics(track_id_or_url: str) -> Optional[str]
```

Extract only the lyrics for a track (requires authentication).

**Parameters:**
- `track_id_or_url` (str): Spotify track ID or URL

**Returns:**
- Lyrics text or None if not available

#### download_preview_mp3

```python
download_preview_mp3(
    track_id_or_url: str,
    output_dir: str = ".",
    filename: Optional[str] = None
) -> str
```

Download 30-second preview MP3.

**Parameters:**
- `track_id_or_url` (str): Spotify track ID or URL
- `output_dir` (str): Directory to save the file
- `filename` (Optional[str]): Custom filename (defaults to track name)

**Returns:**
- Path to downloaded file

#### download_cover

```python
download_cover(
    resource_id_or_url: str,
    output_dir: str = ".",
    size: str = "large",
    filename: Optional[str] = None
) -> str
```

Download cover art image.

**Parameters:**
- `resource_id_or_url` (str): Spotify resource ID or URL
- `output_dir` (str): Directory to save the file
- `size` (str): Image size - "small", "medium", or "large"
- `filename` (Optional[str]): Custom filename

**Returns:**
- Path to downloaded file

#### get_all_info

```python
get_all_info(spotify_url: str) -> Dict[str, Any]
```

Automatically detect resource type and extract information.

**Parameters:**
- `spotify_url` (str): Any Spotify URL

**Returns:**
- Appropriate data based on URL type

#### close

```python
close() -> None
```

Clean up resources (required when using Selenium backend).### Error Handling

```python
from spotify_scraper import (
    SpotifyClient,
    SpotifyScraperError,
    URLError,
    NetworkError,
    ExtractionError,
    AuthenticationError,
    MediaError
)

client = SpotifyClient()

try:
    track = client.get_track_info("invalid_id")
except URLError as e:
    print(f"Invalid URL: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
except SpotifyScraperError as e:
    print(f"General error: {e}")
```

### Batch Processing

```python
# Process multiple items efficiently
track_urls = [
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
    "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b",
    "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
]

client = SpotifyClient()
tracks = []

for url in track_urls:
    try:
        track = client.get_track_info(url)
        tracks.append(track)
    except Exception as e:
        print(f"Failed to get track {url}: {e}")

# Always close when using Selenium
if client.browser_type == "selenium":
    client.close()
```

### Performance Tips

1. **Enable caching** for repeated requests
2. **Use connection pooling** by reusing the same client instance
3. **Handle rate limiting** with appropriate delays

## Utility Classes

### SpotifyBulkOperations

```python
from spotify_scraper.utils import SpotifyBulkOperations

bulk = SpotifyBulkOperations(client)

# Get multiple tracks
tracks = bulk.get_multiple_tracks(track_urls)

# Get artist discography  
discography = bulk.get_artist_discography(artist_url)

# Get full playlist (handles pagination)
full_playlist = bulk.get_full_playlist(playlist_url)
```

### SpotifyDataAnalyzer

```python
from spotify_scraper.utils import SpotifyDataAnalyzer

analyzer = SpotifyDataAnalyzer()

# Analyze playlist
stats = analyzer.analyze_playlist(playlist_data)

# Get genre distribution
genres = analyzer.get_genre_distribution(tracks)

# Calculate audio features
features = analyzer.calculate_audio_features(tracks)
```

## See Also

- [Extractors](extractors.md) - Data extraction components
- [Exceptions](exceptions.md) - Error handling
- [Media](media.md) - Media download handlers
- [Utils](utils.md) - Utility functions
- [Examples](../examples/index.md) - Practical examples