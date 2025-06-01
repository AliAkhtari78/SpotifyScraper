# Frequently Asked Questions

Common questions and solutions for SpotifyScraper users.

## Table of Contents

- [General Questions](#general-questions)
- [Installation Issues](#installation-issues)
- [Usage Questions](#usage-questions)
- [Error Solutions](#error-solutions)
- [Performance & Optimization](#performance--optimization)
- [Legal & Ethical](#legal--ethical)

## General Questions

### What is SpotifyScraper?

SpotifyScraper is a Python library that extracts data from Spotify's web player without requiring API authentication. It parses the web interface to provide structured metadata about tracks, albums, artists, and playlists.

### How is this different from the official Spotify API?

| Feature | SpotifyScraper | Official API |
|---------|---------------|--------------|
| Authentication | Not required | Required |
| Rate Limits | No official limits | Strict limits |
| Data Access | Public data only | User-specific data |
| Setup Time | Immediate | Registration needed |
| Maintenance | May need updates | Stable interface |

### What data can I extract?

- **Tracks**: Name, artists, album, duration, popularity, preview URL
- **Albums**: All tracks, release date, cover art, artist info
- **Artists**: Biography, genres, follower count, top tracks
- **Playlists**: All tracks, owner info, description
- **Media**: Cover images, 30-second preview clips
- **Lyrics**: Available with authentication cookies

### Do I need a Spotify account?

No account is needed for basic functionality. However, some features (like lyrics) require authentication via cookies.

## Installation Issues

### Installation fails with pip

**Problem**: `pip install spotifyscraper` fails

**Solutions**:
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try with --user flag
pip install --user spotifyscraper

# For specific Python version
python3.9 -m pip install spotifyscraper

# If behind proxy
pip install --proxy http://proxy.server:port spotifyscraper
```

### Selenium browser issues

**Problem**: "No module named 'selenium'" or browser errors

**Solution**:
```bash
# Install with Selenium support
pip install spotifyscraper[selenium]

# Install browser driver
# For Chrome
pip install webdriver-manager

# For Firefox
# Download geckodriver manually
```

### Import errors

**Problem**: `ImportError: cannot import name 'SpotifyClient'`

**Solution**:
```python
# Correct import
from spotify_scraper import SpotifyClient

# NOT these:
# from spotifyscraper import SpotifyClient  # Wrong package name
# import spotify_scraper.SpotifyClient      # Wrong syntax
```

## Usage Questions

### How do I get lyrics?

Lyrics require authentication cookies:

```python
# 1. Export cookies from your browser (Netscape format)
# 2. Use the cookie file
client = SpotifyClient(cookie_file="cookies.txt")
track = client.get_track_info_with_lyrics(track_url)
print(track['lyrics'])
```

### How do I download all tracks from a playlist?

```python
from spotify_scraper.utils.common import SpotifyBulkOperations

bulk = SpotifyBulkOperations()

# Get playlist
playlist = client.get_playlist_info(playlist_url)

# Extract track URLs
track_urls = []
for item in playlist['tracks']:
    if item['track'] and item['track'].get('id'):
        track_urls.append(f"https://open.spotify.com/track/{item['track']['id']}")

# Download all previews and covers
results = bulk.batch_download(track_urls, output_dir="playlist_media/")
print(f"Downloaded {results['successful']} items")
```

### Can I get user playlists or private data?

No. SpotifyScraper only accesses publicly available data. It cannot:
- Access private playlists
- Get user listening history
- Retrieve personal recommendations
- Access saved/liked songs

### How do I handle large playlists?

For playlists with many tracks, process in batches:

```python
def process_large_playlist(playlist_url, batch_size=50):
    playlist = client.get_playlist_info(playlist_url)
    tracks = playlist['tracks']
    
    for i in range(0, len(tracks), batch_size):
        batch = tracks[i:i + batch_size]
        # Process batch
        for item in batch:
            # Your processing logic
            pass
        
        # Add delay to avoid rate limiting
        time.sleep(1)
```

## Error Solutions

### URLError: Invalid Spotify URL

**Problem**: URL validation fails

**Solution**:
```python
from spotify_scraper.utils.url import is_spotify_url, get_url_type

# Check URL validity
if is_spotify_url(url):
    url_type = get_url_type(url)
    print(f"Valid {url_type} URL")
else:
    print("Invalid Spotify URL")

# Supported URL formats:
# https://open.spotify.com/track/ID
# https://open.spotify.com/album/ID
# https://open.spotify.com/artist/ID
# https://open.spotify.com/playlist/ID
# spotify:track:ID (URI format)
```

### NetworkError: Connection failed

**Problem**: Network requests fail

**Solutions**:
```python
# 1. Increase timeout
config = Config(timeout=30, max_retries=5)
client = SpotifyClient(config=config)

# 2. Use proxy
config = Config(proxy="http://proxy:8080")

# 3. Add retry logic
for attempt in range(3):
    try:
        data = client.get_track_info(url)
        break
    except NetworkError:
        if attempt < 2:
            time.sleep(2 ** attempt)
        else:
            raise
```

### ParsingError: Failed to extract data

**Problem**: Parser cannot find expected data

**Possible causes**:
1. Spotify changed their HTML structure
2. Page requires JavaScript rendering
3. Geographic restrictions

**Solutions**:
```python
# Use Selenium for JavaScript content
config = Config(browser_type="selenium")
client = SpotifyClient(config=config)

# Check library version
import spotify_scraper
print(spotify_scraper.__version__)
# Update if outdated: pip install -U spotifyscraper
```

### Download fails silently

**Problem**: `download_preview_mp3()` returns None

**Common reasons**:
1. Track has no preview available
2. Geographic restrictions
3. Network issues

**Solution**:
```python
# Check if preview exists
track = client.get_track_info(track_url)
if track.get('preview_url'):
    path = client.download_preview_mp3(track_url)
    if path:
        print(f"Downloaded to: {path}")
    else:
        print("Download failed")
else:
    print("No preview available for this track")
```

## Performance & Optimization

### How can I speed up bulk operations?

1. **Reuse client instances**:
```python
# Good - reuse client
client = SpotifyClient()
for url in urls:
    data = client.get_track_info(url)

# Bad - creates new client each time
for url in urls:
    client = SpotifyClient()
    data = client.get_track_info(url)
    client.close()
```

2. **Use parallel processing**:
```python
from concurrent.futures import ThreadPoolExecutor

def process_url(url):
    return client.get_track_info(url)

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(process_url, urls))
```

3. **Cache results**:
```python
import pickle

# Save results
with open('cache.pkl', 'wb') as f:
    pickle.dump(results, f)

# Load from cache
with open('cache.pkl', 'rb') as f:
    results = pickle.load(f)
```

### Memory usage with large datasets

For large operations, process data in streams:

```python
def process_playlist_stream(playlist_url):
    playlist = client.get_playlist_info(playlist_url)
    
    # Process tracks one by one instead of loading all
    for track in playlist['tracks']:
        # Process track
        yield {
            'name': track.get('name', 'Unknown'),
            'artists': [a['name'] for a in track['artists']]
        }
        
# Use generator
for track_data in process_playlist_stream(url):
    print(track_data)  # Processes one at a time
```

### Best browser choice?

- **Use `requests` (default)** for:
  - Most operations
  - Better performance
  - Lower resource usage
  
- **Use `selenium`** for:
  - JavaScript-heavy pages
  - When requests fails
  - Debugging (non-headless mode)

```python
# Performance comparison
import time

# Requests (faster)
start = time.time()
client = SpotifyClient()
data = client.get_track_info(url)
print(f"Requests: {time.time() - start:.2f}s")

# Selenium (slower but more reliable)
start = time.time()
config = Config(browser_type="selenium", headless=True)
client = SpotifyClient(config=config)
data = client.get_track_info(url)
print(f"Selenium: {time.time() - start:.2f}s")
```

## Legal & Ethical

### Is this legal?

SpotifyScraper accesses only publicly available data. However:
- Always respect Spotify's Terms of Service
- Don't use for commercial purposes without permission
- Respect rate limits and server resources
- Give attribution when using Spotify data

### Can I use this for commercial projects?

You should:
1. Review Spotify's Terms of Service
2. Consider using the official API for commercial use
3. Respect intellectual property rights
4. Not redistribute copyrighted content

### How do I use this responsibly?

Best practices:
```python
# 1. Add delays between requests
import time

for url in urls:
    data = client.get_track_info(url)
    time.sleep(1)  # Be respectful

# 2. Handle errors gracefully
try:
    data = client.get_track_info(url)
except Exception as e:
    logging.error(f"Failed: {e}")
    # Don't retry immediately

# 3. Cache results to avoid repeated requests
# 4. Use official API when possible
# 5. Don't overload servers
```

### What about copyright?

- Metadata (titles, artists, etc.) is generally factual information
- Preview clips are provided by Spotify for sampling
- Lyrics may be copyrighted - use responsibly
- Don't redistribute full songs or copyrighted content

## Troubleshooting Checklist

When encountering issues:

1. ✅ Check your internet connection
2. ✅ Verify the URL is valid and accessible
3. ✅ Update to the latest version: `pip install -U spotifyscraper`
4. ✅ Try with Selenium if requests fails
5. ✅ Check if the content is geo-restricted
6. ✅ Look for similar issues on GitHub
7. ✅ Enable debug logging for more details

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Now run your code - you'll see detailed logs
client = SpotifyClient()
```

## Still Need Help?

- 📖 Check the [full documentation](https://spotifyscraper.readthedocs.io)
- 🐛 Report issues on [GitHub](https://github.com/AliAkhtari78/SpotifyScraper/issues)
- 💬 Search existing issues for solutions
- 📧 Contact: aliakhtari78@hotmail.com

Remember to include:
- Python version
- SpotifyScraper version
- Full error traceback
- Minimal code to reproduce the issue