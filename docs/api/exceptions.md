# Exceptions Module

The `exceptions` module defines all custom exceptions used by SpotifyScraper.

## Exception Hierarchy

```
Exception
└── SpotifyScraperError (base exception)
    ├── URLError (invalid Spotify URLs)
    ├── NetworkError (connection/network issues)
    ├── ExtractionError (data parsing failures)
    ├── AuthenticationError (auth/cookie issues)
    └── MediaError (download failures)
```

## Base Exception

### SpotifyScraperError

```python
from spotify_scraper import SpotifyScraperError
```

Base exception for all SpotifyScraper errors.

**Example:**
```python
from spotify_scraper import SpotifyClient, SpotifyScraperError

client = SpotifyClient()

try:
    track = client.get_track_info("invalid")
except SpotifyScraperError as e:
    print(f"SpotifyScraper error: {e}")
```

## Specific Exceptions

### URLError

Raised when a Spotify URL is invalid or malformed.

```python
from spotify_scraper import SpotifyClient, URLError

client = SpotifyClient()

try:
    track = client.get_track_info("not-a-valid-url")
except URLError as e:
    print(f"Invalid URL: {e}")
```

### NetworkError

Raised for network-related issues (connection failures, timeouts).

```python
from spotify_scraper import SpotifyClient, NetworkError

client = SpotifyClient()

try:
    track = client.get_track_info(track_url)
except NetworkError as e:
    print(f"Network issue: {e}")
    # Retry with exponential backoff
```

### ExtractionError

Raised when data extraction or parsing fails.

```python
from spotify_scraper import SpotifyClient, ExtractionError

client = SpotifyClient()

try:
    track = client.get_track_info(track_url)
except ExtractionError as e:
    print(f"Failed to extract data: {e}")
    # Log and skip this item
```

### AuthenticationError

Raised when authentication is required or fails.

```python
from spotify_scraper import SpotifyClient, AuthenticationError

# Without authentication
client = SpotifyClient()

try:
    lyrics = client.get_track_lyrics(track_url)
except AuthenticationError as e:
    print(f"Authentication required: {e}")
    # Need to provide cookie_file
    
# With authentication
client = SpotifyClient(cookie_file="spotify_cookies.txt")
try:
    lyrics = client.get_track_lyrics(track_url)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Cookies may be expired
```

### MediaError

Raised when media download fails.

```python
from spotify_scraper import SpotifyClient, MediaError

client = SpotifyClient()

try:
    preview_path = client.download_preview_mp3(track_url)
except MediaError as e:
    print(f"Download failed: {e}")
    # Track may not have a preview available
```

## Error Handling Best Practices

### Comprehensive Error Handling

```python
from spotify_scraper import (
    SpotifyClient,
    SpotifyScraperError,
    URLError,
    NetworkError,
    ExtractionError,
    AuthenticationError,
    MediaError
)
import time
import logging

logger = logging.getLogger(__name__)
client = SpotifyClient()

def safe_extract(url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """Safely extract data with comprehensive error handling."""
    for attempt in range(max_retries):
        try:
            return client.get_track_info(url)
            
        except URLError as e:
            logger.error(f"Invalid URL: {e}")
            return None  # Can't retry invalid URLs
            
        except NetworkError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Network error, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                logger.error(f"Network error after {max_retries} attempts: {e}")
                return None
                
        except ExtractionError as e:
            logger.error(f"Extraction failed: {e}")
            return None  # Can't retry extraction errors
            
        except AuthenticationError as e:
            logger.error(f"Authentication issue: {e}")
            return None  # Need to fix auth first
            
        except SpotifyScraperError as e:
            logger.error(f"Unexpected error: {e}")
            return None
```

### Batch Processing with Error Handling

```python
def process_tracks(urls: List[str]) -> Dict[str, Any]:
    """Process multiple tracks with proper error handling."""
    results = {
        'success': [],
        'failed': []
    }
    
    client = SpotifyClient()
    
    for url in urls:
        try:
            track = client.get_track_info(url)
            results['success'].append(track)
            
        except URLError:
            results['failed'].append({
                'url': url,
                'error': 'Invalid URL'
            })
            
        except NetworkError:
            # Could implement retry logic here
            results['failed'].append({
                'url': url,
                'error': 'Network error'
            })
            
        except Exception as e:
            results['failed'].append({
                'url': url,
                'error': str(e)
            })
            
    # Clean up if using Selenium
    if client.browser_type == "selenium":
        client.close()
        
    return results
```

## See Also

- [Client Module](client.md) - Main client interface
- [Basic Usage](../guide/basic-usage.md) - Getting started guide
- [Troubleshooting](../troubleshooting.md) - Common issues and solutions