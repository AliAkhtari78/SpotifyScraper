# Quick Start Guide

Get started with SpotifyScraper in minutes! This guide will walk you through installation, basic usage, and common tasks.

## Installation

### Basic Installation

```bash
# Install from PyPI
pip install spotifyscraper

# Or install with optional dependencies
pip install spotifyscraper[selenium,media]
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper

# Install in development mode
pip install -e ".[dev]"
```

## Your First Script

Here's the simplest way to extract track information:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser

# Create a client
browser = RequestsBrowser()
client = SpotifyClient(browser=browser)

# Extract track information
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track_data = client.get_track(track_url)

# Display results
print(f"Track: {track_data['name']}")
print(f"Artist: {track_data['artists'][0]['name']}")
print(f"Album: {track_data['album']['name']}")
print(f"Duration: {track_data['duration_ms'] / 1000:.2f} seconds")
```

## Common Use Cases

### 1. Extract Track Information

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser

def get_track_info(url):
    browser = RequestsBrowser()
    client = SpotifyClient(browser=browser)
    
    track = client.get_track(url)
    
    return {
        "title": track['name'],
        "artist": track['artists'][0]['name'],
        "album": track['album']['name'],
        "duration": track['duration_ms'],
        "preview_url": track.get('preview_url'),
        "release_date": track['album'].get('release_date')
    }

# Example usage
info = get_track_info("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
print(info)
```

### 2. Download Track Preview

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.media import AudioDownloader

def download_track_preview(url, output_folder="downloads"):
    browser = RequestsBrowser()
    client = SpotifyClient(browser=browser)
    
    # Get track data
    track_data = client.get_track(url)
    
    # Check if preview is available
    if not track_data.get('preview_url'):
        print("No preview available for this track")
        return None
    
    # Download preview
    audio_downloader = AudioDownloader(browser)
    file_path = audio_downloader.download_preview(
        track_data,
        path=output_folder,
        with_cover=True  # Embed cover art
    )
    
    print(f"Downloaded: {file_path}")
    return file_path

