# Quick Start Guide

Get started with SpotifyScraper in minutes! This guide will walk you through installation, basic usage, and common tasks.

## Installation

### Basic Installation

```bash
# Install from PyPI
pip install spotifyscraper

# Or install with optional dependencies
pip install "spotifyscraper[selenium]"  # For Selenium support
pip install eyeD3  # For MP3 metadata support
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper

# Install in development mode
pip install -e .
```

## Your First Script

Here's the simplest way to extract track information:

```python
from spotify_scraper import SpotifyClient

# Create a client
client = SpotifyClient()

# Extract track information
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track = client.get_track_info(track_url)

# Display results
print(f"Track: {track.get('name', 'Unknown')}")
print(f"Artist: {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")
print(f"Album: {track.get('album', {}).get('name', 'Unknown')}")
print(f"Duration: {track.get('duration_ms', 0) / 1000:.2f} seconds")

# Always close when done
client.close()
```

## Common Use Cases

### 1. Extract Track Information

```python
from spotify_scraper import SpotifyClient

def get_track_details(url):
    client = SpotifyClient()
    
    try:
        track = client.get_track_info(url)
        
        return {
            "title": track.get('name', 'Unknown'),
            "artists": [artist.get('name', 'Unknown') for artist in track['artists']],
            "album": track.get('album', {}).get('name', 'Unknown'),
            "duration_seconds": track.get('duration_ms', 0) / 1000,
            "preview_url": track.get('preview_url'),
            "popularity": track.get('popularity', 0),
            "explicit": track.get('explicit', False)
        }
    finally:
        client.close()

# Example usage
info = get_track_details("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
print(f"Track: {info['title']} by {', '.join(info['artists'])}")
```

### 2. Download Track Preview

```python
from spotify_scraper import SpotifyClient

def download_track_preview(url, output_folder="downloads"):
    client = SpotifyClient()
    
    try:
        # Download preview MP3 with embedded cover art
        file_path = client.download_preview_mp3(
            url, 
            path=output_folder,
            with_cover=True  # Embed album cover in MP3
        )
        print(f"Downloaded to: {file_path}")
        return file_path
    except Exception as e:
        print(f"Download failed: {e}")
        return None
    finally:
        client.close()

# Example usage
download_track_preview("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
```

### 3. Download Cover Art

```python
from spotify_scraper import SpotifyClient

def download_album_cover(url, size="large"):
    client = SpotifyClient()
    
    try:
        # Download cover image
        cover_path = client.download_cover(
            url,
            path="covers/",
            quality_preference=[size]  # "large", "medium", or "small"
        )
        
        if cover_path:
            print(f"Cover saved to: {cover_path}")
        return cover_path
    finally:
        client.close()

# Example usage - works with track, album, artist, or playlist URLs
download_album_cover("https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv")
```

### 4. Extract Album Information

```python
from spotify_scraper import SpotifyClient

def get_album_tracklist(album_url):
    client = SpotifyClient()
    
    try:
        album = client.get_album_info(album_url)
        
        print(f"Album: {album.get('name', 'Unknown')}")
        print(f"Artist: {(album.get('artists', [{}])[0].get('name', 'Unknown') if album.get('artists') else 'Unknown')}")
        print(f"Release Date: {album.get('release_date', 'N/A')}")
        print(f"Total Tracks: {album.get('total_tracks', 0)}")
        print(f"\nTracks ({album.get('total_tracks', 0)}):")
        
        total_duration_ms = 0
        for track in album['tracks']:
            duration_sec = track.get('duration_ms', 0) / 1000
            total_duration_ms += track.get('duration_ms', 0)
            print(f"{track['track_number']:2d}. {track.get('name', 'Unknown')} ({duration_sec:.2f}s)")
        
        print(f"\nTotal Duration: {total_duration_ms / 60000:.2f} minutes")
    finally:
        client.close()

# Example usage
get_album_tracklist("https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv")
```

### 5. Extract Playlist Information

