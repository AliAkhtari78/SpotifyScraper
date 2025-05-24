# SpotifyScraper Architecture

This guide provides a deep dive into the internal architecture and design patterns of SpotifyScraper.

## Overview

SpotifyScraper follows a modular, layered architecture designed for flexibility, maintainability, and extensibility.

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│              (CLI Commands, User Scripts)                │
├─────────────────────────────────────────────────────────┤
│                      Client Layer                        │
│                   (SpotifyClient)                        │
├─────────────────────────────────────────────────────────┤
│                    Extractor Layer                       │
│        (Track, Album, Artist, Playlist Extractors)      │
├─────────────────────────────────────────────────────────┤
│                     Parser Layer                         │
│                    (JSONParser)                          │
├─────────────────────────────────────────────────────────┤
│                    Browser Layer                         │
│          (RequestsBrowser, SeleniumBrowser)             │
├─────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                    │
│      (Config, Cache, Authentication, Logging)           │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. SpotifyClient

The main entry point that orchestrates all operations.

```python
# src/spotify_scraper/client.py
class SpotifyClient:
    """Main client for interacting with Spotify"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.browser = self._create_browser()
        self.parser = JSONParser()
        self._init_extractors()
```    def _create_browser(self) -> BaseBrowser:
        """Factory method for browser creation"""
        if self.config.use_selenium:
            return SeleniumBrowser(self.config)
        return RequestsBrowser(self.config)
    
    def _init_extractors(self):
        """Initialize all extractors"""
        self.track_extractor = TrackExtractor(self.parser)
        self.album_extractor = AlbumExtractor(self.parser)
        self.artist_extractor = ArtistExtractor(self.parser)
        self.playlist_extractor = PlaylistExtractor(self.parser)
```

**Key Responsibilities:**
- Manages browser instances
- Coordinates extractors
- Handles configuration
- Provides unified API

### 2. Browser Layer

Abstract interface for different HTTP client implementations.

```python
# src/spotify_scraper/browsers/base.py
from abc import ABC, abstractmethod

class BaseBrowser(ABC):
    """Abstract base class for browsers"""
    
    @abstractmethod
    def get(self, url: str) -> str:
        """Fetch content from URL"""
        pass
```

**Implementations:**

1. **RequestsBrowser** - Lightweight, fast
   - Uses `requests` library
   - Suitable for most scraping needs
   - Lower resource usage

2. **SeleniumBrowser** - JavaScript support
   - Uses Selenium WebDriver
   - Handles dynamic content
   - Bypasses some anti-scraping measures