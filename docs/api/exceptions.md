# Exceptions Module

The `exceptions` module defines all custom exceptions used by SpotifyScraper.

## Exception Hierarchy

```
Exception
└── SpotifyScraperError (base exception)
    ├── NetworkError
    │   ├── ConnectionError
    │   ├── TimeoutError
    │   └── RateLimitError
    ├── ParsingError
    │   ├── JSONParsingError
    │   └── DataExtractionError
    ├── ValidationError
    │   ├── InvalidURLError
    │   └── InvalidIDError
    └── ConfigurationError
```

## Base Exception

### SpotifyScraperError

```python
from spotify_scraper import SpotifyScraperError
```

Base exception for all SpotifyScraper errors.

**Example:**
```python
try:
    client.get_track("invalid")
except SpotifyScraperError as e:
    print(f"SpotifyScraper error: {e}")
```

## Network Exceptions

### NetworkError

Base class for network-related errors.

```python
from spotify_scraper.exceptions import NetworkError
```### ConnectionError

Raised when unable to connect to Spotify.

```python
except ConnectionError as e:
    print("Failed to connect to Spotify")
```

### TimeoutError

Raised when a request times out.

```python
except TimeoutError as e:
    print("Request timed out")
```

### RateLimitError

Raised when hitting Spotify's rate limits.

```python
except RateLimitError as e:
    print("Rate limited, waiting...")
    time.sleep(60)
```

## Parsing Exceptions

### ParsingError

Base class for parsing-related errors.

### JSONParsingError

Raised when JSON parsing fails.

```python
except JSONParsingError as e:
    print(f"Failed to parse JSON: {e}")
```

### DataExtractionError

Raised when data extraction fails.

```python
except DataExtractionError as e:
    print(f"Failed to extract data: {e}")
```## Validation Exceptions

### ValidationError

Base class for validation errors.

### InvalidURLError

Raised when URL is invalid.

```python
except InvalidURLError as e:
    print(f"Invalid URL: {e}")
```

### InvalidIDError

Raised when Spotify ID is invalid.

```python
except InvalidIDError as e:
    print(f"Invalid ID format: {e}")
```

## Configuration Exceptions

### ConfigurationError

Raised when configuration is invalid.

```python
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Error Handling Best Practices

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.exceptions import (
    NetworkError,
    RateLimitError,
    ParsingError
)

client = SpotifyClient()

try:
    track = client.get_track(track_id)
except RateLimitError:
    time.sleep(60)
    track = client.get_track(track_id)
except NetworkError:
    # Retry with backoff
    pass
except ParsingError:
    # Log and skip
    pass
```