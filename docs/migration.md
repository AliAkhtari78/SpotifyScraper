# Migration Guide: v1.x to v2.0

This guide helps you upgrade from SpotifyScraper v1.x to v2.0.

## Overview of Changes

SpotifyScraper v2.0 is a complete rewrite with a cleaner API, better performance, and more features. While the core functionality remains the same, the API has been significantly improved.

### Key Improvements in v2.0
- ✅ Simplified API with intuitive method names
- ✅ Better error handling with specific exceptions
- ✅ Type hints throughout for better IDE support
- ✅ Improved performance with connection pooling
- ✅ Built-in media download capabilities
- ✅ Support for Spotify's modern React-based interface

---

## Breaking Changes

### 1. Import Changes

**v1.x:**
```python
from SpotifyScraper.scraper import Scraper, Request
```

**v2.0:**
```python
from spotify_scraper import SpotifyClient
```

### 2. Client Initialization

**v1.x:**
```python
request = Request().request()
scraper = Scraper(session=request)
```

**v2.0:**
```python
client = SpotifyClient()
```

### 3. Method Names

| v1.x Method | v2.0 Method | Notes |
|-------------|-------------|-------|
| `get_track_url_info()` | `get_track_info()` | Cleaner name |
| `get_track_id_info()` | `get_track_info()` | Same method handles both |
| `get_album_url_info()` | `get_album_info()` | Cleaner name |
| `get_album_id_info()` | `get_album_info()` | Same method handles both |
| `get_artist_url_info()` | `get_artist_info()` | Cleaner name |
| `get_playlist_url_info()` | `get_playlist_info()` | Cleaner name |

### 4. Parameter Changes

**v1.x:**
```python
# Separate URL and ID methods
track = scraper.get_track_url_info(url='https://...')
track = scraper.get_track_id_info(track_id='6rqhFgbbKwnb9MLmUQDhG6')
```

**v2.0:**
```python
# Single method handles both
track = client.get_track_info('https://...')
track = client.get_track_info('spotify:track:6rqhFgbbKwnb9MLmUQDhG6')
```

### 5. Return Value Changes

v2.0 returns cleaner, more consistent data structures:

**v1.x:**
```python
track = {
    'track_id': '...',
    'track_name': '...',
    'track_artists': ['...'],
    # Inconsistent naming
}
```

**v2.0:**
```python
track = {
    'id': '...',
    'name': '...',
    'artists': [{'id': '...', 'name': '...', 'uri': '...'}],
    # Consistent, nested structure
}
```

---

## Migration Examples

### Basic Track Extraction

**v1.x:**
```python
from SpotifyScraper.scraper import Scraper, Request

request = Request().request()
scraper = Scraper(session=request)

track = scraper.get_track_url_info(
    url='https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6'
)
print(track['track_name'])
```

**v2.0:**
```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

track = client.get_track_info(
    'https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6'
)
print(track.get('name', 'Unknown'))
```

### Album Extraction with Tracks

**v1.x:**
```python
album = scraper.get_album_url_info(
    url='https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv'
)
# Access nested in 'album_tracks'
for track in album['album_tracks']:
    print(track['track_name'])
```

**v2.0:**
```python
album = client.get_album_info(
    'https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv'
)
# Cleaner structure
for track in album['tracks']:
    print(track.get('name', 'Unknown'))
```

### Error Handling

**v1.x:**
```python
try:
    track = scraper.get_track_url_info(url='...')
except Exception as e:
    # Generic exception
    print(f"Error: {e}")
```

**v2.0:**
```python
from spotify_scraper import (
    SpotifyClient, 
    URLError, 
    NetworkError, 
    ExtractionError
)

try:
    track = client.get_track_info('...')
except URLError:
    print("Invalid Spotify URL")
except NetworkError:
    print("Network connection failed")
except ExtractionError:
    print("Could not extract data")
```

---

## New Features in v2.0

### 1. Built-in Media Downloads

v2.0 includes media download capabilities:

```python
# Download track preview
preview_path = client.download_preview_mp3(track_url, path="previews/")

# Download cover art
cover_path = client.download_cover(album_url, path="covers/")
```

### 2. Authentication Support

Access lyrics and other authenticated features:

```python
# Use cookie authentication
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Get track with lyrics
track = client.get_track_info_with_lyrics(track_url)
```

### 3. Better Browser Options

```python
# Use Selenium for complex scenarios
client = SpotifyClient(browser_type="selenium")

# Use lightweight requests (default)
client = SpotifyClient(browser_type="requests")
```