```python
from spotify_scraper import SpotifyClient

def analyze_playlist(playlist_url):
    client = SpotifyClient()
    
    try:
        playlist = client.get_playlist_info(playlist_url)
        
        print(f"Playlist: {playlist.get('name', 'Unknown')}")
        print(f"Owner: {playlist.get('owner', {}).get('display_name', playlist.get('owner', {}).get('id', 'Unknown'))}")
        print(f"Total Tracks: {playlist.get('track_count', 0)}")
        
        if playlist.get('description'):
            # Note: description may not always be available
if 'description' in playlist:
    print(f"Description: {playlist.get('description', '')}")
        
        # Calculate total duration
        total_ms = sum(item['track']['duration_ms'] for item in playlist['tracks'])
        hours = total_ms // 3600000
        minutes = (total_ms % 3600000) // 60000
        print(f"Total Duration: {hours}h {minutes}m")
        
        # Show first 5 tracks
        print("\nFirst 5 tracks:")
        for i, item in enumerate(playlist['tracks'][:5], 1):
            track = item['track']
            artists = ', '.join([a['name'] for a in track['artists']])
            print(f"{i}. {track.get('name', 'Unknown')} - {artists}")
    finally:
        client.close()

# Example usage
analyze_playlist("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
```

### 6. Get Track Lyrics (Requires Authentication)

```python
from spotify_scraper import SpotifyClient

def get_track_with_lyrics(url, cookie_file):
    # Create client with authentication
    client = SpotifyClient(cookie_file=cookie_file)
    
    try:
        # Get track info with lyrics
        track = client.get_track_info_with_lyrics(url)
        
        print(f"Track: {track.get('name', 'Unknown')}")
        print(f"Artist: {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")
        
        if track.get('lyrics'):
            print("\nLyrics:")
            print("-" * 50)
            print(track['lyrics'])
        else:
            print("\nNo lyrics available for this track")
    finally:
        client.close()

# Example usage (requires spotify_cookies.txt file)
get_track_with_lyrics(
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
    "spotify_cookies.txt"
)
```

## Working with URLs

### URL Validation and Parsing

```python
from spotify_scraper import is_spotify_url, extract_id, get_url_type

def analyze_url(url):
    # Check if it's valid
    if not is_spotify_url(url):
        print("Not a valid Spotify URL")
        return
    
    # Get Spotify ID
    spotify_id = extract_id(url)
    
    # Get URL type
    url_type = get_url_type(url)
    
    print(f"Valid Spotify URL")
    print(f"Type: {url_type}")
    print(f"ID: {spotify_id}")

# Example usage
analyze_url("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6?si=abcd123")
```

### Automatic URL Type Detection

```python
from spotify_scraper import SpotifyClient

def process_any_url(url):
    client = SpotifyClient()
    
    try:
        # Automatically detects URL type and extracts appropriate data
        data = client.get_all_info(url)
        
        print(f"Type: {data['type']}")
        print(f"Name: {data.get('name', 'Unknown')}")
        
        if data['type'] == 'track':
            print(f"Artists: {', '.join([a['name'] for a in data['artists']])}")
        elif data['type'] == 'album':
            print(f"Total Tracks: {data['total_tracks']}")
        elif data['type'] == 'artist':
            print(f"Genres: {', '.join(data.get('genres', []))}")
        elif data['type'] == 'playlist':
            print(f"Owner: {data.get('owner', {}).get('display_name', 'Unknown')}")
    finally:
        client.close()

# Works with any Spotify URL type
process_any_url("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
process_any_url("https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv")
process_any_url("https://open.spotify.com/artist/1dfeR4HaWDbWqFHLkxsg1d")
process_any_url("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
```

## Error Handling

Always handle potential errors gracefully:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.core.exceptions import (
    URLError,
    ScrapingError,
    AuthenticationError,
    MediaError
)

