# Examples

Real-world examples and code snippets for SpotifyScraper.

## 📚 Table of Contents

- [Basic Examples](#basic-examples)
- [Advanced Examples](#advanced-examples)
- [Integration Examples](#integration-examples)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)

## Basic Examples

### Extract Track Information

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Single track
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track = client.get_track_info(track_url)

print(f"Track: {track['name']}")
print(f"Artist: {', '.join(artist['name'] for artist in track['artists'])}")
print(f"Album: {track['album']['name']}")
print(f"Duration: {track['duration_ms'] / 1000 / 60:.1f} minutes")
```

### Download Track Preview and Cover

```python
# Download preview MP3
preview_path = client.download_preview_mp3(
    track_url,
    path="downloads/previews/",
    filename="song_preview"
)

# Download cover art
cover_path = client.download_cover(
    track_url,
    path="downloads/covers/",
    size=640  # 640x640 pixels
)

print(f"Preview: {preview_path}")
print(f"Cover: {cover_path}")
```

### Process an Entire Album

```python
album_url = "https://open.spotify.com/album/3yyMKUSiCVByiZGLNQpS1G"
album = client.get_album_info(album_url)

print(f"Album: {album['name']} by {album['artists'][0]['name']}")
print(f"Released: {album['release_date']}")
print(f"Tracks: {album['total_tracks']}")

# Process each track
for i, track in enumerate(album['tracks'], 1):
    print(f"{i:2d}. {track['name']} ({track['duration_ms'] / 1000:.0f}s)")
```

### Extract Artist Information

```python
artist_url = "https://open.spotify.com/artist/0TnOYISbd1XYRBk9myaseg"
artist = client.get_artist_info(artist_url)

print(f"Artist: {artist['name']}")
print(f"Followers: {artist['followers']:,}")
print(f"Monthly Listeners: {artist['monthly_listeners']:,}")
print(f"Genres: {', '.join(artist['genres'])}")

# Top tracks
print("\nTop Tracks:")
for i, track in enumerate(artist['top_tracks'][:5], 1):
    print(f"{i}. {track['name']}")
```

### Process Playlist

```python
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
playlist = client.get_playlist_info(playlist_url, tracks_limit=50)

print(f"Playlist: {playlist['name']}")
print(f"By: {playlist['owner']['display_name']}")
print(f"Tracks: {playlist['total_tracks']}")

# Save playlist to file
import json
with open("playlist.json", "w") as f:
    json.dump(playlist, f, indent=2)
```

## Advanced Examples

### Authenticated Features (Lyrics)

```python
# Initialize with cookies
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Get track with lyrics
track = client.get_track_info_with_lyrics(track_url)

if track.get('lyrics'):
    print(f"Lyrics for {track['name']}:")
    print(track['lyrics']['text'])
else:
    print("Lyrics not available")
```

### Batch Processing with Progress

```python
from tqdm import tqdm

urls = [
    "https://open.spotify.com/track/...",
    "https://open.spotify.com/track/...",
    # ... more URLs
]

results = []
for url in tqdm(urls, desc="Processing tracks"):
    try:
        track = client.get_track_info(url)
        results.append({
            'url': url,
            'name': track['name'],
            'artists': [a['name'] for a in track['artists']],
            'duration': track['duration_ms']
        })
    except Exception as e:
        print(f"Failed to process {url}: {e}")
```

### Caching and Performance

```python
import time

# Enable caching
client = SpotifyClient(
    cache_enabled=True,
    cache_dir=".spotify_cache"
)

# First call - fetches from Spotify
start = time.time()
track1 = client.get_track_info(track_url)
print(f"First call: {time.time() - start:.2f}s")

# Second call - uses cache
start = time.time()
track2 = client.get_track_info(track_url)
print(f"Cached call: {time.time() - start:.2f}s")
```

### Custom Session Configuration

```python
import requests

# Create custom session with headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'MyApp/1.0',
    'Accept-Language': 'en-US,en;q=0.9'
})

# Use proxy
proxy = "http://proxy.example.com:8080"

client = SpotifyClient(
    session=session,
    proxy=proxy,
    timeout=60,
    max_retries=5
)
```

## Integration Examples

### Flask Web Application

```python
from flask import Flask, jsonify, request
from spotify_scraper import SpotifyClient

app = Flask(__name__)
client = SpotifyClient()

@app.route('/api/track')
def get_track():
    url = request.args.get('url')
    try:
        track = client.get_track_info(url)
        return jsonify(track)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/download/preview')
def download_preview():
    url = request.args.get('url')
    try:
        path = client.download_preview_mp3(url)
        return jsonify({'path': path})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
```

### Discord Bot Integration

```python
import discord
from discord.ext import commands
from spotify_scraper import SpotifyClient

bot = commands.Bot(command_prefix='!')
spotify = SpotifyClient()

@bot.command()
async def track(ctx, url: str):
    """Get track information"""
    try:
        track = spotify.get_track_info(url)
        embed = discord.Embed(
            title=track['name'],
            description=f"by {', '.join(a['name'] for a in track['artists'])}",
            color=0x1DB954
        )
        embed.add_field(name="Album", value=track['album']['name'])
        embed.add_field(name="Duration", value=f"{track['duration_ms'] / 1000:.0f}s")
        if track['album']['images']:
            embed.set_thumbnail(url=track['album']['images'][0]['url'])
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {e}")

bot.run('YOUR_BOT_TOKEN')
```

### Data Analysis with Pandas

```python
import pandas as pd
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Analyze playlist
playlist_url = "https://open.spotify.com/playlist/..."
playlist = client.get_playlist_info(playlist_url)

# Convert to DataFrame
tracks_data = []
for track in playlist['tracks']:
    tracks_data.append({
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'duration_ms': track['duration_ms'],
        'popularity': track.get('popularity', 0),
        'explicit': track.get('explicit', False)
    })

df = pd.DataFrame(tracks_data)

# Analysis
print(f"Total duration: {df['duration_ms'].sum() / 1000 / 60:.1f} minutes")
print(f"Average track length: {df['duration_ms'].mean() / 1000:.1f} seconds")
print(f"Most common artist: {df['artist'].value_counts().iloc[0]}")
print(f"Explicit tracks: {df['explicit'].sum()} ({df['explicit'].mean() * 100:.1f}%)")
```

## Error Handling

### Comprehensive Error Handling

```python
from spotify_scraper import (
    SpotifyClient, URLError, NetworkError,
    AuthenticationError, ExtractionError
)

client = SpotifyClient()

def safe_extract(url):
    """Safely extract data with proper error handling"""
    try:
        return client.get_all_info(url)
    except URLError as e:
        print(f"Invalid URL: {e}")
        return None
    except NetworkError as e:
        print(f"Network issue: {e}")
        # Retry logic here
        return None
    except AuthenticationError as e:
        print(f"Authentication required: {e}")
        return None
    except ExtractionError as e:
        print(f"Failed to extract data: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### Retry with Exponential Backoff

```python
import time

def extract_with_retry(client, url, max_retries=3):
    """Extract data with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            return client.get_track_info(url)
        except NetworkError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
            time.sleep(wait_time)
```

## Performance Optimization

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
import time

urls = ["https://open.spotify.com/track/..." for _ in range(10)]

# Sequential processing
start = time.time()
results_seq = []
for url in urls:
    results_seq.append(client.get_track_info(url))
print(f"Sequential: {time.time() - start:.2f}s")

# Parallel processing
start = time.time()
with ThreadPoolExecutor(max_workers=5) as executor:
    results_par = list(executor.map(client.get_track_info, urls))
print(f"Parallel: {time.time() - start:.2f}s")
```

### Memory-Efficient Playlist Processing

```python
def process_large_playlist(playlist_url, batch_size=50):
    """Process large playlist in batches"""
    offset = 0
    all_tracks = []
    
    while True:
        # Note: This is pseudo-code, actual implementation may vary
        playlist = client.get_playlist_info(
            playlist_url,
            tracks_limit=batch_size,
            offset=offset
        )
        
        tracks = playlist.get('tracks', [])
        if not tracks:
            break
            
        all_tracks.extend(tracks)
        offset += batch_size
        
        # Process batch
        for track in tracks:
            # Process each track
            pass
            
    return all_tracks
```

### Custom Cache Implementation

```python
import pickle
import hashlib
from pathlib import Path

class CachedSpotifyClient(SpotifyClient):
    def __init__(self, cache_dir=".cache", **kwargs):
        super().__init__(**kwargs)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, url):
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_track_info(self, url):
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        # Check cache
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        
        # Fetch and cache
        data = super().get_track_info(url)
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
        
        return data
```