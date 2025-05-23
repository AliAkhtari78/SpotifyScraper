# SpotifyClient API Reference

The `SpotifyClient` class is the main interface for interacting with SpotifyScraper. It provides high-level methods for extracting data from Spotify URLs.

## Class: SpotifyClient

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser

browser = RequestsBrowser()
client = SpotifyClient(browser=browser)
```

### Constructor

#### `__init__(browser: Optional[Browser] = None)`

Initialize a new SpotifyClient instance.

**Parameters:**
- `browser` (Optional[Browser]): Browser instance to use for web requests. If None, a default RequestsBrowser will be created.

**Example:**
```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser, SeleniumBrowser

# Using RequestsBrowser (lightweight, fast)
browser = RequestsBrowser()
client = SpotifyClient(browser=browser)

# Using SeleniumBrowser (for complex scenarios)
selenium_browser = SeleniumBrowser()
client = SpotifyClient(browser=selenium_browser)

# Using default browser
client = SpotifyClient()
```

### Methods

#### `get_track(url: str) -> TrackData`

Extract track information from a Spotify track URL.

**Parameters:**
- `url` (str): Spotify track URL (regular or embed format)

**Returns:**
- `TrackData`: Dictionary containing track information

**Raises:**
- `SpotifyScraperError`: If extraction fails
- `URLError`: If the URL is invalid

**Example:**
```python
# Regular track URL
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track_data = client.get_track(track_url)

# Embed track URL
embed_url = "https://open.spotify.com/embed/track/6rqhFgbbKwnb9MLmUQDhG6"
track_data = client.get_track(embed_url)

# Access track information
print(f"Track: {track_data['name']}")
print(f"Artist: {track_data['artists'][0]['name']}")
print(f"Album: {track_data['album']['name']}")
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

#### `get_album(url: str) -> AlbumData`

Extract album information from a Spotify album URL.

**Parameters:**
- `url` (str): Spotify album URL

**Returns:**
- `AlbumData`: Dictionary containing album information

**Raises:**
- `SpotifyScraperError`: If extraction fails
- `URLError`: If the URL is invalid

**Example:**
```python
album_url = "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"
album_data = client.get_album(album_url)

print(f"Album: {album_data['name']}")
print(f"Artist: {album_data['artists'][0]['name']}")
print(f"Release Date: {album_data['release_date']}")
print(f"Total Tracks: {album_data['total_tracks']}")

# List all tracks
for track in album_data['tracks']:
    print(f"  {track['track_number']}. {track['name']}")
```

#### `get_artist(url: str) -> ArtistData`

Extract artist information from a Spotify artist URL.

**Parameters:**
- `url` (str): Spotify artist URL

**Returns:**
- `ArtistData`: Dictionary containing artist information

**Raises:**
- `SpotifyScraperError`: If extraction fails
- `URLError`: If the URL is invalid

**Example:**
```python
artist_url = "https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb"
artist_data = client.get_artist(artist_url)

print(f"Artist: {artist_data['name']}")
print(f"Verified: {artist_data.get('is_verified', False)}")
print(f"Biography: {artist_data.get('bio', 'No biography available')}")

# Top tracks
for track in artist_data.get('top_tracks', []):
    print(f"  - {track['name']}")
```

#### `get_playlist(url: str) -> PlaylistData`

Extract playlist information from a Spotify playlist URL.

**Parameters:**
- `url` (str): Spotify playlist URL

**Returns:**
- `PlaylistData`: Dictionary containing playlist information

**Raises:**
- `SpotifyScraperError`: If extraction fails
- `URLError`: If the URL is invalid

**Example:**
```python
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
playlist_data = client.get_playlist(playlist_url)

print(f"Playlist: {playlist_data['name']}")
print(f"Owner: {playlist_data['owner']['name']}")
print(f"Description: {playlist_data.get('description', '')}")
print(f"Track Count: {playlist_data['track_count']}")

# List first 10 tracks
for i, track in enumerate(playlist_data['tracks'][:10]):
    print(f"{i+1}. {track['name']} - {track['artists'][0]['name']}")
```

#### `close()`

Close the client and release any resources.

**Example:**
```python
client = SpotifyClient(browser=SeleniumBrowser())
try:
    # Use the client
    track_data = client.get_track(url)
finally:
    # Always close when using Selenium
    client.close()
```

## Context Manager Support

SpotifyClient can be used as a context manager for automatic resource cleanup:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import SeleniumBrowser

with SpotifyClient(browser=SeleniumBrowser()) as client:
    track_data = client.get_track(track_url)
    album_data = client.get_album(album_url)
    # Client automatically closes when exiting the context
```

## Authentication

To access additional features like lyrics, you can use cookie-based authentication:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser

# Load cookies from file
browser = RequestsBrowser(cookie_file="spotify_cookies.txt")
client = SpotifyClient(browser=browser)

# Now lyrics will be included in track data
track_data = client.get_track(track_url)
if 'lyrics' in track_data:
    for line in track_data['lyrics']['lines']:
        print(f"{line['start_time_ms']}: {line['words']}")
```

## Error Handling

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.core.exceptions import (
    SpotifyScraperError,
    URLError,
    NetworkError,
    ExtractionError
)

client = SpotifyClient()

try:
    track_data = client.get_track(url)
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