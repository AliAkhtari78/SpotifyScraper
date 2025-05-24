# Extractors Module

The `extractors` module contains specialized classes for extracting data from different Spotify entities.

## Overview

Extractors transform raw JSON data from Spotify pages into structured, consistent data formats.

```python
from spotify_scraper.extractors import (
    TrackExtractor,
    AlbumExtractor,
    ArtistExtractor,
    PlaylistExtractor
)
```

## TrackExtractor

Extracts track information from Spotify HTML pages.

### Methods

#### extract

```python
extract(html: str, url: str) -> Dict[str, Any]
```

Extract track data from HTML content.

**Parameters:**
- `html` (str): Raw HTML content from Spotify
- `url` (str): URL of the track page

**Returns:**
- Dict containing track metadata

**Example:**
```python
from spotify_scraper.extractors import TrackExtractor
from spotify_scraper.parsers import JSONParser

parser = JSONParser()
extractor = TrackExtractor(parser)

# Assuming you have HTML content
track_data = extractor.extract(html_content, track_url)
```### Data Structure

```python
{
    "id": "4iV5W9uYEdYUVa79Axb7Rh",
    "name": "Hotel California",
    "duration_ms": 391376,
    "explicit": False,
    "artists": [
        {
            "id": "0OdUWJ0sBjDrqHygGUXeCF",
            "name": "Eagles",
            "type": "artist"
        }
    ],
    "album": {
        "id": "4aawyAB9vmqN3uQ7FjRGTy",
        "name": "Hotel California",
        "images": [
            {
                "url": "https://i.scdn.co/image/...",
                "width": 640,
                "height": 640
            }
        ]
    },
    "track_number": 1,
    "disc_number": 1,
    "popularity": 89,
    "preview_url": "https://p.scdn.co/mp3-preview/...",
    "external_urls": {
        "spotify": "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
    },
    "uri": "spotify:track:4iV5W9uYEdYUVa79Axb7Rh"
}
```

## AlbumExtractor

Extracts album information including track listings.

### Methods

#### extract

```python
extract(html: str, url: str) -> Dict[str, Any]
```

Extract album data from HTML content.**Parameters:**
- `html` (str): Raw HTML content from Spotify
- `url` (str): URL of the album page

**Returns:**
- Dict containing album metadata and tracks

### Data Structure

```python
{
    "id": "4aawyAB9vmqN3uQ7FjRGTy",
    "name": "Hotel California",
    "album_type": "album",
    "release_date": "1976-12-08",
    "total_tracks": 9,
    "artists": [
        {
            "id": "0OdUWJ0sBjDrqHygGUXeCF",
            "name": "Eagles"
        }
    ],
    "tracks": [
        {
            "id": "4iV5W9uYEdYUVa79Axb7Rh",
            "name": "Hotel California",
            "duration_ms": 391376,
            "track_number": 1
        }
        // ... more tracks
    ],
    "images": [...],
    "copyrights": [...],
    "label": "Asylum Records"
}
```

## ArtistExtractor

Extracts artist profile information.

### Methods

#### extract

```python
extract(html: str, url: str) -> Dict[str, Any]
```

Extract artist data from HTML content.**Parameters:**
- `html` (str): Raw HTML content from Spotify
- `url` (str): URL of the artist page

**Returns:**
- Dict containing artist metadata

### Data Structure

```python
{
    "id": "0OdUWJ0sBjDrqHygGUXeCF",
    "name": "Eagles",
    "genres": ["classic rock", "rock", "soft rock"],
    "popularity": 83,
    "followers": {
        "total": 28543211
    },
    "images": [...],
    "type": "artist",
    "uri": "spotify:artist:0OdUWJ0sBjDrqHygGUXeCF"
}
```

## PlaylistExtractor

Extracts playlist information including all tracks.

### Methods

#### extract

```python
extract(html: str, url: str) -> Dict[str, Any]
```

Extract playlist data from HTML content.

**Parameters:**
- `html` (str): Raw HTML content from Spotify
- `url` (str): URL of the playlist page

**Returns:**
- Dict containing playlist metadata and tracks

## See Also

- [Client](client.md) - Main client interface
- [Parser](parsers.md) - JSON parsing utilities
- [Custom Extractors](../advanced/custom-extractors.md) - Creating custom extractors