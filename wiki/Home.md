# SpotifyScraper Wiki

## Overview

SpotifyScraper is a powerful Python library for extracting data from Spotify's web player. Built for speed and reliability, it provides a clean API for accessing track, album, artist, and playlist information without requiring Spotify API credentials.

### Key Features

- 🚀 **Fast and Efficient**: Uses optimized web scraping techniques for quick data extraction
- 🔐 **No API Key Required**: Works without Spotify Developer credentials
- 📊 **Comprehensive Data**: Extract detailed metadata, lyrics, and media files
- 🎵 **Media Downloads**: Download preview MP3s and cover images
- 🌐 **Flexible Browser Backends**: Choose between lightweight requests or full Selenium support
- 🔧 **Modern Python**: Type hints, async support, and clean API design
- 📦 **Easy Installation**: Available on PyPI with minimal dependencies

## Quick Example

```python
from spotify_scraper import SpotifyClient

# Create a client
client = SpotifyClient()

# Extract track information
track = client.get_track_info("https://open.spotify.com/track/...")
print(f"{track['name']} by {track['artists'][0]['name']}")

# Download preview and cover
client.download_preview_mp3(track_url, path="previews/")
client.download_cover(track_url, path="covers/")
```

## Supported Data Types

- **Tracks**: Name, artists, album, duration, preview URL, lyrics (with auth)
- **Albums**: Track listing, release date, label, cover art
- **Artists**: Biography, top tracks, discography, monthly listeners
- **Playlists**: Track list, description, owner, collaborative status

## Requirements

- Python 3.8+
- Works on Windows, macOS, Linux, BSD
- Internet connection

## Documentation

- [Installation Guide](Installation)
- [Quick Start](Quick-Start)
- [API Reference](API-Reference)
- [Examples](Examples)
- [FAQ](FAQ)

## Why SpotifyScraper?

Unlike the official Spotify API, SpotifyScraper:
- Requires no registration or API keys
- Has no rate limits or quotas
- Can download preview MP3s and cover images
- Provides a simpler, more intuitive API
- Works with any Spotify URL format

## License

SpotifyScraper is released under the MIT License. See [LICENSE](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
- **Documentation**: [Read the Docs](https://spotifyscraper.readthedocs.io/)

---

*SpotifyScraper v2.0.0 - Last updated: January 2025*