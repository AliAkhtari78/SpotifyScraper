# SpotifyScraper Documentation

<div align="center">

![SpotifyScraper Logo](https://raw.githubusercontent.com/AliAkhtari78/SpotifyScraper/master/docs/_static/logo.png)

**The Ultimate Python Library for Spotify Data Extraction**

**Version 2.0.0 | © 2025 Ali Akhtari**

[![PyPI version](https://badge.fury.io/py/spotifyscraper.svg)](https://badge.fury.io/py/spotifyscraper)
[![Python Support](https://img.shields.io/pypi/pyversions/spotifyscraper.svg)](https://pypi.org/project/spotifyscraper/)
[![Documentation Status](https://readthedocs.org/projects/spotifyscraper/badge/?version=latest)](https://spotifyscraper.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

[**Installation**](#installation) • [**Quick Start**](examples/quickstart.md) • [**API Reference**](api/index.md) • [**Examples**](examples/index.md) • [**FAQ**](faq.md)

</div>

---

## Welcome to SpotifyScraper

SpotifyScraper is a powerful, modern Python library designed to extract data from Spotify's web player without requiring API credentials. Built for reliability, performance, and ease of use, it provides a comprehensive toolkit for accessing Spotify's vast music database.

### 🚀 Why SpotifyScraper?

- **Zero Authentication**: No API keys, no OAuth, no hassle
- **Comprehensive Data**: Extract tracks, albums, artists, playlists, and lyrics
- **High Performance**: Optimized for speed with intelligent caching
- **Type Safe**: Full type hints for better IDE support
- **Battle Tested**: Used in production by thousands of developers
- **Active Development**: Regular updates and community support

### 🎯 Perfect For

- **Music Analytics**: Analyze trends, popularity, and musical patterns
- **Research Projects**: Academic research on music data
- **Personal Tools**: Build your own music management systems
- **Data Science**: Create datasets for machine learning
- **Content Creation**: Generate playlists and music recommendations

---

## 📦 Installation

### Basic Installation

```bash
pip install spotifyscraper
```

### Installation with Optional Features

```bash
# With Selenium support for complex scenarios
pip install "spotifyscraper[selenium]"

# With enhanced media handling
pip install "spotifyscraper[media]"

# All features
pip install "spotifyscraper[all]"
```

### Development Installation

```bash
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper
pip install -e ".[dev]"
```

---

## 🏃 Quick Start

### Your First Script

```python
from spotify_scraper import SpotifyClient

# Initialize the client
client = SpotifyClient()

# Extract track information
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track = client.get_track_info(track_url)

print(f"🎵 {track['name']}")
print(f"👤 {track['artists'][0]['name']}")
print(f"⏱️ {track['duration_ms'] / 1000:.0f} seconds")

# Always close when done
client.close()
```

### Download Media

```python
# Download track preview
preview_path = client.download_preview_mp3(track_url, path="downloads/")
print(f"✅ Preview saved to: {preview_path}")

# Download album cover
cover_path = client.download_cover(track_url, path="covers/")
print(f"🖼️ Cover saved to: {cover_path}")
```

---

## 📚 Documentation Overview

### 🚀 Getting Started
- [**Installation Guide**](getting-started/installation.md) - Detailed installation instructions
- [**Quick Start Tutorial**](examples/quickstart.md) - Get up and running in minutes
- [**Configuration**](getting-started/configuration.md) - Configure SpotifyScraper for your needs

### 📖 User Guide
- [**Basic Usage**](guide/basic-usage.md) - Core functionality and common tasks
- [**Authentication**](guide/authentication.md) - Access premium features with cookies
- [**Media Downloads**](guide/media-downloads.md) - Download audio and images
- [**Error Handling**](guide/error-handling.md) - Handle errors gracefully

### 🔧 API Reference
- [**SpotifyClient**](api/client.md) - Main client class
- [**Extractors**](api/extractors.md) - Data extraction classes
- [**Media Handlers**](api/media.md) - Audio and image downloaders
- [**Exceptions**](api/exceptions.md) - Error types and handling
- [**Utilities**](api/utils.md) - Helper functions

### 💡 Examples
- [**Quick Examples**](examples/quickstart.md) - Common use cases
- [**Advanced Patterns**](examples/advanced.md) - Complex scenarios
- [**Real-World Projects**](examples/projects.md) - Complete applications
- [**CLI Usage**](examples/cli.md) - Command-line interface

### 🛠️ Advanced Topics
- [**Performance Optimization**](advanced/performance.md) - Speed up your scripts
- [**Scaling Guide**](advanced/scaling.md) - Handle large-scale extraction
- [**Custom Extractors**](advanced/custom-extractors.md) - Extend functionality
- [**Architecture**](advanced/architecture.md) - Internal design

### 📚 Resources
- [**FAQ**](faq.md) - Frequently asked questions
- [**Troubleshooting**](troubleshooting.md) - Common issues and solutions
- [**Migration Guide**](migration.md) - Upgrading from v1.x
- [**Changelog**](changelog.md) - Version history

---

## 🌟 Key Features

### Data Extraction
- **Tracks**: Title, artists, album, duration, preview URLs, lyrics
- **Albums**: Full track listings, release dates, cover art
- **Artists**: Biography, top tracks, discography, monthly listeners
- **Playlists**: Complete track lists, descriptions, owner info

### Media Handling
- **Audio Preview**: Download 30-second MP3 previews
- **Cover Art**: High-resolution album/playlist covers
- **Metadata**: Automatic ID3 tag embedding
- **Batch Downloads**: Efficient bulk operations

### Advanced Features
- **Smart Caching**: Reduce API calls and improve speed
- **Proxy Support**: Route through proxy servers
- **Rate Limiting**: Automatic request throttling
- **Error Recovery**: Robust retry mechanisms

---

## 💻 Supported Platforms

- ✓ **Windows** (10, 11)
- ✓ **macOS** (10.15+)
- ✓ **Linux** (Ubuntu, Debian, Fedora, etc.)
- ✓ **Python** (3.8, 3.9, 3.10, 3.11, 3.12)

---

## 🤝 Community & Support

### Get Help
- 📖 [Documentation](https://spotifyscraper.readthedocs.io)
- 💬 [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
- 🐛 [Issue Tracker](https://github.com/AliAkhtari78/SpotifyScraper/issues)

### Contributing
- 🔧 [Contributing Guide](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/CONTRIBUTING.md)
- 📝 [Code of Conduct](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/CODE_OF_CONDUCT.md)
- 🎯 [Development Setup](contributing.md)

---

## ⚠️ Important Notes

### Limitations
SpotifyScraper uses Spotify's embed API to provide reliable, authentication-free access. This approach has some limitations:

- **Album Names**: Track objects may have empty album names (images are always available)
- **Rate Limits**: Spotify may rate limit excessive requests
- **Regional Availability**: Some content may be region-restricted

### Legal Disclaimer
This library is for educational and personal use. Always respect Spotify's Terms of Service and copyright laws. Be mindful of rate limits and use the library responsibly.

---

## 🚀 What's Next?

<div class="grid">
  <div class="card">
    <h3>📖 Quick Start Guide</h3>
    <p>Learn the basics in 5 minutes</p>
    <a href="examples/quickstart.md" class="button">Get Started →</a>
  </div>
  
  <div class="card">
    <h3>🔧 API Reference</h3>
    <p>Detailed documentation of all classes</p>
    <a href="api/index.md" class="button">Explore API →</a>
  </div>
  
  <div class="card">
    <h3>💡 Examples</h3>
    <p>Real-world code examples</p>
    <a href="examples/index.md" class="button">View Examples →</a>
  </div>
</div>

---

<div align="center">
  <p><strong>SpotifyScraper v2.0.0 - Documentation Last Updated: May 2025</strong></p>
  <p>Built with ❤️ by <a href="https://github.com/AliAkhtari78">Ali Akhtari</a> and contributors</p>
  <p>
    <a href="https://github.com/AliAkhtari78/SpotifyScraper">GitHub</a> •
    <a href="https://pypi.org/project/spotifyscraper/">PyPI</a> •
    <a href="https://spotifyscraper.readthedocs.io">Documentation</a>
  </p>
  <p><small>© 2025 Ali Akhtari. Licensed under MIT.</small></p>
</div>