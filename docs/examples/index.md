# Examples & Tutorials

Learn SpotifyScraper through practical, real-world examples.

## 📚 Example Categories

### 🚀 Getting Started
- [**Quick Start Guide**](quickstart.md) - Your first SpotifyScraper script
- [**Basic Examples**](#basic-examples) - Common use cases
- [**CLI Usage**](cli.md) - Command-line interface

### 🔧 Intermediate
- [**Advanced Patterns**](advanced.md) - Complex scenarios
- [**Error Handling**](#error-handling-examples) - Robust scripts
- [**Batch Processing**](#batch-processing) - Handle multiple items

### 💡 Real-World Projects
- [**Music Analytics**](#music-analytics) - Analyze music data
- [**Playlist Manager**](#playlist-manager) - Manage playlists
- [**Music Discovery**](#music-discovery) - Find new music
- [**Data Collection**](#data-collection) - Build datasets

---

## Basic Examples

### Extract Track Information
```python
from spotify_scraper import SpotifyClient

# Initialize client
client = SpotifyClient()

# Get track data
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track = client.get_track_info(track_url)

# Display information
print(f"Track: {track.get('name', 'Unknown')}")
print(f"Artist: {', '.join(a['name'] for a in track['artists'])}")
print(f"Duration: {track.get('duration_ms', 0) / 1000:.1f} seconds")
print(f"Explicit: {'Yes' if track.get('is_explicit') else 'No'}")
```

### Download Track Preview
```python
# Download preview MP3
preview_path = client.download_preview_mp3(
    track_url,
    path="previews/",
    with_cover=True  # Embed album art
)
print(f"Preview saved to: {preview_path}")
```

### Extract Album with Tracks
```python
# Get album information
album_url = "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"
album = client.get_album_info(album_url)

print(f"\nAlbum: {album.get('name', 'Unknown')}")
print(f"Artist: {(album.get('artists', [{}])[0].get('name', 'Unknown') if album.get('artists') else 'Unknown')}")
print(f"Released: {album.get('release_date', 'N/A')}")
print(f"\nTracks ({album.get('total_tracks', 0)}):")

for track in album['tracks']:
    duration = track.get('duration_ms', 0) / 1000
    print(f"{track['track_number']:2d}. {track.get('name', 'Unknown')} ({duration:.1f}s)")
```

### Extract Playlist
```python
# Get playlist data
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
playlist = client.get_playlist_info(playlist_url)

print(f"Playlist: {playlist.get('name', 'Unknown')}")
print(f"By: {playlist.get('owner', {}).get('display_name', playlist.get('owner', {}).get('id', 'Unknown'))}")
print(f"Tracks: {playlist.get('track_count', 0)}")

# Calculate total duration
total_ms = sum(t['duration_ms'] for t in playlist['tracks'])
hours = total_ms // 3600000
minutes = (total_ms % 3600000) // 60000
print(f"Duration: {hours}h {minutes}m")
```

---

## Error Handling Examples

### Robust Extraction with Retry
```python
import time
from spotify_scraper import SpotifyClient, NetworkError, ExtractionError

def extract_with_retry(url, max_retries=3, delay=1.0):
    """Extract data with automatic retry on failure."""
    client = SpotifyClient()
    
    for attempt in range(max_retries):
        try:
            return client.get_track_info(url)
        except NetworkError as e:
            if attempt < max_retries - 1:
                print(f"Network error, retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise
        except ExtractionError as e:
            print(f"Extraction failed: {e}")
            return None
```

### Safe Batch Processing
```python
def process_urls_safely(urls):
    """Process multiple URLs with error handling."""
    client = SpotifyClient()
    results = []
    
    for i, url in enumerate(urls):
        try:
            print(f"Processing {i+1}/{len(urls)}: {url}")
            data = client.get_track_info(url)
            results.append({
                'url': url,
                'success': True,
                'data': data
            })
        except Exception as e:
            print(f"Failed: {e}")
            results.append({
                'url': url,
                'success': False,
                'error': str(e)
            })
        
        # Rate limiting
        if i < len(urls) - 1:
            time.sleep(0.5)
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"\nProcessed: {successful}/{len(results)} successful")
    
    return results
```

---

## Batch Processing

### Download Multiple Previews
```python
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from spotify_scraper import SpotifyClient

def download_preview(url, output_dir="downloads"):
    """Download a single preview."""
    client = SpotifyClient()
    try:
        filename = client.download_preview_mp3(url, path=output_dir)
        return {'url': url, 'filename': filename, 'success': True}
    except Exception as e:
        return {'url': url, 'error': str(e), 'success': False}

def batch_download_previews(urls, output_dir="downloads", max_workers=3):
    """Download multiple previews concurrently."""
    os.makedirs(output_dir, exist_ok=True)
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_url = {
            executor.submit(download_preview, url, output_dir): url 
            for url in urls
        }
        
        # Process completed tasks
        for future in as_completed(future_to_url):
            result = future.result()
            results.append(result)
            
            if result['success']:
                print(f"✓ Downloaded: {result['filename']}")
            else:
                print(f"✗ Failed: {result['error']}")
    
    return results

# Example usage
track_urls = [
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
    "https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv",
    "https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI3"
]

results = batch_download_previews(track_urls)
```

---

## Music Analytics

### Track Popularity Analysis
```python
import statistics
from datetime import datetime

def analyze_artist_popularity(artist_url):
    """Analyze an artist's track popularity."""
    client = SpotifyClient()
    artist = client.get_artist_info(artist_url)
    
    print(f"\nAnalyzing: {artist.get('name', 'Unknown')}")
    print(f"Followers: {artist.get('followers', 0):,}")
    
    # Get top tracks
    top_tracks = artist.get('top_tracks', [])
    if not top_tracks:
        print("No top tracks available")
        return
    
    # Extract popularity scores
    popularities = [t.get('popularity', 0) for t in top_tracks]
    
    # Calculate statistics
    stats = {
        'average': statistics.mean(popularities),
        'median': statistics.median(popularities),
        'std_dev': statistics.stdev(popularities) if len(popularities) > 1 else 0,
        'min': min(popularities),
        'max': max(popularities)
    }
    
    print(f"\nTop Tracks Popularity Analysis:")
    print(f"Average: {stats['average']:.1f}")
    print(f"Median: {stats['median']:.1f}")
    print(f"Range: {stats['min']} - {stats['max']}")
    print(f"Std Dev: {stats['std_dev']:.1f}")
    
    # Show top 5 most popular
    print(f"\nTop 5 Most Popular Tracks:")
    sorted_tracks = sorted(top_tracks, key=lambda x: x.get('popularity', 0), reverse=True)
    for i, track in enumerate(sorted_tracks[:5]):
        print(f"{i+1}. {track.get('name', 'Unknown')} (Popularity: {track.get('popularity', 0)})")
    
    return stats
```

### Genre Analysis
```python
from collections import Counter

def analyze_playlist_genres(playlist_url):
    """Analyze genres in a playlist."""
    client = SpotifyClient()
    playlist = client.get_playlist_info(playlist_url)
    
    print(f"Analyzing: {playlist.get('name', 'Unknown')}")
    
    # Collect all artist IDs
    artist_ids = set()
    for track in playlist['tracks']:
        for artist in track.get('artists', []):
            if artist.get('id'):
                artist_ids.add(artist['id'])
    
    # Get genre information
    all_genres = []
    for artist_id in artist_ids:
        try:
            artist_url = f"https://open.spotify.com/artist/{artist_id}"
            artist = client.get_artist_info(artist_url)
            all_genres.extend(artist.get('genres', []))
            time.sleep(0.5)  # Rate limiting
        except:
            continue
    
    # Count genres
    genre_counts = Counter(all_genres)
    
    print(f"\nTop Genres:")
    for genre, count in genre_counts.most_common(10):
        print(f"- {genre}: {count} artists")
    
    return genre_counts
```

---

## Playlist Manager

### Playlist Duplicates Finder
```python
def find_duplicate_tracks(playlist_url):
    """Find duplicate tracks in a playlist."""
    client = SpotifyClient()
    playlist = client.get_playlist_info(playlist_url)
    
    print(f"Checking: {playlist.get('name', 'Unknown')}")
    
    # Track occurrences
    track_counts = {}
    duplicates = []
    
    for track in playlist['tracks']:
        track_id = track.get('id')
        if not track_id:
            continue
            
        if track_id in track_counts:
            track_counts[track_id]['count'] += 1
            duplicates.append(track)
        else:
            track_counts[track_id] = {
                'count': 1,
                'name': track.get('name', 'Unknown'),
                'artists': (track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')
            }
    
    # Report duplicates
    if duplicates:
        print(f"\nFound {len(duplicates)} duplicate entries:")
        for track in duplicates:
            print(f"- {track.get('name', 'Unknown')} by {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")
    else:
        print("\nNo duplicates found!")
    
    return duplicates
```

### Playlist Comparison
```python
def compare_playlists(playlist1_url, playlist2_url):
    """Compare two playlists."""
    client = SpotifyClient()
    
    # Get both playlists
    pl1 = client.get_playlist_info(playlist1_url)
    pl2 = client.get_playlist_info(playlist2_url)
    
    print(f"Comparing:")
    print(f"1. {pl1['name']} ({pl1['track_count']} tracks)")
    print(f"2. {pl2['name']} ({pl2['track_count']} tracks)")
    
    # Get track IDs
    tracks1 = {t['id'] for t in pl1['tracks'] if t.get('id')}
    tracks2 = {t['id'] for t in pl2['tracks'] if t.get('id')}
    
    # Calculate overlaps
    common = tracks1 & tracks2
    only_in_1 = tracks1 - tracks2
    only_in_2 = tracks2 - tracks1
    
    print(f"\nResults:")
    print(f"- Common tracks: {len(common)}")
    print(f"- Only in playlist 1: {len(only_in_1)}")
    print(f"- Only in playlist 2: {len(only_in_2)}")
    print(f"- Similarity: {len(common) / max(len(tracks1), len(tracks2)) * 100:.1f}%")
    
    return {
        'common': common,
        'only_in_1': only_in_1,
        'only_in_2': only_in_2
    }
```

---

## Music Discovery

### Find Similar Artists
```python
def discover_similar_artists(seed_artists, max_depth=2):
    """Discover artists through related artists."""
    client = SpotifyClient()
    discovered = set()
    to_explore = set(seed_artists)
    explored = set()
    
    for depth in range(max_depth):
        print(f"\nExploring depth {depth + 1}...")
        next_explore = set()
        
        for artist_url in to_explore:
            if artist_url in explored:
                continue
                
            try:
                artist = client.get_artist_info(artist_url)
                explored.add(artist_url)
                
                # Get related artists
                related = artist.get('related_artists', [])
                for rel in related:
                    rel_url = f"https://open.spotify.com/artist/{rel['id']}"
                    if rel_url not in discovered:
                        discovered.add(rel_url)
                        next_explore.add(rel_url)
                        print(f"  Found: {rel['name']}")
                
                time.sleep(0.5)  # Rate limiting
            except:
                continue
        
        to_explore = next_explore
    
    print(f"\nDiscovered {len(discovered)} artists!")
    return discovered
```

---

## Data Collection

### Build Track Dataset
```python
import csv
import json
from datetime import datetime

def build_track_dataset(track_urls, output_format='csv'):
    """Build a dataset from track URLs."""
    client = SpotifyClient()
    dataset = []
    
    print(f"Building dataset from {len(track_urls)} tracks...")
    
    for i, url in enumerate(track_urls):
        try:
            track = client.get_track_info(url)
            
            # Extract relevant fields
            data = {
                'id': track['id'],
                'name': track.get('name', 'Unknown'),
                'artist': (track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown'),
                'artist_id': track['artists'][0]['id'],
                'album': track.get('album', {}).get('name', ''),
                'duration_ms': track.get('duration_ms', 0),
                'popularity': track.get('popularity', 0),
                'explicit': track.get('is_explicit', False),
                'preview_url': track.get('preview_url', ''),
                'release_date': track.get('release_date', ''),
                'extracted_at': datetime.now().isoformat()
            }
            
            dataset.append(data)
            print(f"  [{i+1}/{len(track_urls)}] ✓ {data.get('name', 'Unknown')}")
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"  [{i+1}/{len(track_urls)}] ✗ Failed: {e}")
    
    # Save dataset
    if output_format == 'csv':
        filename = f"tracks_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=dataset[0].keys())
            writer.writeheader()
            writer.writerows(dataset)
    else:  # JSON
        filename = f"tracks_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)
    
    print(f"\nDataset saved to: {filename}")
    print(f"Total tracks: {len(dataset)}")
    
    return dataset
```

---

## Next Steps

Ready to build something amazing? Here are some ideas:

1. **Music Recommendation System** - Build recommendations based on audio features
2. **Playlist Generator** - Create playlists based on mood or tempo
3. **Music Trends Analyzer** - Track popularity changes over time
4. **Album Art Collage Maker** - Create visual collages from album covers
5. **Lyrics Analysis Tool** - Analyze sentiment and themes in lyrics

For more advanced examples and patterns, check out:
- [Advanced Usage Guide](advanced.md)
- [Performance Optimization](../advanced/performance.md)
- [API Reference](../api/index.md)

---

## Contributing Examples

Have a cool example to share? We'd love to include it!

1. Fork the repository
2. Add your example to this documentation
3. Submit a pull request

Help make SpotifyScraper better for everyone! 🎵