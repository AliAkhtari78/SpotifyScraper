# Client Module

The `client` module provides the main `SpotifyClient` class for interacting with Spotify.

## SpotifyClient

```python
from spotify_scraper import SpotifyClient
```

The main client class that orchestrates all Spotify data extraction operations.

### Constructor

```python
SpotifyClient(config: Optional[Config] = None)
```

**Parameters:**
- `config` (Optional[Config]): Configuration object. If not provided, uses default configuration.

**Example:**
```python
from spotify_scraper import SpotifyClient, Config

# Default client
client = SpotifyClient()

# Client with custom config
config = Config(cache_enabled=True, request_timeout=60)
client = SpotifyClient(config)
```

### Methods

#### get_track

```python
get_track(track_id_or_url: str) -> Dict[str, Any]
```

Extract track information from Spotify.

**Parameters:**
- `track_id_or_url` (str): Spotify track ID or URL (including embed URLs)

**Returns:**
- Dict containing track metadata**Example:**
```python
track = client.get_track("4iV5W9uYEdYUVa79Axb7Rh")
track = client.get_track("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
```

#### get_album

```python
get_album(album_id_or_url: str) -> Dict[str, Any]
```

Extract album information including all tracks.

**Parameters:**
- `album_id_or_url` (str): Spotify album ID or URL

**Returns:**
- Dict containing album metadata and track list

**Example:**
```python
album = client.get_album("4aawyAB9vmqN3uQ7FjRGTy")
print(f"Album: {album['name']} by {album['artists'][0]['name']}")
print(f"Tracks: {len(album['tracks'])}")
```

#### get_artist

```python
get_artist(artist_id_or_url: str) -> Dict[str, Any]
```

Extract artist information.

**Parameters:**
- `artist_id_or_url` (str): Spotify artist ID or URL

**Returns:**
- Dict containing artist metadata

**Example:**
```python
artist = client.get_artist("0OdUWJ0sBjDrqHygGUXeCF")
print(f"Artist: {artist['name']}")
print(f"Genres: {', '.join(artist['genres'])}")
```#### get_playlist

```python
get_playlist(playlist_id_or_url: str) -> Dict[str, Any]
```

Extract playlist information including all tracks.

**Parameters:**
- `playlist_id_or_url` (str): Spotify playlist ID or URL

**Returns:**
- Dict containing playlist metadata and track list

**Example:**
```python
playlist = client.get_playlist("37i9dQZF1DXcBWIGoYBM5M")
print(f"Playlist: {playlist['name']}")
print(f"Owner: {playlist['owner']['name']}")
print(f"Tracks: {playlist['total_tracks']}")
```

### Advanced Usage

#### Error Handling

```python
from spotify_scraper import SpotifyClient, SpotifyScraperError

client = SpotifyClient()

try:
    track = client.get_track("invalid_id")
except SpotifyScraperError as e:
    print(f"Error: {e}")
```

#### Batch Processing

```python
# Process multiple items efficiently
track_ids = ["id1", "id2", "id3"]
tracks = []

for track_id in track_ids:
    try:
        track = client.get_track(track_id)
        tracks.append(track)
    except Exception as e:
        print(f"Failed to get track {track_id}: {e}")
```#### Custom Configuration

```python
from spotify_scraper import SpotifyClient, Config

# Configure for production use
config = Config(
    cache_enabled=True,
    cache_ttl=7200,  # 2 hours
    request_timeout=30,
    max_retries=5,
    retry_delay=1.0,
    use_selenium=False,
    log_level="WARNING"
)

client = SpotifyClient(config)
```

### Performance Tips

1. **Enable caching** for repeated requests
2. **Use connection pooling** by reusing the same client instance
3. **Handle rate limiting** with appropriate delays

## See Also

- [Config](config.md) - Configuration options
- [Extractors](extractors.md) - Data extraction components
- [Exceptions](exceptions.md) - Error handling
- [Examples](../examples/index.md) - Practical examples