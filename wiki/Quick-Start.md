# Quick Start Guide

Get up and running with SpotifyScraper in 5 minutes!

## 🎯 Your First Script

### Step 1: Import and Initialize

```python
from spotify_scraper import SpotifyClient

# Create a client instance
client = SpotifyClient()
```

### Step 2: Extract Track Information

```python
# Spotify track URL
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"

# Get track metadata
track = client.get_track_info(track_url)

# Display information
print(f"Track: {track['name']}")
print(f"Artist: {track['artists'][0]['name']}")
print(f"Album: {track['album']['name']}")
print(f"Duration: {track['duration_ms'] / 1000:.0f} seconds")
```

### Step 3: Download Media

```python
# Download 30-second preview
preview_path = client.download_preview_mp3(track_url, path="downloads/")
print(f"Preview saved to: {preview_path}")

# Download cover art
cover_path = client.download_cover(track_url, path="covers/")
print(f"Cover saved to: {cover_path}")
```

## 📊 Working with Different Content Types

### Albums

```python
album_url = "https://open.spotify.com/album/3yyMKUSiCVByiZGLNQpS1G"
album = client.get_album_info(album_url)

print(f"Album: {album['name']}")
print(f"Artist: {album['artists'][0]['name']}")
print(f"Tracks: {album['total_tracks']}")

# List all tracks
for track in album['tracks']:
    print(f"  - {track['name']} ({track['duration_ms'] / 1000:.0f}s)")
```

### Artists

```python
artist_url = "https://open.spotify.com/artist/0TnOYISbd1XYRBk9myaseg"
artist = client.get_artist_info(artist_url)

print(f"Artist: {artist['name']}")
print(f"Followers: {artist['followers']:,}")
print(f"Monthly Listeners: {artist['monthly_listeners']:,}")

# Top tracks
for track in artist['top_tracks'][:5]:
    print(f"  - {track['name']}")
```

### Playlists

```python
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
playlist = client.get_playlist_info(playlist_url)

print(f"Playlist: {playlist['name']}")
print(f"Description: {playlist['description']}")
print(f"Tracks: {playlist['total_tracks']}")
print(f"Owner: {playlist['owner']['display_name']}")
```

## 🔐 Authenticated Features

Some features require authentication via cookies:

### Getting Spotify Cookies

1. Open Spotify Web Player in your browser
2. Log in to your account
3. Export cookies using a browser extension
4. Save as `cookies.txt`

### Using Authenticated Client

```python
# Initialize with cookies
client = SpotifyClient(cookie_file="cookies.txt")

# Now you can access lyrics
track_with_lyrics = client.get_track_info_with_lyrics(track_url)
if track_with_lyrics.get('lyrics'):
    print(f"Lyrics:\n{track_with_lyrics['lyrics']['text']}")
```

## 🛡️ Error Handling

```python
from spotify_scraper import URLError, NetworkError

try:
    track = client.get_track_info(track_url)
except URLError as e:
    print(f"Invalid URL: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## ⚡ Performance Tips

### Enable Caching

```python
# Client with caching enabled
client = SpotifyClient(cache_enabled=True)

# First call fetches from Spotify
track1 = client.get_track_info(track_url)  # Network request

# Second call uses cache
track2 = client.get_track_info(track_url)  # From cache
```

### Batch Operations

```python
urls = [
    "https://open.spotify.com/track/...",
    "https://open.spotify.com/track/...",
    "https://open.spotify.com/track/..."
]

# Process multiple URLs
results = []
for url in urls:
    try:
        track = client.get_track_info(url)
        results.append(track)
    except Exception as e:
        print(f"Failed to process {url}: {e}")
```

## 💻 Command Line Usage

SpotifyScraper includes a CLI interface:

```bash
# Get track info
spotify-scraper track https://open.spotify.com/track/... --format json

# Download media
spotify-scraper download track https://open.spotify.com/track/... --audio --cover

# Get playlist tracks
spotify-scraper playlist https://open.spotify.com/playlist/... --tracks-only
```

## 🎨 Output Formats

### JSON Output

```python
import json

track = client.get_track_info(track_url)
print(json.dumps(track, indent=2))
```

### Custom Formatting

```python
def format_track(track):
    return f"{track['name']} - {', '.join(a['name'] for a in track['artists'])}"

track = client.get_track_info(track_url)
print(format_track(track))
```

## 📚 Next Steps

- Explore [Advanced Examples](Examples)
- Read the [API Reference](API-Reference)
- Learn about [Error Handling](Error-Handling)
- Check out [Performance Optimization](Performance)