# Advanced Usage Guide

This guide covers advanced features and patterns for power users of SpotifyScraper.

## Authentication and Limitations

### Lyrics API Requirements

**Important**: Spotify's lyrics API requires OAuth Bearer token authentication. Cookie-based authentication alone is **not sufficient** for accessing lyrics.

```python
from spotify_scraper import SpotifyClient

# Cookie authentication attempt - WILL NOT WORK for lyrics
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# This will return None - lyrics require OAuth token
track_data = client.get_track_info_with_lyrics("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
if track_data.get('lyrics'):
    print("Lyrics available!")  # This won't execute
else:
    print("Lyrics not available - OAuth authentication required")
```

### Why Cookie Authentication Isn't Enough

Spotify's lyrics are provided through a specialized API endpoint (`spclient.wg.spotify.com/color-lyrics/v2/track/`) that requires:

1. **OAuth Bearer Token**: Not just cookies
2. **Proper Authorization Header**: `Authorization: Bearer <token>`
3. **Valid Spotify Web API Access**: Through official OAuth flow

### Alternative: Using Spotify Web API

For lyrics access, consider using the official Spotify Web API with proper OAuth:

```python
# Example using spotipy library (not part of SpotifyScraper)
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Set up OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="http://localhost:8888/callback",
    scope="user-read-currently-playing"
))

# Get track details (note: Spotify API doesn't provide lyrics directly)
track = sp.current_user_playing_track()
```

### What Cookie Authentication CAN Do

Cookie authentication with SpotifyScraper is still useful for:

```python
from spotify_scraper import SpotifyClient

# Cookie file authentication
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Access private playlists
private_playlist = client.get_playlist_info("https://open.spotify.com/playlist/your_private_playlist_id")

# Get enhanced metadata
track = client.get_track_info("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")

# Higher rate limits for bulk operations
album = client.get_album_info("https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv")
```

## Using Selenium Browser

For complex scenarios requiring JavaScript execution:

```python
from spotify_scraper import SpotifyClient

# Use Selenium browser type
client = SpotifyClient(browser_type="selenium")

try:
    # Extract data as usual
    track_data = client.get_track_info(url)
    album_data = client.get_album_info(album_url)
finally:
    # Always close when using Selenium
    client.close()
```

## Advanced Data Extraction

### Extracting Lyrics with Timing

```python
from spotify_scraper import SpotifyClient

class LyricsExtractor:
    def __init__(self, cookie_file):
        self.client = SpotifyClient(cookie_file=cookie_file)
    
    def get_lyrics_formatted(self, track_url):
        """Extract and format lyrics."""
        track_data = self.client.get_track_info_with_lyrics(track_url)
        
        if not track_data.get('lyrics'):
            return None
        
        # Lyrics are returned as plain text
        lyrics_text = track_data['lyrics']
        
        return {
            'track': track_data.get('name', 'Unknown'),
            'artist': track_data['artists'][0]['name'],
            'lyrics': lyrics_text
        }
    
    def export_to_txt(self, track_url, output_file):
        """Export lyrics to text file."""
        lyrics_data = self.get_lyrics_formatted(track_url)
        if not lyrics_data:
            return False
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write metadata
            f.write(f"{lyrics_data['track']}\n")
            f.write(f"by {lyrics_data['artist']}\n\n")
            
            # Write lyrics
            f.write(lyrics_data['lyrics'])
        
        return True

# Usage
extractor = LyricsExtractor(cookie_file="spotify_cookies.txt")
extractor.export_to_txt(
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
    "bohemian_rhapsody.txt"
)
```

### Artist Deep Analysis

