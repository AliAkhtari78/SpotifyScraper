# Media Handlers API Reference

SpotifyScraper provides specialized classes for downloading and processing media files from Spotify, including audio previews and cover images.

## AudioDownloader

Download and process audio preview files from Spotify tracks.

### Class: AudioDownloader

```python
from spotify_scraper.media import AudioDownloader
from spotify_scraper.browsers import RequestsBrowser

browser = RequestsBrowser()
audio_downloader = AudioDownloader(browser)
```

#### Constructor

##### `__init__(browser: Browser)`

Initialize an AudioDownloader instance.

**Parameters:**
- `browser` (Browser): Browser instance for web interactions

#### Methods

##### `download_preview(track_data: TrackData, filename: Optional[str] = None, path: str = "", with_cover: bool = True) -> str`

Download preview MP3 for a track.

**Parameters:**
- `track_data` (TrackData): Track data from TrackExtractor
- `filename` (Optional[str]): Custom filename (optional)
- `path` (str): Directory to save the audio (default: current directory)
- `with_cover` (bool): Whether to embed the cover image (default: True)

**Returns:**
- `str`: Path to the downloaded audio file

**Raises:**
- `DownloadError`: If download fails
- `MediaError`: If metadata processing fails

**Example:**
```python
from spotify_scraper import SpotifyClient
from spotify_scraper.media import AudioDownloader
from spotify_scraper.browsers import RequestsBrowser

# Get track data
browser = RequestsBrowser()
client = SpotifyClient(browser=browser)
track_data = client.get_track("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")

# Download preview
audio_downloader = AudioDownloader(browser)

# Download with default filename
file_path = audio_downloader.download_preview(track_data)
print(f"Downloaded to: {file_path}")

# Download with custom filename
custom_path = audio_downloader.download_preview(
    track_data,
    filename="my_favorite_song.mp3",
    path="downloads"
)

# Download without cover embedding
no_cover_path = audio_downloader.download_preview(
    track_data,
    with_cover=False
)
```

### Features

#### Automatic Filename Generation

If no filename is provided, AudioDownloader generates one automatically:

```python
# Filename format: "{track_name}_by_{artist_name}.mp3"
# Special characters are replaced with underscores

track_data = {
    "name": "Bohemian Rhapsody",
    "artists": [{"name": "Queen"}]
}

# Generated filename: "Bohemian_Rhapsody_by_Queen.mp3"
```

#### Metadata Embedding

When `with_cover=True`, the downloader embeds metadata using eyeD3:

- Track title
- Artist name
- Album name
- Cover image

```python
# Download with full metadata
file_path = audio_downloader.download_preview(
    track_data,
    with_cover=True  # Embeds cover and metadata
)

# The MP3 file will have:
# - ID3 tags with track information
# - Embedded album artwork
# - Proper metadata for music players
```

#### Error Handling

```python
from spotify_scraper.core.exceptions import DownloadError, MediaError

try:
    file_path = audio_downloader.download_preview(track_data)
except DownloadError as e:
    print(f"Download failed: {e}")
    print(f"URL: {e.url}")
    print(f"Target path: {e.path}")
except MediaError as e:
    print(f"Media processing error: {e}")
```

## ImageDownloader

Download cover images and other image assets from Spotify.

### Class: ImageDownloader

```python
from spotify_scraper.media import ImageDownloader
from spotify_scraper.browsers import RequestsBrowser

browser = RequestsBrowser()
image_downloader = ImageDownloader(browser)
```

#### Constructor

##### `__init__(browser: Browser)`

Initialize an ImageDownloader instance.

**Parameters:**
- `browser` (Browser): Browser instance for web interactions

#### Methods

##### `download_cover(entity_data: Union[TrackData, AlbumData, ArtistData, PlaylistData], filename: Optional[str] = None, path: str = "", size: str = "large") -> str`

Download cover image for a Spotify entity.

**Parameters:**
- `entity_data` (Union[TrackData, AlbumData, ArtistData, PlaylistData]): Entity data from an extractor
- `filename` (Optional[str]): Custom filename (optional)
- `path` (str): Directory to save the image (default: current directory)
- `size` (str): Image size - "small", "medium", or "large" (default: "large")

**Returns:**
- `str`: Path to the downloaded image

**Raises:**
- `DownloadError`: If download fails

**Example:**
```python
from spotify_scraper import SpotifyClient
from spotify_scraper.media import ImageDownloader
from spotify_scraper.browsers import RequestsBrowser

browser = RequestsBrowser()
client = SpotifyClient(browser=browser)

# Download track cover
track_data = client.get_track("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
image_downloader = ImageDownloader(browser)

# Download large cover
large_cover = image_downloader.download_cover(track_data, size="large")

# Download with custom filename
custom_cover = image_downloader.download_cover(
    track_data,
    filename="album_art.jpg",
    path="images"
)

# Download different sizes
small_cover = image_downloader.download_cover(track_data, size="small")
medium_cover = image_downloader.download_cover(track_data, size="medium")
```

### Image Sizes

The `size` parameter determines which image to download:

- **"small"**: Smallest available image (typically ~64x64)
- **"medium"**: Medium-sized image (typically ~300x300)
- **"large"**: Largest available image (typically ~640x640)

```python
# Example: Download all available sizes
sizes = ["small", "medium", "large"]
for size in sizes:
    file_path = image_downloader.download_cover(
        track_data,
        filename=f"cover_{size}.jpg",
        size=size
    )
    print(f"{size}: {file_path}")
```

### Entity Type Support

ImageDownloader works with all Spotify entity types:

