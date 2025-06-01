# Bulk Operations Examples

The `SpotifyBulkOperations` class provides powerful utilities for processing multiple Spotify URLs efficiently.

## Basic Usage

### Processing Multiple URLs

```python
from spotify_scraper.utils.common import SpotifyBulkOperations

# Process multiple URLs
urls = [
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
    "https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp",
    "https://open.spotify.com/artist/00FQb4jTyendYWaN8pK0wa"
]

bulk = SpotifyBulkOperations()
results = bulk.process_urls(urls, operation="all_info")

# Export results
bulk.export_to_json(results, "spotify_data.json")
bulk.export_to_csv(results, "spotify_data.csv")
```

## Operations

### Available Operations

- `"info"` - Get basic metadata for each URL
- `"download"` - Download media files (audio previews, covers)
- `"both"` - Get metadata and download media
- `"all_info"` - Get all available information including lyrics (requires auth for tracks)

### Examples

#### Get Information Only

```python
bulk = SpotifyBulkOperations()
results = bulk.process_urls(urls, operation="info")

# Access results
for url, result in results["results"].items():
    if "error" not in result:
        info = result["info"]
        print(f"{info.get('name', 'Unknown')} - Type: {result['type']}")
```

#### Download Media Files

```python
# Download audio previews and covers
results = bulk.process_urls(
    urls, 
    operation="download",
    output_dir="downloads/"
)

# Check download results
for url, result in results["results"].items():
    if "downloads" in result:
        print(f"Downloaded: {result['downloads']}")
```

#### Get All Information

```python
# Get comprehensive data including lyrics (requires authentication for tracks)
results = bulk.process_urls(urls, operation="all_info")

# Access track lyrics
track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
lyrics = results["results"][track_url]["info"].get("lyrics")
```

## Batch Downloads

### Download Media from Multiple URLs

```python
# Download only covers
download_results = bulk.batch_download(
    urls,
    output_dir="covers/",
    media_types=["cover"],
    skip_errors=True
)

print(f"Successfully downloaded: {download_results['successful']}")
print(f"Failed: {download_results['failed']}")
```

### Download All Media Types

```python
# Download both audio and covers
download_results = bulk.batch_download(
    urls,
    output_dir="media/",
    media_types=["audio", "cover"]
)
```

## Processing URL Files

### Read URLs from a File

```python
# Create a file with URLs (one per line)
# Comments starting with # are ignored
with open("urls.txt", "w") as f:
    f.write("""
# My favorite tracks
https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
https://open.spotify.com/track/1dfeR4HaWDbWqFHLkxsg1d

# Albums to download
spotify:album:0JGOiO34nwfUdDrD612dOp
""")

# Process all URLs from file
results = bulk.process_url_file(
    "urls.txt",
    operation="both",
    output_dir="output/"
)
```

## Extracting URLs from Text

### Parse URLs from Any Text

```python
text = """
Check out these amazing tracks:
- One More Time: https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
- Bohemian Rhapsody: spotify:track:1dfeR4HaWDbWqFHLkxsg1d
  
And this classic album: https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp
"""

# Extract all Spotify URLs and URIs
urls = bulk.extract_urls_from_text(text)
print(f"Found {len(urls)} URLs")

# Process extracted URLs
results = bulk.process_urls(urls)
```

## Export Options

### Export to JSON

```python
# Export with full structure
bulk.export_to_json(results, "output.json")

# Export only successful results
successful_results = {
    url: data 
    for url, data in results["results"].items() 
    if "error" not in data
}
bulk.export_to_json(successful_results, "successful.json")
```

### Export to CSV

```python
# Export to CSV with flattened structure
bulk.export_to_csv(results, "output.csv")

# The CSV will include columns based on the type of content:
# - Tracks: id, name, artists, album, duration_ms, popularity, preview_url
# - Albums: id, name, artists, release_date, total_tracks, album_type
# - Artists: id, name, genres, followers, popularity
# - Playlists: id, name, owner, total_tracks, public, collaborative
```

## Advanced Usage

### Custom Client Configuration

```python
from spotify_scraper import SpotifyClient

# Create client with custom configuration
client = SpotifyClient(
    browser_type="selenium",
    cookie_file="spotify_cookies.txt",
    log_level="DEBUG"
)

# Use custom client with bulk operations
bulk = SpotifyBulkOperations(client=client)
```

### Error Handling

```python
results = bulk.process_urls(urls, operation="all_info")

# Check for errors
if results["failed"] > 0:
    print(f"Failed to process {results['failed']} URLs:")
    for url, result in results["results"].items():
        if "error" in result:
            print(f"  - {url}: {result['error']}")
```

### Creating Datasets

```python
# Create a dataset from multiple sources
playlist_urls = [
    "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
    "https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd"
]

# Extract all tracks from playlists
all_tracks = []
for url in playlist_urls:
    playlist = client.get_playlist_info(url)
    tracks = playlist.get("tracks", {}).get("items", [])
    all_tracks.extend([item["track"] for item in tracks if item.get("track")])

# Create dataset
bulk.create_dataset(
    [f"https://open.spotify.com/track/{t['id']}" for t in all_tracks],
    "playlist_tracks_dataset.json",
    format="json"
)
```

## Performance Tips

1. **Batch Processing**: Process URLs in batches to avoid rate limiting
2. **Skip Errors**: Use `skip_errors=True` to continue processing even if some URLs fail
3. **Selective Downloads**: Only download the media types you need
4. **Use URL Files**: For large lists, store URLs in a file and use `process_url_file()`

## Example: Complete Workflow

```python
from spotify_scraper.utils.common import SpotifyBulkOperations
from pathlib import Path

# Initialize bulk operations
bulk = SpotifyBulkOperations()

# Define URLs to process
urls = [
    "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
    "https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp",
    "https://open.spotify.com/artist/00FQb4jTyendYWaN8pK0wa",
    "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
]

# Create output directory
output_dir = Path("spotify_analysis")
output_dir.mkdir(exist_ok=True)

# Process all URLs
print("Processing URLs...")
results = bulk.process_urls(urls, operation="all_info")

# Export data
print("Exporting data...")
bulk.export_to_json(results, output_dir / "all_data.json")
bulk.export_to_csv(results, output_dir / "summary.csv")

# Download media
print("Downloading media...")
download_results = bulk.batch_download(
    urls,
    output_dir / "media",
    media_types=["cover"],
    skip_errors=True
)

# Print summary
print(f"\nProcessing complete:")
print(f"- Processed: {results['processed']} URLs")
print(f"- Failed: {results['failed']} URLs")
print(f"- Downloaded: {download_results['successful']} items")

# Cleanup
bulk.client.close()
```