```python
from spotify_scraper import SpotifyClient

class ArtistAnalyzer:
    def __init__(self):
        self.client = SpotifyClient()
    
    def analyze_artist(self, artist_url):
        """Perform deep analysis of an artist."""
        artist_data = self.client.get_artist_info(artist_url)
        
        analysis = {
            'basic_info': {
                'name': artist_data.get('name', 'Unknown'),
                'id': artist_data['id'],
                'verified': artist_data.get('is_verified', False)
            },
            'popularity': self._analyze_popularity(artist_data),
            'discography': self._analyze_discography(artist_data),
            'top_tracks': self._get_top_tracks(artist_data)
        }
        
        return analysis
    
    def _analyze_popularity(self, artist_data):
        """Analyze artist popularity metrics."""
        stats = artist_data.get('stats', {})
        return {
            'monthly_listeners': stats.get('monthly_listeners', 0),
            'follower_count': stats.get('followers', 0),
            'world_rank': stats.get('world_rank', None)
        }
    
    def _analyze_discography(self, artist_data):
        """Analyze artist's discography statistics."""
        discography = artist_data.get('discography_stats', {})
        return {
            'total_albums': discography.get('albums', 0),
            'total_singles': discography.get('singles', 0),
            'total_compilations': discography.get('compilations', 0),
            'appears_on': discography.get('appears_on', 0)
        }
    
    def _get_top_tracks(self, artist_data):
        """Extract top tracks information."""
        top_tracks = []
        for track in artist_data.get('top_tracks', [])[:10]:
            top_tracks.append({
                'name': track.get('name', 'Unknown'),
                'play_count': track.get('play_count', 0),
                'album': track.get('album', {}).get('name', 'Unknown')
            })
        return top_tracks

# Usage
analyzer = ArtistAnalyzer()
analysis = analyzer.analyze_artist("https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb")
print(f"Artist: {analysis['basic_info']['name']}")
print(f"Monthly Listeners: {analysis['popularity']['monthly_listeners']:,}")
```

## Parallel Processing

### Concurrent Extraction

```python
import concurrent.futures
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser
import time

class ParallelExtractor:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
    
    def extract_tracks(self, urls):
        """Extract multiple tracks in parallel."""
        results = []
        
        def extract_single(url):
            client = SpotifyClient()
            try:
                data = client.get_track_info(url)
                time.sleep(0.5)  # Rate limiting
                return {'url': url, 'success': True, 'data': data}
            except Exception as e:
                return {'url': url, 'success': False, 'error': str(e)}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(extract_single, url): url for url in urls}
            
            for future in concurrent.futures.as_completed(future_to_url):
                result = future.result()
                results.append(result)
                
                if result['success']:
                    print(f"✅ Extracted: {result['data']['name']}")
                else:
                    print(f"❌ Failed: {result['error']}")
        
        return results

# Usage
extractor = ParallelExtractor(max_workers=3)
urls = [
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
    "https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv",
    # Add more URLs
]
results = extractor.extract_tracks(urls)
```

### Async Downloads

```python
import asyncio
import aiohttp
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser

class AsyncDownloader:
    def __init__(self):
        self.browser = RequestsBrowser()
        self.client = SpotifyClient(browser=self.browser)
    
    async def download_file(self, session, url, filename):
        """Async download a file."""
        async with session.get(url) as response:
            content = await response.read()
            with open(filename, 'wb') as f:
                f.write(content)
            return filename
    
    async def batch_download_previews(self, track_urls):
        """Download multiple track previews asynchronously."""
        # First, get all track data
        tracks_data = []
        for url in track_urls:
            try:
                data = self.client.get_track_info(url)
                if data.get('preview_url'):
                    tracks_data.append(data)
            except Exception as e:
                print(f"Failed to get track data: {e}")
        
        # Download previews asynchronously
        async with aiohttp.ClientSession() as session:
            tasks = []
            for track in tracks_data:
                filename = f"{track.get('name', 'Unknown')}.mp3".replace('/', '_')
                task = self.download_file(
                    session,
                    track.get('preview_url', 'Not available'),
                    filename
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results

# Usage
downloader = AsyncDownloader()
urls = [
    "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
    "https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv",
]

# Run async downloads
loop = asyncio.get_event_loop()
results = loop.run_until_complete(downloader.batch_download_previews(urls))
```

## Custom Extractors

### Create Your Own Extractor

