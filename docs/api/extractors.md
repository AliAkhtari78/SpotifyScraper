# Extractors API Reference

Extractors are specialized classes that handle data extraction for specific Spotify entity types. Each extractor knows how to parse and structure data for its entity type.

## Base Extractor Pattern

All extractors follow a common pattern:

```python
from spotify_scraper.browsers import Browser
from spotify_scraper.extractors import TrackExtractor

browser = Browser()
extractor = TrackExtractor(browser)
data = extractor.extract(url)
```

## TrackExtractor

Extract information from Spotify track URLs.

### Class: TrackExtractor

```python
from spotify_scraper.extractors import TrackExtractor
```

#### Constructor

##### `__init__(browser: Browser)`

Initialize a TrackExtractor instance.

**Parameters:**
- `browser` (Browser): Browser instance for web requests

#### Methods

##### `extract(url: str) -> TrackData`

Extract track information from a URL.

**Parameters:**
- `url` (str): Spotify track URL (regular or embed format)

**Returns:**
- `TrackData`: Dictionary containing track information

**Example:**
```python
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.extractors import TrackExtractor

browser = RequestsBrowser()
extractor = TrackExtractor(browser)

# Extract from regular URL
track_data = extractor.extract("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")

# Extract from embed URL
embed_data = extractor.extract("https://open.spotify.com/embed/track/6rqhFgbbKwnb9MLmUQDhG6")
```

##### `get_track_info(track_data: Dict[str, Any]) -> Dict[str, Any]`

Parse track information from raw data.

**Parameters:**
- `track_data` (Dict): Raw track data from Spotify

**Returns:**
- `Dict`: Parsed track information

##### `get_lyrics(track_id: str) -> Optional[LyricsData]`

Get lyrics for a track (requires authentication).

**Parameters:**
- `track_id` (str): Spotify track ID

**Returns:**
- `Optional[LyricsData]`: Lyrics data if available, None otherwise

## AlbumExtractor

Extract information from Spotify album URLs.

### Class: AlbumExtractor

```python
from spotify_scraper.extractors import AlbumExtractor
```

#### Constructor

##### `__init__(browser: Browser)`

Initialize an AlbumExtractor instance.

**Parameters:**
- `browser` (Browser): Browser instance for web requests

#### Methods

##### `extract(url: str) -> AlbumData`

Extract album information from a URL.

**Parameters:**
- `url` (str): Spotify album URL

**Returns:**
- `AlbumData`: Dictionary containing album information

**Example:**
```python
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.extractors import AlbumExtractor

browser = RequestsBrowser()
extractor = AlbumExtractor(browser)

album_data = extractor.extract("https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv")

print(f"Album: {album_data['name']}")
print(f"Artist: {album_data['artists'][0]['name']}")
print(f"Tracks: {len(album_data['tracks'])}")
```

## ArtistExtractor

Extract information from Spotify artist URLs.

### Class: ArtistExtractor

```python
from spotify_scraper.extractors import ArtistExtractor
```

#### Constructor

##### `__init__(browser: Browser)`

Initialize an ArtistExtractor instance.

**Parameters:**
- `browser` (Browser): Browser instance for web requests

#### Methods

##### `extract(url: str) -> ArtistData`

Extract artist information from a URL.

**Parameters:**
- `url` (str): Spotify artist URL

**Returns:**
- `ArtistData`: Dictionary containing artist information

**Example:**
```python
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.extractors import ArtistExtractor

browser = RequestsBrowser()
extractor = ArtistExtractor(browser)

artist_data = extractor.extract("https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb")

print(f"Artist: {artist_data['name']}")
print(f"Verified: {artist_data.get('is_verified', False)}")
print(f"Monthly Listeners: {artist_data.get('stats', {}).get('monthly_listeners', 0)}")
```

## PlaylistExtractor

Extract information from Spotify playlist URLs.

### Class: PlaylistExtractor

```python
from spotify_scraper.extractors import PlaylistExtractor
```

#### Constructor

##### `__init__(browser: Browser)`

Initialize a PlaylistExtractor instance.

**Parameters:**
- `browser` (Browser): Browser instance for web requests

#### Methods

##### `extract(url: str) -> PlaylistData`

Extract playlist information from a URL.

**Parameters:**
- `url` (str): Spotify playlist URL

