# Examples

This page contains comprehensive examples demonstrating various SpotifyScraper use cases.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Authentication Examples](#authentication-examples)
3. [Batch Processing](#batch-processing)
4. [Error Handling](#error-handling)
5. [Media Downloads](#media-downloads)
6. [Advanced Use Cases](#advanced-use-cases)
7. [CLI Examples](#cli-examples)

## Basic Examples

### Simple Track Extraction

```python
from spotify_scraper import SpotifyClient

# Create client
client = SpotifyClient()

# Extract track info
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track = client.get_track_info(track_url)

# Display information
print(f"Track: {track['name']}")
print(f"Artist: {', '.join([a['name'] for a in track['artists']])}")
print(f"Album: {track['album']['name']}")
print(f"Duration: {track['duration_ms'] / 60000:.2f} minutes")
print(f"Popularity: {track['popularity']}/100")
print(f"Preview URL: {track.get('preview_url', 'Not available')}")

# Clean up
client.close()
```

### Working with Albums

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Get album information
album_url = "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"
album = client.get_album_info(album_url)

print(f"Album: {album['name']}")
print(f"Artist: {album['artists'][0]['name']}")
print(f"Release Date: {album['release_date']}")
print(f"Label: {album.get('label', 'Unknown')}")
print(f"\nTracklist ({album['total_tracks']} tracks):")

# List all tracks with duration
total_duration = 0
for i, track in enumerate(album['tracks']['items'], 1):
    duration_sec = track['duration_ms'] / 1000
    total_duration += duration_sec
    print(f"{i:2d}. {track['name']} - {duration_sec // 60:.0f}:{duration_sec % 60:02.0f}")

print(f"\nTotal Duration: {total_duration // 60:.0f}:{total_duration % 60:02.0f}")

client.close()
```

### Artist Analysis

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Get artist information
artist_url = "https://open.spotify.com/artist/1dfeR4HaWDbWqFHLkxsg1d"
artist = client.get_artist_info(artist_url)

print(f"Artist: {artist['name']}")
print(f"Genres: {', '.join(artist.get('genres', []))}")
print(f"Followers: {artist['followers']['total']:,}")
print(f"Popularity: {artist['popularity']}/100")

# Top tracks
if 'top_tracks' in artist:
    print(f"\nTop Tracks:")
    for i, track in enumerate(artist['top_tracks'][:5], 1):
        print(f"{i}. {track['name']}")

# Related artists
if 'related_artists' in artist:
    print(f"\nRelated Artists:")
    for related in artist['related_artists'][:5]:
        print(f"- {related['name']}")

client.close()
```

### Playlist Explorer

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Get playlist information
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
playlist = client.get_playlist_info(playlist_url)

print(f"Playlist: {playlist['name']}")
print(f"Created by: {playlist['owner']['display_name']}")
print(f"Description: {playlist.get('description', 'No description')}")
print(f"Total Tracks: {playlist['tracks']['total']}")

# Calculate total duration
total_ms = sum(track['track']['duration_ms'] for track in playlist['tracks']['items'])
hours = total_ms // 3600000
minutes = (total_ms % 3600000) // 60000

print(f"Total Duration: {hours}h {minutes}m")

# Show first 10 tracks
print("\nFirst 10 tracks:")
for i, item in enumerate(playlist['tracks']['items'][:10], 1):
    track = item['track']
    artists = ', '.join([a['name'] for a in track['artists']])
    print(f"{i:2d}. {track['name']} - {artists}")

client.close()
```

## Authentication Examples

### Using Cookie File

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.core.exceptions import AuthenticationError

# Create authenticated client
client = SpotifyClient(cookie_file="spotify_cookies.txt")

track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"

try:
    # Get track with lyrics
    track = client.get_track_info_with_lyrics(track_url)
    
    print(f"Track: {track['name']}")
    print(f"Artist: {track['artists'][0]['name']}")
    
    if track.get('lyrics'):
        print("\nLyrics:")
        print("-" * 50)
        print(track['lyrics'])
    else:
        print("\nNo lyrics available for this track")
        
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    print("Please check your cookie file")

client.close()
```

### Using Cookie Dictionary

```python
from spotify_scraper import SpotifyClient

# Using cookies directly
cookies = {
    "sp_t": "your_auth_token_here",
    "sp_dc": "your_dc_token_here"
}

client = SpotifyClient(cookies=cookies)

# Now you can access lyrics
track = client.get_track_info_with_lyrics(track_url)
```

## Batch Processing

### Process Multiple Tracks

```python
from spotify_scraper import SpotifyClient
import time
import csv

# List of track URLs
track_urls = [
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
    "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp",
    "https://open.spotify.com/track/1h2xVEoJORqrg71HocgqXd",
]

client = SpotifyClient()
results = []

print("Processing tracks...")
for i, url in enumerate(track_urls, 1):
    print(f"[{i}/{len(track_urls)}] Processing: {url}")
    
    try:
        track = client.get_track_info(url)
        results.append({
            'name': track['name'],
            'artists': ', '.join([a['name'] for a in track['artists']]),
            'album': track['album']['name'],
            'duration_ms': track['duration_ms'],
            'popularity': track['popularity'],
            'preview_url': track.get('preview_url', '')
        })
        print(f"  ✓ {track['name']} - {results[-1]['artists']}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
        results.append({'url': url, 'error': str(e)})
    
    # Be nice to Spotify's servers
    time.sleep(0.5)

# Save to CSV
with open('tracks.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'artists', 'album', 'duration_ms', 'popularity', 'preview_url'])
    writer.writeheader()
    writer.writerows(results)

print(f"\nProcessed {len(results)} tracks. Results saved to tracks.csv")
client.close()
```

### Process Artist Discography

```python
from spotify_scraper import SpotifyClient
import json

def get_artist_discography(client, artist_url):
    """Get all albums for an artist."""
    artist = client.get_artist_info(artist_url)
    
    discography = {
        'artist': artist['name'],
        'artist_id': artist['id'],
        'albums': [],
        'singles': [],
        'compilations': []
    }
    
    # Process different album types
    for album_type, key in [('albums', 'albums'), ('singles', 'singles'), ('compilations', 'compilations')]:
        if key in artist:
            for album in artist[key]:
                album_data = {
                    'name': album['name'],
                    'id': album['id'],
                    'release_date': album.get('release_date', ''),
                    'total_tracks': album.get('total_tracks', 0)
                }
                discography[album_type].append(album_data)
    
    return discography

# Example usage
client = SpotifyClient()
artist_url = "https://open.spotify.com/artist/1dfeR4HaWDbWqFHLkxsg1d"

print("Fetching artist discography...")
discography = get_artist_discography(client, artist_url)

print(f"\nDiscography for {discography['artist']}:")
print(f"Albums: {len(discography['albums'])}")
print(f"Singles: {len(discography['singles'])}")
print(f"Compilations: {len(discography['compilations'])}")

# Save to JSON
with open(f"{discography['artist']}_discography.json", 'w', encoding='utf-8') as f:
    json.dump(discography, f, indent=2, ensure_ascii=False)

client.close()
```

## Error Handling

### Comprehensive Error Handling

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.core.exceptions import (
    URLError, ScrapingError, AuthenticationError, MediaError
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_extract(client, url):
    """Safely extract information with comprehensive error handling."""
    try:
        # Validate URL first
        if not url.startswith(('https://open.spotify.com', 'spotify:')):
            raise URLError(f"Invalid URL format: {url}")
        
        # Extract information
        info = client.get_all_info(url)
        
        # Check for API errors
        if 'error' in info:
            raise ScrapingError(f"API Error: {info['error']}")
        
        logger.info(f"Successfully extracted: {info['name']}")
        return info
        
    except URLError as e:
        logger.error(f"URL Error: {e}")
        return {'error': 'invalid_url', 'message': str(e)}
        
    except ScrapingError as e:
        logger.error(f"Scraping Error: {e}")
        return {'error': 'scraping_failed', 'message': str(e)}
        
    except AuthenticationError as e:
        logger.error(f"Authentication Error: {e}")
        return {'error': 'auth_required', 'message': str(e)}
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {'error': 'unknown', 'message': str(e)}

# Example usage
client = SpotifyClient()

test_urls = [
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",  # Valid
    "https://open.spotify.com/invalid/123",  # Invalid
    "not_a_url",  # Invalid format
]

for url in test_urls:
    print(f"\nProcessing: {url}")
    result = safe_extract(client, url)
    
    if 'error' in result:
        print(f"  Failed: {result['message']}")
    else:
        print(f"  Success: {result.get('name', 'Unknown')}")

client.close()
```

## Media Downloads

### Download Album Covers

```python
from spotify_scraper import SpotifyClient
from pathlib import Path

def download_album_covers(album_urls, output_dir="album_covers"):
    """Download covers for multiple albums."""
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    client = SpotifyClient()
    downloaded = []
    
    for url in album_urls:
        try:
            # Get album info
            album = client.get_album_info(url)
            album_name = album['name'].replace('/', '_')  # Safe filename
            
            # Download cover
            cover_path = client.download_cover(
                url,
                path=str(output_path),
                filename=f"{album_name}_cover"
            )
            
            if cover_path:
                downloaded.append({
                    'album': album['name'],
                    'artist': album['artists'][0]['name'],
                    'path': cover_path
                })
                print(f"✓ Downloaded: {album['name']}")
            
        except Exception as e:
            print(f"✗ Failed: {url} - {e}")
    
    client.close()
    return downloaded

# Example usage
album_urls = [
    "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv",
    "https://open.spotify.com/album/6dVIqQ8qmQ5GBnJ9shOYGE",
]

covers = download_album_covers(album_urls)
print(f"\nDownloaded {len(covers)} album covers")
```

### Download Track Previews with Metadata

```python
from spotify_scraper import SpotifyClient
from pathlib import Path
import json

def download_track_preview_with_metadata(track_url, output_dir="previews"):
    """Download preview MP3 and save metadata."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    client = SpotifyClient()
    
    try:
        # Get track info
        track = client.get_track_info(track_url)
        
        # Create safe filename
        artist_name = track['artists'][0]['name'].replace('/', '_')
        track_name = track['name'].replace('/', '_')
        base_filename = f"{artist_name} - {track_name}"
        
        # Download preview with cover
        if track.get('preview_url'):
            mp3_path = client.download_preview_mp3(
                track_url,
                path=str(output_path),
                with_cover=True
            )
            print(f"✓ Downloaded preview: {mp3_path}")
            
            # Save metadata
            metadata = {
                'track_id': track['id'],
                'name': track['name'],
                'artists': [a['name'] for a in track['artists']],
                'album': track['album']['name'],
                'duration_ms': track['duration_ms'],
                'preview_duration_ms': 30000,  # Usually 30 seconds
                'popularity': track['popularity'],
                'explicit': track.get('explicit', False),
                'preview_path': mp3_path
            }
            
            metadata_path = output_path / f"{base_filename}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Saved metadata: {metadata_path}")
            return metadata
        else:
            print("✗ No preview available for this track")
            return None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None
    finally:
        client.close()

# Example usage
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
metadata = download_track_preview_with_metadata(track_url)
```

## Advanced Use Cases

### Playlist Analyzer

```python
from spotify_scraper import SpotifyClient
from collections import Counter
import statistics

def analyze_playlist(playlist_url):
    """Analyze a playlist's characteristics."""
    client = SpotifyClient()
    
    try:
        playlist = client.get_playlist_info(playlist_url)
        
        # Extract data
        artists = []
        albums = []
        durations = []
        popularities = []
        
        for item in playlist['tracks']['items']:
            track = item['track']
            artists.extend([a['name'] for a in track['artists']])
            albums.append(track['album']['name'])
            durations.append(track['duration_ms'])
            popularities.append(track.get('popularity', 0))
        
        # Analyze
        analysis = {
            'name': playlist['name'],
            'owner': playlist['owner']['display_name'],
            'total_tracks': len(playlist['tracks']['items']),
            'total_duration_hours': sum(durations) / 3600000,
            'avg_track_duration_min': statistics.mean(durations) / 60000,
            'avg_popularity': statistics.mean(popularities) if popularities else 0,
            'unique_artists': len(set(artists)),
            'unique_albums': len(set(albums)),
            'top_artists': Counter(artists).most_common(10),
            'top_albums': Counter(albums).most_common(5)
        }
        
        return analysis
        
    finally:
        client.close()

# Example usage
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
analysis = analyze_playlist(playlist_url)

print(f"Playlist: {analysis['name']}")
print(f"Owner: {analysis['owner']}")
print(f"Total Tracks: {analysis['total_tracks']}")
print(f"Duration: {analysis['total_duration_hours']:.1f} hours")
print(f"Average Track Duration: {analysis['avg_track_duration_min']:.1f} minutes")
print(f"Average Popularity: {analysis['avg_popularity']:.0f}/100")
print(f"Unique Artists: {analysis['unique_artists']}")
print(f"Unique Albums: {analysis['unique_albums']}")

print("\nTop Artists:")
for artist, count in analysis['top_artists'][:5]:
    print(f"  {artist}: {count} tracks")
```

### Track Comparison

```python
from spotify_scraper import SpotifyClient

def compare_tracks(track_urls):
    """Compare multiple tracks."""
    client = SpotifyClient()
    tracks_data = []
    
    try:
        # Fetch all track data
        for url in track_urls:
            track = client.get_track_info(url)
            tracks_data.append(track)
        
        # Compare
        print("Track Comparison")
        print("=" * 80)
        
        # Basic info
        for track in tracks_data:
            artists = ', '.join([a['name'] for a in track['artists']])
            print(f"\n{track['name']} by {artists}")
            print(f"  Album: {track['album']['name']}")
            print(f"  Duration: {track['duration_ms'] / 60000:.2f} min")
            print(f"  Popularity: {track['popularity']}/100")
            print(f"  Explicit: {'Yes' if track.get('explicit') else 'No'}")
            print(f"  Preview: {'Available' if track.get('preview_url') else 'Not available'}")
        
        # Find most/least popular
        sorted_by_popularity = sorted(tracks_data, key=lambda x: x['popularity'], reverse=True)
        print(f"\nMost Popular: {sorted_by_popularity[0]['name']} ({sorted_by_popularity[0]['popularity']}/100)")
        print(f"Least Popular: {sorted_by_popularity[-1]['name']} ({sorted_by_popularity[-1]['popularity']}/100)")
        
        # Find longest/shortest
        sorted_by_duration = sorted(tracks_data, key=lambda x: x['duration_ms'], reverse=True)
        print(f"\nLongest: {sorted_by_duration[0]['name']} ({sorted_by_duration[0]['duration_ms'] / 60000:.2f} min)")
        print(f"Shortest: {sorted_by_duration[-1]['name']} ({sorted_by_duration[-1]['duration_ms'] / 60000:.2f} min)")
        
    finally:
        client.close()

# Example usage
track_urls = [
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",  # Bohemian Rhapsody
    "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp",  # Mr. Blue Sky
    "https://open.spotify.com/track/1h2xVEoJORqrg71HocgqXd",  # Stairway to Heaven
]

compare_tracks(track_urls)
```

### Create M3U Playlist

```python
from spotify_scraper import SpotifyClient
from pathlib import Path

def create_m3u_from_spotify_playlist(playlist_url, output_file="playlist.m3u"):
    """Create M3U playlist file from Spotify playlist."""
    client = SpotifyClient()
    
    try:
        playlist = client.get_playlist_info(playlist_url)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write extended M3U header
            f.write("#EXTM3U\n")
            f.write(f"#PLAYLIST:{playlist['name']}\n\n")
            
            for item in playlist['tracks']['items']:
                track = item['track']
                artists = ', '.join([a['name'] for a in track['artists']])
                duration_sec = track['duration_ms'] // 1000
                
                # Write track info
                f.write(f"#EXTINF:{duration_sec},{artists} - {track['name']}\n")
                
                # Write preview URL if available
                if track.get('preview_url'):
                    f.write(f"{track['preview_url']}\n")
                else:
                    f.write(f"# No preview available\n")
                
                f.write("\n")
        
        print(f"Created M3U playlist: {output_file}")
        print(f"Total tracks: {len(playlist['tracks']['items'])}")
        
    finally:
        client.close()

# Example usage
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
create_m3u_from_spotify_playlist(playlist_url, "top_hits.m3u")
```

## CLI Examples

### Command Line Usage

```bash
# Get track information
spotify-scraper track https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6

# Get album information with JSON output
spotify-scraper album https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv --format json

# Get artist information
spotify-scraper artist https://open.spotify.com/artist/1dfeR4HaWDbWqFHLkxsg1d

# Get playlist information
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M

# Download track preview
spotify-scraper download track https://open.spotify.com/track/... --output-dir ./previews

# Download album cover
spotify-scraper download album https://open.spotify.com/album/... --output-dir ./covers

# Batch process from file
spotify-scraper batch tracks.txt --output results.json

# With authentication for lyrics
spotify-scraper track https://open.spotify.com/track/... --cookie-file cookies.txt --with-lyrics
```

### Shell Script Example

```bash
#!/bin/bash
# Download previews for a playlist

PLAYLIST_URL="https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
OUTPUT_DIR="playlist_previews"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Get playlist tracks
echo "Fetching playlist tracks..."
spotify-scraper playlist "$PLAYLIST_URL" --format json > playlist.json

# Extract track URLs using jq
TRACK_URLS=$(jq -r '.tracks.items[].track.external_urls.spotify' playlist.json)

# Download each preview
echo "Downloading previews..."
for url in $TRACK_URLS; do
    echo "Processing: $url"
    spotify-scraper download track "$url" --output-dir "$OUTPUT_DIR" || echo "Failed: $url"
    sleep 1  # Be nice to the server
done

echo "Done! Downloaded to $OUTPUT_DIR"
```

## Performance Tips

1. **Use connection pooling for batch operations:**
   ```python
   client = SpotifyClient()
   # Process multiple URLs with same client
   for url in urls:
       # ...
   client.close()  # Close once at the end
   ```

2. **Add delays between requests:**
   ```python
   import time
   time.sleep(0.5)  # 500ms delay
   ```

3. **Use browser_type="requests" for better performance:**
   ```python
   client = SpotifyClient(browser_type="requests")
   ```

4. **Cache results when possible:**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def get_cached_track(url):
       return client.get_track_info(url)
   ```

5. **Handle rate limiting gracefully:**
   ```python
   import time
   from random import uniform
   
   def respectful_fetch(urls):
       for url in urls:
           try:
               yield client.get_track_info(url)
               time.sleep(uniform(0.5, 1.5))  # Random delay
           except Exception as e:
               if "rate" in str(e).lower():
                   time.sleep(30)  # Back off on rate limit
               else:
                   raise
   ```