# Utilities API Reference

SpotifyScraper provides various utility functions for URL manipulation, logging, and common operations.

## URL Utilities

The `spotify_scraper.utils.url` module provides comprehensive URL manipulation functions.

### Import

```python
from spotify_scraper.utils.url import (
    is_spotify_url,
    get_url_type,
    extract_id,
    clean_url,
    convert_to_embed_url,
    convert_to_regular_url,
    convert_spotify_uri_to_url,
    convert_url_to_spotify_uri,
    validate_url,
    build_url,
    extract_url_components
)
```

### Functions

#### `is_spotify_url(url: str) -> bool`

Check if a URL is a valid Spotify URL.

**Parameters:**
- `url` (str): URL to check

**Returns:**
- `bool`: True if valid Spotify URL, False otherwise

**Example:**
```python
>>> is_spotify_url("https://open.spotify.com/track/123")
True
>>> is_spotify_url("https://example.com/track/123")
False
```

#### `get_url_type(url: str) -> URLType`

Get the type of Spotify URL.

**Parameters:**
- `url` (str): Spotify URL

**Returns:**
- `URLType`: One of "track", "album", "artist", "playlist", "search", or "unknown"

**Raises:**
- `URLError`: If not a valid Spotify URL

**Example:**
```python
>>> get_url_type("https://open.spotify.com/track/123")
"track"
>>> get_url_type("https://open.spotify.com/album/456")
"album"
>>> get_url_type("https://open.spotify.com/embed/track/123")
"track"
```

#### `extract_id(url: str) -> str`

Extract the Spotify ID from a URL.

**Parameters:**
- `url` (str): Spotify URL

**Returns:**
- `str`: Spotify ID

**Raises:**
- `URLError`: If URL is invalid or ID cannot be extracted

**Example:**
```python
>>> extract_id("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
"6rqhFgbbKwnb9MLmUQDhG6"
>>> extract_id("https://open.spotify.com/embed/track/6rqhFgbbKwnb9MLmUQDhG6")
"6rqhFgbbKwnb9MLmUQDhG6"
```

#### `clean_url(url: str) -> str`

Clean a Spotify URL by removing query parameters.

**Parameters:**
- `url` (str): Spotify URL

**Returns:**
- `str`: Cleaned URL

**Example:**
```python
>>> clean_url("https://open.spotify.com/track/123?si=abcd&utm_source=copy")
"https://open.spotify.com/track/123"
```

#### `convert_to_embed_url(url: str) -> str`

Convert a regular Spotify URL to an embed URL.

**Parameters:**
- `url` (str): Regular Spotify URL

**Returns:**
- `str`: Equivalent embed URL

**Raises:**
- `URLError`: If URL is invalid or cannot be converted

**Example:**
```python
>>> convert_to_embed_url("https://open.spotify.com/track/123")
"https://open.spotify.com/embed/track/123"
```

#### `convert_to_regular_url(url: str) -> str`

Convert an embed Spotify URL to a regular URL.

**Parameters:**
- `url` (str): Embed Spotify URL

**Returns:**
- `str`: Equivalent regular URL

**Raises:**
- `URLError`: If URL is invalid or cannot be converted

**Example:**
```python
>>> convert_to_regular_url("https://open.spotify.com/embed/track/123")
"https://open.spotify.com/track/123"
```

#### `convert_spotify_uri_to_url(uri: str) -> str`

Convert a Spotify URI to a regular URL.

**Parameters:**
- `uri` (str): Spotify URI (e.g., "spotify:track:6rqhFgbbKwnb9MLmUQDhG6")

**Returns:**
- `str`: Equivalent regular URL

**Raises:**
- `URLError`: If URI is invalid or cannot be converted

**Example:**
```python
>>> convert_spotify_uri_to_url("spotify:track:6rqhFgbbKwnb9MLmUQDhG6")
"https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
>>> convert_spotify_uri_to_url("spotify:album:4LH4d3cOWNNsVw41Gqt2kv")
"https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"
```

#### `convert_url_to_spotify_uri(url: str) -> str`

Convert a Spotify URL to a URI.

**Parameters:**
- `url` (str): Spotify URL

