# Features

SpotifyScraper offers comprehensive features for extracting data from Spotify.

## Core Features

### 🎵 Music Data Extraction
- **Tracks** - Complete metadata including artists, album, duration
- **Albums** - Full album info with track listings and artwork
- **Artists** - Profile data, genres, popularity, discography
- **Playlists** - All tracks, owner info, collaborative status

### 🔧 Technical Features
- **Multiple Browser Backends** - Requests or Selenium
- **Flexible Input** - URLs or IDs, including embed URLs
- **Advanced Caching** - Memory, disk, or Redis backends
- **Robust Error Handling** - Automatic retries

### 💻 Developer Features
- **Clean API** - Simple, intuitive methods
- **Type Safety** - Full type hints
- **Extensibility** - Plugin architecture
- **Configuration** - Multiple config sources

### 🚀 Performance
- **Optimization** - Connection pooling
- **Scalability** - Distributed processing
- **Efficiency** - Low memory footprint

## CLI Features

```bash
# Extract track
spotify-scraper track TRACK_ID

# Batch process
spotify-scraper batch tracks.txt -o results.json

# Export playlist
spotify-scraper playlist PLAYLIST_ID --format csv
```

## Coming Soon
- GraphQL API support
- Real-time updates
- Advanced audio analysis

See [Examples](examples/index.md) for practical usage.