```python
# Track cover (from album)
track_data = client.get_track(track_url)
track_cover = image_downloader.download_cover(track_data)

# Album cover
album_data = client.get_album(album_url)
album_cover = image_downloader.download_cover(album_data)

# Artist image
artist_data = client.get_artist(artist_url)
artist_image = image_downloader.download_cover(artist_data)

# Playlist cover
playlist_data = client.get_playlist(playlist_url)
playlist_cover = image_downloader.download_cover(playlist_data)
```

## Complete Media Download Example

Here's a comprehensive example showing both audio and image downloads:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.media import AudioDownloader, ImageDownloader
from spotify_scraper.core.exceptions import DownloadError
import os

def download_track_media(track_url, output_dir="spotify_downloads"):
    """Download both audio preview and cover art for a track."""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components
    browser = RequestsBrowser()
    client = SpotifyClient(browser=browser)
    audio_downloader = AudioDownloader(browser)
    image_downloader = ImageDownloader(browser)
    
    try:
        # Get track data
        print(f"Fetching track data from: {track_url}")
        track_data = client.get_track(track_url)
        
        # Extract names for file naming
        track_name = track_data['name']
        artist_name = track_data['artists'][0]['name']
        
        print(f"\nTrack: {track_name}")
        print(f"Artist: {artist_name}")
        
        # Download audio preview
        if track_data.get('preview_url'):
            print("\nDownloading audio preview...")
            audio_path = audio_downloader.download_preview(
                track_data,
                path=output_dir,
                with_cover=True
            )
            print(f"Audio saved to: {audio_path}")
        else:
            print("\nNo preview available for this track")
        
        # Download cover images
        print("\nDownloading cover images...")
        for size in ["small", "medium", "large"]:
            cover_path = image_downloader.download_cover(
                track_data,
                filename=f"{artist_name} - {track_name} ({size}).jpg",
                path=output_dir,
                size=size
            )
            print(f"Cover ({size}) saved to: {cover_path}")
        
        print("\n✅ Download complete!")
        
    except DownloadError as e:
        print(f"\n❌ Download error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        client.close()

# Usage
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
download_track_media(track_url)
```

## Batch Media Downloads

Example for downloading media for multiple tracks:

```python
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.media import AudioDownloader, ImageDownloader
import time

def batch_download_tracks(track_urls, output_dir="batch_downloads"):
    """Download media for multiple tracks."""
    
    browser = RequestsBrowser()
    client = SpotifyClient(browser=browser)
    audio_downloader = AudioDownloader(browser)
    image_downloader = ImageDownloader(browser)
    
    results = []
    
    for i, url in enumerate(track_urls, 1):
        print(f"\nProcessing track {i}/{len(track_urls)}")
        
        try:
            # Get track data
            track_data = client.get_track(url)
            track_name = track_data['name']
            
            result = {
                "url": url,
                "name": track_name,
                "audio": None,
                "cover": None,
                "error": None
            }
            
            # Download audio
            if track_data.get('preview_url'):
                audio_path = audio_downloader.download_preview(
                    track_data,
                    path=f"{output_dir}/audio"
                )
                result["audio"] = audio_path
            
            # Download cover
            cover_path = image_downloader.download_cover(
                track_data,
                path=f"{output_dir}/covers",
                size="large"
            )
            result["cover"] = cover_path
            
            results.append(result)
            
            # Be respectful to Spotify's servers
            time.sleep(1)
            
        except Exception as e:
            results.append({
                "url": url,
                "error": str(e)
            })
    
    client.close()
    return results

# Usage
urls = [
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
    "https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv",
    # Add more URLs
]

results = batch_download_tracks(urls)

# Print summary
successful = sum(1 for r in results if not r.get("error"))
print(f"\n✅ Successfully downloaded: {successful}/{len(results)}")
```

## Custom Media Processing

Example of custom post-processing for downloaded media:

```python
from spotify_scraper.media import AudioDownloader, ImageDownloader
from PIL import Image
import os

class CustomMediaProcessor:
    def __init__(self, browser):
        self.audio_downloader = AudioDownloader(browser)
        self.image_downloader = ImageDownloader(browser)
    
    def download_and_resize_cover(self, track_data, size=(300, 300)):
        """Download cover and resize it."""
        # Download original
        original_path = self.image_downloader.download_cover(
            track_data,
            filename="original.jpg"
        )
        
        # Resize
        img = Image.open(original_path)
        img_resized = img.resize(size, Image.Resampling.LANCZOS)
        
        # Save resized
        resized_path = original_path.replace("original", f"resized_{size[0]}x{size[1]}")
        img_resized.save(resized_path)
        
        # Clean up original if needed
        os.remove(original_path)
        
        return resized_path
    
    def download_preview_with_fade(self, track_data):
        """Download preview and apply fade in/out (requires pydub)."""
        # Download audio
        audio_path = self.audio_downloader.download_preview(
            track_data,
            with_cover=False
        )
        
        try:
            from pydub import AudioSegment
            
            # Load audio
            audio = AudioSegment.from_mp3(audio_path)
            
            # Apply fade in/out
            audio_faded = audio.fade_in(1000).fade_out(1000)
            
            # Save
            faded_path = audio_path.replace(".mp3", "_faded.mp3")
            audio_faded.export(faded_path, format="mp3")
            
            # Clean up original
            os.remove(audio_path)
            
            return faded_path
        except ImportError:
            print("pydub not installed, returning original file")
            return audio_path
```

## Best Practices

1. **Always handle missing preview URLs**: Not all tracks have preview URLs
2. **Use appropriate image sizes**: Download only the sizes you need
3. **Implement rate limiting**: Add delays between downloads
4. **Handle errors gracefully**: Use try-except blocks for robust error handling
5. **Clean up resources**: Close browser instances when done
6. **Respect copyright**: Downloaded content is for personal use only