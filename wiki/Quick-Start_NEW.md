# Quick Start Guide

Get up and running with SpotifyScraper in minutes. This guide covers the essential steps to start extracting Spotify data.

## Installation

```bash
# Basic installation
pip install spotifyscraper

# With Selenium support (for JavaScript-heavy pages)
pip install spotifyscraper[selenium]

# All features
pip install spotifyscraper[all]
```

## Your First Script

### Extract Track Information

```python
from spotify_scraper import SpotifyClient

# Initialize client
client = SpotifyClient()

# Get track info
track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
track = client.get_track_info(track_url)

# Display results
print(f"Track: {track.get('name', 'Unknown')}")
print(f"Artist: {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")
print(f"Album: {track.get('album', {}).get('name', 'Unknown')}")
print(f"Duration: {track.get('duration_ms', 0) // 1000} seconds")

# Clean up
client.close()
```

### Download Media

```python
# Download cover art
cover_path = client.download_cover(track_url, output_dir="covers/")
print(f"Cover saved to: {cover_path}")

# Download preview clip
preview_path = client.download_preview_mp3(track_url, output_dir="previews/")
print(f"Preview saved to: {preview_path}")
```

## Using the CLI

SpotifyScraper includes a powerful command-line interface:

```bash
# Get track info
spotify-scraper track https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh

# Download album with covers
spotify-scraper download album https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp

# Export playlist to JSON
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --output playlist.json
```

## Common Use Cases

### 1. Process Multiple Tracks

```python
from spotify_scraper import SpotifyBulkOperations

# Initialize bulk operations
bulk = SpotifyBulkOperations()

# Process multiple URLs
urls = [
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
    "https://open.spotify.com/track/5W3cjX2J3tjhG8zb6u0qHn",
    "https://open.spotify.com/track/1prhCmPbZNOvgpwdKArY4a"
]

results = bulk.process_urls(urls, operation="info")
for url, data in results['results'].items():
    if 'info' in data:
        print(f"{data['info']['name']} - {data['info']['artists'][0]['name']}")
```

### 2. Export Playlist

```python
# Get playlist data
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
playlist = client.get_playlist_info(playlist_url)

# Export to JSON
import json
with open('playlist.json', 'w') as f:
    json.dump(playlist, f, indent=2)

# Export track list to CSV
import csv
with open('tracks.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Title', 'Artist', 'Album', 'Duration'])
    
    for track in playlist['tracks']:
        writer.writerow([
            track.get('name', 'Unknown'),
            ', '.join(a['name'] for a in track['artists']),
            track.get('album', {}).get('name', 'Unknown'),
            track.get('duration_ms', 0) // 1000
        ])
```

### 3. Get Artist Discography

```python
# Get artist info
artist_url = "https://open.spotify.com/artist/3fMbdgg4jU18AjLCKBhRSm"
artist = client.get_artist_info(artist_url)

print(f"Artist: {artist.get('name', 'Unknown')}")
print(f"Genres: {', '.join(artist.get('genres', []))}")
print(f"Followers: {artist.get('followers', {}).get('total', 'N/A'):,}")

# Get top tracks
if artist.get('top_tracks'):
    print("\nTop Tracks:")
    for i, track in enumerate(artist.get('top_tracks', [])[:5], 1):
        print(f"{i}. {track.get('name', 'Unknown')}")
```

## Configuration Options

### Using Different Browsers

```python
# Use Selenium for JavaScript-heavy content
from spotify_scraper.core.config import Config

config = Config(browser_type="selenium", headless=True)
client = SpotifyClient(config=config)
```

### Authentication for Premium Features

```python
# Use cookies for authenticated features (e.g., lyrics)
client = SpotifyClient(cookie_file="cookies.txt")

# Get track with lyrics
track = client.get_track_info_with_lyrics(track_url)
if track.get('lyrics'):
    print(track['lyrics'])
```

## Error Handling

```python
from spotify_scraper.core.exceptions import SpotifyScraperError

try:
    track = client.get_track_info(track_url)
except SpotifyScraperError as e:
    print(f"Error: {e}")
    # Handle specific error types
    if isinstance(e, URLError):
        print("Invalid Spotify URL")
    elif isinstance(e, NetworkError):
        print("Network connection issue")
```

## Next Steps

- Explore [API Reference](API-Reference.md) for detailed documentation
- Check out [Examples](Examples.md) for more use cases
- Read the [FAQ](FAQ.md) for common questions
- View [advanced features](https://github.com/AliAkhtari78/SpotifyScraper#advanced-features) in the main documentation

## Need Help?

- 📖 [Full Documentation](https://spotifyscraper.readthedocs.io)
- 💬 [GitHub Issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
- 📧 [Contact](mailto:aliakhtari78@hotmail.com)