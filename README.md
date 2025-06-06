# SpotifyScraper

[![PyPI version](https://badge.fury.io/py/spotifyscraper.svg)](https://badge.fury.io/py/spotifyscraper)
[![Python Support](https://img.shields.io/pypi/pyversions/spotifyscraper.svg)](https://pypi.org/project/spotifyscraper/)
[![Documentation Status](https://readthedocs.org/projects/spotifyscraper/badge/?version=latest)](https://spotifyscraper.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/AliAkhtari78/SpotifyScraper/branch/master/graph/badge.svg)](https://codecov.io/gh/AliAkhtari78/SpotifyScraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Extract Spotify data without the official API**. Access tracks, albums, artists, playlists, and podcasts - no authentication required.

## Why SpotifyScraper?

- 🔓 **No API Key Required** - Start extracting data immediately
- 🚀 **Fast & Lightweight** - Optimized for speed and minimal dependencies  
- 📊 **Complete Metadata** - Get all available track, album, artist details
- 🎙️ **Podcast Support** - Extract podcast episodes and show information
- 💿 **Media Downloads** - Download cover art and preview clips
- 🔄 **Bulk Operations** - Process multiple URLs efficiently
- 🛡️ **Robust & Reliable** - Comprehensive error handling and retries

## Installation

```bash
# Basic installation
pip install spotifyscraper

# With Selenium support (for JavaScript-heavy pages)
pip install spotifyscraper[selenium]

# All features
pip install spotifyscraper[all]
```

## Quick Start

### Basic Usage

```python
from spotify_scraper import SpotifyClient

# Initialize client
client = SpotifyClient()

# Get track info
track = client.get_track_info("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
print(f"{track.get('name', 'Unknown')} by {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")
# Output: One More Time by Daft Punk

# Download cover art
cover_path = client.download_cover("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
print(f"Cover saved to: {cover_path}")

client.close()
```

### CLI Usage

```bash
# Get track info
spotify-scraper track https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh

# Download album with covers
spotify-scraper download album https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp --with-covers

# Export playlist to JSON
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --output playlist.json
```

## Core Features

### 🎵 Track Information

```python
# Get complete track metadata
track = client.get_track_info(track_url)

# Available data:
# - name, id, uri, duration_ms
# - artists (with names and IDs)  
# - album (with name, ID, release date, images)
# - preview_url (30-second MP3)
# - is_explicit, is_playable
# Note: popularity field is NOT available via web scraping

# Note: Lyrics require OAuth authentication, not just cookies
# SpotifyScraper currently cannot access lyrics as Spotify requires
# OAuth Bearer tokens for the lyrics API endpoint
client = SpotifyClient(cookie_file="cookies.txt")
track = client.get_track_info_with_lyrics(track_url)
# track['lyrics'] will be None - OAuth required
```

### 💿 Album Information

```python
# Get album with all tracks
album = client.get_album_info(album_url)

print(f"Album: {album.get('name', 'Unknown')}")
print(f"Artist: {(album.get('artists', [{}])[0].get('name', 'Unknown') if album.get('artists') else 'Unknown')}")
print(f"Released: {album.get('release_date', 'N/A')}")
print(f"Tracks: {album.get('total_tracks', 0)}")

# List all tracks
for track in album['tracks']:
    print(f"  {track['track_number']}. {track.get('name', 'Unknown')}")
```

### 👤 Artist Information

```python
# Get artist profile
artist = client.get_artist_info(artist_url)

print(f"Artist: {artist.get('name', 'Unknown')}")
print(f"Followers: {artist.get('followers', {}).get('total', 'N/A'):,}")
print(f"Genres: {', '.join(artist.get('genres', []))}")
print(f"Popularity: {artist.get('popularity', 'N/A')}/100")

# Get top tracks
for track in artist.get('top_tracks', [])[:5]:
    print(f"  - {track.get('name', 'Unknown')}")
```

### 📋 Playlist Information

```python
# Get playlist details
playlist = client.get_playlist_info(playlist_url)

print(f"Playlist: {playlist.get('name', 'Unknown')}")
print(f"Owner: {playlist.get('owner', {}).get('display_name', playlist.get('owner', {}).get('id', 'Unknown'))}")
print(f"Tracks: {playlist.get('track_count', 0)}")
print(f"Followers: {playlist.get('followers', {}).get('total', 'N/A'):,}")

# Get all tracks
for track in playlist['tracks']:
    print(f"  - {track.get('name', 'Unknown')} by {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")
```

### 🎙️ Podcast Support (NEW!)

#### Episode Information

```python
# Get episode details
episode = client.get_episode_info(episode_url)

print(f"Episode: {episode.get('name', 'Unknown')}")
print(f"Show: {episode.get('show', {}).get('name', 'Unknown')}")
print(f"Duration: {episode.get('duration_ms', 0) / 1000 / 60:.1f} minutes")
print(f"Release Date: {episode.get('release_date', 'N/A')}")
print(f"Has Video: {'Yes' if episode.get('has_video') else 'No'}")

# Download episode preview (1-2 minute clip)
preview_path = client.download_episode_preview(
    episode_url,
    path="podcast_previews/",
    filename="episode_preview"
)
print(f"Preview downloaded to: {preview_path}")
```

#### Show Information

```python
# Get podcast show details
show = client.get_show_info(show_url)

print(f"Show: {show.get('name', 'Unknown')}")
print(f"Publisher: {show.get('publisher', 'Unknown')}")
print(f"Total Episodes: {show.get('total_episodes', 'N/A')}")
print(f"Categories: {', '.join(show.get('categories', []))}")

# Get recent episodes
for episode in show.get('episodes', [])[:5]:
    print(f"  - {episode.get('name', 'Unknown')} ({episode.get('duration_ms', 0) / 1000 / 60:.1f} min)")
```

#### CLI Commands for Podcasts

```bash
# Get episode info
spotify-scraper episode info https://open.spotify.com/episode/...

# Download episode preview
spotify-scraper episode download https://open.spotify.com/episode/... -o previews/

# Get show info with episodes
spotify-scraper show info https://open.spotify.com/show/...

# List show episodes
spotify-scraper show episodes https://open.spotify.com/show/... -o episodes.json
```

**Note**: Full episode downloads require Spotify Premium authentication. SpotifyScraper currently supports preview clips only.

### 📥 Media Downloads

```python
# Download track preview (30-second MP3)
audio_path = client.download_preview_mp3(
    track_url,
    path="previews/",
    filename="custom_name.mp3"
)

# Download cover art
cover_path = client.download_cover(
    album_url,
    path="covers/",
    size_preference="large",  # small, medium, large
    format="jpeg"  # jpeg or png
)

# Download all playlist covers
from spotify_scraper.utils.common import SpotifyBulkOperations

bulk = SpotifyBulkOperations(client)
covers = bulk.download_playlist_covers(
    playlist_url,
    output_dir="playlist_covers/"
)
```

### 🔄 Bulk Operations

```python
from spotify_scraper.utils.common import SpotifyBulkOperations

# Process multiple URLs
urls = [
    "https://open.spotify.com/track/...",
    "https://open.spotify.com/album/...",
    "https://open.spotify.com/artist/..."
]

bulk = SpotifyBulkOperations()
results = bulk.process_urls(urls, operation="all_info")

# Export results
bulk.export_to_json(results, "spotify_data.json")
bulk.export_to_csv(results, "spotify_data.csv")

# Batch download media
downloads = bulk.batch_download(
    urls,
    output_dir="downloads/",
    media_types=["audio", "cover"]
)
```

### 📊 Data Analysis

```python
from spotify_scraper.utils.common import SpotifyDataAnalyzer

analyzer = SpotifyDataAnalyzer()

# Analyze playlist
stats = analyzer.analyze_playlist(playlist_data)
print(f"Total duration: {stats['basic_stats']['total_duration_formatted']}")
print(f"Most common artist: {stats['artist_stats']['top_artists'][0]}")
print(f"Average popularity: {stats['basic_stats']['average_popularity']}")

# Compare playlists
comparison = analyzer.compare_playlists(playlist1, playlist2)
print(f"Common tracks: {comparison['track_comparison']['common_tracks']}")
print(f"Similarity: {comparison['track_comparison']['similarity_percentage']:.1f}%")
```

## Advanced Configuration

### Browser Selection

```python
# Use requests (default, fast)
client = SpotifyClient(browser_type="requests")

# Use Selenium (for JavaScript content)
client = SpotifyClient(browser_type="selenium")

# Auto-detect (falls back to Selenium if needed)
client = SpotifyClient(browser_type="auto")
```

### Authentication

```python
# Using cookies file (exported from browser)
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Using cookie dictionary
client = SpotifyClient(cookies={"sp_t": "your_token"})

# Using headers
client = SpotifyClient(headers={
    "User-Agent": "Custom User Agent",
    "Accept-Language": "en-US,en;q=0.9"
})
```

### Proxy Support

```python
client = SpotifyClient(proxy={
    "http": "http://proxy.example.com:8080",
    "https": "https://proxy.example.com:8080"
})
```

### Logging

```python
# Set logging level
client = SpotifyClient(log_level="DEBUG")

# Or use standard logging
import logging
logging.basicConfig(level=logging.INFO)
```

## API Reference

### SpotifyClient

The main client for interacting with Spotify.

**Methods:**
- `get_track_info(url)` - Get track metadata
- `get_track_lyrics(url)` - Get track lyrics (requires auth)
- `get_track_info_with_lyrics(url)` - Get track with lyrics
- `get_album_info(url)` - Get album metadata
- `get_artist_info(url)` - Get artist metadata
- `get_playlist_info(url)` - Get playlist metadata
- `download_preview_mp3(url, path, filename)` - Download track preview
- `download_cover(url, path, size_preference, format)` - Download cover art
- `close()` - Close the client and clean up resources

### SpotifyBulkOperations

Utilities for processing multiple URLs.

**Methods:**
- `process_urls(urls, operation)` - Process multiple URLs
- `export_to_json(data, output_file)` - Export to JSON
- `export_to_csv(data, output_file)` - Export to CSV
- `batch_download(urls, output_dir, media_types)` - Batch download media
- `process_url_file(file_path, operation)` - Process URLs from file
- `extract_urls_from_text(text)` - Extract Spotify URLs from text

### SpotifyDataAnalyzer

Tools for analyzing Spotify data.

**Methods:**
- `analyze_playlist(playlist_data)` - Get playlist statistics
- `compare_playlists(playlist1, playlist2)` - Compare two playlists

## Examples

### Download All Album Tracks

```python
# Get album info
album = client.get_album_info(album_url)

# Download all track previews
for track in album['tracks']:
    track_url = f"https://open.spotify.com/track/{track['id']}"
    client.download_preview_mp3(track_url, path=f"album_{album.get('name', 'Unknown')}/")
```

### Export Artist Discography

```python
artist = client.get_artist_info(artist_url)

# Get all albums
albums_data = []
for album in artist['albums']['items']:
    album_url = f"https://open.spotify.com/album/{album['id']}"
    album = client.get_album_info(album_url)
    albums_data.append(album_info)

# Export to JSON
import json
with open(f"{artist.get('name', 'Unknown')}_discography.json", "w") as f:
    json.dump(albums_data, f, indent=2)
```

### Create Playlist Report

```python
from spotify_scraper.utils.common import SpotifyDataFormatter

formatter = SpotifyDataFormatter()

# Get playlist
playlist = client.get_playlist_info(playlist_url)

# Create markdown report
markdown = formatter.format_playlist_markdown(playlist)
with open("playlist_report.md", "w") as f:
    f.write(markdown)

# Create M3U file
tracks = [item['track'] for item in playlist['tracks']]
formatter.export_to_m3u(tracks, "playlist.m3u")
```

## Error Handling

```python
from spotify_scraper.core.exceptions import (
    SpotifyScraperError,
    URLError,
    DataExtractionError,
    DownloadError
)

try:
    track = client.get_track_info(url)
except URLError:
    print("Invalid Spotify URL")
except DataExtractionError as e:
    print(f"Failed to extract data: {e}")
except SpotifyScraperError as e:
    print(f"General error: {e}")
```

## Command Line Interface

```bash
# General syntax
spotify-scraper [COMMAND] [URL] [OPTIONS]

# Commands:
#   track      Get track information
#   album      Get album information
#   artist     Get artist information
#   playlist   Get playlist information
#   download   Download media files

# Global options:
#   --output, -o      Output file path
#   --format, -f      Output format (json, csv, txt)
#   --pretty          Pretty print output
#   --log-level       Set logging level
#   --cookies         Cookie file path

# Examples:
spotify-scraper track $URL --pretty
spotify-scraper album $URL -o album.json
spotify-scraper playlist $URL -f csv -o playlist.csv
spotify-scraper download track $URL --with-cover --path downloads/
```

## Environment Variables

Configure SpotifyScraper using environment variables:

```bash
export SPOTIFY_SCRAPER_LOG_LEVEL=DEBUG
export SPOTIFY_SCRAPER_BROWSER_TYPE=selenium
export SPOTIFY_SCRAPER_COOKIE_FILE=/path/to/cookies.txt
export SPOTIFY_SCRAPER_PROXY_HTTP=http://proxy:8080
```

## Requirements

- Python 3.8 or higher
- Operating System: Windows, macOS, Linux, BSD
- Dependencies:
  - requests (for basic operations)
  - beautifulsoup4 (for HTML parsing)
  - selenium (optional, for JavaScript content)

## Troubleshooting

### Common Issues

**1. SSL Certificate Errors**
```python
client = SpotifyClient(verify_ssl=False)  # Not recommended for production
```

**2. Rate Limiting**
```python
import time
for url in urls:
    track = client.get_track_info(url)
    time.sleep(1)  # Add delay between requests
```

**3. Cloudflare Protection**
```python
# Use Selenium backend
client = SpotifyClient(browser_type="selenium")
```

**4. Missing Data**
```python
# Some fields might be None
track = client.get_track_info(url)
artist_name = track.get('artists', [{}])[0].get('name', 'Unknown')
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/CONTRIBUTING.md) for details.

```bash
# Clone the repository
git clone https://github.com/AliAkhtari78/SpotifyScraper.git

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black src/ tests/
flake8 src/ tests/
mypy src/
```

## License

SpotifyScraper is released under the MIT License. See [LICENSE](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/LICENSE) for details.

## Disclaimer

This library is for educational and personal use only. Always respect Spotify's Terms of Service and robots.txt. The authors are not responsible for any misuse of this library.

## Support

- 📚 [Documentation](https://spotifyscraper.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/AliAkhtari78/SpotifyScraper/issues)
- 💬 [Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
- 📧 [Email](mailto:aliakhtari78@hotmail.com)

---

**SpotifyScraper** - Extract Spotify data with ease 🎵

Made with ❤️ by [Ali Akhtari](https://github.com/AliAkhtari78)