**Returns:**
- `PlaylistData`: Dictionary containing playlist information

**Example:**
```python
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.extractors import PlaylistExtractor

browser = RequestsBrowser()
extractor = PlaylistExtractor(browser)

playlist_data = extractor.extract("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")

print(f"Playlist: {playlist_data['name']}")
print(f"Tracks: {playlist_data['track_count']}")
print(f"Owner: {playlist_data['owner']['name']}")
```

## Direct Extractor Usage

While the `SpotifyClient` is the recommended interface, you can use extractors directly for more control:

```python
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.extractors import TrackExtractor, AlbumExtractor
from spotify_scraper.parsers import JSONParser

# Create browser with custom settings
browser = RequestsBrowser(
    headers={'User-Agent': 'Custom User Agent'},
    timeout=30
)

# Use extractors directly
track_extractor = TrackExtractor(browser)
album_extractor = AlbumExtractor(browser)

# Extract data
track_data = track_extractor.extract(track_url)
album_data = album_extractor.extract(album_url)

# Access the parser directly if needed
parser = JSONParser()
raw_html = browser.get(url)
parsed_data = parser.parse(raw_html)
```

## Custom Extractors

You can create custom extractors by extending the base pattern:

```python
from typing import Dict, Any
from spotify_scraper.browsers import Browser
from spotify_scraper.core.exceptions import ExtractionError

class CustomExtractor:
    def __init__(self, browser: Browser):
        self.browser = browser
    
    def extract(self, url: str) -> Dict[str, Any]:
        # Validate URL
        if not self._validate_url(url):
            raise ExtractionError(f"Invalid URL: {url}")
        
        # Fetch page
        html = self.browser.get(url)
        
        # Parse data
        data = self._parse_data(html)
        
        # Process and return
        return self._process_data(data)
    
    def _validate_url(self, url: str) -> bool:
        # Custom validation logic
        return "spotify.com" in url
    
    def _parse_data(self, html: str) -> Dict[str, Any]:
        # Custom parsing logic
        pass
    
    def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Custom processing logic
        pass
```

## Error Handling

All extractors raise specific exceptions:

```python
from spotify_scraper.core.exceptions import (
    ExtractionError,
    ParsingError,
    URLError
)

try:
    data = extractor.extract(url)
except URLError as e:
    print(f"Invalid URL: {e}")
except ParsingError as e:
    print(f"Failed to parse page: {e}")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
```

## Performance Considerations

1. **Reuse Extractors**: Create once and reuse for multiple extractions
2. **Browser Caching**: Some browsers cache responses automatically
3. **Parallel Extraction**: Use threading for multiple URLs (with care)

```python
import concurrent.futures
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.extractors import TrackExtractor

browser = RequestsBrowser()
extractor = TrackExtractor(browser)

urls = [
    "https://open.spotify.com/track/...",
    "https://open.spotify.com/track/...",
    # more URLs
]

# Parallel extraction (be mindful of rate limits)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(extractor.extract, urls))
```

## Data Structure Reference

### TrackData
- `id`: Spotify track ID
- `name`: Track name
- `uri`: Spotify URI
- `type`: "track"
- `duration_ms`: Duration in milliseconds
- `artists`: List of artist objects
- `album`: Album object
- `preview_url`: Preview URL (optional)
- `is_playable`: Playability flag
- `is_explicit`: Explicit content flag
- `lyrics`: Lyrics object (optional, requires auth)

### AlbumData
- `id`: Spotify album ID
- `name`: Album name
- `uri`: Spotify URI
- `type`: "album"
- `artists`: List of artist objects
- `images`: List of image objects
- `release_date`: Release date
- `total_tracks`: Track count
- `tracks`: List of track objects

### ArtistData
- `id`: Spotify artist ID
- `name`: Artist name
- `uri`: Spotify URI
- `type`: "artist"
- `is_verified`: Verification status
- `bio`: Biography (optional)
- `images`: List of image objects
- `stats`: Statistics object
- `top_tracks`: List of top tracks

### PlaylistData
- `id`: Spotify playlist ID
- `name`: Playlist name
- `uri`: Spotify URI
- `type`: "playlist"
- `description`: Description (optional)
- `owner`: Owner object
- `images`: List of image objects
- `track_count`: Number of tracks
- `tracks`: List of track objects