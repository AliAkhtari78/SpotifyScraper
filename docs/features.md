# Features

SpotifyScraper offers comprehensive features for extracting data from Spotify.

## Core Features

### 🎵 Music Data Extraction
- **Tracks** - Complete metadata including artists, album, duration, preview URLs
- **Albums** - Full album info with track listings and artwork
- **Artists** - Profile data, genres, popularity, top tracks
- **Playlists** - All tracks, owner info, descriptions
- **Lyrics** - Not available (requires OAuth Bearer tokens, not supported)

### 📥 Media Download
- **Audio Previews** - Download 30-second MP3 previews
- **Cover Art** - Download album/track artwork in multiple sizes
- **Metadata Embedding** - Add cover art to downloaded MP3s

### 🔧 Technical Features
- **Multiple Browser Backends** - RequestsBrowser (default) or SeleniumBrowser
- **Flexible Input** - URLs or IDs, including embed URLs
- **Smart URL Handling** - Automatic conversion and validation
- **Robust Error Handling** - Custom exception hierarchy
- **Type Safety** - Full type hints and TypedDict structures

### 💻 Developer Features
- **Clean API** - Simple, intuitive methods like `get_track_info()`
- **Modular Architecture** - Separate extractors for each resource type
- **Extensible Design** - Easy to add custom extractors
- **Comprehensive Logging** - Built-in logger with configurable levels

### 🚀 Performance
- **Efficient Parsing** - Optimized JSON extraction
- **Connection Reuse** - Session management for better performance
- **Low Memory Footprint** - Streaming downloads for media files

## CLI Features

### Command Line Interface
- **Track Operations** - Extract info, download preview/cover
- **Album Operations** - Get full album data with all tracks
- **Artist Operations** - Extract artist profile and stats
- **Playlist Operations** - Export playlists with all track details
- **Batch Processing** - Process multiple URLs from files
- **Multiple Export Formats** - JSON, CSV, YAML output

```bash
# Extract track information
spotify-scraper track https://open.spotify.com/track/TRACK_ID

# Download track preview and cover
spotify-scraper download https://open.spotify.com/track/TRACK_ID

# Export playlist to CSV
spotify-scraper playlist https://open.spotify.com/playlist/PLAYLIST_ID --format csv

# Batch process URLs from file
spotify-scraper download --from-file urls.txt --output-dir ./downloads
```

## Data Structures

### Type-Safe Responses
All methods return properly typed dictionaries with consistent structure:

- **TrackInfo** - id, name, artists, album, duration_ms, preview_url, etc.
- **AlbumInfo** - id, name, artists, tracks, release_date, images, etc.
- **ArtistInfo** - id, name, genres, popularity, followers, images, etc.
- **PlaylistInfo** - id, name, owner, tracks, track_count, description, etc.

## Utility Features

### URL Utilities
- `is_spotify_url()` - Validate Spotify URLs
- `extract_id()` - Extract ID from any Spotify URL
- `convert_to_embed_url()` - Convert regular URLs to embed format
- `get_url_type()` - Detect resource type from URL

### Bulk Operations
- `SpotifyBulkOperations` - Process multiple resources efficiently
- `SpotifyDataAnalyzer` - Analyze playlists and track collections

## Authentication

- **Cookie-Based Auth** - Use browser cookies for authenticated features
- **Lyrics Access** - Not available (requires OAuth authentication)
- **No API Keys Required** - Works without Spotify API credentials

## Error Handling

- **SpotifyScraperError** - Base exception class
- **URLError** - Invalid Spotify URL errors
- **NetworkError** - Connection and timeout issues
- **ExtractionError** - Data parsing failures
- **AuthenticationError** - Cookie/auth problems
- **MediaError** - Download failures

See [Examples](examples/index.md) for practical usage and [API Reference](api/index.md) for detailed documentation.