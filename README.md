# SpotifyScraper 🎵

![Version](https://img.shields.io/badge/version-2.0.0-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Maintained](https://img.shields.io/badge/Maintained-Yes-green.svg)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://spotifyscraper.readthedocs.io/en/latest/)

A modern Python library for extracting data from Spotify's web interface without using the official API.

## 🚀 Quick Example

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

## 🌟 Features

- 💾 **Extract detailed information** from Spotify tracks, albums, artists, and playlists
- 🎧 **Download preview audio** with metadata and embedded cover art
- 🖼️ **Download cover images** in various sizes and formats
- 🔍 **Search for content** and get structured results
- 🔐 **Authentication support** for accessing additional content
- 🖥️ **Browser abstraction** with support for both requests and Selenium
- 🔄 **Graceful fallbacks** when content structure changes

## 📋 Requirements

- Python 3.8 or higher
- Works on Windows, macOS, Linux, and other platforms
- Internet connection

## 📦 Installation

### Quick Installation

```bash
pip install -U spotifyscraper
```

### Installation with Selenium Support

For advanced features like accessing authenticated content:

```bash
pip install -U "spotifyscraper[selenium]"
```

### Development Installation

For contributing to the project:

```bash
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper
pip install -e ".[dev]"
```

## 📖 Usage Examples

### Extract Track Information

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

### Extract Album Information

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

### Extract Artist Information

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

### Extract Playlist Information

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

### Download Preview MP3

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

### Download Cover Image

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

### With Authentication

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
```

## 🔄 Migrating from 1.x

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

## 📚 Documentation

- [Full Documentation](https://spotifyscraper.readthedocs.io/) - Complete API reference and guides
- [Examples](https://github.com/AliAkhtari78/SpotifyScraper/tree/main/examples) - More usage examples
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to the project

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See the [Contributing Guide](CONTRIBUTING.md) for more details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Get in touch

- Report bugs, suggest features, or view the source code [on GitHub](https://github.com/AliAkhtari78/SpotifyScraper).
- Read the [documentation](https://spotifyscraper.readthedocs.io/) for more detailed information.
- Contact the author through [GitHub](https://github.com/AliAkhtari78) or [website](https://aliakhtari.com/).
