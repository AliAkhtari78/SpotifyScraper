# Frequently Asked Questions (FAQ)

Find answers to common questions about SpotifyScraper.

## Table of Contents
- [General Questions](#general-questions)
- [Installation Issues](#installation-issues)
- [Usage Questions](#usage-questions)
- [Authentication & Cookies](#authentication--cookies)
- [Data Extraction](#data-extraction)
- [Media Downloads](#media-downloads)
- [Performance & Scaling](#performance--scaling)
- [Errors & Troubleshooting](#errors--troubleshooting)
- [Legal & Ethical](#legal--ethical)

---

## General Questions

### What is SpotifyScraper?
SpotifyScraper is a Python library that extracts data from Spotify's web player without requiring API credentials. It can retrieve information about tracks, albums, artists, and playlists, as well as download preview audio and cover images.

### How is this different from Spotify's official API?
| Feature | SpotifyScraper | Spotify Web API |
|---------|----------------|-----------------|
| Authentication | Not required* | OAuth required |
| Rate Limits | Generous | Strict (varies by tier) |
| Data Access | Public data only | Full catalog access |
| Setup Complexity | Simple | Complex OAuth flow |
| Use Case | Quick extraction | Full applications |

*Note: Lyrics are not available. Spotify's lyrics API requires OAuth Bearer tokens, not cookie authentication

### What Python versions are supported?
SpotifyScraper supports Python 3.8 and above. We recommend using Python 3.10+ for the best experience.

### Is SpotifyScraper free to use?
Yes! SpotifyScraper is open-source software released under the MIT License. You can use it for free in both personal and commercial projects.

---

## Installation Issues

### Why is pip install failing?
Common solutions:
1. Upgrade pip: `pip install --upgrade pip`
2. Use Python 3: `python3 -m pip install spotifyscraper`
3. Install in virtual environment
4. Check [Installation Guide](getting-started/installation.md)

### How do I install on Windows?
```bash
# Using PowerShell or Command Prompt
pip install spotifyscraper

# If pip is not recognized
python -m pip install spotifyscraper
```

### Can I install without admin rights?
Yes, use the `--user` flag:
```bash
pip install --user spotifyscraper
```

### How do I install optional dependencies?
```bash
# For Selenium support
pip install spotifyscraper[selenium]

# For enhanced media features
pip install spotifyscraper[media]

# Everything
pip install spotifyscraper[all]
```

---

## Usage Questions

### How do I extract track information?
```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()
track = client.get_track_info("https://open.spotify.com/track/...")
print(track.get('name', 'Unknown'), (track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown'))
```

### Can I extract multiple items at once?
Yes, but process them sequentially to avoid rate limits:
```python
urls = [url1, url2, url3]
results = []

for url in urls:
    data = client.get_track_info(url)
    results.append(data)
    time.sleep(0.5)  # Be respectful
```

### How do I know what type of URL I have?
```python
from spotify_scraper import is_spotify_url, extract_id

if is_spotify_url(url):
    spotify_id = extract_id(url)
    # URL is valid
```

### Can I use Spotify URIs instead of URLs?
Currently, SpotifyScraper works with URLs. Convert URIs to URLs:
```python
# Convert spotify:track:ID to URL
track_id = "6rqhFgbbKwnb9MLmUQDhG6"
url = f"https://open.spotify.com/track/{track_id}"
```

---

## Authentication & Cookies

### Do I need a Spotify account?
No account is needed for basic features. Cookie authentication can provide higher rate limits and access to private playlists, but lyrics are not available (they require OAuth tokens).

### How do I get cookies for authentication?
1. Install a browser extension like "cookies.txt"
2. Log into Spotify Web Player
3. Export cookies to a file
4. Use with SpotifyScraper:
```python
client = SpotifyClient(cookie_file="spotify_cookies.txt")
```

### How long do cookies last?
Spotify cookies typically last 1 year, but may expire sooner if:
- You log out
- You change your password
- Spotify invalidates them

### Can I use my Spotify API credentials?
No, SpotifyScraper doesn't use Spotify's official API. It works by parsing the web player interface.

---

## Data Extraction

### Why is the album name empty for tracks?
This is a limitation of Spotify's embed API. Track data from embed URLs doesn't include album names, though album images are always available. This is not a bug but a Spotify limitation.

### What data can I extract?

#### Tracks
- Title, artists, duration
- Album (images only, name may be empty)
- Preview URL (if available)
- Release date
- Track number
- Explicit flag
- Lyrics (not available - requires OAuth, not supported)

#### Albums
- Title, artists, release date
- All tracks with details
- Cover images
- Total track count

#### Artists
- Name, genres, popularity
- Biography
- Top tracks
- Monthly listeners
- Images

#### Playlists
- Name, description, owner
- All tracks
- Total duration
- Cover image

### Can I get user-specific data?
No, SpotifyScraper only accesses publicly available data. It cannot access:
- Private playlists
- User libraries
- Listening history
- Personal recommendations

### How accurate is the data?
The data comes directly from Spotify's web player, so it's as accurate as what Spotify displays. However, some fields may be:
- Region-specific
- Subject to change
- Unavailable for certain content

---

## Media Downloads

### What audio quality are the previews?
Spotify provides 30-second previews in:
- Format: MP3
- Bitrate: 96-128 kbps
- Sample Rate: 44.1 kHz

### Can I download full songs?
No, SpotifyScraper only downloads the preview clips that Spotify makes publicly available. It does not and cannot download full tracks.

### What image sizes are available?
Cover images typically come in three sizes:
- Small: 64x64
- Medium: 300x300
- Large: 640x640

### How do I embed metadata in downloads?
```python
# Download with metadata embedding
path = client.download_preview_mp3(
    url,
    path="downloads/",
    with_cover=True  # Embeds cover art
)
```

### Where are files saved?
By default, files are saved to the current directory. Specify a path:
```python
# Save to specific directory
client.download_preview_mp3(url, path="my_music/previews/")
client.download_cover(url, path="my_music/covers/")
```

---

## Performance & Scaling

### How can I speed up extraction?
1. **Reuse client instances** - Don't create new clients for each request
2. **Use requests backend** - Faster than Selenium for most cases
3. **Implement caching** - Store results to avoid repeated requests
4. **Parallel processing** - Use with caution and rate limiting

### What are the rate limits?
Spotify doesn't publish exact limits, but general guidelines:
- Keep requests under 10/minute for safety
- Add delays between requests (0.5-1 second)
- Monitor for 429 (rate limit) errors

### Can I run this in production?
Yes, but consider:
- Implement proper error handling
- Add retry logic with backoff
- Monitor rate limits
- Use caching
- Consider Spotify's ToS

### How do I handle large-scale extraction?
```python
import time
from typing import List

def batch_extract(urls: List[str], delay: float = 1.0):
    """Extract data with rate limiting."""
    client = SpotifyClient()
    results = []
    
    for i, url in enumerate(urls):
        try:
            data = client.get_track_info(url)
            results.append(data)
            
            # Progress
            print(f"Processed {i+1}/{len(urls)}")
            
            # Rate limit
            if i < len(urls) - 1:
                time.sleep(delay)
                
        except Exception as e:
            print(f"Failed: {url} - {e}")
            results.append(None)
    
    return results
```

---

## Errors & Troubleshooting

### Common Errors and Solutions

#### URLError: Invalid URL
- Ensure URL is from open.spotify.com
- Check URL format is correct
- Remove any query parameters

#### NetworkError: Connection failed
- Check internet connection
- Try again later
- Consider using a proxy

#### ExtractionError: Failed to extract data
- Content might be region-restricted
- Page structure might have changed
- Try updating SpotifyScraper

#### AuthenticationError: Authentication required
- Feature requires cookies
- Cookies might have expired
- Re-export cookies from browser

### How do I enable debug logging?
```python
client = SpotifyClient(log_level="DEBUG")
```

Or configure logging globally:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### What if Spotify changes their website?
SpotifyScraper is actively maintained. If Spotify changes their structure:
1. Check for updates: `pip install --upgrade spotifyscraper`
2. Report issues on GitHub
3. The community usually provides fixes quickly

---

## Legal & Ethical

### Is this legal?
SpotifyScraper accesses publicly available data from Spotify's web player. However:
- Always respect Spotify's Terms of Service
- Use responsibly and ethically
- Don't violate copyright laws
- Consider rate limits

### Can I use this commercially?
The library itself is MIT licensed, so yes. However:
- Respect Spotify's ToS
- The data you extract may have restrictions
- Consider getting proper licenses for commercial use

### Is this officially supported by Spotify?
No, this is an independent project not affiliated with Spotify. For official support, use Spotify's Web API.

### What about copyright?
SpotifyScraper only accesses:
- Metadata (facts, not copyrightable)
- 30-second previews (fair use for preview purposes)
- Public images

Never use it to:
- Circumvent DRM
- Download full tracks
- Violate copyright

---

## Still Have Questions?

If your question isn't answered here:

1. 📖 Check the [documentation](index.md)
2. 🔍 Search [GitHub issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
3. 💬 Ask on [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
4. 📧 Contact the maintainers

---

## Contributing to FAQ

Found a common question that's not here? Please:
1. Open a [documentation issue](https://github.com/AliAkhtari78/SpotifyScraper/issues/new)
2. Submit a pull request
3. Help others in discussions

Your contributions help improve the documentation for everyone!