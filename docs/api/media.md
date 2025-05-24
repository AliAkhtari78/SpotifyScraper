# Media Module

The `media` module provides utilities for handling Spotify media files like audio and images.

## Overview

```python
from spotify_scraper.media import AudioDownloader, ImageDownloader
```

## AudioDownloader

Handles downloading and processing of audio preview files.

### Methods

#### download_preview

```python
download_preview(preview_url: str, output_path: str) -> bool
```

Download audio preview from Spotify.

**Parameters:**
- `preview_url` (str): URL of the preview file
- `output_path` (str): Where to save the file

**Returns:**
- bool: True if successful, False otherwise

**Example:**
```python
from spotify_scraper.media import AudioDownloader

downloader = AudioDownloader()
track = client.get_track("4iV5W9uYEdYUVa79Axb7Rh")

if track.get('preview_url'):
    success = downloader.download_preview(
        track['preview_url'],
        "preview.mp3"
    )
```

## ImageDownloader

Handles downloading of album artwork and artist images.

### Methods#### download_image

```python
download_image(image_url: str, output_path: str, size: str = "large") -> bool
```

Download image from Spotify CDN.

**Parameters:**
- `image_url` (str): URL of the image
- `output_path` (str): Where to save the file
- `size` (str): Image size - "small", "medium", or "large"

**Returns:**
- bool: True if successful

**Example:**
```python
from spotify_scraper.media import ImageDownloader

downloader = ImageDownloader()
album = client.get_album("4aawyAB9vmqN3uQ7FjRGTy")

# Download largest image
if album.get('images'):
    image_url = album['images'][0]['url']
    downloader.download_image(
        image_url,
        "album_cover.jpg",
        size="large"
    )
```

#### batch_download

```python
batch_download(images: List[Dict], output_dir: str) -> List[str]
```

Download multiple images.

**Example:**
```python
# Download all album covers from a playlist
playlist = client.get_playlist("37i9dQZF1DXcBWIGoYBM5M")
downloaded = downloader.batch_download(
    [track['album']['images'] for track in playlist['tracks']],
    "album_covers/"
)
```