# Creating Custom Extractors

This guide explains how to extend SpotifyScraper with custom extractors for specialized data extraction needs.

## Understanding the Extractor Architecture

SpotifyScraper uses a modular architecture that makes it easy to add custom extractors:

```
SpotifyClient
    ├── Browser (handles HTTP requests)
    ├── Parser (extracts JSON data)
    └── Extractors (transform raw data)
        ├── TrackExtractor
        ├── AlbumExtractor
        ├── ArtistExtractor
        └── PlaylistExtractor
```

## Base Extractor Pattern

All extractors follow a common pattern:

```python
from typing import Dict, Any, Optional
from spotify_scraper.extractors.base import BaseExtractor

class CustomExtractor(BaseExtractor):
    """Extract custom data from Spotify pages"""
    
    def __init__(self, parser):
        self.parser = parser
    
    def extract(self, html: str, url: str) -> Dict[str, Any]:
        """Extract data from HTML content"""
        # Parse JSON data from HTML
        json_data = self.parser.extract_json(html)
        
        # Transform data to desired format
        result = self._transform_data(json_data, url)
        
        return result
    
    def _transform_data(self, data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Transform raw data to desired format"""
        raise NotImplementedError
```