# Frequently Asked Questions (FAQ)

## General Questions

### What is SpotifyScraper?

SpotifyScraper is a Python library that extracts data from Spotify's web player without requiring API credentials. It can retrieve information about tracks, albums, artists, and playlists, as well as download preview MP3s and cover images.

### How is this different from the official Spotify API?

| Feature | SpotifyScraper | Official Spotify API |
|---------|----------------|---------------------|
| Registration Required | No | Yes |
| API Key Required | No | Yes |
| Rate Limits | No formal limits | 180 requests/min |
| Preview Downloads | Yes | No |
| Cover Downloads | Yes | Limited |
| Lyrics Access | Yes (with auth) | No |
| Setup Complexity | Simple | Complex |

### Is SpotifyScraper legal to use?

SpotifyScraper accesses publicly available web content. However, you should:
- Respect Spotify's Terms of Service
- Not use it for commercial purposes without permission
- Be respectful with request frequency
- Only use downloaded content for personal use

### What Python versions are supported?

SpotifyScraper supports Python 3.8 and above. We recommend using the latest stable Python version for best performance.

## Installation Issues

### ImportError: No module named 'spotify_scraper'

**Problem:** Python can't find the installed package.

**Solutions:**
1. Ensure you installed it: `pip install spotifyscraper`
2. Check you're in the right environment: `pip list | grep spotify`
3. Try reinstalling: `pip install --force-reinstall spotifyscraper`

### SSL Certificate errors during installation

**Problem:** SSL verification fails when downloading packages.

**Solutions:**
```bash
# Update certificates
pip install --upgrade certifi

# Or temporarily bypass (not recommended for production)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org spotifyscraper
```

### Permission denied errors

**Problem:** No permission to install packages globally.

**Solutions:**
```bash
# Install for current user only
pip install --user spotifyscraper

# Or use a virtual environment (recommended)
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
pip install spotifyscraper
```

## Usage Questions

### How do I get lyrics for tracks?

Lyrics require authentication via Spotify cookies:

```python
# 1. Export cookies from your browser using a "cookies.txt" extension
# 2. Use the cookie file with SpotifyClient
client = SpotifyClient(cookie_file="spotify_cookies.txt")
track = client.get_track_info_with_lyrics(track_url)
print(track['lyrics'])
```

### Why am I getting "No preview available"?

Not all tracks on Spotify have preview URLs. This is a Spotify limitation, not a SpotifyScraper issue. Previews are typically available for:
- Popular tracks
- Tracks available in your region
- Non-restricted content

### How do I handle rate limiting?

While SpotifyScraper doesn't enforce rate limits, Spotify might block excessive requests:

```python
import time

# Add delays between requests
for url in urls:
    data = client.get_track_info(url)
    time.sleep(1)  # Wait 1 second between requests
```

### Can I download full songs?

No. SpotifyScraper can only download 30-second preview clips that Spotify makes publicly available. Full song downloads would violate copyright laws and Spotify's terms of service.

### How do I get high-quality cover images?

```python
# Download largest available cover
client.download_cover(
    url,
    quality_preference=["large", "medium", "small"]
)

# The actual resolution depends on what Spotify provides
# Typically: large = 640x640, medium = 300x300, small = 64x64
```

## Authentication Questions

### How do I export Spotify cookies?

