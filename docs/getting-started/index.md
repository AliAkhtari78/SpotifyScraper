# Getting Started

Welcome to SpotifyScraper - your gateway to effortless Spotify data extraction! This section will guide you from zero to hero, helping you understand, install, and configure SpotifyScraper for your projects.

---

## What You'll Learn

<div class="grid-cards">
  <div class="card">
    <h3>📦 Installation</h3>
    <p>Multiple installation methods for every platform and use case</p>
  </div>
  
  <div class="card">
    <h3>⚙️ Configuration</h3>
    <p>Customize SpotifyScraper to match your needs perfectly</p>
  </div>
  
  <div class="card">
    <h3>🚀 Quick Start</h3>
    <p>Get your first data extraction running in under 5 minutes</p>
  </div>
  
  <div class="card">
    <h3>💡 Best Practices</h3>
    <p>Learn from experienced users and avoid common pitfalls</p>
  </div>
</div>

---

## Why SpotifyScraper?

### 🎯 Zero Authentication Required
Unlike the official Spotify API, SpotifyScraper doesn't require:
- API keys or client secrets
- OAuth authentication flows
- App registration or approval
- Rate limit management

### 🛠️ Simple Yet Powerful
```python
# This is all you need to get started!
from spotify_scraper import SpotifyClient

client = SpotifyClient()
track = client.get_track_info("spotify_track_url")
print(f"Track: {track.get('name', 'Unknown')} by {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")
```

### 📊 Comprehensive Data Access
Extract detailed information about:
- **Tracks**: Title, artists, album, duration, preview URLs, lyrics
- **Albums**: Full track listings, release dates, cover art, label info
- **Artists**: Biography, genres, popularity, follower count, top tracks
- **Playlists**: Complete track lists, descriptions, owner information

---

## Quick Example

Let's see SpotifyScraper in action with a real example:

```python
from spotify_scraper import SpotifyClient

# Initialize the client
client = SpotifyClient()

# Extract track information
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track = client.get_track_info(track_url)

# Display the results
print(f"Track: {track.get('name', 'Unknown')}")
print(f"Artist: {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")
print(f"Album: {track.get('album', {}).get('name', 'Unknown')}")
print(f"Duration: {track.get('duration_ms', 0) / 1000:.0f} seconds")

# Download preview audio (if available)
if track.get('preview_url'):
    preview_path = client.download_preview_mp3(track_url, path="downloads/")
    print(f"Preview saved to: {preview_path}")

# Don't forget to clean up!
client.close()
```

**Output:**
```
Track: Sweet Child O' Mine
Artist: Guns N' Roses
Album: Appetite For Destruction
Duration: 303 seconds
Preview saved to: downloads/sweet_child_o_mine.mp3
```

---

## Your Journey Starts Here

### Step 1: Installation

Choose your preferred installation method:

```bash
# Basic installation
pip install spotifyscraper

# With all features
pip install "spotifyscraper[all]"

# Development version
pip install git+https://github.com/AliAkhtari78/SpotifyScraper.git
```

📖 **[Read the Complete Installation Guide →](installation.md)**

### Step 2: Configuration

Configure SpotifyScraper for your specific needs:

```python
# Example: Optimized for batch processing
client = SpotifyClient(
    browser_type="requests",      # Fast HTTP client
    timeout=45,                   # Reasonable timeout
    use_cache=True,              # Enable caching
    rate_limit=True,             # Respect rate limits
    log_level="INFO"             # Moderate logging
)
```

⚙️ **[Explore All Configuration Options →](configuration.md)**

### Step 3: Start Building

With SpotifyScraper installed and configured, you're ready to:
- Extract data from any Spotify URL
- Download preview audio and cover art
- Build music analytics applications
- Create playlist management tools
- And much more!

---

## Common Use Cases

### 🎵 Music Analytics
```python
# Analyze an artist's top tracks
artist = client.get_artist_info(artist_url)
print(f"Monthly Listeners: {artist['stats']['monthlyListeners']:,}")
```

