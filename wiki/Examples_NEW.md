# Examples

Real-world examples demonstrating SpotifyScraper capabilities.

## Table of Contents

- [Basic Operations](#basic-operations)
- [Bulk Processing](#bulk-processing)
- [Data Export](#data-export)
- [Analysis & Statistics](#analysis--statistics)
- [Media Downloads](#media-downloads)
- [Error Handling](#error-handling)
- [Advanced Patterns](#advanced-patterns)

## Basic Operations

### Extract and Display Track Information

```python
from spotify_scraper import SpotifyClient

# Initialize client
client = SpotifyClient()

# Get track information
track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
track = client.get_track_info(track_url)

# Display formatted information
print(f"Track: {track.get('name', 'Unknown')}")
print(f"Artist(s): {', '.join(a['name'] for a in track['artists'])}")
print(f"Album: {track.get('album', {}).get('name', 'Unknown')}")
print(f"Released: {track['album'].get('release_date', 'N/A')}")
print(f"Duration: {track.get('duration_ms', 0) // 60000}:{(track.get('duration_ms', 0) % 60000) // 1000:02d}")
print(f"Explicit: {'Yes' if track.get('is_explicit', False) else 'No'}")

if track.get('preview_url'):
    print(f"Preview available: {track.get('preview_url', 'Not available')}")

client.close()
```

### Get Complete Album with Tracks

```python
# Get album information
album_url = "https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp"
album = client.get_album_info(album_url)

print(f"\nAlbum: {album.get('name', 'Unknown')}")
print(f"Artist: {(album.get('artists', [{}])[0].get('name', 'Unknown') if album.get('artists') else 'Unknown')}")
print(f"Released: {album.get('release_date', 'N/A')}")
print(f"Total tracks: {album.get('total_tracks', 0)}")

# List all tracks
print("\nTracklist:")
for i, item in enumerate(album['tracks'], 1):
    duration = item['duration_ms'] // 1000
    print(f"{i:2d}. {item['name']} ({duration // 60}:{duration % 60:02d})")
```

## Bulk Processing

### Process Multiple URLs from File

```python
from spotify_scraper.utils.common import SpotifyBulkOperations

# Read URLs from file
with open('spotify_urls.txt', 'r') as f:
    urls = [line.strip() for line in f if line.strip()]

# Process all URLs
bulk = SpotifyBulkOperations()
results = bulk.process_urls(urls, operation="info")

# Save results
bulk.export_to_json(results, "spotify_data.json")

# Summary
print(f"Processed: {results['processed']}")
print(f"Failed: {results['failed']}")
```

### Extract URLs from Text

```python
# Extract Spotify URLs from any text
text = """
Check out these tracks:
- https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
- One More Time by Daft Punk
- spotify:track:5W3cjX2J3tjhG8zb6u0qHn
- Also this album: https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp
"""

bulk = SpotifyBulkOperations()
urls = bulk.extract_urls_from_text(text)

print(f"Found {len(urls)} Spotify URLs:")
for url in urls:
    print(f"- {url}")
```

## Data Export

### Export Playlist to Multiple Formats

```python
import json
import csv
from spotify_scraper.utils.common import SpotifyDataFormatter

# Get playlist
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
playlist = client.get_playlist_info(playlist_url)

# 1. Export as JSON
with open('playlist.json', 'w', encoding='utf-8') as f:
    json.dump(playlist, f, indent=2, ensure_ascii=False)

# 2. Export as CSV
with open('playlist_tracks.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Position', 'Title', 'Artist(s)', 'Album', 'Duration', 'Added Date'])
    
    for i, item in enumerate(playlist['tracks'], 1):
        track = item['track']
        writer.writerow([
            i,
            track.get('name', 'Unknown'),
            ', '.join(a['name'] for a in track['artists']),
            track.get('album', {}).get('name', 'Unknown'),
            f"{track.get('duration_ms', 0) // 60000}:{(track.get('duration_ms', 0) % 60000) // 1000:02d}",
            item.get('added_at', 'N/A')
        ])

# 3. Export as Markdown
formatter = SpotifyDataFormatter()
markdown = formatter.format_playlist_markdown(playlist)
with open('playlist.md', 'w', encoding='utf-8') as f:
    f.write(markdown)

# 4. Export as M3U playlist
tracks = [item['track'] for item in playlist['tracks']]
formatter.export_to_m3u(tracks, 'playlist.m3u')

print(f"Exported playlist '{playlist.get('name', 'Unknown')}' to multiple formats")
```

### Create Dataset from Artist Discography

```python
# Get all albums from an artist
artist_url = "https://open.spotify.com/artist/3fMbdgg4jU18AjLCKBhRSm"
artist = client.get_artist_info(artist_url)

all_tracks = []

# Note: This example shows the concept - full discography requires additional API calls
print(f"Creating dataset for {artist.get('name', 'Unknown')}...")

# Export to structured dataset
dataset = {
    "artist": {
        "name": artist.get('name', 'Unknown'),
        "genres": artist.get('genres', []),
        "popularity": artist.get('popularity', 'N/A'),
        "followers": artist.get('followers', {}).get('total', 'N/A')
    },
    "tracks": all_tracks,
    "generated_at": datetime.now().isoformat()
}

with open(f"{artist.get('name', 'Unknown')}_dataset.json", 'w', encoding='utf-8') as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)
```

## Analysis & Statistics

### Analyze Playlist Composition

```python
from spotify_scraper.utils.common import SpotifyDataAnalyzer

# Get playlist
playlist = client.get_playlist_info(playlist_url)

# Analyze
analyzer = SpotifyDataAnalyzer()
analysis = analyzer.analyze_playlist(playlist)

# Display insights
print(f"\n📊 Playlist Analysis: {playlist.get('name', 'Unknown')}")
print(f"{'='*50}")

print(f"\n📈 Basic Statistics:")
print(f"Total tracks: {analysis['basic_stats']['total_tracks']}")
print(f"Total duration: {analysis['basic_stats']['total_duration_formatted']}")
print(f"Average track duration: {analysis['basic_stats']['average_track_duration_formatted']}")

print(f"\n🎤 Top Artists:")
for artist, count in analysis['artist_stats']['top_artists'][:5]:
    print(f"{artist}: {count} tracks")

print(f"\n📅 Release Years:")
years = analysis['temporal_stats']['release_year_distribution']
for year in sorted(years.keys(), reverse=True)[:5]:
    print(f"{year}: {years[year]} tracks")

# Note: Popularity data is not available via web scraping
# The analyzer's popularity features require data from Spotify's official API
```

### Compare Multiple Playlists

```python
# Get two playlists to compare
playlist1 = client.get_playlist_info("https://open.spotify.com/playlist/...")
playlist2 = client.get_playlist_info("https://open.spotify.com/playlist/...")

# Compare
comparison = analyzer.compare_playlists(playlist1, playlist2)

print(f"\n🔄 Playlist Comparison")
print(f"{'='*50}")
print(f"Comparing: '{comparison['playlist1_name']}' vs '{comparison['playlist2_name']}'")

print(f"\n📊 Track Statistics:")
print(f"Playlist 1: {comparison['track_comparison']['playlist1_total']} tracks")
print(f"Playlist 2: {comparison['track_comparison']['playlist2_total']} tracks")
print(f"Common tracks: {comparison['track_comparison']['common_tracks']}")
print(f"Similarity: {comparison['track_comparison']['similarity_percentage']:.1f}%")

print(f"\n🎤 Artist Overlap:")
print(f"Common artists: {comparison['artist_comparison']['common_artists']}")
print(f"Top shared artists: {', '.join(comparison['artist_comparison']['common_artist_names'][:5])}")
```

## Media Downloads

### Download All Album Covers from Playlist

```python
# Download unique album covers from a playlist
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

bulk = SpotifyBulkOperations()
downloaded = bulk.download_playlist_covers(
    playlist_url,
    output_dir="playlist_covers/",
    size_preference="large"
)

print(f"Downloaded {len(downloaded)} unique album covers")
```

### Batch Download with Progress

```python
from tqdm import tqdm

# URLs to process
track_urls = [
    "https://open.spotify.com/track/...",
    # ... more URLs
]

# Download with progress bar
downloaded_files = []

with tqdm(total=len(track_urls), desc="Downloading") as pbar:
    for url in track_urls:
        try:
            # Download preview
            preview_path = client.download_preview_mp3(
                url, 
                output_dir="previews/"
            )
            
            # Download cover
            cover_path = client.download_cover(
                url,
                output_dir="covers/"
            )
            
            downloaded_files.append({
                "url": url,
                "preview": preview_path,
                "cover": cover_path
            })
            
        except Exception as e:
            print(f"\nError with {url}: {e}")
        
        pbar.update(1)

print(f"\nSuccessfully downloaded {len(downloaded_files)} items")
```

## Error Handling

### Robust Processing with Retry Logic

```python
from spotify_scraper.core.exceptions import NetworkError, SpotifyScraperError
import time

def get_track_with_retry(client, url, max_retries=3):
    """Get track info with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            return client.get_track_info(url)
        except NetworkError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Network error, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        except SpotifyScraperError as e:
            print(f"Failed to get track: {e}")
            return None

# Use the function
track = get_track_with_retry(client, track_url)
if track:
    print(f"Successfully retrieved: {track.get('name', 'Unknown')}")
```

### Handle Different Error Types

```python
from spotify_scraper.core.exceptions import (
    URLError, NetworkError, ParsingError, 
    AuthenticationError, MediaError
)

def safe_process_url(client, url):
    """Process URL with comprehensive error handling."""
    try:
        # Validate URL first
        if not is_spotify_url(url):
            print(f"Skipping non-Spotify URL: {url}")
            return None
        
        # Get URL type
        url_type = get_url_type(url)
        
        # Process based on type
        if url_type == "track":
            return client.get_track_info(url)
        elif url_type == "album":
            return client.get_album_info(url)
        elif url_type == "playlist":
            return client.get_playlist_info(url)
        elif url_type == "artist":
            return client.get_artist_info(url)
            
    except URLError:
        print(f"Invalid Spotify URL format: {url}")
    except NetworkError as e:
        print(f"Network error: {e}")
    except ParsingError:
        print(f"Failed to parse data from: {url}")
    except AuthenticationError:
        print(f"Authentication required for: {url}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    return None
```

## Advanced Patterns

### Parallel Processing with Threading

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

def process_urls_parallel(urls: List[str], max_workers: int = 5) -> Dict[str, Any]:
    """Process multiple URLs in parallel."""
    results = {}
    
    with SpotifyClient() as client:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(client.get_track_info, url): url 
                for url in urls
            }
            
            # Process results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    results[url] = {"status": "success", "data": data}
                except Exception as e:
                    results[url] = {"status": "error", "error": str(e)}
    
    return results

# Use parallel processing
urls = ["https://open.spotify.com/track/..." for _ in range(10)]
results = process_urls_parallel(urls)
print(f"Processed {len(results)} URLs in parallel")
```

### Create Spotify URL Archive

```python
import sqlite3
from datetime import datetime

class SpotifyArchive:
    """Archive Spotify data in SQLite database."""
    
    def __init__(self, db_path: str = "spotify_archive.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id TEXT PRIMARY KEY,
                name TEXT,
                artists TEXT,
                album TEXT,
                duration_ms INTEGER,
                popularity INTEGER,
                data JSON,
                archived_at TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def archive_track(self, track_data: Dict[str, Any]):
        """Archive track data."""
        self.conn.execute("""
            INSERT OR REPLACE INTO tracks 
            (id, name, artists, album, duration_ms, popularity, data, archived_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            track_data['id'],
            track_data.get('name', 'Unknown'),
            ', '.join(a['name'] for a in track_data['artists']),
            track_data['album']['name'],
            track_data['duration_ms'],
            track_data['popularity'],
            json.dumps(track_data),
            datetime.now()
        ))
        self.conn.commit()
    
    def search(self, query: str) -> List[Dict]:
        """Search archived tracks."""
        cursor = self.conn.execute("""
            SELECT * FROM tracks 
            WHERE name LIKE ? OR artists LIKE ?
            ORDER BY popularity DESC
        """, (f"%{query}%", f"%{query}%"))
        
        return [dict(row) for row in cursor]

# Use the archive
archive = SpotifyArchive()
client = SpotifyClient()

# Archive tracks
track_urls = ["https://open.spotify.com/track/..."]
for url in track_urls:
    track = client.get_track_info(url)
    archive.archive_track(track)

# Search archive
results = archive.search("Daft Punk")
print(f"Found {len(results)} archived tracks")
```

### Generate Playlist Report

```python
from datetime import datetime

def generate_playlist_report(playlist_url: str, output_file: str = "playlist_report.html"):
    """Generate comprehensive HTML report for a playlist."""
    
    client = SpotifyClient()
    playlist = client.get_playlist_info(playlist_url)
    
    analyzer = SpotifyDataAnalyzer()
    analysis = analyzer.analyze_playlist(playlist)
    
    # Generate HTML report
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Playlist Report: {playlist.get('name', 'Unknown')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #1db954; }}
            .stats {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #1db954; color: white; }}
        </style>
    </head>
    <body>
        <h1>Playlist Report: {playlist.get('name', 'Unknown')}</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <h2>Overview</h2>
            <p><strong>Owner:</strong> {playlist.get('owner', {}).get('display_name', playlist.get('owner', {}).get('id', 'Unknown'))}</p>
            <p><strong>Total Tracks:</strong> {analysis['basic_stats']['total_tracks']}</p>
            <p><strong>Total Duration:</strong> {analysis['basic_stats']['total_duration_formatted']}</p>
            <p><strong>Average Popularity:</strong> {analysis['basic_stats']['average_popularity']:.1f}/100</p>
        </div>
        
        <h2>Top Artists</h2>
        <table>
            <tr><th>Artist</th><th>Track Count</th></tr>
            {"".join(f"<tr><td>{artist}</td><td>{count}</td></tr>" 
                     for artist, count in analysis['artist_stats']['top_artists'][:10])}
        </table>
        
        <h2>Track List</h2>
        <table>
            <tr><th>#</th><th>Title</th><th>Artist(s)</th><th>Album</th><th>Duration</th></tr>
            {"".join(f'''<tr>
                <td>{i}</td>
                <td>{item['track']['name']}</td>
                <td>{', '.join(a['name'] for a in item['track']['artists'])}</td>
                <td>{item['track']['album']['name']}</td>
                <td>{item['track']['duration_ms'] // 60000}:{(item['track']['duration_ms'] % 60000) // 1000:02d}</td>
            </tr>''' for i, item in enumerate(playlist['tracks'], 1))}
        </table>
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Report generated: {output_file}")
    client.close()

# Generate report
generate_playlist_report("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
```

## Tips & Best Practices

1. **Always close clients** when done or use context managers
2. **Handle errors gracefully** - Network issues are common
3. **Respect rate limits** - Add delays for bulk operations
4. **Cache results** when possible to avoid redundant requests
5. **Use appropriate browser** - `requests` for most cases, `selenium` for dynamic content
6. **Process in batches** for large datasets
7. **Validate URLs** before processing
8. **Log operations** for debugging and monitoring

## See Also

- [API Reference](API-Reference.md) - Complete API documentation
- [Quick Start](Quick-Start.md) - Getting started guide
- [FAQ](FAQ.md) - Common questions and issues