# Quick Start Guide

Get up and running with SpotifyScraper in just a few minutes!

## Installation

```bash
pip install spotifyscraper
```

## Basic Usage

### 1. Import and Initialize

```python
from spotify_scraper import SpotifyClient

# Create a client instance
client = SpotifyClient()
```

### 2. Extract Track Information

```python
# Get track info
track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
track_info = client.get_track_info(track_url)

print(f"Track: {track_info['name']}")
print(f"Artist: {track_info['artists'][0]['name']}")
print(f"Duration: {track_info['duration_ms']} ms")
```

### 3. Extract Album Information

```python
# Get album info
album_url = "https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp"
album_info = client.get_album_info(album_url)

print(f"Album: {album_info['name']}")
print(f"Total Tracks: {album_info['total_tracks']}")
```

### 4. Extract Playlist Information

```python
# Get playlist info
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
playlist_info = client.get_playlist_info(playlist_url)

print(f"Playlist: {playlist_info['name']}")
print(f"Total Tracks: {playlist_info['track_count']}")
```

### 5. Download Media

```python
# Download cover image
cover_path = client.download_cover(track_url, path="covers/")
print(f"Cover saved to: {cover_path}")

# Download track preview (30 seconds)
preview_path = client.download_preview_mp3(track_url, path="previews/")
print(f"Preview saved to: {preview_path}")
```

### 6. Clean Up

```python
# Always close the client when done
client.close()
```

## Using Context Manager

For automatic cleanup, use the client as a context manager:

```python
from spotify_scraper import SpotifyClient

with SpotifyClient() as client:
    track_info = client.get_track_info("https://open.spotify.com/track/...")
    print(track_info['name'])
# Client is automatically closed
```

**Note**: The context manager is a convenience wrapper, not all features may be available in this mode.

## CLI Usage

SpotifyScraper also provides a command-line interface:

```bash
# Get track info
spotify-scraper track https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh

# Get album info with pretty output
spotify-scraper album https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp --pretty

# Download track preview
spotify-scraper download track https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh

# Save playlist info to file
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M -o playlist.json
```

## Error Handling

Always wrap your code in try-except blocks:

```python
from spotify_scraper import SpotifyClient, URLError, NetworkError

client = SpotifyClient()

try:
    track_info = client.get_track_info("https://open.spotify.com/track/invalid")
except URLError as e:
    print(f"Invalid URL: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
finally:
    client.close()
```

## Next Steps

- Learn about [Authentication](API-Reference#authentication) for accessing lyrics
- Explore [Advanced Features](API-Reference#advanced-features)
- See more [Examples](Examples)
- Check the [API Reference](API-Reference) for detailed documentation

## Common Issues

1. **No preview available**: Not all tracks have preview URLs
2. **Authentication required**: Some features like lyrics require cookies
3. **Rate limiting**: Add delays between requests if processing many URLs

For more help, see the [FAQ](FAQ) or [Troubleshooting](FAQ#troubleshooting) guide.