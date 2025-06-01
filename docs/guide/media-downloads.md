# Media Downloads Guide

This guide covers how to download audio previews, cover art, and other media files using SpotifyScraper.

## Table of Contents
- [Overview](#overview)
- [Audio Downloads](#audio-downloads)
- [Image Downloads](#image-downloads)
- [Bulk Downloads](#bulk-downloads)
- [Download Configuration](#download-configuration)
- [File Management](#file-management)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

---

## Overview

SpotifyScraper can download various types of media from Spotify:

### Available Media Types

- **Audio Previews**: 30-second MP3 previews of tracks
- **Cover Art**: Album and playlist cover images
- **Artist Images**: Artist profile pictures and banners
- **Metadata**: Embedded ID3 tags in downloaded files

### Download Features

- **High Quality**: Download the highest available quality
- **Automatic Naming**: Smart file naming with artist and track info
- **Metadata Embedding**: Automatic ID3 tag embedding in MP3 files
- **Batch Processing**: Download multiple files efficiently
- **Progress Tracking**: Real-time download progress

---

## Audio Downloads

### Basic Audio Preview Download

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Download track preview
track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
preview_path = client.download_preview_mp3(track_url)
print(f"Preview downloaded to: {preview_path}")

client.close()
```

### Download to Specific Location

```python
# Download to specific directory
preview_path = client.download_preview_mp3(
    track_url,
    path="./downloads/previews/"
)

# Download with custom filename
preview_path = client.download_preview_mp3(
    track_url,
    path="./downloads/",
    filename="my_preview.mp3"
)
```

### Download with Metadata

```python
# Download with embedded metadata
preview_path = client.download_preview_mp3(
    track_url,
    path="./downloads/",
    embed_metadata=True,        # Embed ID3 tags
    add_cover_art=True         # Embed album cover
)
```

### Advanced Audio Download Options

```python
# Advanced download with all options
preview_path = client.download_preview_mp3(
    track_url,
    path="./music/previews/",
    filename=None,              # Auto-generate filename
    quality="high",             # Download quality
    embed_metadata=True,        # Add ID3 tags
    add_cover_art=True,         # Embed cover art
    overwrite=False,           # Don't overwrite existing files
    create_dirs=True,          # Create directories if they don't exist
    progress_callback=None      # Progress callback function
)
```

### Custom Progress Tracking

```python
def download_progress(current, total, filename):
    """Custom progress callback."""
    percent = (current / total) * 100
    print(f"Downloading {filename}: {percent:.1f}%")

# Use progress callback
preview_path = client.download_preview_mp3(
    track_url,
    path="./downloads/",
    progress_callback=download_progress
)
```

---

## Image Downloads

### Album Cover Downloads

```python
# Download album cover
cover_path = client.download_cover(track_url)
print(f"Cover downloaded to: {cover_path}")

# Download cover with specific size
cover_path = client.download_cover(
    track_url,
    path="./covers/",
    size="large",              # "small", "medium", "large", or specific px
    format="jpg"               # "jpg", "png", "webp"
)
```

### Artist Image Downloads

```python
# Download artist profile image
artist_url = "https://open.spotify.com/artist/4tZwfgrHOc3mvqYlEYSvVi"
artist_image = client.download_artist_image(
    artist_url,
    path="./artist_images/",
    size="large"
)
```

### Playlist Cover Downloads

```python
# Download playlist cover
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd"
playlist_cover = client.download_playlist_cover(
    playlist_url,
    path="./playlist_covers/"
)
```

### High-Resolution Downloads

```python
# Download highest resolution available
cover_path = client.download_cover(
    track_url,
    path="./hq_covers/",
    size="max",                # Download maximum resolution
    format="png"               # PNG for best quality
)

# Download specific resolution
cover_path = client.download_cover(
    track_url,
    size="640x640",           # Specific pixel dimensions
    format="jpg"
)
```

---

## Bulk Downloads

### Download Multiple Previews

```python
# List of track URLs
track_urls = [
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
    "https://open.spotify.com/track/0VjIjW4GlULA4LGvdpEiDz"
]

# Download all previews
downloaded_files = client.bulk_download_previews(
    track_urls,
    path="./bulk_downloads/",
    max_concurrent=5,          # Parallel downloads
    progress_callback=None     # Overall progress callback
)

print(f"Downloaded {len(downloaded_files)} files")
```

### Download Album Content

```python
# Download all content from an album
album_url = "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy"

# Get album info first
album = client.get_album_info(album_url)

# Create album directory
album_dir = f"./downloads/{album.get('name', 'Unknown')}"

# Download album cover
cover_path = client.download_cover(
    album_url,
    path=album_dir,
    filename="cover.jpg"
)

# Download all track previews
for track in album['tracks']:
    preview_path = client.download_preview_mp3(
        track['external_urls']['spotify'],
        path=f"{album_dir}/previews/",
        embed_metadata=True
    )
```

### Playlist Bulk Download

```python
def download_playlist_content(playlist_url, base_path="./downloads/"):
    """Download all content from a playlist."""
    
    # Get playlist info
    playlist = client.get_playlist_info(playlist_url)
    playlist_name = playlist.get('name', 'Unknown')
    playlist_dir = f"{base_path}/{playlist_name}"
    
    # Download playlist cover
    cover_path = client.download_playlist_cover(
        playlist_url,
        path=playlist_dir,
        filename="playlist_cover.jpg"
    )
    
    # Download track previews
    downloaded_previews = []
    for item in playlist['tracks']['items']:
        if item['track'] and item['track']['preview_url']:
            try:
                preview_path = client.download_preview_mp3(
                    item['track']['external_urls']['spotify'],
                    path=f"{playlist_dir}/tracks/",
                    embed_metadata=True,
                    add_cover_art=True
                )
                downloaded_previews.append(preview_path)
            except Exception as e:
                print(f"Failed to download {item['track']['name']}: {e}")
    
    return {
        'playlist_cover': cover_path,
        'track_previews': downloaded_previews,
        'total_tracks': len(playlist['tracks']['items'])
    }

# Use the function
result = download_playlist_content("https://open.spotify.com/playlist/...")
print(f"Downloaded {len(result['track_previews'])} out of {result['total_tracks']} tracks")
```

---

## Download Configuration

### Default Download Settings

```python
# Configure default download behavior
client = SpotifyClient(
    download_path="./music_downloads/",     # Default download directory
    create_directories=True,                # Auto-create directories
    overwrite_existing=False,              # Don't overwrite existing files
    embed_metadata=True,                   # Always embed metadata
    default_audio_quality="high",          # Default audio quality
    default_image_format="jpg",            # Default image format
    max_concurrent_downloads=10            # Parallel download limit
)
```

### Quality Settings

```python
# Audio quality options
audio_qualities = {
    "low": "96kbps",       # Smaller file size
    "medium": "160kbps",   # Balanced
    "high": "320kbps"      # Best quality (if available)
}

# Image size options
image_sizes = {
    "small": "64x64",      # Thumbnail
    "medium": "300x300",   # Standard
    "large": "640x640",    # High quality
    "max": "original"      # Highest available
}
```

### Custom Naming Patterns

```python
# Custom filename patterns
def custom_filename_pattern(track_info):
    """Create custom filename from track info."""
    artist = track_info['artists'][0]['name']
    title = track.get('name', 'Unknown')
    album = track_info['album']['name']
    
    # Clean filename (remove invalid characters)
    filename = f"{artist} - {title} ({album})"
    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '(', ')'))
    
    return f"{filename}.mp3"

# Use custom naming
preview_path = client.download_preview_mp3(
    track_url,
    path="./downloads/",
    filename_generator=custom_filename_pattern
)
```

---

## File Management

### Organizing Downloads

```python
import os
from pathlib import Path

def organize_downloads_by_artist(download_dir):
    """Organize downloaded files by artist."""
    
    download_path = Path(download_dir)
    
    for file_path in download_path.glob("*.mp3"):
        # Extract artist from filename (assuming "Artist - Title.mp3" format)
        filename = file_path.stem
        if " - " in filename:
            artist = filename.split(" - ")[0]
            
            # Create artist directory
            artist_dir = download_path / artist
            artist_dir.mkdir(exist_ok=True)
            
            # Move file to artist directory
            new_path = artist_dir / file_path.name
            file_path.rename(new_path)
            print(f"Moved {file_path.name} to {artist_dir}")

# Organize existing downloads
organize_downloads_by_artist("./downloads/")
```

### Duplicate Detection

```python
import hashlib

def find_duplicate_files(directory):
    """Find duplicate files in download directory."""
    
    file_hashes = {}
    duplicates = []
    
    for file_path in Path(directory).rglob("*"):
        if file_path.is_file():
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            if file_hash in file_hashes:
                duplicates.append((file_path, file_hashes[file_hash]))
            else:
                file_hashes[file_hash] = file_path
    
    return duplicates

# Find and handle duplicates
duplicates = find_duplicate_files("./downloads/")
for duplicate, original in duplicates:
    print(f"Duplicate: {duplicate} (original: {original})")
    # Optionally remove duplicates
    # duplicate.unlink()
```

### Metadata Management

```python
import eyed3

def update_mp3_metadata(file_path, track_info):
    """Update MP3 metadata with track information."""
    
    audiofile = eyed3.load(file_path)
    if audiofile.tag is None:
        audiofile.initTag()
    
    # Set basic metadata
    audiofile.tag.title = track.get('name', 'Unknown')
    audiofile.tag.artist = track_info['artists'][0]['name']
    audiofile.tag.album = track_info['album']['name']
    audiofile.tag.album_artist = track_info['album']['artists'][0]['name']
    
    # Set additional metadata
    if 'track_number' in track_info:
        audiofile.tag.track_num = track_info['track_number']
    
    if 'release_date' in track_info['album']:
        year = track_info['album'].get('release_date', '')[:4] if track_info['album'].get('release_date') else 'Unknown'
        audiofile.tag.recording_date = year
    
    # Save changes
    audiofile.tag.save()

# Update metadata for all downloaded files
for mp3_file in Path("./downloads/").glob("*.mp3"):
    # Get track info and update metadata
    # track = client.get_track_info(...)
    # update_mp3_metadata(mp3_file, track_info)
    pass
```

---

## Advanced Features

### Resume Interrupted Downloads

```python
class ResumableDownloader:
    def __init__(self, client):
        self.client = client
        self.download_log = "download_log.json"
    
    def download_with_resume(self, urls, download_dir):
        """Download files with resume capability."""
        
        completed = self.load_completed_downloads()
        
        for url in urls:
            if url in completed:
                print(f"Skipping {url} (already downloaded)")
                continue
            
            try:
                file_path = self.client.download_preview_mp3(
                    url,
                    path=download_dir
                )
                
                # Log successful download
                self.log_completed_download(url, file_path)
                print(f"Downloaded: {file_path}")
                
            except Exception as e:
                print(f"Failed to download {url}: {e}")
    
    def load_completed_downloads(self):
        """Load list of completed downloads."""
        try:
            with open(self.download_log, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def log_completed_download(self, url, file_path):
        """Log completed download."""
        completed = self.load_completed_downloads()
        completed[url] = str(file_path)
        
        with open(self.download_log, 'w') as f:
            json.dump(completed, f, indent=2)

# Use resumable downloader
downloader = ResumableDownloader(client)
downloader.download_with_resume(track_urls, "./downloads/")
```

### Download Queue Management

```python
import queue
import threading
import time

class DownloadQueue:
    def __init__(self, client, max_workers=5):
        self.client = client
        self.queue = queue.Queue()
        self.max_workers = max_workers
        self.workers = []
        self.results = []
    
    def add_download(self, url, path, **kwargs):
        """Add download to queue."""
        self.queue.put((url, path, kwargs))
    
    def start_downloads(self):
        """Start download workers."""
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker)
            worker.start()
            self.workers.append(worker)
    
    def _worker(self):
        """Download worker thread."""
        while True:
            try:
                url, path, kwargs = self.queue.get(timeout=1)
                
                file_path = self.client.download_preview_mp3(
                    url, path=path, **kwargs
                )
                
                self.results.append({
                    'url': url,
                    'file_path': file_path,
                    'status': 'success'
                })
                
                self.queue.task_done()
                
            except queue.Empty:
                break
            except Exception as e:
                self.results.append({
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
                self.queue.task_done()
    
    def wait_completion(self):
        """Wait for all downloads to complete."""
        self.queue.join()
        for worker in self.workers:
            worker.join()

# Use download queue
download_queue = DownloadQueue(client, max_workers=3)

# Add downloads to queue
for url in track_urls:
    download_queue.add_download(url, "./downloads/", embed_metadata=True)

# Start and wait for completion
download_queue.start_downloads()
download_queue.wait_completion()

# Check results
successful = [r for r in download_queue.results if r['status'] == 'success']
failed = [r for r in download_queue.results if r['status'] == 'error']

print(f"Downloaded: {len(successful)}, Failed: {len(failed)}")
```

### Download with Validation

```python
import os
from mutagen.mp3 import MP3

def validate_downloaded_file(file_path):
    """Validate downloaded MP3 file."""
    
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size < 1000:  # Less than 1KB
        return False, "File too small"
    
    # Check if it's a valid MP3
    try:
        audio = MP3(file_path)
        if audio.info.length < 10:  # Less than 10 seconds
            return False, "Audio too short"
        
        return True, "Valid MP3 file"
        
    except Exception as e:
        return False, f"Invalid MP3: {e}"

def download_with_validation(client, url, path):
    """Download file and validate it."""
    
    file_path = client.download_preview_mp3(url, path=path)
    
    is_valid, message = validate_downloaded_file(file_path)
    
    if not is_valid:
        print(f"❌ Invalid download: {message}")
        os.remove(file_path)  # Remove invalid file
        return None
    else:
        print(f"✅ Valid download: {file_path}")
        return file_path

# Use validation
valid_file = download_with_validation(client, track_url, "./downloads/")
```

---

## Troubleshooting

### Common Download Issues

#### 1. No Preview Available

```python
def safe_download_preview(client, url, path):
    """Safely download preview with fallback."""
    
    try:
        # Check if preview is available
        track = client.get_track_info(url)
        
        if not track.get('preview_url'):
            print(f"No preview available for: {track.get('name', 'Unknown')}")
            return None
        
        return client.download_preview_mp3(url, path=path)
        
    except Exception as e:
        print(f"Download failed: {e}")
        return None

# Use safe download
file_path = safe_download_preview(client, track_url, "./downloads/")
```

#### 2. Network Issues

```python
import time
import random

def download_with_retry(client, url, path, max_retries=3):
    """Download with retry on network errors."""
    
    for attempt in range(max_retries):
        try:
            return client.download_preview_mp3(url, path=path)
            
        except Exception as e:
            if attempt < max_retries - 1:
                delay = random.uniform(1, 3) * (attempt + 1)
                print(f"Download failed, retrying in {delay:.1f}s: {e}")
                time.sleep(delay)
            else:
                print(f"Download failed after {max_retries} attempts: {e}")
                raise

# Use retry logic
file_path = download_with_retry(client, track_url, "./downloads/")
```

#### 3. Permission Issues

```python
import os
import stat

def ensure_write_permissions(directory):
    """Ensure directory has write permissions."""
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Check and fix permissions
    dir_stat = os.stat(directory)
    if not dir_stat.st_mode & stat.S_IWRITE:
        os.chmod(directory, dir_stat.st_mode | stat.S_IWRITE)

# Ensure permissions before downloading
ensure_write_permissions("./downloads/")
file_path = client.download_preview_mp3(url, path="./downloads/")
```

#### 4. Disk Space Issues

```python
import shutil

def check_disk_space(path, required_mb=100):
    """Check if enough disk space is available."""
    
    free_bytes = shutil.disk_usage(path).free
    free_mb = free_bytes / (1024 * 1024)
    
    if free_mb < required_mb:
        raise Exception(f"Insufficient disk space: {free_mb:.1f}MB available, {required_mb}MB required")
    
    return True

# Check space before downloading
check_disk_space("./downloads/", required_mb=50)
file_path = client.download_preview_mp3(url, path="./downloads/")
```

### Download Performance Issues

```python
# Optimize download performance
client = SpotifyClient(
    download_timeout=300,           # 5 minute timeout
    max_concurrent_downloads=3,     # Limit concurrent downloads
    download_chunk_size=8192,       # Download chunk size
    verify_ssl=True,               # Keep SSL verification
    connection_pool_size=10        # Connection pool size
)
```

---

## Next Steps

Now that you can download media:

1. 🎵 Explore [advanced usage patterns](../guide/basic-usage.md)
2. 🔧 Configure [download settings](../getting-started/configuration.md)
3. 🛠️ Handle [download errors](../guide/error-handling.md)
4. 📊 Build [bulk processing scripts](../examples/bulk_operations.md)

---

## Getting Help

If you need help with downloads:

1. Check the [FAQ](../faq.md) for common download issues
2. Review [troubleshooting guide](../troubleshooting.md)
3. Ask on [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
4. Report download bugs on [Issue Tracker](https://github.com/AliAkhtari78/SpotifyScraper/issues)