**Returns:**
- `str`: Equivalent Spotify URI

**Raises:**
- `URLError`: If URL is invalid or cannot be converted

**Example:**
```python
>>> convert_url_to_spotify_uri("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
"spotify:track:6rqhFgbbKwnb9MLmUQDhG6"
```

#### `validate_url(url: str, expected_type: Optional[URLType] = None) -> bool`

Validate a Spotify URL.

**Parameters:**
- `url` (str): URL to validate
- `expected_type` (Optional[URLType]): Expected URL type

**Returns:**
- `bool`: True if valid

**Raises:**
- `URLError`: If URL is invalid

**Example:**
```python
>>> validate_url("https://open.spotify.com/track/123")
True
>>> validate_url("https://open.spotify.com/track/123", expected_type="track")
True
>>> validate_url("https://open.spotify.com/album/123", expected_type="track")
URLError: URL is not a Spotify track URL
```

#### `build_url(resource_type: URLType, resource_id: str, embed: bool = False, query_params: Optional[Dict[str, str]] = None) -> str`

Build a Spotify URL for a given resource.

**Parameters:**
- `resource_type` (URLType): Resource type ("track", "album", "artist", "playlist")
- `resource_id` (str): Resource ID
- `embed` (bool): Whether to create an embed URL (default: False)
- `query_params` (Optional[Dict[str, str]]): Query parameters to include

**Returns:**
- `str`: Constructed URL

**Raises:**
- `URLError`: If parameters are invalid

**Example:**
```python
>>> build_url("track", "6rqhFgbbKwnb9MLmUQDhG6")
"https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"

>>> build_url("track", "6rqhFgbbKwnb9MLmUQDhG6", embed=True)
"https://open.spotify.com/embed/track/6rqhFgbbKwnb9MLmUQDhG6"

>>> build_url("track", "123", query_params={"si": "abcd"})
"https://open.spotify.com/track/123?si=abcd"
```

#### `extract_url_components(url: str) -> Tuple[URLType, str, Dict[str, str]]`

Extract components from a Spotify URL.

**Parameters:**
- `url` (str): Spotify URL

**Returns:**
- `Tuple[URLType, str, Dict[str, str]]`: (resource_type, resource_id, query_params)

**Raises:**
- `URLError`: If URL is invalid or components cannot be extracted

**Example:**
```python
>>> extract_url_components("https://open.spotify.com/track/123?si=abcd")
("track", "123", {"si": "abcd"})
```

## Logging Utilities

The `spotify_scraper.utils.logger` module provides logging configuration.

### Import

```python
from spotify_scraper.utils.logger import setup_logger, get_logger
```

### Functions

#### `setup_logger(name: str = "spotify_scraper", level: str = "INFO") -> logging.Logger`

Set up a logger with console output.

**Parameters:**
- `name` (str): Logger name (default: "spotify_scraper")
- `level` (str): Logging level (default: "INFO")

**Returns:**
- `logging.Logger`: Configured logger

**Example:**
```python
import logging
from spotify_scraper.utils.logger import setup_logger

# Set up basic logging
logger = setup_logger()

# Set up with debug level
debug_logger = setup_logger(level="DEBUG")

# Set up for specific module
module_logger = setup_logger(name="my_module", level="WARNING")
```

#### `get_logger(name: str) -> logging.Logger`

Get a logger instance.

**Parameters:**
- `name` (str): Logger name

**Returns:**
- `logging.Logger`: Logger instance

**Example:**
```python
from spotify_scraper.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Processing track...")
logger.debug("Track details: %s", track_data)
```

## Common Utilities

The `spotify_scraper.utils.common` module provides general utility functions.

### Import

```python
from spotify_scraper.utils.common import (
    sanitize_filename,
    format_duration,
    parse_date,
    retry_with_backoff
)
```

### Functions

#### `sanitize_filename(filename: str, replacement: str = "_") -> str`

Sanitize a filename for safe filesystem usage.

**Parameters:**
- `filename` (str): Original filename
- `replacement` (str): Character to replace invalid characters with (default: "_")

**Returns:**
- `str`: Sanitized filename