def safe_extract_track(url):
    client = SpotifyClient()
    
    try:
        track = client.get_track_info(url)
        return {
            "success": True,
            "data": track
        }
    except URLError as e:
        return {
            "success": False,
            "error": "Invalid Spotify URL",
            "details": str(e)
        }
    except ScrapingError as e:
        return {
            "success": False,
            "error": "Failed to extract data",
            "details": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Unexpected error",
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

## Batch Processing

Process multiple URLs efficiently:

```python
from spotify_scraper import SpotifyClient
import time

def batch_extract_tracks(urls):
    client = SpotifyClient()
    results = []
    
    try:
        for i, url in enumerate(urls, 1):
            print(f"Processing {i}/{len(urls)}: {url}")
            
            try:
                track = client.get_track_info(url)
                results.append({
                    "url": url,
                    "name": track.get('name', 'Unknown'),
                    "artists": [a['name'] for a in track['artists']],
                    "success": True
                })
            except Exception as e:
                results.append({
                    "url": url,
                    "success": False,
                    "error": str(e)
                })
            
            # Be respectful to Spotify's servers
            time.sleep(0.5)
    finally:
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
        artists = ', '.join(result['artists'])
        print(f"✅ {result['name']} - {artists}")
    else:
        print(f"❌ Failed: {result['error']}")
```

## Complete Example: Spotify Data Analyzer

Here's a complete example that combines multiple features:

```python
from spotify_scraper import SpotifyClient, is_spotify_url, get_url_type
import os
import json
from datetime import datetime

class SpotifyAnalyzer:
    def __init__(self, cookie_file=None):
        self.client = SpotifyClient(cookie_file=cookie_file)
        self.results_dir = "spotify_analysis"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def analyze(self, url, download_media=False):
        """Analyze any Spotify URL and optionally download media."""
        
        # Validate URL
        if not is_spotify_url(url):
            return {"error": "Invalid Spotify URL"}
        
        # Determine URL type
        url_type = get_url_type(url)
        
        try:
            # Extract data based on type
            if url_type == "track":
                return self._analyze_track(url, download_media)
            elif url_type == "album":
                return self._analyze_album(url, download_media)
            elif url_type == "artist":
                return self._analyze_artist(url)
            elif url_type == "playlist":
                return self._analyze_playlist(url)
            else:
                return {"error": f"Unsupported URL type: {url_type}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_track(self, url, download_media):
        """Analyze a track."""
        track = self.client.get_track_info(url)
        
        analysis = {
            "type": "track",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "id": track['id'],
                "name": track.get('name', 'Unknown'),
                "artists": [a['name'] for a in track['artists']],
                "album": track.get('album', {}).get('name', 'Unknown'),
                "duration_seconds": track.get('duration_ms', 0) / 1000,
                "popularity": track.get('popularity', 0),
                "explicit": track.get('explicit', False),
                "preview_available": bool(track.get('preview_url'))
            }
        }
        
        # Download media if requested
        if download_media:
            media_dir = os.path.join(self.results_dir, f"track_{track['id']}")
            os.makedirs(media_dir, exist_ok=True)
            
            # Save metadata
            with open(os.path.join(media_dir, "metadata.json"), 'w') as f:
                json.dump(analysis, f, indent=2)
            
            # Download preview if available
            if track.get('preview_url'):
                try:
                    audio_path = self.client.download_preview_mp3(
                        url,
                        path=media_dir,
                        with_cover=True
                    )
                    analysis['downloaded_audio'] = audio_path
                except Exception as e:
                    analysis['audio_error'] = str(e)
            
            # Download cover
            try:
                cover_path = self.client.download_cover(url, path=media_dir)
                analysis['downloaded_cover'] = cover_path
            except Exception as e:
                analysis['cover_error'] = str(e)
        
        return analysis
    
    def _analyze_album(self, url, download_media):
        """Analyze an album."""
        album = self.client.get_album_info(url)
        
        analysis = {
            "type": "album",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "id": album['id'],
                "name": album.get('name', 'Unknown'),
                "artists": [a['name'] for a in album['artists']],
                "release_date": album.get('release_date', 'N/A'),
                "total_tracks": album.get('total_tracks', 0),
                "label": album.get('label', 'Unknown'),
                "tracks": [
                    {
                        "number": t['track_number'],
                        "name": t['name'],
                        "duration_seconds": t['duration_ms'] / 1000
                    }
                    for t in album['tracks']
                ]
            }
        }
        
        if download_media:
            media_dir = os.path.join(self.results_dir, f"album_{album['id']}")
            os.makedirs(media_dir, exist_ok=True)
            
            # Save metadata
            with open(os.path.join(media_dir, "metadata.json"), 'w') as f:
                json.dump(analysis, f, indent=2)
            
            # Download cover
            try:
                cover_path = self.client.download_cover(url, path=media_dir)
                analysis['downloaded_cover'] = cover_path
            except Exception as e:
                analysis['cover_error'] = str(e)
        
        return analysis
    
    def _analyze_artist(self, url):
        """Analyze an artist."""
        artist = self.client.get_artist_info(url)
        
        return {
            "type": "artist",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "id": artist['id'],
                "name": artist.get('name', 'Unknown'),
                "genres": artist.get('genres', []),
                "popularity": artist.get('popularity', 0),
                "followers": artist.get('followers', {}).get('total', 'N/A'),
                "verified": artist.get('verified', False),
                "top_tracks": [
                    {"name": t['name'], "popularity": t.get('popularity', 0)}
                    for t in artist.get('top_tracks', [])[:5]
                ]
            }
        }
    
    def _analyze_playlist(self, url):
        """Analyze a playlist."""
        playlist = self.client.get_playlist_info(url)
        
        # Calculate statistics
        tracks = playlist['tracks']
        total_duration_ms = sum(item['track']['duration_ms'] for item in tracks)
        
        # Get unique artists
        all_artists = []
        for item in tracks:
            all_artists.extend([a['name'] for a in item['track']['artists']])
        
        unique_artists = list(set(all_artists))
        
        return {
            "type": "playlist",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "id": playlist['id'],
                "name": playlist.get('name', 'Unknown'),
                "owner": playlist.get('owner', {}).get('display_name', playlist.get('owner', {}).get('id', 'Unknown')),
                "description": playlist.get('description', ''),
                "public": playlist.get('public', True),
                "collaborative": playlist.get('collaborative', False),
                "total_tracks": playlist.get('track_count', 0),
                "total_duration_hours": total_duration_ms / 3600000,
                "unique_artists": len(unique_artists),
                "sample_tracks": [
                    {
                        "name": item['track']['name'],
                        "artists": [a['name'] for a in item['track']['artists']]
                    }
                    for item in tracks[:5]
                ]
            }
        }
    
    def close(self):
        """Clean up resources."""
        self.client.close()

# Usage example
analyzer = SpotifyAnalyzer()

# Analyze different types of content
urls = [
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
    "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv",
    "https://open.spotify.com/artist/1dfeR4HaWDbWqFHLkxsg1d",
    "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
]

for url in urls:
    print(f"\nAnalyzing: {url}")
    result = analyzer.analyze(url, download_media=True)
    
    if "error" not in result:
        print(f"Type: {result['type']}")
        print(f"Name: {result['data']['name']}")
        
        # Save full analysis
        filename = f"{result['type']}_{result['data']['id']}_analysis.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Analysis saved to: {filename}")
    else:
        print(f"Error: {result['error']}")

analyzer.close()
```

## Performance Tips

1. **Reuse Client Instances**: Create one client and use it for multiple operations
2. **Add Delays**: Wait at least 0.5 seconds between requests
3. **Use Requests Backend**: It's faster than Selenium for most use cases
4. **Handle Errors Gracefully**: Not all content is available everywhere
5. **Close Resources**: Always call `client.close()` when done

## Next Steps

Now that you've learned the basics:

1. Check out the [Advanced Usage Guide](advanced.md) for complex scenarios
2. Learn about [Authentication](../guide/authentication.md) for accessing lyrics
3. Explore the [API Reference](../api/client.md) for detailed documentation
4. See [Real-World Examples](https://github.com/AliAkhtari78/SpotifyScraper/tree/master/examples)

## Common Issues

- **No Preview Available**: Not all tracks have preview URLs
- **Empty Album Names**: The embed API sometimes returns empty album names (but images are available)
- **Rate Limiting**: Add delays between requests to avoid being blocked
- **Authentication Required**: Lyrics require valid Spotify cookies

For more help, see the [FAQ](../faq.md) and [Troubleshooting Guide](../troubleshooting.md).