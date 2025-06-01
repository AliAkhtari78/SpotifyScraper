# SpotifyScraper

**Extract Spotify data without the official API**. Access tracks, albums, artists, and playlists - no authentication required.

## Features

- 🔓 **No API Key Required** - Start extracting data immediately
- 🚀 **Fast & Lightweight** - Optimized for speed and minimal dependencies  
- 📊 **Complete Metadata** - Get all available track, album, artist details
- 💿 **Media Downloads** - Download cover art and preview clips
- 🔄 **Bulk Operations** - Process multiple URLs efficiently
- 🛡️ **Robust & Reliable** - Comprehensive error handling and retries

## Installation

```bash
pip install spotifyscraper
```

## Quick Start

```python
from spotify_scraper import SpotifyClient

# Initialize client
client = SpotifyClient()

# Get track info
track = client.get_track_info("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
print(f"{track.get('name', 'Unknown')} by {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")

# Download cover art
cover_path = client.download_cover("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")

client.close()
```

## Main Features

### Extract Data
- **Tracks**: Name, artists, album, duration, preview URL, popularity
- **Albums**: Track listing, release date, label, cover art
- **Artists**: Biography, top tracks, monthly listeners, genres
- **Playlists**: All tracks, owner info, description

### Download Media
- 30-second preview MP3s
- Album/track cover art in multiple sizes
- Batch download support

### Bulk Operations
```python
from spotify_scraper.utils.common import SpotifyBulkOperations

bulk = SpotifyBulkOperations()
urls = ["track_url_1", "track_url_2", "album_url"]

# Process multiple URLs
results = bulk.process_urls(urls, operation="all_info")

# Export data
bulk.export_to_json(results, "spotify_data.json")
bulk.export_to_csv(results, "spotify_data.csv")
```

## CLI Usage

```bash
# Get track info
spotify-scraper track [URL]

# Download album with covers  
spotify-scraper download album [URL] --with-covers

# Export playlist as JSON
spotify-scraper playlist [URL] --output playlist.json
```

## Requirements

- Python 3.8+
- Works on Windows, macOS, Linux

## Documentation

Full documentation: https://spotifyscraper.readthedocs.io/

- Installation guide
- API reference  
- Examples and tutorials
- CLI documentation
- Troubleshooting

## License

MIT License - see LICENSE file for details.

## Links

- GitHub: https://github.com/AliAkhtari78/SpotifyScraper
- Documentation: https://spotifyscraper.readthedocs.io/
- Issues: https://github.com/AliAkhtari78/SpotifyScraper/issues