# Frequently Asked Questions (FAQ)

Common questions and answers about SpotifyScraper.

## 📋 Table of Contents

- [General Questions](#general-questions)
- [Installation Issues](#installation-issues)
- [Usage Questions](#usage-questions)
- [Error Solutions](#error-solutions)
- [Legal & Ethical](#legal--ethical)

## General Questions

### What is SpotifyScraper?

SpotifyScraper is a Python library that extracts data from Spotify's web player without requiring API credentials. It can fetch metadata for tracks, albums, artists, and playlists, as well as download preview audio and cover images.

### Do I need a Spotify API key?

No! SpotifyScraper works without any API keys or OAuth authentication. It uses Spotify's public embed API to extract data.

### What data can I extract?

- **Tracks**: Name, artists, album, duration, preview URL, explicit flag
- **Albums**: Name, artists, release date, track listing, cover art
- **Artists**: Name, followers, monthly listeners, top tracks, genres
- **Playlists**: Name, description, owner, track listing
- **Lyrics**: Available with authentication (cookies)

### What are the limitations?

- **30-second previews**: Full tracks are not available
- **Rate limits**: Spotify may limit excessive requests
- **Authentication**: Some features (lyrics) require cookies
- **Regional restrictions**: Some content may be geo-blocked

### Is it faster than the official API?

For basic metadata extraction, SpotifyScraper is comparable in speed. With caching enabled, subsequent requests are much faster since they don't require network calls.

## Installation Issues

### pip install fails with "No matching distribution"

Update pip and try again:
```bash
python -m pip install --upgrade pip
pip install spotifyscraper
```

### ImportError: No module named 'spotify_scraper'

Make sure you installed the package:
```bash
pip install spotifyscraper
```

Note: The package name is `spotifyscraper` (no underscore), but you import it as `spotify_scraper` (with underscore).

### SSL Certificate errors

Try installing with trusted hosts:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org spotifyscraper
```

### Permission denied during installation

Install with user flag:
```bash
pip install --user spotifyscraper
```

## Usage Questions

### How do I get lyrics?

Lyrics require authentication. You need to export cookies from your browser:

1. Log in to Spotify Web Player
2. Export cookies using a browser extension
3. Save as `cookies.txt`
4. Use authenticated client:

```python
client = SpotifyClient(cookie_file="cookies.txt")
track = client.get_track_info_with_lyrics(url)
```

### How do I download all tracks from a playlist?

```python
playlist = client.get_playlist_info(playlist_url)
for track in playlist['tracks']:
    try:
        preview_path = client.download_preview_mp3(
            track['external_urls']['spotify']
        )
        print(f"Downloaded: {track['name']}")
    except Exception as e:
        print(f"Failed: {track['name']} - {e}")
```

### Can I get full songs instead of previews?

No, SpotifyScraper only provides access to 30-second preview clips. Full tracks are protected by DRM and not accessible through the web player.

### How do I use a proxy?

```python
client = SpotifyClient(proxy="http://proxy.example.com:8080")
```

### How do I increase timeout for slow connections?

```python
client = SpotifyClient(timeout=60)  # 60 seconds
```

### Can I disable caching?

```python
client = SpotifyClient(cache_enabled=False)
```

## Error Solutions

### URLError: Invalid Spotify URL

Make sure the URL is a valid Spotify link:
- ✅ `https://open.spotify.com/track/...`
- ❌ `spotify:track:...` (URI format not supported)
- ❌ `https://spotify.com/...` (wrong domain)

### NetworkError: Connection timeout

1. Check your internet connection
2. Increase timeout: `client = SpotifyClient(timeout=60)`
3. Try using a proxy
4. Check if Spotify is accessible in your region

### AuthenticationError: Cookies required

Some features need authentication:
```python
client = SpotifyClient(cookie_file="spotify_cookies.txt")
```

### ExtractionError: Failed to extract data

This can happen if:
- Content is not available in your region
- Spotify changed their web player structure
- The content was removed

Try updating to the latest version:
```bash
pip install --upgrade spotifyscraper
```

### Rate limit errors

If you're getting rate limited:
1. Add delays between requests: `time.sleep(1)`
2. Use caching to avoid repeated requests
3. Reduce parallel requests
4. Use a proxy to distribute requests

## Legal & Ethical

### Is this legal?

SpotifyScraper accesses publicly available data from Spotify's web player. However:
- Always respect Spotify's Terms of Service
- Don't use it for commercial purposes without permission
- Respect rate limits and don't overload servers
- Give credit to artists and Spotify

### Can I use this for my commercial app?

You should:
1. Review Spotify's Terms of Service
2. Consider using the official Spotify API instead
3. Contact Spotify for commercial licensing
4. Consult with a legal professional

### Is this ethical?

Consider these guidelines:
- Use responsibly and don't abuse the service
- Support artists by using official Spotify apps
- Don't redistribute copyrighted content
- Use for personal/educational purposes

### Will my IP get banned?

To avoid issues:
- Don't make excessive requests
- Use reasonable delays between requests
- Enable caching to reduce requests
- Respect rate limits

### Can I sell data extracted with this?

No. The data belongs to Spotify and the content creators. You should not sell or commercially distribute data extracted using this library.

## 🤔 Still Have Questions?

- 📖 Check the [Documentation](https://spotifyscraper.readthedocs.io)
- 💬 Ask in [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
- 🐛 Report bugs in [Issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
- 📧 Contact: aliakhtari78@hotmail.com