### 📥 Media Downloads
```python
# Download album cover in high resolution
cover_path = client.download_cover(album_url, size="large")
```

### 📋 Playlist Management
```python
# Extract all tracks from a playlist
playlist = client.get_playlist_info(playlist_url)
for track in playlist['tracks']:
    print(f"- {track.get('name', 'Unknown')} by {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}")
```

### 🔍 Batch Processing
```python
# Process multiple URLs efficiently
urls = ["url1", "url2", "url3"]
results = client.get_multiple(urls, entity_type="track")
```

---

## Platform Support

SpotifyScraper works seamlessly across all major platforms:

| Platform | Python Versions | Status |
|----------|----------------|---------|
| Windows 10/11 | 3.8 - 3.12 | ✅ Fully Supported |
| macOS 10.15+ | 3.8 - 3.12 | ✅ Fully Supported |
| Ubuntu/Debian | 3.8 - 3.12 | ✅ Fully Supported |
| Docker | 3.8 - 3.12 | ✅ Fully Supported |

---

## Best Practices

### ✅ DO
- Use context managers (`with` statements) for automatic cleanup
- Enable caching for better performance
- Respect rate limits to avoid being blocked
- Handle errors gracefully with try-except blocks
- Close the client when done

### ❌ DON'T
- Make excessive requests in short periods
- Share authentication cookies publicly
- Ignore error messages
- Use outdated versions
- Violate Spotify's Terms of Service

---

## Troubleshooting Tips

### 🔧 Common Issues

1. **Import Error**: Make sure SpotifyScraper is installed:
   ```bash
   pip install --upgrade spotifyscraper
   ```

2. **Connection Error**: Check your internet connection and proxy settings

3. **Rate Limiting**: Add delays between requests:
   ```python
   client = SpotifyClient(request_delay=1)  # 1 second delay
   ```

4. **Missing Data**: Some fields may be region-restricted or require authentication

---

## What's Next?

<div class="next-steps">
  <a href="installation.md" class="step-card">
    <h3>📦 Installation Guide</h3>
    <p>Detailed installation instructions for every platform and scenario</p>
    <span class="arrow">→</span>
  </a>
  
  <a href="configuration.md" class="step-card">
    <h3>⚙️ Configuration Guide</h3>
    <p>Learn how to configure SpotifyScraper for optimal performance</p>
    <span class="arrow">→</span>
  </a>
  
  <a href="../examples/quickstart.md" class="step-card">
    <h3>🚀 Quick Start Tutorial</h3>
    <p>Build your first SpotifyScraper project in 5 minutes</p>
    <span class="arrow">→</span>
  </a>
  
  <a href="../guide/basic-usage.md" class="step-card">
    <h3>📖 Basic Usage Guide</h3>
    <p>Master the core features and common patterns</p>
    <span class="arrow">→</span>
  </a>
</div>

---

## Need Help?

We're here to support your journey:

- 💬 **[GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)** - Ask questions and share ideas
- 🐛 **[Issue Tracker](https://github.com/AliAkhtari78/SpotifyScraper/issues)** - Report bugs or request features
- 📚 **[FAQ](../faq.md)** - Answers to frequently asked questions
- 🔧 **[Troubleshooting](../troubleshooting.md)** - Solutions to common problems

---

## Ready to Start?

You're just a few steps away from extracting Spotify data like a pro! Begin with the [Installation Guide](installation.md) and follow the journey through configuration to your first working script.

<div class="cta-box">
  <h3>🎉 Let's Get Started!</h3>
  <p>Install SpotifyScraper now and join thousands of developers building amazing music applications.</p>
  <a href="installation.md" class="cta-button">Start Installation →</a>
</div>

---

<div class="footer-note">
  <p><em>SpotifyScraper is an open-source project. We welcome contributions and feedback!</em></p>
  <p><a href="https://github.com/AliAkhtari78/SpotifyScraper">⭐ Star us on GitHub</a></p>
</div>