```python
from typing import Dict, Any
from spotify_scraper.browsers import Browser
from spotify_scraper.parsers import JSONParser
from spotify_scraper import ExtractionError
from spotify_scraper.utils import is_spotify_url, extract_id

class PodcastExtractor:
    """Custom extractor for Spotify podcasts."""
    
    def __init__(self, browser: Browser):
        self.browser = browser
        self.parser = JSONParser()
    
    def extract(self, url: str) -> Dict[str, Any]:
        """Extract podcast episode information."""
        # Validate URL
        if not self._is_podcast_url(url):
            raise ExtractionError("Not a valid podcast URL")
        
        # Get episode ID
        episode_id = extract_id(url)
        
        # Fetch page
        html = self.browser.get(url)
        
        # Parse data
        raw_data = self.parser.parse(html)
        
        # Extract podcast data
        return self._process_podcast_data(raw_data, episode_id)
    
    def _is_podcast_url(self, url: str) -> bool:
        """Check if URL is a podcast episode."""
        return "episode" in url or "show" in url
    
    def _process_podcast_data(self, data: Dict[str, Any], episode_id: str) -> Dict[str, Any]:
        """Process raw data into structured podcast data."""
        # Custom processing logic here
        episode_data = data.get('episode', {})
        
        return {
            'id': episode_id,
            'name': episode_data.get('name'),
            'description': episode_data.get('description'),
            'duration_ms': episode_data.get('duration_ms'),
            'release_date': episode_data.get('release_date'),
            'show': {
                'name': episode_data.get('show', {}).get('name'),
                'publisher': episode_data.get('show', {}).get('publisher')
            }
        }

# Usage
browser = RequestsBrowser()
podcast_extractor = PodcastExtractor(browser)
episode_data = podcast_extractor.extract("https://open.spotify.com/episode/...")
```

## Data Export and Integration

### Export to Multiple Formats

```python
import json
import csv
import pandas as pd
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser

class DataExporter:
    def __init__(self):
        self.browser = RequestsBrowser()
        self.client = SpotifyClient(browser=self.browser)
    
    def export_playlist(self, playlist_url, format='json'):
        """Export playlist data in various formats."""
        playlist_data = self.client.get_playlist_info(playlist_url)
        
        if format == 'json':
            return self._export_json(playlist_data)
        elif format == 'csv':
            return self._export_csv(playlist_data)
        elif format == 'excel':
            return self._export_excel(playlist_data)
        elif format == 'markdown':
            return self._export_markdown(playlist_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self, data):
        """Export to JSON file."""
        filename = f"{data.get('name', 'Unknown')}.json".replace('/', '_')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filename
    
    def _export_csv(self, data):
        """Export tracks to CSV file."""
        filename = f"{data.get('name', 'Unknown')}.csv".replace('/', '_')
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'position', 'name', 'artist', 'album', 'duration_ms'
            ])
            writer.writeheader()
            
            for i, track in enumerate(data['tracks'], 1):
                writer.writerow({
                    'position': i,
                    'name': track.get('name', 'Unknown'),
                    'artist': (track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown'),
                    'album': track.get('album', {}).get('name', 'Unknown'),
                    'duration_ms': track.get('duration_ms', 0)
                })
        
        return filename
    
    def _export_excel(self, data):
        """Export to Excel file with formatting."""
        filename = f"{data.get('name', 'Unknown')}.xlsx".replace('/', '_')
        
        # Prepare data for DataFrame
        tracks_data = []
        for i, track in enumerate(data['tracks'], 1):
            tracks_data.append({
                'Position': i,
                'Track': track.get('name', 'Unknown'),
                'Artist': (track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown'),
                'Album': track.get('album', {}).get('name', 'Unknown'),
                'Duration': f"{track.get('duration_ms', 0) // 60000}:{(track.get('duration_ms', 0) % 60000) // 1000:02d}",
                'Explicit': '✓' if track.get('is_explicit') else ''
            })
        
        # Create DataFrame and save to Excel
        df = pd.DataFrame(tracks_data)
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Tracks', index=False)
            
            # Add metadata sheet
            metadata = pd.DataFrame({
                'Property': ['Playlist Name', 'Owner', 'Total Tracks', 'Description'],
                'Value': [
                    data.get('name', 'Unknown'),
                    data['owner']['name'],
                    data['track_count'],
                    data.get('description', 'N/A')
                ]
            })
            metadata.to_excel(writer, sheet_name='Metadata', index=False)
        
        return filename
    
    def _export_markdown(self, data):
        """Export to Markdown file."""
        filename = f"{data.get('name', 'Unknown')}.md".replace('/', '_')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# {data.get('name', 'Unknown')}\n\n")
            f.write(f"**Owner:** {data['owner']['name']}  \n")
            f.write(f"**Tracks:** {data['track_count']}  \n\n")
            
            if data.get('description'):
                f.write(f"## Description\n{data['description']}\n\n")
            
            f.write("## Track List\n\n")
            f.write("| # | Track | Artist | Album | Duration |\n")
            f.write("|---|-------|--------|-------|----------|\n")
            
            for i, track in enumerate(data['tracks'], 1):
                duration = f"{track.get('duration_ms', 0) // 60000}:{(track.get('duration_ms', 0) % 60000) // 1000:02d}"
                f.write(f"| {i} | {track.get('name', 'Unknown')} | {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')} | {track.get('album', {}).get('name', 'Unknown')} | {duration} |\n")
        
        return filename

# Usage
exporter = DataExporter()

# Export playlist in different formats
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
json_file = exporter.export_playlist(playlist_url, format='json')
csv_file = exporter.export_playlist(playlist_url, format='csv')
excel_file = exporter.export_playlist(playlist_url, format='excel')
markdown_file = exporter.export_playlist(playlist_url, format='markdown')
```

