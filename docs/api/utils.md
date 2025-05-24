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

#### extract_id_from_url

```python
extract_id_from_url(url: str) -> str
```

Extract Spotify ID from URL.

**Example:**
```python
from spotify_scraper.utils.url import extract_id_from_url

track_id = extract_id_from_url("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh")
# Returns: "4iV5W9uYEdYUVa79Axb7Rh"
```

#### get_entity_type

```python
get_entity_type(url: str) -> str
```Determine entity type from URL.

**Example:**
```python
entity_type = get_entity_type("https://open.spotify.com/album/123")
# Returns: "album"
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

#### retry_with_backoff

```python
retry_with_backoff(func: Callable, max_retries: int = 3, initial_delay: float = 1.0)
```

Retry a function with exponential backoff.

**Example:**
```python
from spotify_scraper.utils.common import retry_with_backoff

result = retry_with_backoff(
    lambda: client.get_track(track_id),
    max_retries=5,
    initial_delay=2.0
)
```