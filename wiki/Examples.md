# Examples

Real-world examples and code snippets for SpotifyScraper.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Authentication Examples](#authentication-examples)
- [Bulk Operations](#bulk-operations)
- [Data Analysis](#data-analysis)
- [Error Handling](#error-handling)
- [Integration Examples](#integration-examples)
- [CLI Examples](#cli-examples)

## Basic Examples

### Simple Track Extraction

```python
from spotify_scraper import SpotifyClient

# Initialize client
client = SpotifyClient()

# Get track info
track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
track_info = client.get_track_info(track_url)

print(f"Track: {track_info['name']}")
print(f"Artist: {track_info['artists'][0]['name']}")
print(f"Album: {track_info['album']['name']}")
print(f"Duration: {track_info['duration_ms'] / 1000:.2f} seconds")

# Don't forget to close
client.close()
```

### Extract Album with All Tracks

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

album_url = "https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp"
album_info = client.get_album_info(album_url)

print(f"Album: {album_info['name']}")
print(f"Artist: {album_info['artists'][0]['name']}")
print(f"Release Date: {album_info['release_date']}")
print(f"Total Tracks: {album_info['total_tracks']}")

# List all tracks
for i, track in enumerate(album_info['tracks'], 1):
    print(f"{i}. {track['name']} ({track['duration_ms'] / 1000:.2f}s)")

client.close()
```

### Download Media

```python
from spotify_scraper import SpotifyClient
import os

client = SpotifyClient()

track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"

# Create directories
os.makedirs("downloads/covers", exist_ok=True)
os.makedirs("downloads/previews", exist_ok=True)

# Download cover image
cover_path = client.download_cover(
    track_url,
    path="downloads/covers/",
    quality_preference=["large", "medium", "small"]
)
print(f"Cover downloaded: {cover_path}")

# Download preview with embedded cover
preview_path = client.download_preview_mp3(
    track_url,
    path="downloads/previews/",
    with_cover=True
)
print(f"Preview downloaded: {preview_path}")

client.close()
```

## Authentication Examples

### Using Cookie File

```python
from spotify_scraper import SpotifyClient

# Export cookies from your browser to a file
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Now you can access lyrics
track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
lyrics = client.get_track_lyrics(track_url)

if lyrics:
    print("Lyrics:")
    print(lyrics)
else:
    print("No lyrics available")

client.close()
```

### Using Cookie Dictionary

```python
from spotify_scraper import SpotifyClient

# Use cookies directly
cookies = {
    "sp_t": "your_auth_token_here",
    "sp_dc": "your_dc_token_here"
}

client = SpotifyClient(cookies=cookies)

# Get track with lyrics
track_with_lyrics = client.get_track_info_with_lyrics(
    "https://open.spotify.com/track/...",
    require_lyrics_auth=True
)

client.close()
```

## Bulk Operations

### Process Multiple URLs

```python
from spotify_scraper.utils.common import SpotifyBulkOperations
import time

# URLs to process
urls = [
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
    "https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp",
    "https://open.spotify.com/artist/00FQb4jTyendYWaN8pK0wa",
    "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
]

# Initialize bulk processor
bulk = SpotifyBulkOperations()

# Process all URLs
results = bulk.process_urls(urls, operation="all_info", delay=1)

# Export results
bulk.export_to_json(results, "spotify_data.json")
bulk.export_to_csv(results, "spotify_data.csv")

print(f"Processed {len(results['successful'])} URLs successfully")
print(f"Failed: {len(results['failed'])}")
```

### Create Dataset from Playlist

```python
from spotify_scraper.utils.common import SpotifyBulkOperations

bulk = SpotifyBulkOperations()

# Create a dataset from playlist tracks
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
dataset = bulk.create_dataset_from_playlist(
    playlist_url,
    include_audio_features=False,  # Audio features require API access
    output_file="playlist_dataset.json"
)

print(f"Dataset created with {dataset['metadata']['total_tracks']} tracks")
```

## Data Analysis

### Analyze Playlist

```python
from spotify_scraper.utils.common import SpotifyDataAnalyzer

analyzer = SpotifyDataAnalyzer()

playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
stats = analyzer.analyze_playlist(playlist_url)

print("Playlist Analysis:")
print(f"Total Duration: {stats['total_duration_formatted']}")
print(f"Average Track Length: {stats['average_duration_formatted']}")
print(f"Explicit Tracks: {stats['explicit_percentage']:.1f}%")

print("\nTop Artists:")
for artist, count in stats['most_common_artists'][:5]:
    print(f"  {artist}: {count} tracks")

print("\nRelease Years:")
for year, count in sorted(stats['release_years'].items())[-5:]:
    print(f"  {year}: {count} tracks")
```

### Compare Playlists

```python
from spotify_scraper.utils.common import SpotifyDataAnalyzer

analyzer = SpotifyDataAnalyzer()

playlist1 = "https://open.spotify.com/playlist/..."
playlist2 = "https://open.spotify.com/playlist/..."

comparison = analyzer.compare_playlists(playlist1, playlist2)

print(f"Common Tracks: {len(comparison['common_tracks'])}")
print(f"Common Artists: {len(comparison['common_artists'])}")
print(f"Similarity Score: {comparison['similarity_score']:.2%}")

print("\nUnique to Playlist 1:")
for track in comparison['unique_to_playlist1'][:5]:
    print(f"  - {track['name']} by {track['artists'][0]['name']}")
```

## Error Handling

### Comprehensive Error Handling

```python
from spotify_scraper import (
    SpotifyClient,
    URLError,
    NetworkError,
    ExtractionError,
    AuthenticationError,
    MediaError
)

client = SpotifyClient()

def safe_extract(url):
    try:
        info = client.get_all_info(url)
        return info
    except URLError as e:
        print(f"Invalid URL: {e}")
    except NetworkError as e:
        print(f"Network error: {e}")
        # Could retry with exponential backoff
    except AuthenticationError as e:
        print(f"Authentication required: {e}")
    except ExtractionError as e:
        print(f"Failed to extract data: {e}")
    except MediaError as e:
        print(f"Media operation failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

# Use the safe function
result = safe_extract("https://open.spotify.com/track/...")
if result:
    print(f"Successfully extracted: {result['name']}")

client.close()
```

### Retry Logic

```python
from spotify_scraper import SpotifyClient, NetworkError
import time

def extract_with_retry(client, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.get_all_info(url)
        except NetworkError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    
client = SpotifyClient()
try:
    result = extract_with_retry(client, "https://open.spotify.com/track/...")
except NetworkError:
    print("Failed after all retries")
finally:
    client.close()
```

## Integration Examples

### Flask Web Application

```python
from flask import Flask, jsonify, request
from spotify_scraper import SpotifyClient, URLError
import atexit

app = Flask(__name__)

# Global client instance
client = SpotifyClient()

# Ensure cleanup on exit
atexit.register(lambda: client.close())

@app.route('/api/track/<track_id>')
def get_track(track_id):
    try:
        url = f"https://open.spotify.com/track/{track_id}"
        track_info = client.get_track_info(url)
        return jsonify(track_info)
    except URLError:
        return jsonify({"error": "Invalid track ID"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_by_url():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    try:
        info = client.get_all_info(url)
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Discord Bot

```python
import discord
from discord.ext import commands
from spotify_scraper import SpotifyClient, is_spotify_url

bot = commands.Bot(command_prefix='!')
client = SpotifyClient()

@bot.command()
async def spotify(ctx, url):
    """Extract Spotify track info"""
    if not is_spotify_url(url):
        await ctx.send("Please provide a valid Spotify URL")
        return
    
    try:
        info = client.get_all_info(url)
        
        embed = discord.Embed(
            title=info['name'],
            url=url,
            color=0x1DB954  # Spotify green
        )
        
        if info['type'] == 'track':
            embed.add_field(name="Artist", value=info['artists'][0]['name'])
            embed.add_field(name="Album", value=info['album']['name'])
            embed.add_field(name="Duration", value=f"{info['duration_ms'] / 1000:.0f}s")
        
        if 'images' in info and info['images']:
            embed.set_thumbnail(url=info['images'][0]['url'])
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# Run bot
bot.run('YOUR_BOT_TOKEN')
```

### Data Export Script

```python
from spotify_scraper.utils.common import SpotifyDataFormatter, SpotifyBulkOperations
import sys

def export_playlist_data(playlist_url, output_format='json'):
    """Export playlist data in various formats"""
    
    # Get playlist data
    bulk = SpotifyBulkOperations()
    formatter = SpotifyDataFormatter()
    
    print(f"Fetching playlist data...")
    client = bulk.client
    playlist_info = client.get_playlist_info(playlist_url)
    
    # Format based on output type
    if output_format == 'json':
        formatter.export_to_json(playlist_info, 'playlist_export.json')
    elif output_format == 'csv':
        # Convert tracks to CSV
        tracks_data = []
        for track in playlist_info['tracks']:
            tracks_data.append({
                'name': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else '',
                'album': track['album']['name'] if track.get('album') else '',
                'duration_ms': track.get('duration_ms', 0),
                'preview_url': track.get('preview_url', '')
            })
        formatter.export_to_csv(tracks_data, 'playlist_tracks.csv')
    elif output_format == 'table':
        print(formatter.format_as_table(playlist_info['tracks'][:20]))
    
    client.close()
    print(f"Export complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_playlist.py <playlist_url> [format]")
        sys.exit(1)
    
    url = sys.argv[1]
    fmt = sys.argv[2] if len(sys.argv) > 2 else 'json'
    export_playlist_data(url, fmt)
```

## CLI Examples

### Basic CLI Usage

```bash
# Get track information
spotify-scraper track https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh

# Pretty print album info
spotify-scraper album https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp --pretty

# Save playlist to JSON
spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M -o playlist.json

# Download track preview with cover
spotify-scraper download track https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh --with-cover

# Use different output formats
spotify-scraper track https://open.spotify.com/track/... --format yaml
spotify-scraper track https://open.spotify.com/track/... --format table
```

### Advanced CLI Usage

```bash
# Use with authentication
spotify-scraper track https://open.spotify.com/track/... --cookie-file cookies.txt --with-lyrics

# Use Selenium browser
spotify-scraper track https://open.spotify.com/track/... --browser selenium

# Set log level
spotify-scraper --log-level DEBUG track https://open.spotify.com/track/...

# Download batch
spotify-scraper download batch urls.txt --output downloads/

# Extract only track list from album
spotify-scraper album https://open.spotify.com/album/... --tracks-only
```

### Scripting with CLI

```bash
#!/bin/bash

# Extract multiple tracks
TRACKS=(
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
    "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b"
    "https://open.spotify.com/track/1p80LdxRV74UKvL8gnD7ky"
)

for track in "${TRACKS[@]}"; do
    echo "Processing: $track"
    spotify-scraper track "$track" -o "data/$(basename $track).json"
    spotify-scraper download cover "$track" -o "covers/$(basename $track).jpg"
    sleep 1  # Rate limiting
done
```