# Example usage
download_track_preview("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
```

### 3. Download Cover Art

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.media import ImageDownloader

def download_album_cover(url, size="large"):
    browser = RequestsBrowser()
    client = SpotifyClient(browser=browser)
    
    # Get track data
    track_data = client.get_track(url)
    
    # Download cover
    image_downloader = ImageDownloader(browser)
    cover_path = image_downloader.download_cover(
        track_data,
        size=size  # "small", "medium", or "large"
    )
    
    print(f"Cover saved to: {cover_path}")
    return cover_path

# Example usage
download_album_cover("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
```

### 4. Extract Album Tracks

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser

def get_album_tracks(album_url):
    browser = RequestsBrowser()
    client = SpotifyClient(browser=browser)
    
    album = client.get_album(album_url)
    
    print(f"Album: {album['name']}")
    print(f"Artist: {album['artists'][0]['name']}")
    print(f"Release Date: {album['release_date']}")
    print(f"\nTracks ({album['total_tracks']}):")
    
    for track in album['tracks']:
        duration_sec = track['duration_ms'] / 1000
        print(f"{track['track_number']:2d}. {track['name']} ({duration_sec:.2f}s)")

# Example usage
get_album_tracks("https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv")
```

### 5. Extract Playlist Information

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser

def analyze_playlist(playlist_url):
    browser = RequestsBrowser()
    client = SpotifyClient(browser=browser)
    
    playlist = client.get_playlist(playlist_url)
    
    print(f"Playlist: {playlist['name']}")
    print(f"Owner: {playlist['owner']['name']}")
    print(f"Tracks: {playlist['track_count']}")
    
    if playlist.get('description'):
        print(f"Description: {playlist['description']}")
    
    # Show first 5 tracks
    print("\nFirst 5 tracks:")
    for i, track in enumerate(playlist['tracks'][:5], 1):
        artist = track['artists'][0]['name']
        print(f"{i}. {track['name']} - {artist}")

# Example usage
analyze_playlist("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
```

## Working with URLs

### URL Validation and Parsing

```python
from spotify_scraper.utils.url import (
    is_spotify_url,
    get_url_type,
    extract_id,
    clean_url
)

def analyze_url(url):
    # Clean the URL
    clean = clean_url(url)
    
    # Check if it's valid
    if not is_spotify_url(url):
        print("Not a valid Spotify URL")
        return
    
    # Get URL info
    url_type = get_url_type(url)
    spotify_id = extract_id(url)
    
    print(f"URL Type: {url_type}")
    print(f"Spotify ID: {spotify_id}")
    print(f"Clean URL: {clean}")

# Example usage
analyze_url("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6?si=abcd123")
```

### Convert Between URL Formats

```python
from spotify_scraper.utils.url import (
    convert_to_embed_url,
    convert_spotify_uri_to_url,
    convert_url_to_spotify_uri
)

# Regular URL to embed URL
regular_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
embed_url = convert_to_embed_url(regular_url)
print(f"Embed URL: {embed_url}")

# Spotify URI to URL
uri = "spotify:track:6rqhFgbbKwnb9MLmUQDhG6"
url = convert_spotify_uri_to_url(uri)
print(f"URL from URI: {url}")

# URL to Spotify URI
uri = convert_url_to_spotify_uri(regular_url)
print(f"URI from URL: {uri}")
```

## Error Handling

Always handle potential errors:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.core.exceptions import (
    SpotifyScraperError,
    URLError,
    NetworkError,
    ExtractionError
)

def safe_extract_track(url):
    browser = RequestsBrowser()
    client = SpotifyClient(browser=browser)
    
    try:
        track_data = client.get_track(url)
        return {
            "success": True,
            "data": track_data
        }
    except URLError as e:
        return {
            "success": False,
            "error": "Invalid URL",
            "details": str(e)
        }
    except NetworkError as e:
        return {
            "success": False,
            "error": "Network error",
            "details": str(e)
        }
    except ExtractionError as e:
        return {
            "success": False,
            "error": "Extraction failed",
            "details": str(e)
        }
    except SpotifyScraperError as e:
        return {
            "success": False,
            "error": "General error",
            "details": str(e)
        }
    finally:
        client.close()

# Example usage
result = safe_extract_track("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
if result["success"]:
    print(f"Track: {result['data']['name']}")
else:
    print(f"Error: {result['error']} - {result['details']}")
```

## Using Context Managers

For automatic resource cleanup:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser

# The client will automatically close when done
with SpotifyClient(browser=RequestsBrowser()) as client:
    track = client.get_track("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
    album = client.get_album("https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv")
    
    print(f"Track: {track['name']}")
    print(f"Album: {album['name']}")
```

## Batch Processing

Process multiple URLs efficiently:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser
import time

def batch_extract_tracks(urls):
    browser = RequestsBrowser()
    client = SpotifyClient(browser=browser)
    
    results = []
    
    for url in urls:
        try:
            print(f"Processing: {url}")
            track_data = client.get_track(url)
            results.append({
                "url": url,
                "name": track_data['name'],
                "artist": track_data['artists'][0]['name'],
                "success": True
            })
            
            # Be respectful to Spotify's servers
            time.sleep(0.5)
            
        except Exception as e:
            results.append({
                "url": url,
                "success": False,
                "error": str(e)
            })
    
    client.close()
    return results

# Example usage
urls = [
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
    "https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv",
    "https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI3"
]

results = batch_extract_tracks(urls)

# Print summary
successful = sum(1 for r in results if r["success"])
print(f"\nProcessed {successful}/{len(results)} tracks successfully")

for result in results:
    if result["success"]:
        print(f"✅ {result['name']} - {result['artist']}")
    else:
        print(f"❌ Failed: {result['error']}")
```

## Complete Example: Track Analysis Tool

Here's a complete example that combines multiple features:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.media import AudioDownloader, ImageDownloader
from spotify_scraper.utils.url import is_spotify_url, get_url_type
import os

class TrackAnalyzer:
    def __init__(self):
        self.browser = RequestsBrowser()
        self.client = SpotifyClient(browser=self.browser)
        self.audio_downloader = AudioDownloader(self.browser)
        self.image_downloader = ImageDownloader(self.browser)
    
    def analyze(self, url, download_media=False):
        # Validate URL
        if not is_spotify_url(url):
            return {"error": "Invalid Spotify URL"}
        
        if get_url_type(url) != "track":
            return {"error": "URL is not a track"}
        
        try:
            # Extract track data
            track_data = self.client.get_track(url)
            
            # Build analysis
            analysis = {
                "track": {
                    "name": track_data['name'],
                    "id": track_data['id'],
                    "duration_seconds": track_data['duration_ms'] / 1000,
                    "explicit": track_data.get('is_explicit', False)
                },
                "artist": {
                    "name": track_data['artists'][0]['name'],
                    "id": track_data['artists'][0]['id']
                },
                "album": {
                    "name": track_data['album']['name'],
                    "release_date": track_data['album'].get('release_date'),
                    "total_tracks": track_data['album'].get('total_tracks')
                },
                "preview_available": bool(track_data.get('preview_url'))
            }
            
            # Download media if requested
            if download_media:
                media_dir = f"media/{track_data['id']}"
                os.makedirs(media_dir, exist_ok=True)
                
                # Download preview if available
                if track_data.get('preview_url'):
                    audio_path = self.audio_downloader.download_preview(
                        track_data,
                        path=media_dir
                    )
                    analysis['downloaded_audio'] = audio_path
                
                # Download cover
                cover_path = self.image_downloader.download_cover(
                    track_data,
                    path=media_dir,
                    size="large"
                )
                analysis['downloaded_cover'] = cover_path
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def close(self):
        self.client.close()

# Usage
analyzer = TrackAnalyzer()

# Analyze a track
url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
result = analyzer.analyze(url, download_media=True)

if "error" not in result:
    print(f"Track: {result['track']['name']}")
    print(f"Artist: {result['artist']['name']}")
    print(f"Album: {result['album']['name']}")
    print(f"Duration: {result['track']['duration_seconds']:.2f} seconds")
    print(f"Explicit: {result['track']['explicit']}")
    
    if result.get('downloaded_audio'):
        print(f"\nAudio downloaded: {result['downloaded_audio']}")
    if result.get('downloaded_cover'):
        print(f"Cover downloaded: {result['downloaded_cover']}")
else:
    print(f"Error: {result['error']}")

analyzer.close()
```

## Next Steps

Now that you've learned the basics:

1. Check out the [Advanced Usage Guide](advanced.md) for more complex scenarios
2. Learn about the [CLI Interface](cli.md) for command-line usage
3. Explore the [API Reference](../api/) for detailed documentation
4. See the [examples folder](https://github.com/AliAkhtari78/SpotifyScraper/tree/master/examples) for more code samples

## Tips

- Always close resources when done (use context managers or call `.close()`)
- Add delays between requests to avoid rate limiting
- Handle errors gracefully - not all tracks have previews
- Use the appropriate browser (RequestsBrowser for most cases)
- Check if data exists before accessing it (use `.get()` method)