# Exceptions API Reference

SpotifyScraper provides a comprehensive exception hierarchy for precise error handling. All exceptions inherit from `SpotifyScraperError`.

## Exception Hierarchy

```
SpotifyScraperError (base exception)
├── URLError
├── ParsingError
├── ExtractionError
├── NetworkError
├── AuthenticationError
│   └── TokenError
├── BrowserError
└── MediaError
    └── DownloadError
```

## Base Exception

### SpotifyScraperError

Base exception for all SpotifyScraper errors.

```python
from spotify_scraper.core.exceptions import SpotifyScraperError

try:
    # SpotifyScraper operations
    pass
except SpotifyScraperError as e:
    print(f"SpotifyScraper error: {e}")
```

**Alias:** `ScrapingError` (for backward compatibility)

## URL Exceptions

### URLError

Exception raised for errors related to URLs.

**Constructor:**
```python
URLError(message="Invalid URL", url=None)
```

**Parameters:**
- `message` (str): Error message
- `url` (str, optional): The problematic URL

**Attributes:**
- `url`: The URL that caused the error

**Example:**
```python
from spotify_scraper.core.exceptions import URLError

try:
    client.get_track("invalid-url")
except URLError as e:
    print(f"URL Error: {e}")
    print(f"Problematic URL: {e.url}")
```

## Parsing Exceptions

### ParsingError

Exception raised for errors during parsing of HTML or JSON data.

**Constructor:**
```python
ParsingError(message="Failed to parse data", data_type=None, details=None)
```

**Parameters:**
- `message` (str): Error message
- `data_type` (str, optional): Type of data that failed to parse (e.g., "HTML", "JSON")
- `details` (str, optional): Additional details about the error

**Attributes:**
- `data_type`: Type of data that failed
- `details`: Additional error details

**Example:**
```python
from spotify_scraper.core.exceptions import ParsingError

try:
    # Parsing operation
    pass
except ParsingError as e:
    print(f"Parsing Error: {e}")
    if e.data_type:
        print(f"Failed to parse: {e.data_type}")
    if e.details:
        print(f"Details: {e.details}")
```

## Extraction Exceptions

### ExtractionError

Exception raised for errors during data extraction.

**Constructor:**
```python
ExtractionError(message="Failed to extract data", entity_type=None, url=None)
```

**Parameters:**
- `message` (str): Error message
- `entity_type` (str, optional): Type of entity being extracted (e.g., "track", "album")
- `url` (str, optional): The URL being processed

**Attributes:**
- `entity_type`: Type of entity
- `url`: URL being processed

**Example:**
```python
from spotify_scraper.core.exceptions import ExtractionError

try:
    track_data = client.get_track(url)
except ExtractionError as e:
    print(f"Extraction Error: {e}")
    print(f"Entity type: {e.entity_type}")
    print(f"URL: {e.url}")
```

## Network Exceptions

### NetworkError

Exception raised for network-related errors.

**Constructor:**
```python
NetworkError(message="Network error", url=None, status_code=None)
```

**Parameters:**
- `message` (str): Error message
- `url` (str, optional): The URL that was being accessed
- `status_code` (int, optional): HTTP status code received

**Attributes:**
- `url`: URL that failed
- `status_code`: HTTP status code

**Example:**
```python
from spotify_scraper.core.exceptions import NetworkError

try:
    data = client.get_track(url)
except NetworkError as e:
    print(f"Network Error: {e}")
    if e.status_code:
        print(f"HTTP Status: {e.status_code}")
    if e.url:
        print(f"Failed URL: {e.url}")
```

## Authentication Exceptions

### AuthenticationError

Exception raised for authentication-related errors.

**Constructor:**
```python
AuthenticationError(message="Authentication error", auth_type=None)
```

**Parameters:**
- `message` (str): Error message
- `auth_type` (str, optional): Type of authentication that failed (e.g., "cookie", "token")

**Attributes:**
- `auth_type`: Type of authentication

**Example:**
```python
from spotify_scraper.core.exceptions import AuthenticationError

try:
    # Access authenticated content
    lyrics = track_data.get('lyrics')
except AuthenticationError as e:
    print(f"Authentication Error: {e}")
    print(f"Auth type: {e.auth_type}")
```

### TokenError

Exception raised for errors related to authentication tokens. Inherits from `AuthenticationError`.

**Constructor:**
```python
TokenError(message="Token error", token_type=None, details=None)
```

**Parameters:**
- `message` (str): Error message
- `token_type` (str, optional): Type of token (e.g., "access", "refresh")
- `details` (str, optional): Additional details about the error