## Performance Optimization

### Caching Strategy

```python
import time
import pickle
from functools import lru_cache
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser

class CachedSpotifyClient:
    def __init__(self, cache_file='spotify_cache.pkl'):
        self.browser = RequestsBrowser()
        self.client = SpotifyClient(browser=self.browser)
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load cache from disk."""
        try:
            with open(self.cache_file, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_cache(self):
        """Save cache to disk."""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache, f)
    
    @lru_cache(maxsize=128)
    def get_track(self, url, max_age=3600):
        """Get track data with caching."""
        # Check cache
        if url in self.cache:
            cached_data, timestamp = self.cache[url]
            if time.time() - timestamp < max_age:
                print(f"Cache hit for: {url}")
                return cached_data
        
        # Fetch fresh data
        print(f"Cache miss, fetching: {url}")
        track_data = self.client.get_track_info(url)
        
        # Update cache
        self.cache[url] = (track_data, time.time())
        self._save_cache()
        
        return track_data
    
    def clear_cache(self):
        """Clear all cached data."""
        self.cache = {}
        self._save_cache()
        self.get_track.cache_clear()

# Usage
cached_client = CachedSpotifyClient()

# First call - fetches from Spotify
track1 = cached_client.get_track("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")

# Second call - returns from cache
track2 = cached_client.get_track("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
```

### Connection Pooling

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from spotify_scraper.browsers import RequestsBrowser

class OptimizedBrowser(RequestsBrowser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure connection pooling
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

# Usage
optimized_browser = OptimizedBrowser()
client = SpotifyClient(browser=optimized_browser)
```

## Error Recovery and Resilience

### Robust Extraction with Retry

```python
import time
from typing import List, Dict, Any
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper import NetworkError, ExtractionError

class ResilientExtractor:
    def __init__(self, max_retries=3, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.browser = RequestsBrowser()
        self.client = SpotifyClient(browser=self.browser)
    
    def extract_with_retry(self, url: str) -> Dict[str, Any]:
        """Extract data with automatic retry on failure."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return self.client.get_track_info(url)
            except NetworkError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    print(f"Network error, retrying in {wait_time}s...")
                    time.sleep(wait_time)
            except ExtractionError as e:
                # Don't retry extraction errors
                raise
        
        raise last_error
    
    def batch_extract_resilient(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Extract multiple URLs with individual error handling."""
        results = []
        
        for url in urls:
            try:
                data = self.extract_with_retry(url)
                results.append({
                    'url': url,
                    'success': True,
                    'data': data
                })
            except Exception as e:
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'error_type': type(e).__name__
                })
        
        return results

# Usage
extractor = ResilientExtractor(max_retries=3)
urls = [
    "https://open.spotify.com/track/valid_track",
    "https://open.spotify.com/track/invalid_track",
    # More URLs
]

results = extractor.batch_extract_resilient(urls)

# Analyze results
successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"Successful: {len(successful)}/{len(results)}")
for failure in failed:
    print(f"Failed: {failure['url']} - {failure['error_type']}: {failure['error']}")
