# Welcome to SpotifyScraper

**Extract Spotify data without the official API**. Access tracks, albums, artists, and playlists - no authentication required.

## What is SpotifyScraper?

SpotifyScraper is a Python library that allows you to extract data from Spotify's web player without using the official API. It provides a simple, intuitive interface for accessing track metadata, album information, artist profiles, and playlist contents.

## Key Features

- 🔓 **No API Key Required** - Start extracting data immediately
- 🚀 **Fast & Lightweight** - Optimized for speed and minimal dependencies  
- 📊 **Complete Metadata** - Get all available track, album, artist details
- 💿 **Media Downloads** - Download cover art and preview clips
- 🔄 **Bulk Operations** - Process multiple URLs efficiently
- 🛡️ **Robust & Reliable** - Comprehensive error handling and retries

## Quick Example

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

## Navigation

### Getting Started
- [Installation](Installation) - How to install SpotifyScraper
- [Quick Start](Quick-Start) - Get up and running quickly
- [Examples](Examples) - Common use cases and code samples

### API Documentation
- [API Reference](API-Reference) - Complete API documentation
- [CLI Usage](CLI-Usage) - Command-line interface guide
- [Configuration](Configuration) - Advanced configuration options

### Resources
- [FAQ](FAQ) - Frequently asked questions
- [Troubleshooting](Troubleshooting) - Common issues and solutions
- [Contributing](Contributing) - How to contribute to the project

## Why Choose SpotifyScraper?

| Feature | SpotifyScraper | Official API |
|---------|---------------|--------------|
| API Key Required | ❌ No | ✅ Yes |
| Rate Limits | ❌ No | ✅ Yes |
| Download Previews | ✅ Yes | ❌ No |
| Download Covers | ✅ Yes | ⚠️ Limited |
| Setup Complexity | Simple | Complex |
| Authentication | Optional | Required |

## Supported Data Types

### 🎵 Tracks
- Track name, ID, URI
- Artists (with IDs and URIs)
- Album information
- Duration and popularity
- Preview URL (30-second MP3)
- Lyrics (with authentication)

### 💿 Albums
- Album name, ID, URI
- All tracks with metadata
- Release date and label
- Cover art in multiple sizes
- Total tracks and duration

### 👤 Artists
- Artist name, ID, URI
- Biography and genres
- Top tracks
- Monthly listeners
- Follower count

### 📋 Playlists
- Playlist name and description
- All tracks with metadata
- Owner information
- Follower count
- Collaborative status

## Installation

```bash
# Basic installation
pip install spotifyscraper

# With all features
pip install spotifyscraper[all]
```

See the [Installation Guide](Installation) for more options.

## Community

- 🐛 [Report Issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
- 💬 [Join Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
- ⭐ [Star on GitHub](https://github.com/AliAkhtari78/SpotifyScraper)

## License

SpotifyScraper is released under the [MIT License](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/LICENSE).

---

**Current Version:** v2.0.19 | **Last Updated:** May 2025