### 4. Type Hints

All methods now have proper type hints:

```python
def get_track_info(self, url: str) -> Dict[str, Any]:
    """Extract track information."""
    ...
```

---

## Compatibility Layer

For easier migration, you can use a compatibility wrapper:

```python
# compatibility.py
from spotify_scraper import SpotifyClient

class Request:
    def request(self):
        return self

class Scraper:
    def __init__(self, session=None):
        self.client = SpotifyClient()
    
    def get_track_url_info(self, url):
        data = self.client.get_track_info(url)
        # Transform to v1 format
        return {
            'track_id': data['id'],
            'track_name': data.get('name', 'Unknown'),
            'track_artists': [a['name'] for a in data['artists']],
            # ... map other fields
        }
    
    def get_album_url_info(self, url):
        data = self.client.get_album_info(url)
        # Transform to v1 format
        return {
            'album_id': data['id'],
            'album_name': data.get('name', 'Unknown'),
            'album_tracks': data['tracks'],
            # ... map other fields
        }
```

---

## Step-by-Step Migration

### 1. Update Imports

```python
# Find and replace
# OLD: from SpotifyScraper.scraper import Scraper, Request
# NEW: from spotify_scraper import SpotifyClient
```

### 2. Update Initialization

```python
# Replace request/scraper pattern
# OLD:
# request = Request().request()
# scraper = Scraper(session=request)

# NEW:
client = SpotifyClient()
```

### 3. Update Method Calls

```python
# Update method names
# OLD: scraper.get_track_url_info(url='...')
# NEW: client.get_track_info('...')

# OLD: scraper.get_track_id_info(track_id='...')
# NEW: client.get_track_info('spotify:track:...')
```

### 4. Update Data Access

```python
# Update field names
# OLD: track['track_name']
# NEW: track.get('name', 'Unknown')

# OLD: track['track_artists']
# NEW: [a['name'] for a in track['artists']]
```

### 5. Add Error Handling

```python
# Add specific exception handling
from spotify_scraper import URLError, NetworkError

try:
    data = client.get_track_info(url)
except URLError:
    # Handle invalid URL
except NetworkError:
    # Handle network issues
```

---

## Common Migration Issues

### Issue: "No module named 'SpotifyScraper.scraper'"

**Solution**: Update imports to use `spotify_scraper` (lowercase, underscore)

### Issue: "AttributeError: 'Scraper' object has no attribute 'get_track_url_info'"

**Solution**: You're mixing v1 and v2 code. Use `SpotifyClient` and new method names.

### Issue: "KeyError: 'track_name'"

**Solution**: Field names have changed. Use `name` instead of `track_name`.

### Issue: Different data structure

**Solution**: v2.0 has cleaner, more consistent data structures. Update your code to use the new format.

---

## Testing Your Migration

Create a test script to verify your migration:

```python
def test_migration():
    """Test that migration was successful."""
    from spotify_scraper import SpotifyClient
    
    client = SpotifyClient()
    
    # Test track extraction
    track = client.get_track_info(
        "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
    )
    assert 'name' in track
    assert 'artists' in track
    print("✓ Track extraction works")
    
    # Test album extraction
    album = client.get_album_info(
        "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"
    )
    assert 'name' in album
    assert 'tracks' in album
    print("✓ Album extraction works")
    
    print("\nMigration successful! 🎉")

if __name__ == "__main__":
    test_migration()
```

---

## Getting Help

If you encounter issues during migration:

1. Check this guide for common issues
2. Read the [API documentation](api/index.md)
3. Search [GitHub issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
4. Ask on [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)

---

## Why Upgrade?

### Benefits of v2.0
- 🚀 **Faster**: Improved performance with connection pooling
- 🎯 **Cleaner API**: Intuitive method names and consistent data
- 🛡️ **Better Errors**: Specific exceptions for different failures
- 📝 **Type Hints**: Full IDE support with autocompletion
- 📥 **Downloads**: Built-in media download capabilities
- 🔧 **Maintained**: Active development and bug fixes

### Long-term Support
- v1.x is no longer maintained
- v2.0 is actively developed with regular updates
- Security fixes only applied to v2.0

---

## Summary

While v2.0 includes breaking changes, the migration is straightforward:

1. Update imports
2. Use `SpotifyClient` instead of `Scraper`
3. Update method names (remove `_url_info` suffix)
4. Update field names in returned data
5. Add proper error handling

The benefits of cleaner code, better performance, and new features make the upgrade worthwhile!