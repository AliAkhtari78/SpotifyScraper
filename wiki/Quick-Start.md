# Quick Start Guide

This guide will get you up and running with SpotifyScraper in just a few minutes.

## Basic Usage

### 1. Import and Create Client

```python
from spotify_scraper import SpotifyClient

# Create a basic client
client = SpotifyClient()
```

### 2. Extract Track Information

```python
# Get track info
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track = client.get_track_info(track_url)

# Access track data
print(f"Track: {track['name']}")
print(f"Artist: {track['artists'][0]['name']}")
print(f"Album: {track['album']['name']}")
print(f"Duration: {track['duration_ms'] / 1000:.1f} seconds")
```

### 3. Download Media Files

```python
# Download 30-second preview MP3
mp3_path = client.download_preview_mp3(track_url, path="downloads/")
print(f"Preview downloaded to: {mp3_path}")

# Download album cover
cover_path = client.download_cover(track_url, path="covers/")
print(f"Cover downloaded to: {cover_path}")
```

## Working with Different Content Types

### Albums

```python
album_url = "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"
album = client.get_album_info(album_url)

print(f"Album: {album['name']}")
print(f"Artist: {album['artists'][0]['name']}")
print(f"Release Date: {album['release_date']}")
print(f"Total Tracks: {album['total_tracks']}")

# List all tracks
for i, track in enumerate(album['tracks']['items'], 1):
    print(f"{i}. {track['name']} ({track['duration_ms'] / 1000:.1f}s)")
```

### Artists

```python
artist_url = "https://open.spotify.com/artist/1dfeR4HaWDbWqFHLkxsg1d"
artist = client.get_artist_info(artist_url)

print(f"Artist: {artist['name']}")
print(f"Genres: {', '.join(artist['genres'])}")
print(f"Followers: {artist['followers']['total']:,}")
print(f"Popularity: {artist['popularity']}/100")
```

### Playlists

```python
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
playlist = client.get_playlist_info(playlist_url)

print(f"Playlist: {playlist['name']}")
print(f"Owner: {playlist['owner']['display_name']}")
print(f"Tracks: {playlist['tracks']['total']}")
print(f"Description: {playlist['description']}")
```

## Advanced Features

### Authentication for Lyrics

Some features like lyrics require authentication:

```python
# Option 1: Use cookies.txt file
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Option 2: Use cookie dictionary
client = SpotifyClient(cookies={"sp_t": "your_auth_token"})

# Get track with lyrics
track = client.get_track_info_with_lyrics(track_url)
if track['lyrics']:
    print(f"Lyrics:\n{track['lyrics']}")
```

### Custom Configuration

```python
# Configure client with options
client = SpotifyClient(
    browser_type="selenium",  # Use Selenium for JS support
    log_level="DEBUG",        # Enable debug logging
    proxy={                   # Use proxy server
        "http": "http://proxy.example.com:8080",
        "https": "https://proxy.example.com:8080"
    }
)
```

### Automatic URL Detection

```python
# Works with any Spotify URL type
mixed_urls = [
    "https://open.spotify.com/track/...",
    "https://open.spotify.com/album/...",
    "https://open.spotify.com/artist/...",
    "https://open.spotify.com/playlist/..."
]

for url in mixed_urls:
    info = client.get_all_info(url)
    print(f"{info['type']}: {info['name']}")
```

## Utility Functions

```python
from spotify_scraper import is_spotify_url, extract_id, get_url_type

# Validate URLs
url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
print(f"Valid URL: {is_spotify_url(url)}")  # True

# Extract Spotify ID
track_id = extract_id(url)
print(f"Track ID: {track_id}")  # 6rqhFgbbKwnb9MLmUQDhG6

# Determine URL type
url_type = get_url_type(url)
print(f"URL Type: {url_type}")  # track
```

## Error Handling

```python
from spotify_scraper.core.exceptions import URLError, ScrapingError

try:
    track = client.get_track_info("invalid_url")
except URLError as e:
    print(f"Invalid URL: {e}")
except ScrapingError as e:
    print(f"Scraping failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Always close the client when done:**
   ```python
   client.close()
   ```

2. **Use context managers (if available):**
   ```python
   with SpotifyClient() as client:
       track = client.get_track_info(url)
   ```

3. **Handle missing preview URLs:**
   ```python
   if track.get('preview_url'):
       client.download_preview_mp3(track_url)
   else:
       print("No preview available for this track")
   ```

4. **Check for errors in responses:**
   ```python
   info = client.get_track_info(url)
   if 'error' not in info:
       # Process data
       pass
   ```

## Next Steps

- Explore [Advanced Examples](Examples) for more use cases
- Check the [API Reference](API-Reference) for detailed documentation
- Learn about [authentication](API-Reference#authentication) for protected content
- See [FAQ](FAQ) for common questions