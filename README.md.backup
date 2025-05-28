# SpotifyScraper

[![PyPI version](https://badge.fury.io/py/spotifyscraper.svg)](https://badge.fury.io/py/spotifyscraper)
[![Python Support](https://img.shields.io/pypi/pyversions/spotifyscraper.svg)](https://pypi.org/project/spotifyscraper/)
[![Documentation Status](https://readthedocs.org/projects/spotifyscraper/badge/?version=latest)](https://spotifyscraper.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/AliAkhtari78/SpotifyScraper/branch/master/graph/badge.svg)](https://codecov.io/gh/AliAkhtari78/SpotifyScraper)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Python library for extracting data from Spotify without using the official API. Extract tracks, albums, artists, and playlists with ease!

## 🎵 Features

- **No API Key Required**: Access Spotify data without authentication
- **Multiple Data Types**: Extract tracks, albums, artists, and playlists
- **Media Downloads**: Download cover images and 30-second preview MP3s
- **Flexible Browsers**: Use lightweight requests or full Selenium automation
- **CLI Interface**: Command-line tool for quick data extraction
- **Type Safety**: Full type hints and TypedDict support
- **Error Handling**: Comprehensive exception hierarchy
- **Bulk Operations**: Process multiple URLs efficiently
- **Data Analysis**: Built-in playlist analysis and comparison tools

## 📦 Installation

### Basic Installation
```bash
pip install spotifyscraper
```

### With Selenium Support
```bash
pip install "spotifyscraper[selenium]"
```

### Development Installation
```bash
pip install "spotifyscraper[dev]"
```

### Full Installation (All Features)
```bash
pip install "spotifyscraper[all]"
```

## 🚀 Quick Start

### Python Library Usage

```python
from spotify_scraper import SpotifyClient

# Initialize client
client = SpotifyClient()

# Get track information
track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
track_info = client.get_track_info(track_url)
print(f"Track: {track_info['name']} by {track_info['artists'][0]['name']}")

# Get album with tracks
album_url = "https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp"
album_info = client.get_album_info(album_url)
print(f"Album: {album_info['name']} ({album_info['total_tracks']} tracks)")

# Download cover art
cover_path = client.download_cover(track_url, path="covers/")
print(f"Cover saved to: {cover_path}")

# Don't forget to close the client
client.close()
```

### CLI Usage

```bash
# Get track info
spotify-scraper track https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh

# Get album info with pretty output
spotify-scraper album https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp --pretty

# Download track preview
spotify-scraper download track https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh --with-cover

# Get playlist info in JSON format
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --output playlist.json
```

## 📖 Detailed Usage

### Client Configuration

```python
from spotify_scraper import SpotifyClient

# Initialize with custom settings
client = SpotifyClient(
    browser_type="selenium",     # Use Selenium for JavaScript content
    log_level="DEBUG",          # Set logging level
    proxy={
        "http": "http://proxy.example.com:8080",
        "https": "https://proxy.example.com:8080"
    }
)
```

### Authentication (Optional)

Some features like lyrics require authentication via cookies:

```python
# Using cookie file (exported from browser)
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Using cookie dictionary
client = SpotifyClient(cookies={"sp_t": "your_token_here"})
```

### Error Handling

```python
from spotify_scraper import SpotifyClient, URLError, NetworkError, ExtractionError

client = SpotifyClient()

try:
    track_info = client.get_track_info("https://open.spotify.com/track/invalid")
except URLError as e:
    print(f"Invalid URL: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
finally:
    client.close()
```

### Bulk Operations

```python
from spotify_scraper.utils.common import SpotifyBulkOperations

# Process multiple URLs
urls = [
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
    "https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp",
    "https://open.spotify.com/artist/00FQb4jTyendYWaN8pK0wa"
]

bulk = SpotifyBulkOperations()
results = bulk.process_urls(urls, operation="all_info")

# Export results
bulk.export_to_json(results, "spotify_data.json")
bulk.export_to_csv(results, "spotify_data.csv")
```

### Data Analysis

```python
from spotify_scraper.utils.common import SpotifyDataAnalyzer

analyzer = SpotifyDataAnalyzer()

# Analyze playlist
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
stats = analyzer.analyze_playlist(playlist_url)

print(f"Total duration: {stats['total_duration_formatted']}")
print(f"Average track length: {stats['average_duration_formatted']}")
print(f"Most common artist: {stats['most_common_artists'][0]}")

# Compare playlists
playlist1 = "https://open.spotify.com/playlist/..."
playlist2 = "https://open.spotify.com/playlist/..."
comparison = analyzer.compare_playlists(playlist1, playlist2)

print(f"Common tracks: {len(comparison['common_tracks'])}")
print(f"Similarity score: {comparison['similarity_score']:.2%}")
```

## 📊 Data Structures

### Track Data
```python
{
    "id": "4iV5W9uYEdYUVa79Axb7Rh",
    "name": "Harder Better Faster Stronger",
    "uri": "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
    "type": "track",
    "duration_ms": 225400,
    "artists": [
        {
            "name": "Daft Punk",
            "uri": "spotify:artist:4tZwfgrHOc3mvqYlEYSvVi",
            "id": "4tZwfgrHOc3mvqYlEYSvVi"
        }
    ],
    "album": {
        "name": "Discovery",
        "uri": "spotify:album:2noRn2Aes5aoNVsU6iWThc",
        "images": [...]
    },
    "preview_url": "https://p.scdn.co/mp3-preview/...",
    "is_playable": true,
    "is_explicit": false
}
```

### Album Data
```python
{
    "id": "0JGOiO34nwfUdDrD612dOp",
    "name": "Discovery",
    "uri": "spotify:album:0JGOiO34nwfUdDrD612dOp",
    "type": "album",
    "artists": [...],
    "images": [...],
    "release_date": "2001-03-07",
    "total_tracks": 14,
    "tracks": [...]
}
```

## 🛠️ Advanced Features

### Custom Browser Backend

```python
# Use Selenium for JavaScript-heavy content
client = SpotifyClient(browser_type="selenium")

# Selenium will be used automatically if requests fails
client = SpotifyClient(browser_type="auto")
```

### Logging Configuration

```python
import logging

# Configure logging
client = SpotifyClient(
    log_level="DEBUG",
    log_file="spotify_scraper.log"
)

# Or configure globally
logging.basicConfig(level=logging.DEBUG)
```

### Environment Variables

Configure via environment variables (prefix with `SPOTIFY_SCRAPER_`):

```bash
export SPOTIFY_SCRAPER_LOG_LEVEL=DEBUG
export SPOTIFY_SCRAPER_BROWSER_TYPE=selenium
export SPOTIFY_SCRAPER_COOKIE_FILE=/path/to/cookies.txt
```

### Bulk Operations

Process multiple URLs efficiently:

```python
from spotify_scraper.utils.common import SpotifyBulkOperations

# Process multiple URLs
urls = [
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
    "https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp",
    "https://open.spotify.com/artist/00FQb4jTyendYWaN8pK0wa"
]

bulk = SpotifyBulkOperations()
results = bulk.process_urls(urls, operation="all_info")

# Export results
bulk.export_to_json(results, "spotify_data.json")
bulk.export_to_csv(results, "spotify_data.csv")
```

## 🎯 CLI Commands

### Track Command
```bash
spotify-scraper track [URL] [OPTIONS]

Options:
  -o, --output PATH      Output file path
  -p, --pretty          Pretty print output
  -f, --format FORMAT   Output format (json/yaml/table)
  --with-lyrics         Include lyrics (requires auth)
```

### Album Command
```bash
spotify-scraper album [URL] [OPTIONS]

Options:
  -o, --output PATH      Output file path
  -p, --pretty          Pretty print output
  -f, --format FORMAT   Output format (json/yaml/table)
  --tracks-only         Only output track list
```

### Playlist Command
```bash
spotify-scraper playlist [URL] [OPTIONS]

Options:
  -o, --output PATH      Output file path
  -p, --pretty          Pretty print output
  -f, --format FORMAT   Output format (json/yaml/table)
```

### Download Command
```bash
# Download cover image
spotify-scraper download cover [URL] --output cover.jpg

# Download track preview with cover
spotify-scraper download track [URL] --with-cover

# Batch download from URL list
spotify-scraper download batch urls.txt --output downloads/
```

## 🔧 Troubleshooting

### Common Issues

1. **No track preview available**
   - Not all tracks have preview URLs
   - Try using a different track

2. **Authentication required for lyrics**
   - Export cookies from your browser
   - Use `--cookie-file` option

3. **Selenium browser errors**
   - Install Chrome/Chromium
   - Install appropriate driver (chromedriver)

4. **Rate limiting**
   - Add delays between requests
   - Use proxy rotation

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This library is for educational and personal use only. Respect Spotify's Terms of Service and use responsibly.

## 🔗 Links

- [Documentation](https://spotifyscraper.readthedocs.io/)
- [GitHub Repository](https://github.com/AliAkhtari78/SpotifyScraper)
- [PyPI Package](https://pypi.org/project/spotifyscraper/)
- [Issue Tracker](https://github.com/AliAkhtari78/SpotifyScraper/issues)