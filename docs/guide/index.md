# User Guide

Welcome to the SpotifyScraper user guide. This section provides detailed tutorials and guides for using the library effectively.

## Getting Started

- [**Basic Usage**](basic-usage.md) - Core functionality and common tasks
- [**Installation**](../getting-started/installation.md) - Detailed installation guide

## Step-by-Step Tutorials

### 🎵 Music Discovery Bot

Build a bot that discovers new music based on your preferences.

```python
from spotify_scraper import SpotifyClient
import random

client = SpotifyClient()

def discover_similar_tracks(track_url, num_recommendations=5):
    """Find similar tracks based on a seed track"""
    # Get the original track
    track = client.get_track(track_url)
    
    # Get the artist
    artist_id = track['artists'][0]['id']
    artist = client.get_artist(artist_id)
    
    # Get tracks from the same album
    album = client.get_album(track['album']['id'])
    
    # Get random tracks from the album
    similar_tracks = random.sample(album['tracks'], 
                                 min(num_recommendations, len(album['tracks'])))
    
    return similar_tracks

# Example usage
seed_track = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
recommendations = discover_similar_tracks(seed_track)

print("🎵 Recommended tracks:")
for track in recommendations:
    print(f"  - {track.get('name', 'Unknown')}")
```

### 📊 Playlist Analyzer
Analyze playlist characteristics and generate insights.```python
def analyze_playlist(playlist_url):
    """Analyze a playlist and generate insights"""
    playlist = client.get_playlist(playlist_url)
    
    # Basic stats
    total_tracks = len(playlist['tracks'])
    total_duration_ms = sum(track.get('duration_ms', 0) for track in playlist['tracks'])
    total_duration_min = total_duration_ms / 60000
    
    # Artist frequency
    artist_count = {}
    for track in playlist['tracks']:
        for artist in track['artists']:
            artist_count[artist.get('name', 'Unknown')] = artist_count.get(artist.get('name', 'Unknown'), 0) + 1
    
    # Most common artists
    top_artists = sorted(artist_count.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"📊 Playlist Analysis: {playlist.get('name', 'Unknown')}")
    print(f"   Total Tracks: {total_tracks}")
    print(f"   Total Duration: {total_duration_min:.1f} minutes")
    print(f"   Top Artists:")
    for artist, count in top_artists:
        print(f"     - {artist}: {count} tracks")
    
    return {
        'total_tracks': total_tracks,
        'duration_minutes': total_duration_min,
        'top_artists': top_artists
    }
```

### 🎼 Batch Album Downloader

Download album artwork and track previews in bulk.

```python
def download_album_media(album_url, output_dir="downloads/"):
    """Download all media from an album"""
    import os
    from spotify_scraper.media import ImageDownloader, AudioDownloader
    
    album = client.get_album(album_url)
    album_dir = os.path.join(output_dir, album.get('name', 'Unknown').replace('/', '-'))
    os.makedirs(album_dir, exist_ok=True)
    
    img_downloader = ImageDownloader()
    audio_downloader = AudioDownloader()
    
    # Download album cover
    if album.get('images'):
        img_downloader.download_image(
            album['images'][0]['url'],
            os.path.join(album_dir, "cover.jpg")
        )