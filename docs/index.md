# SpotifyScraper Documentation

**SpotifyScraper** is a modern, fast, and efficient Python library for extracting data from Spotify's web player. Built for version 2.0, it uses advanced parsing techniques to extract metadata, lyrics, and media from Spotify without requiring API credentials.

## Overview

SpotifyScraper provides:

- **Zero Authentication Required**: Extract publicly available data without Spotify API credentials
- **Modern Architecture**: Handles Spotify's React-based interface using JSON data extraction
- **Multiple Entity Support**: Extract data from tracks, albums, artists, and playlists
- **Media Downloads**: Download preview audio and cover images with metadata
- **Flexible Browser Options**: Use lightweight requests or Selenium for complex scenarios
- **Type Safety**: Full typing support with TypedDict definitions
- **CLI Support**: Command-line interface for quick operations

## Key Features

### Data Extraction
- **Track Information**: Title, artists, album, duration, preview URL, lyrics (with authentication)
- **Album Details**: Track listings, release dates, cover art, artist information
- **Artist Profiles**: Biography, top tracks, discography statistics, images
- **Playlist Contents**: Track listings, descriptions, owner information, cover art

### Media Handling
- **Audio Downloads**: Preview MP3s with embedded metadata and cover art
- **Image Downloads**: High-quality cover art in multiple sizes
- **Metadata Embedding**: Automatic ID3 tag population for downloaded audio

### Advanced Features
- **Cookie-based Authentication**: Access additional content like lyrics
- **Proxy Support**: Route requests through proxies
- **Custom Headers**: Set user agents and other headers
- **Error Handling**: Comprehensive exception hierarchy for precise error handling

## Requirements

- Python 3.6 or higher
- Works on Linux, Windows, macOS, BSD
- Internet connection

## Quick Start

### Installation

```bash
# Install from PyPI
pip install spotifyscraper

# Install from source
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper
pip install -e .
```

### Basic Usage

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser

# Create a client
browser = RequestsBrowser()
client = SpotifyClient(browser=browser)

# Extract track information
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track_data = client.get_track(track_url)

print(f"Track: {track_data['name']}")
print(f"Artist: {track_data['artists'][0]['name']}")
print(f"Album: {track_data['album']['name']}")
```

## Documentation Structure

- **[API Reference](api/)** - Complete API documentation for all classes and functions
  - [Client API](api/client.md) - Main SpotifyClient interface
  - [Extractors](api/extractors.md) - Data extraction classes
  - [Media Handlers](api/media.md) - Audio and image download utilities
  - [Exceptions](api/exceptions.md) - Error handling reference
  - [Utilities](api/utils.md) - Helper functions and utilities

- **[Examples](examples/)** - Practical usage examples
  - [Quick Start Guide](examples/quickstart.md) - Get started in minutes
  - [Advanced Usage](examples/advanced.md) - Complex scenarios and patterns
  - [CLI Guide](examples/cli.md) - Command-line interface documentation

## Version History

### Version 2.0.0 (Current)
- Complete rewrite with modern architecture
- React-based Spotify interface support
- TypedDict type definitions
- Enhanced media downloading
- Improved error handling

### Version 1.x (Legacy)
- BeautifulSoup-based scraping
- Basic track and playlist extraction
- Simple media downloads

## Contributing

SpotifyScraper is an open-source project. Contributions are welcome! Please see our [Contributing Guide](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/AliAkhtari78/SpotifyScraper)
- [PyPI Package](https://pypi.org/project/spotifyscraper/)
- [Issue Tracker](https://github.com/AliAkhtari78/SpotifyScraper/issues)
- [Changelog](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/CHANGELOG.md)