# Media Module

The `media` module provides utilities for handling Spotify media files like audio and images.

## Overview

```python
from spotify_scraper.media import AudioDownloader, ImageDownloader
```

## AudioDownloader

Handles downloading and processing of audio preview files.

### Constructor

```python
AudioDownloader(browser: BaseBrowser)
```

**Parameters:**
- `browser` (BaseBrowser): Browser instance for making requests

### Methods

#### download_preview

```python
download_preview(
    track_data: Dict[str, Any],
    path: str = ".",
    filename: Optional[str] = None,
    with_cover: bool = True
) -> Optional[str]
```

Download audio preview from track data.

**Parameters:**
- `track_data` (Dict[str, Any]): Track data from SpotifyClient
- `path` (str): Directory to save the file
- `filename` (Optional[str]): Custom filename (defaults to track name)
- `with_cover` (bool): Whether to embed cover art in MP3

**Returns:**
- Optional[str]: Path to downloaded file or None if no preview

**Example:**
```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import create_browser
from spotify_scraper.media import AudioDownloader

client = SpotifyClient()
track = client.get_track_info("4iV5W9uYEdYUVa79Axb7Rh")

if track.get('preview_url'):
    browser = create_browser("requests")
    downloader = AudioDownloader(browser)
    file_path = downloader.download_preview(
        track,
        path="downloads/",
        with_cover=True
    )
    print(f"Downloaded to: {file_path}")
```

## ImageDownloader

Handles downloading of album artwork and artist images.

### Constructor

```python
ImageDownloader(browser: BaseBrowser)
```

**Parameters:**
- `browser` (BaseBrowser): Browser instance for making requests

### Methods

#### download_image

```python
download_image(
    resource_data: Dict[str, Any],
    path: str = ".",
    size: str = "large",
    filename: Optional[str] = None
) -> Optional[str]
```

Download image from resource data.

**Parameters:**
- `resource_data` (Dict[str, Any]): Track/album/artist data with images
- `path` (str): Directory to save the file
- `size` (str): Image size - "small", "medium", or "large"
- `filename` (Optional[str]): Custom filename

**Returns:**
- Optional[str]: Path to downloaded file or None if no images

**Example:**
```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import create_browser
from spotify_scraper.media import ImageDownloader

client = SpotifyClient()
album = client.get_album_info("4aawyAB9vmqN3uQ7FjRGTy")

if album.get('images'):
    browser = create_browser("requests")
    downloader = ImageDownloader(browser)
    file_path = downloader.download_image(
        album,
        path="covers/",
        size="large"
    )
    print(f"Downloaded to: {file_path}")
```

## Simplified Usage

For convenience, use the SpotifyClient methods directly:

```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Download track preview
preview_path = client.download_preview_mp3(
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
    output_dir="downloads/"
)

# Download cover art
cover_path = client.download_cover(
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
    output_dir="covers/",
    size="large"
)
```

## See Also

- [Client Module](client.md) - Main client with download methods
- [Examples](../examples/index.md) - Practical download examples