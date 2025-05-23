# SpotifyScraper 🎵

[![PyPI version](https://img.shields.io/pypi/v/spotifyscraper.svg)](https://pypi.org/project/spotifyscraper/)
[![Python Versions](https://img.shields.io/pypi/pyversions/spotifyscraper.svg)](https://pypi.org/project/spotifyscraper/)
[![CI Status](https://github.com/AliAkhtari78/SpotifyScraper/workflows/CI/badge.svg)](https://github.com/AliAkhtari78/SpotifyScraper/actions)
[![Coverage Status](https://codecov.io/gh/AliAkhtari78/SpotifyScraper/branch/master/graph/badge.svg)](https://codecov.io/gh/AliAkhtari78/SpotifyScraper)
[![Documentation Status](https://readthedocs.org/projects/spotifyscraper/badge/?version=latest)](https://spotifyscraper.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/spotifyscraper)](https://pepy.tech/project/spotifyscraper)

**SpotifyScraper** is a powerful, modern Python library that extracts rich metadata from Spotify's web interface without requiring API credentials. Built for developers who need reliable access to Spotify's public data, it offers a clean, type-safe API with comprehensive media download capabilities.

## 🌟 Why SpotifyScraper?

- **No API Key Required**: Access Spotify data without dealing with API registration, rate limits, or quotas
- **Rich Data Extraction**: Get comprehensive metadata including preview URLs, cover art, lyrics, and more
- **Production Ready**: Battle-tested with robust error handling, retries, and fallback mechanisms
- **Type Safe**: Full TypeScript-style type hints for excellent IDE support and fewer runtime errors
- **Media Downloads**: Built-in high-quality audio preview and cover art downloading with metadata
- **Flexible Architecture**: Choose between lightweight requests or powerful Selenium backends
- **Modern Python**: Async support, context managers, and clean pythonic interfaces

## 🚀 Quick Start

```python
from spotify_scraper import SpotifyClient

# Create client (no authentication needed for basic usage)
client = SpotifyClient()

# Get track info
track = client.get_track("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
print(f"Track: {track['name']} by {track['artists'][0]['name']}")

# Download preview
file_path = client.download_preview(track["id"])
print(f"Downloaded preview to {file_path}")

# Download cover image
cover_path = client.download_cover(track["id"])
print(f"Downloaded cover to {cover_path}")
```

## ✨ Features

### Core Capabilities
- 🎵 **Track Extraction**: Complete track metadata including artists, album, duration, popularity, and preview URLs
- 💿 **Album Support**: Full album details with track listings, release dates, and album art
- 🎤 **Artist Profiles**: Artist information including top tracks, monthly listeners, and verified status
- 📝 **Playlist Parsing**: Extract all tracks from public playlists with creator information
- 🎼 **Lyrics Support**: Access song lyrics when available (requires authentication)

### Media Management
- 🎧 **Audio Downloads**: High-quality MP3 previews with embedded metadata (ID3 tags)
- 🖼️ **Cover Art**: Multiple resolution options (300x300, 640x640, original)
- 📊 **Metadata Embedding**: Automatic ID3 tagging with artist, title, album, and cover art
- 🗂️ **Smart Filenames**: Configurable naming patterns with sanitization

### Technical Excellence
- 🔒 **Type Safety**: Comprehensive TypedDict definitions for all data structures
- ⚡ **Performance**: Connection pooling, session reuse, and optional async support
- 🛡️ **Reliability**: Automatic retries, graceful degradation, and detailed error messages
- 🔧 **Flexibility**: Multiple browser backends, authentication options, and configuration
- 📝 **Logging**: Configurable logging with structured output for debugging
- 🌐 **Proxy Support**: Full proxy configuration for both HTTP and SOCKS
- 🔄 **Backward Compatible**: Maintains compatibility with v1.x code

## 📋 Requirements

- **Python**: 3.8, 3.9, 3.10, 3.11, or 3.12
- **Platform**: Windows, macOS, Linux, or any platform supporting Python
- **Memory**: Minimum 512MB RAM (1GB recommended for Selenium backend)
- **Network**: Stable internet connection

## 📦 Installation

### From PyPI (Recommended)

```bash
# Basic installation
pip install spotifyscraper

# With Selenium support for JavaScript-heavy pages
pip install "spotifyscraper[selenium]"

# With development tools
pip install "spotifyscraper[dev]"

# Everything included
pip install "spotifyscraper[all]"
```

### From Source

```bash
# Clone the repository
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper

# Install in development mode
pip install -e ".[dev]"

# Run tests to verify installation
pytest
```

### Using Poetry

```bash
poetry add spotifyscraper

# With optional dependencies
poetry add "spotifyscraper[selenium]"
```

### Using Conda

```bash
# First install pip in conda environment
conda install pip

# Then install spotifyscraper
pip install spotifyscraper
```

## 🎯 Usage Examples

### Basic Usage

#### Extract Track Information

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# From URL
track = client.get_track("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")

# From ID
track = client.get_track_by_id("6rqhFgbbKwnb9MLmUQDhG6")

# Access track data
print(f"Title: {track['name']}")
print(f"Artist: {track['artists'][0]['name']}")
print(f"Album: {track['album']['name']}")
print(f"Release date: {track['release_date']}")
print(f"Preview URL: {track['preview_url']}")
```

#### Extract Album Information

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Get album info
album = client.get_album("https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3")

# Access album data
print(f"Album: {album['name']}")
print(f"Artist: {album['artists'][0]['name']}")
print(f"Release date: {album['release_date']}")
print(f"Total tracks: {album['total_tracks']}")

# Get all tracks in album
for track in album['tracks']:
    print(f"- {track['name']}")
```

#### Extract Artist Information

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Get artist info
artist = client.get_artist("https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb")

# Access artist data
print(f"Artist: {artist['name']}")
print(f"Followers: {artist.get('followers', 'N/A')}")
print(f"Monthly listeners: {artist.get('monthly_listeners', 'N/A')}")

# Get top tracks
for track in artist.get('top_tracks', []):
    print(f"- {track['name']}")
```

#### Extract Playlist Information

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Get playlist info
playlist = client.get_playlist("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")

# Access playlist data
print(f"Playlist: {playlist['name']}")
print(f"Creator: {playlist['owner']['name']}")
print(f"Total tracks: {playlist.get('track_count', 0)}")

# Get tracks in playlist
for track in playlist.get('tracks', []):
    print(f"- {track['name']} by {track['artists'][0]['name']}")
```

### Advanced Usage

#### Download Preview MP3 with Metadata

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Download with default settings
path = client.download_preview("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")

# With custom filename and path
path = client.download_preview(
    "6rqhFgbbKwnb9MLmUQDhG6",
    filename="my_song.mp3",
    path="~/Music",
    with_cover=True,  # Embed cover art
)
```

#### Download High-Resolution Cover Art

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Download with default settings
path = client.download_cover("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")

# With custom filename, path and size
path = client.download_cover(
    "6rqhFgbbKwnb9MLmUQDhG6",
    filename="album_cover.jpg",
    path="~/Pictures",
    size="large",  # 'small', 'medium', or 'large'
)
```

#### Authentication for Premium Features

```python
from spotify_scraper import SpotifyClient

# Create authenticated client
client = SpotifyClient(
    auth_token="your_spotify_auth_token",
    # or
    cookie_file="path/to/cookies.txt",
)

# Get track with lyrics (requires authentication)
track = client.get_track("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
lyrics = client.get_lyrics(track["id"])
print(lyrics["text"])

# Access user-specific content
user_playlists = client.get_user_playlists("spotify_username")
private_playlist = client.get_playlist("private_playlist_id")
```

#### Using Configuration Files

```python
from spotify_scraper import SpotifyClient, Config

# Load configuration from file
config = Config.from_file("config.json")
client = SpotifyClient(config=config)

# Or use environment variables
client = SpotifyClient(
    proxy=os.getenv("SPOTIFY_PROXY"),
    timeout=int(os.getenv("SPOTIFY_TIMEOUT", "30")),
)
```

#### Batch Operations

```python
from spotify_scraper import SpotifyClient
import asyncio

client = SpotifyClient()

# Process multiple tracks
track_urls = [
    "https://open.spotify.com/track/track1",
    "https://open.spotify.com/track/track2",
    "https://open.spotify.com/track/track3",
]

# Synchronous batch processing
tracks = [client.get_track(url) for url in track_urls]

# Download all previews
for track in tracks:
    if track.get("preview_url"):
        client.download_preview(track["id"], path="downloads/")
```

### CLI Usage

```bash
# Get track information
spotifyscraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6

# Download album with previews
spotifyscraper album https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3 --download

# Get artist top tracks
spotifyscraper artist https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb --top-tracks

# Download playlist
spotifyscraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --download --output-dir ./music

# With authentication
spotifyscraper --auth-token YOUR_TOKEN track https://open.spotify.com/track/xyz --lyrics
```

## 📚 API Reference

### SpotifyClient

The main interface for interacting with Spotify content.

```python
class SpotifyClient:
    def __init__(
        self,
        auth_token: Optional[str] = None,
        cookie_file: Optional[str] = None,
        proxy: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        config: Optional[Config] = None,
    ) -> None:
        """Initialize Spotify client with optional authentication and configuration."""
```

#### Key Methods

| Method | Description | Returns |
|--------|-------------|----------|
| `get_track(url_or_id)` | Extract track metadata | `TrackDict` |
| `get_album(url_or_id)` | Extract album with all tracks | `AlbumDict` |
| `get_artist(url_or_id)` | Extract artist profile | `ArtistDict` |
| `get_playlist(url_or_id)` | Extract playlist tracks | `PlaylistDict` |
| `get_lyrics(track_id)` | Get song lyrics (auth required) | `LyricsDict` |
| `download_preview(track_id, **kwargs)` | Download track preview MP3 | `str` (file path) |
| `download_cover(entity_id, **kwargs)` | Download cover art | `str` (file path) |
| `search(query, limit, type)` | Search Spotify content | `SearchResults` |

### Data Types

All returned data uses TypedDict for type safety:

```python
from spotify_scraper.types import TrackDict, AlbumDict, ArtistDict

# Type hints provide IDE support
track: TrackDict = client.get_track("...")
print(track["name"])  # IDE knows this is a string
print(track["duration_ms"])  # IDE knows this is an int
```

## 🔄 Migration from v1.x

If you're upgrading from version 1.x, here are the key changes:

```python
# Old way (1.x)
from SpotifyScraper.scraper import Scraper, Request

request = Request().request()
track_info = Scraper(session=request).get_track_url_info(url='https://open.spotify.com/track/7wqpAYuSk84f0JeqCIETRV')

# New way (2.x)
from spotify_scraper import SpotifyClient

client = SpotifyClient()
track_info = client.get_track('https://open.spotify.com/track/7wqpAYuSk84f0JeqCIETRV')
```

For backward compatibility, the old API is still available:

```python
# Backward compatibility
from spotify_scraper.compat import Scraper, Request

request = Request().request()
track_info = Scraper(session=request).get_track_url_info(url='https://open.spotify.com/track/7wqpAYuSk84f0JeqCIETRV')
```

### Key Changes in v2.0

1. **New API Structure**: Simplified client-based approach
2. **Enhanced Type Safety**: Full type hints throughout
3. **Better Error Handling**: Detailed exceptions with recovery hints
4. **Improved Performance**: Connection pooling and caching
5. **Media Download**: Built-in download capabilities
6. **Async Support**: Optional async/await patterns

See the [CHANGELOG](CHANGELOG.md) for a complete list of changes.

## 📖 Documentation

- 📚 **[Full Documentation](https://spotifyscraper.readthedocs.io/)** - Comprehensive guides and API reference
- 💡 **[Examples](https://github.com/AliAkhtari78/SpotifyScraper/tree/main/examples)** - Real-world usage examples
- 🔧 **[API Reference](https://spotifyscraper.readthedocs.io/en/latest/api/)** - Detailed method documentation
- 📝 **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- 🔄 **[Migration Guide](https://spotifyscraper.readthedocs.io/en/latest/migration/)** - Upgrading from v1.x
- ❓ **[FAQ](https://spotifyscraper.readthedocs.io/en/latest/faq/)** - Common questions and solutions

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=spotify_scraper

# Run linting
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_track_extractor.py

# Run with verbose output
pytest -v

# Run integration tests only
pytest tests/integration/
```

## 🤝 Contributing

We love your input! We want to make contributing to SpotifyScraper as easy and transparent as possible. Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code of Conduct
- Development process
- How to propose changes
- How to report bugs
- How to request features

## 🚀 Performance

- **Fast**: Optimized parsing with minimal overhead
- **Efficient**: Connection pooling reduces latency
- **Scalable**: Process hundreds of tracks per minute
- **Reliable**: Automatic retries with exponential backoff

## 🔒 Security

- **No API Keys**: No risk of key exposure or revocation
- **Read-Only**: Only reads public data, no write operations
- **Input Validation**: All inputs sanitized and validated
- **Secure Connections**: SSL/TLS for all requests

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all [contributors](https://github.com/AliAkhtari78/SpotifyScraper/graphs/contributors) who have helped improve this library
- Inspired by the need for accessible Spotify data extraction
- Built with ❤️ by [Ali Akhtari](https://github.com/AliAkhtari78)

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
- 📖 **Documentation**: [Read the Docs](https://spotifyscraper.readthedocs.io/)
- 💬 **Community**: [Discord Server](https://discord.gg/spotifyscraper)
- 📧 **Email**: [ali@aliakhtari.com](mailto:ali@aliakhtari.com)

## 📈 Project Status

- ✅ **Active Development**: Regular updates and improvements
- 📊 **Downloads**: 50K+ monthly downloads
- ⭐ **Stars**: 1K+ GitHub stars
- 🔧 **Version**: 2.0.0 (Stable)

---

<p align="center">
  Made with ❤️ by the open-source community
</p>
