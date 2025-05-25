# Utils Module

The `utils` module provides utility functions and helpers used throughout SpotifyScraper.

## URL Utilities

```python
from spotify_scraper.utils import url
```

### Functions

#### is_spotify_url

```python
is_spotify_url(url: str) -> bool
```

Check if a URL is a valid Spotify URL.

**Example:**
```python
from spotify_scraper.utils.url import is_spotify_url

is_spotify_url("https://open.spotify.com/track/123")  # True
is_spotify_url("https://example.com")  # False
```

#### extract_id

```python
extract_id(url: str) -> str
```

Extract Spotify ID from URL.

**Example:**
```python
from spotify_scraper.utils.url import extract_id

track_id = extract_id("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
# Returns: "4iV5W9uYEdYUVa79Axb7Rh"
```

#### get_url_type

```python
get_url_type(url: str) -> str
```

Determine entity type from URL.

**Example:**
```python
from spotify_scraper.utils.url import get_url_type

entity_type = get_url_type("https://open.spotify.com/album/123")
# Returns: "album"
```

#### convert_to_embed_url

```python
convert_to_embed_url(url: str) -> str
```

Convert regular Spotify URL to embed format.

**Example:**
```python
from spotify_scraper.utils.url import convert_to_embed_url

embed_url = convert_to_embed_url("https://open.spotify.com/track/123")
# Returns: "https://open.spotify.com/embed/track/123"
```

## Logger Utilities

```python
from spotify_scraper.utils import logger
```

### Functions

#### get_logger

```python
get_logger(name: str, level: str = "INFO") -> logging.Logger
```

Get a configured logger instance.

**Example:**
```python
from spotify_scraper.utils.logger import get_logger

log = get_logger(__name__)
log.info("Starting extraction")
log.error("Failed to extract", exc_info=True)
```

## Common Utilities

```python
from spotify_scraper.utils import common
```

### Functions

#### clean_filename

```python
clean_filename(filename: str) -> str
```

Clean filename for safe file system usage.

**Example:**
```python
from spotify_scraper.utils.common import clean_filename

safe_name = clean_filename("Track/Name: Special?")
# Returns: "Track_Name_ Special_"
```

## Advanced Utilities

### SpotifyBulkOperations

```python
from spotify_scraper.utils import SpotifyBulkOperations

bulk = SpotifyBulkOperations(client)

# Get multiple tracks
track_urls = [
    "https://open.spotify.com/track/123",
    "https://open.spotify.com/track/456"
]
tracks = bulk.get_multiple_tracks(track_urls)

# Get artist discography
discography = bulk.get_artist_discography(artist_url)

# Get full playlist (handles pagination)
full_playlist = bulk.get_full_playlist(playlist_url)
```

### SpotifyDataAnalyzer

```python
from spotify_scraper.utils import SpotifyDataAnalyzer

analyzer = SpotifyDataAnalyzer()

# Analyze playlist
playlist_data = client.get_playlist_info(playlist_url)
stats = analyzer.analyze_playlist(playlist_data)
print(f"Total duration: {stats['total_duration_ms']} ms")
print(f"Average track length: {stats['avg_track_duration_ms']} ms")

# Get genre distribution
genre_dist = analyzer.get_genre_distribution(tracks)
for genre, count in genre_dist.items():
    print(f"{genre}: {count} tracks")
```

## See Also

- [Client Module](client.md) - Main client interface
- [Examples](../examples/index.md) - Usage examples