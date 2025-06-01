# Basic Usage

This guide covers the fundamental usage patterns of SpotifyScraper.

## Getting Started

### Initialize the Client

```python
from spotify_scraper import SpotifyClient

# Create a client instance
client = SpotifyClient()

# Or with custom settings
client = SpotifyClient(
    browser_type="selenium",  # Use Selenium browser
    log_level="DEBUG",        # Set logging level
    cookie_file="cookies.txt" # For authenticated features
)
```

## Extracting Data

### Tracks

```python
# Extract by URL
track = client.get_track_info("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")

# Note: Direct ID extraction is not supported - use full URL

# Access track data
print(f"Track: {track.get('name', 'Unknown')}")
print(f"Artist: {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")
print(f"Duration: {track.get('duration_ms', 0) / 1000:.0f} seconds")
```

### Albums

```python
# Extract album with all tracks
album = client.get_album_info("https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy")

print(f"Album: {album.get('name', 'Unknown')}")
print(f"Release Date: {album.get('release_date', 'N/A')}")

# List all tracks
for i, track in enumerate(album['tracks'], 1):
    print(f"  {i}. {track.get('name', 'Unknown')}")

# Don't forget to close the client
client.close()### Artists

```python
# Extract artist information
artist = client.get_artist_info("https://open.spotify.com/artist/0OdUWJ0sBjDrqHygGUXeCF")

print(f"Artist: {artist.get('name', 'Unknown')}")
if 'stats' in artist:
    print(f"Monthly Listeners: {artist['stats'].get('monthly_listeners', 'N/A'):,}")
```

### Playlists

```python
# Extract playlist with all tracks
playlist = client.get_playlist_info("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")

print(f"Playlist: {playlist.get('name', 'Unknown')}")
print(f"Owner: {playlist.get('owner', {}).get('display_name', playlist.get('owner', {}).get('id', 'Unknown'))}")
# Note: description may not always be available
if 'description' in playlist:
    print(f"Description: {playlist.get('description', '')}")
print(f"Total Tracks: {playlist.get('track_count', 0)}")

# List first 10 tracks
for i, track in enumerate(playlist['tracks'][:10], 1):
    print(f"  {i}. {track.get('name', 'Unknown')} - {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")
```

## Working with URLs

SpotifyScraper accepts various URL formats:

```python
# Regular URLs
client.get_track_info("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")

# Auto-detect URL type
client.get_all_info("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
client.get_all_info("https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy")
client.get_all_info("https://open.spotify.com/artist/0OdUWJ0sBjDrqHygGUXeCF")
client.get_all_info("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")

# Note: Direct ID extraction is not supported - always use full URLs
```

## Next Steps

- [Error Handling](error-handling.md) - Handle errors gracefully
- [Media Downloads](media-downloads.md) - Download audio and images
- [Advanced Usage](../examples/advanced.md) - Complex scenarios