**Example:**
```python
>>> sanitize_filename("Track: Name / Artist")
"Track_ Name _ Artist"
>>> sanitize_filename("Song?.mp3", replacement="-")
"Song-.mp3"
```

#### `format_duration(duration_ms: int) -> str`

Format duration from milliseconds to human-readable format.

**Parameters:**
- `duration_ms` (int): Duration in milliseconds

**Returns:**
- `str`: Formatted duration (e.g., "3:45")

**Example:**
```python
>>> format_duration(225000)
"3:45"
>>> format_duration(3600000)
"1:00:00"
```

#### `parse_date(date_str: str) -> datetime`

Parse a date string into a datetime object.

**Parameters:**
- `date_str` (str): Date string

**Returns:**
- `datetime`: Parsed datetime object

**Example:**
```python
>>> parse_date("2023-12-25")
datetime.datetime(2023, 12, 25, 0, 0)
>>> parse_date("2023-12-25T10:30:00Z")
datetime.datetime(2023, 12, 25, 10, 30)
```

#### `retry_with_backoff(func: Callable, max_retries: int = 3, backoff_factor: float = 2.0)`

Decorator to retry a function with exponential backoff.

**Parameters:**
- `func` (Callable): Function to retry
- `max_retries` (int): Maximum number of retries (default: 3)
- `backoff_factor` (float): Backoff multiplication factor (default: 2.0)

**Example:**
```python
from spotify_scraper.utils.common import retry_with_backoff

@retry_with_backoff(max_retries=3)
def fetch_data(url):
    # This will retry up to 3 times with exponential backoff
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Or use as a function wrapper
retry_fetch = retry_with_backoff(fetch_data, max_retries=5)
data = retry_fetch(url)
```

## Practical Examples

### URL Validation and Processing

```python
from spotify_scraper.utils.url import (
    is_spotify_url,
    get_url_type,
    extract_id,
    clean_url,
    validate_url
)

def process_spotify_url(url):
    # Clean the URL first
    url = clean_url(url)
    
    # Validate it's a Spotify URL
    if not is_spotify_url(url):
        raise ValueError("Not a valid Spotify URL")
    
    # Get the type
    url_type = get_url_type(url)
    
    # Extract the ID
    resource_id = extract_id(url)
    
    return {
        "url": url,
        "type": url_type,
        "id": resource_id
    }

# Example usage
result = process_spotify_url("https://open.spotify.com/track/123?si=abc")
print(result)
# Output: {"url": "https://open.spotify.com/track/123", "type": "track", "id": "123"}
```

### Batch URL Processing

```python
from spotify_scraper.utils.url import extract_url_components, validate_url

def process_url_batch(urls):
    results = []
    
    for url in urls:
        try:
            validate_url(url)
            resource_type, resource_id, params = extract_url_components(url)
            results.append({
                "url": url,
                "type": resource_type,
                "id": resource_id,
                "params": params,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "url": url,
                "status": "error",
                "error": str(e)
            })
    
    return results
```

### Safe File Operations

```python
from spotify_scraper.utils.common import sanitize_filename
from spotify_scraper.media import AudioDownloader

def download_track_safely(track_data, output_dir="downloads"):
    # Create safe filename
    track_name = track_data.get("name", "unknown")
    artist_name = track_data.get("artists", [{}])[0].get("name", "unknown")
    
    filename = f"{artist_name} - {track_name}.mp3"
    safe_filename = sanitize_filename(filename)
    
    # Download with safe filename
    downloader = AudioDownloader(browser)
    return downloader.download_preview(
        track_data,
        filename=safe_filename,
        path=output_dir
    )
```

### Logging Best Practices

```python
from spotify_scraper.utils.logger import get_logger
from spotify_scraper import SpotifyClient

logger = get_logger(__name__)

def extract_tracks_with_logging(urls):
    client = SpotifyClient()
    results = []
    
    for url in urls:
        logger.info(f"Processing URL: {url}")
        try:
            track_data = client.get_track(url)
            logger.debug(f"Successfully extracted: {track_data['name']}")
            results.append(track_data)
        except Exception as e:
            logger.error(f"Failed to extract {url}: {e}", exc_info=True)
    
    logger.info(f"Processed {len(results)}/{len(urls)} tracks successfully")
    return results
```