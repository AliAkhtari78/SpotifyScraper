# Basic Usage

This guide covers the fundamental usage patterns of SpotifyScraper.

## Getting Started

### Initialize the Client

```python
from spotify_scraper import SpotifyClient

# Create a client instance
client = SpotifyClient()

# Or with custom configuration
from spotify_scraper import Config

config = Config(cache_enabled=True, request_timeout=30)
client = SpotifyClient(config)
```

## Extracting Data

### Tracks

```python
# Extract by URL
track = client.get_track("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")

# Extract by ID
track = client.get_track("4iV5W9uYEdYUVa79Axb7Rh")

# Access track data
print(f"Track: {track['name']}")
print(f"Artist: {track['artists'][0]['name']}")
print(f"Duration: {track['duration_ms'] / 1000:.0f} seconds")
```

### Albums

```python
# Extract album with all tracks
album = client.get_album("https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy")

print(f"Album: {album['name']}")
print(f"Release Date: {album['release_date']}")

# List all tracks
for track in album['tracks']:
    print(f"  {track['track_number']}. {track['name']}")### Artists

```python
# Extract artist information
artist = client.get_artist("0OdUWJ0sBjDrqHygGUXeCF")

print(f"Artist: {artist['name']}")
print(f"Genres: {', '.join(artist['genres'])}")
print(f"Followers: {artist['followers']['total']:,}")
```

### Playlists

```python
# Extract playlist with all tracks
playlist = client.get_playlist("37i9dQZF1DXcBWIGoYBM5M")

print(f"Playlist: {playlist['name']}")
print(f"Owner: {playlist['owner']['name']}")
print(f"Description: {playlist['description']}")
print(f"Total Tracks: {playlist['total_tracks']}")

# List first 10 tracks
for i, track in enumerate(playlist['tracks'][:10], 1):
    print(f"  {i}. {track['name']} - {track['artists'][0]['name']}")
```

## Working with URLs

SpotifyScraper accepts various URL formats:

```python
# Regular URLs
client.get_track("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")

# Embed URLs
client.get_track("https://open.spotify.com/embed/track/4iV5W9uYEdYUVa79Axb7Rh")

# Just the ID
client.get_track("4iV5W9uYEdYUVa79Axb7Rh")

# Works for all entity types
client.get_album("album_id_or_url")
client.get_artist("artist_id_or_url")
client.get_playlist("playlist_id_or_url")
```

## Next Steps

- [Error Handling](error-handling.md) - Handle errors gracefully
- [Media Downloads](media-downloads.md) - Download audio and images
- [Advanced Usage](../examples/advanced.md) - Complex scenarios