1. Install a browser extension like "cookies.txt" or "Get cookies.txt"
2. Log in to [Spotify Web Player](https://open.spotify.com)
3. Click the extension and export cookies
4. Save as `spotify_cookies.txt`
5. Use with SpotifyClient: `client = SpotifyClient(cookie_file="spotify_cookies.txt")`

### Which cookies are required?

The most important cookie is `sp_t` (authentication token). Other useful cookies:
- `sp_dc`: Device credentials
- `sp_key`: Session key

### My cookies aren't working

Common issues:
1. **Expired cookies**: Re-export from browser
2. **Wrong format**: Ensure Netscape format (not JSON)
3. **Incomplete export**: Make sure you're logged in when exporting
4. **Region restrictions**: Some content is region-locked

## Error Handling

### URLError: Invalid Spotify URL

**Problem:** The URL format is not recognized.

**Solution:** Ensure you're using valid Spotify URLs:
```python
# Valid formats:
"https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
"https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"
"spotify:track:6rqhFgbbKwnb9MLmUQDhG6"

# Invalid:
"open.spotify.com/track/..."  # Missing https://
"https://spotify.com/..."      # Wrong domain
```

### ScrapingError: Failed to extract data

**Possible causes:**
1. **Network issues**: Check your internet connection
2. **Spotify changes**: The website structure might have changed
3. **Rate limiting**: You're making too many requests
4. **Region blocking**: Content not available in your region

**Solutions:**
```python
# Use Selenium for dynamic content
client = SpotifyClient(browser_type="selenium")

# Add retry logic
import time
for attempt in range(3):
    try:
        data = client.get_track_info(url)
        break
    except ScrapingError:
        if attempt < 2:
            time.sleep(2)
        else:
            raise
```

### MediaError: Failed to download

**Common issues:**
1. **No preview URL**: Track doesn't have a preview
2. **Network timeout**: Slow connection
3. **Disk space**: Insufficient storage
4. **Permissions**: Can't write to directory

**Solutions:**
```python
# Check for preview before downloading
track = client.get_track_info(url)
if track.get('preview_url'):
    client.download_preview_mp3(url)
else:
    print("No preview available")

# Ensure directory exists and is writable
import os
os.makedirs("downloads", exist_ok=True)
```

## Performance Questions

### How can I make SpotifyScraper faster?

1. **Use requests backend** (default):
   ```python
   client = SpotifyClient(browser_type="requests")
   ```

2. **Reuse client instances**:
   ```python
   client = SpotifyClient()
   for url in urls:
       # Process multiple URLs with same client
   client.close()
   ```

3. **Parallel processing** (be careful with rate limits):
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   def fetch_track(url):
       return client.get_track_info(url)
   
   with ThreadPoolExecutor(max_workers=3) as executor:
       results = list(executor.map(fetch_track, urls))
   ```

### Why is Selenium slower than requests?

Selenium launches a full browser, which includes:
- Loading all page resources (CSS, JS, images)
- Executing JavaScript
- Rendering the page

Use Selenium only when necessary (for dynamic content).

## Advanced Questions

### Can I use SpotifyScraper in my web application?

Yes, but consider:
1. **Performance**: Web apps need fast response times
2. **Caching**: Cache results to reduce Spotify requests
3. **Rate limiting**: Implement your own rate limiting
4. **Error handling**: Gracefully handle failures

Example with Flask:
```python
from flask import Flask, jsonify
from spotify_scraper import SpotifyClient
import redis
import json

app = Flask(__name__)
cache = redis.Redis()
client = SpotifyClient()

@app.route('/track/<track_id>')
def get_track(track_id):
    # Check cache first
    cached = cache.get(f"track:{track_id}")
    if cached:
        return json.loads(cached)
    
    # Fetch from Spotify
    try:
        url = f"https://open.spotify.com/track/{track_id}"
        data = client.get_track_info(url)
        
        # Cache for 1 hour
        cache.setex(f"track:{track_id}", 3600, json.dumps(data))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

### Can I contribute to SpotifyScraper?

Yes! We welcome contributions:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/CONTRIBUTING.md) for details.

### How do I report bugs?

1. Check if it's already reported: [GitHub Issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
2. Create a new issue with:
   - Python version
   - SpotifyScraper version
   - Full error traceback
   - Minimal code to reproduce
   - Expected vs actual behavior

## Troubleshooting Checklist

When something doesn't work, check:

- [ ] Latest version installed: `pip install --upgrade spotifyscraper`
- [ ] Valid Spotify URL format
- [ ] Internet connection working
- [ ] Not being rate limited (add delays)
- [ ] Cookies valid and not expired (for features requiring auth)
- [ ] Content available in your region
- [ ] Sufficient disk space for downloads
- [ ] Write permissions for download directory
- [ ] No firewall/proxy blocking requests

## Getting Help

If you can't find an answer here:

1. **Documentation**: [Read the Docs](https://spotifyscraper.readthedocs.io/)
2. **Examples**: Check the [Examples page](Examples)
3. **Issues**: Search [GitHub Issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
4. **Discussions**: Join [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)

Remember to provide:
- Clear description of the problem
- Code that reproduces the issue
- Full error messages
- Your environment details