**Attributes:**
- `token_type`: Type of token
- `details`: Additional details

**Example:**
```python
from spotify_scraper.core.exceptions import TokenError

try:
    # Token-based operation
    pass
except TokenError as e:
    print(f"Token Error: {e}")
    print(f"Token type: {e.token_type}")
    if e.details:
        print(f"Details: {e.details}")
```

## Browser Exceptions

### BrowserError

Exception raised for errors related to browser operation.

**Constructor:**
```python
BrowserError(message="Browser error", browser_type=None)
```

**Parameters:**
- `message` (str): Error message
- `browser_type` (str, optional): Type of browser that encountered the error

**Attributes:**
- `browser_type`: Type of browser

**Example:**
```python
from spotify_scraper.core.exceptions import BrowserError

try:
    browser = SeleniumBrowser()
    browser.get(url)
except BrowserError as e:
    print(f"Browser Error: {e}")
    print(f"Browser type: {e.browser_type}")
```

## Media Exceptions

### MediaError

Exception raised for errors related to media handling.

**Constructor:**
```python
MediaError(message="Media error", media_type=None, path=None)
```

**Parameters:**
- `message` (str): Error message
- `media_type` (str, optional): Type of media (e.g., "image", "audio")
- `path` (str, optional): Path to the media file

**Attributes:**
- `media_type`: Type of media
- `path`: File path

**Example:**
```python
from spotify_scraper.core.exceptions import MediaError

try:
    # Media operation
    pass
except MediaError as e:
    print(f"Media Error: {e}")
    print(f"Media type: {e.media_type}")
    print(f"Path: {e.path}")
```

### DownloadError

Exception raised for errors during file downloads. Inherits from `MediaError`.

**Constructor:**
```python
DownloadError(message="Download failed", url=None, path=None, status_code=None)
```

**Parameters:**
- `message` (str): Error message
- `url` (str, optional): URL that failed to download
- `path` (str, optional): Local path where file was supposed to be saved
- `status_code` (int, optional): HTTP status code received

**Attributes:**
- `url`: Download URL
- `path`: Local file path
- `status_code`: HTTP status code

**Example:**
```python
from spotify_scraper.core.exceptions import DownloadError
from spotify_scraper.media import AudioDownloader

try:
    downloader = AudioDownloader(browser)
    file_path = downloader.download_preview(track_data)
except DownloadError as e:
    print(f"Download Error: {e}")
    print(f"URL: {e.url}")
    print(f"Target path: {e.path}")
    if e.status_code:
        print(f"HTTP Status: {e.status_code}")
```

## Exception Handling Best Practices

### 1. Catch Specific Exceptions

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.core.exceptions import (
    URLError,
    NetworkError,
    ExtractionError,
    AuthenticationError
)

client = SpotifyClient()

try:
    track_data = client.get_track(url)
except URLError:
    print("Invalid Spotify URL provided")
except NetworkError as e:
    print(f"Network issue: {e.status_code}")
except AuthenticationError:
    print("Authentication required for this content")
except ExtractionError as e:
    print(f"Failed to extract {e.entity_type} data")
```

### 2. Use Exception Hierarchy

```python
from spotify_scraper.core.exceptions import (
    SpotifyScraperError,
    AuthenticationError,
    TokenError
)

try:
    # Some operation
    pass
except TokenError as e:
    # Handle token-specific errors
    print(f"Token issue: {e.token_type}")
except AuthenticationError as e:
    # Handle other auth errors
    print(f"Auth issue: {e.auth_type}")
except SpotifyScraperError as e:
    # Handle any other SpotifyScraper error
    print(f"General error: {e}")
```

### 3. Error Recovery

```python
from spotify_scraper.core.exceptions import NetworkError
import time

def get_track_with_retry(client, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.get_track(url)
        except NetworkError as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

### 4. Logging Exceptions

```python
import logging
from spotify_scraper.core.exceptions import SpotifyScraperError

logger = logging.getLogger(__name__)

try:
    data = client.get_track(url)
except SpotifyScraperError as e:
    logger.error(f"Failed to extract track data", exc_info=True)
    # Re-raise or handle as needed
    raise
```

### 5. Custom Error Messages

```python
from spotify_scraper.core.exceptions import URLError, ExtractionError

def safe_extract_track(client, url):
    try:
        return client.get_track(url)
    except URLError:
        return {"error": "Please provide a valid Spotify track URL"}
    except ExtractionError as e:
        return {"error": f"Unable to extract track information: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {type(e).__name__}"}
```