```

## Integration Examples

### Discord Bot Integration

```python
import discord
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.utils.url import is_spotify_url, get_url_type

class SpotifyBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.browser = RequestsBrowser()
        self.spotify_client = SpotifyClient(browser=self.browser)
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        # Check for Spotify URLs in message
        words = message.content.split()
        for word in words:
            if is_spotify_url(word):
                await self.handle_spotify_url(message, word)
    
    async def handle_spotify_url(self, message, url):
        """Process Spotify URL and send embed."""
        url_type = get_url_type(url)
        
        if url_type == "track":
            await self.send_track_embed(message.channel, url)
        elif url_type == "album":
            await self.send_album_embed(message.channel, url)
        # Add more types as needed
    
    async def send_track_embed(self, channel, url):
        """Send track information as Discord embed."""
        try:
            track_data = self.spotify_client.get_track_info(url)
            
            embed = discord.Embed(
                title=track_data.get('name', 'Unknown'),
                url=url,
                description=f"by {track_data['artists'][0]['name']}",
                color=0x1DB954  # Spotify green
            )
            
            # Add fields
            embed.add_field(
                name="Album",
                value=track_data['album']['name'],
                inline=True
            )
            embed.add_field(
                name="Duration",
                value=f"{track_data['duration_ms'] // 60000}:{(track_data['duration_ms'] % 60000) // 1000:02d}",
                inline=True
            )
            
            # Set thumbnail
            if track_data['album'].get('images'):
                embed.set_thumbnail(url=track_data['album']['images'][0]['url'])
            
            await channel.send(embed=embed)
            
        except Exception as e:
            await channel.send(f"Error processing Spotify URL: {e}")

# Run bot
bot = SpotifyBot()
bot.run('YOUR_BOT_TOKEN')
```

### Flask Web API

```python
from flask import Flask, jsonify, request
from spotify_scraper import SpotifyClient
from spotify_scraper.browsers import RequestsBrowser
from spotify_scraper.utils.url import is_spotify_url, get_url_type

app = Flask(__name__)

# Global client instance
browser = RequestsBrowser()
spotify_client = SpotifyClient(browser=browser)

@app.route('/api/track/<track_id>')
def get_track(track_id):
    """Get track information by ID."""
    try:
        url = f"https://open.spotify.com/track/{track_id}"
        track_data = spotify_client.get_track_info(url)
        
        # Simplify response
        return jsonify({
            'id': track_data['id'],
            'name': track_data.get('name', 'Unknown'),
            'artist': track_data['artists'][0]['name'],
            'album': track_data['album']['name'],
            'duration_ms': track_data['duration_ms'],
            'preview_url': track_data.get('preview_url')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/analyze', methods=['POST'])
def analyze_url():
    """Analyze any Spotify URL."""
    data = request.get_json()
    url = data.get('url')
    
    if not url or not is_spotify_url(url):
        return jsonify({'error': 'Invalid Spotify URL'}), 400
    
    url_type = get_url_type(url)
    
    try:
        if url_type == 'track':
            result = spotify_client.get_track_info(url)
        elif url_type == 'album':
            result = spotify_client.get_album_info(url)
        elif url_type == 'artist':
            result = spotify_client.get_artist_info(url)
        elif url_type == 'playlist':
            result = spotify_client.get_playlist_info(url)
        else:
            return jsonify({'error': f'Unsupported URL type: {url_type}'}), 400
        
        return jsonify({
            'type': url_type,
            'data': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## Best Practices

1. **Resource Management**: Always close browsers and clients when done
2. **Rate Limiting**: Implement delays between requests (0.5-1 second recommended)
3. **Error Handling**: Use specific exception types for precise error handling
4. **Caching**: Cache frequently accessed data to reduce API calls
5. **Logging**: Implement proper logging for debugging and monitoring
6. **Authentication**: Use cookies only when necessary (e.g., for lyrics)
7. **Parallel Processing**: Use with caution and reasonable limits
8. **Data Validation**: Always validate data before using it

## Next Steps

- Explore the [CLI documentation](cli.md) for command-line usage
- Check the [API reference](../api/) for detailed documentation
- See the [examples folder](https://github.com/AliAkhtari78/SpotifyScraper/tree/master/examples) for more code samples