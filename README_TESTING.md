# SpotifyScraper v2.0 - Testing Guide

## 🎉 Installation Complete!

SpotifyScraper v2.0 has been successfully installed and tested. Here's what you need to know:

## ✅ What's Working

1. **Package Installation**
   - Successfully installed with all dependencies
   - CLI commands are available via `spotify-scraper`
   - Python API is importable as `spotify_scraper`

2. **Core Features**
   - URL validation and ID extraction
   - Client creation and initialization
   - Backward compatibility layer
   - CLI interface

3. **Available Commands**
   ```bash
   spotify-scraper --help                    # Show help
   spotify-scraper track <url>               # Extract track info
   spotify-scraper album <url>               # Extract album info
   spotify-scraper artist <url>              # Extract artist info
   spotify-scraper playlist <url>            # Extract playlist info
   spotify-scraper download cover <url>      # Download cover image
   spotify-scraper download track <url>      # Download preview MP3
   ```

## 🧪 Testing the Library

### 1. Quick Test
```bash
# Run the simple test script
python examples/simple_test.py
```

### 2. CLI Test
```bash
# Test the CLI with a track URL
spotify-scraper track https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp
```

### 3. Python API Test
```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()
track = client.get_track_info("https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp")
print(track_info)
```

### 4. Direct Extractor Usage
```python
from spotify_scraper.extractors import TrackExtractor
from spotify_scraper.browsers import create_browser

browser = create_browser()
extractor = TrackExtractor(browser)
track = extractor.extract("https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp")
```

## ⚠️ Known Limitations

1. **Network Requests**: Actual data extraction requires internet connection and may be affected by Spotify's rate limiting or changes to their web interface.

2. **Authentication**: Features like lyrics extraction require authentication via cookies. Use the `-c` flag with a cookies.txt file:
   ```bash
   spotify-scraper -c cookies.txt track --with-lyrics <url>
   ```

3. **Media Downloads**: Preview MP3s and cover images are only available for content that Spotify provides previews for.

## 📁 Example Scripts

Check the `examples/` directory for usage examples:
- `simple_test.py` - Basic functionality test
- `basic_usage.py` - Demonstrates API usage
- `cli_examples.sh` - CLI command examples

## 🐛 Troubleshooting

If you encounter issues:

1. **Import Errors**: Make sure you're in the virtual environment:
   ```bash
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Network Errors**: Check your internet connection and proxy settings

3. **Extraction Errors**: Spotify's web interface changes frequently. The library uses multiple fallback methods, but some features may break.

## 🚀 Next Steps

1. Test with real Spotify URLs
2. Try different entity types (tracks, albums, artists, playlists)
3. Experiment with output formats (JSON, YAML, table)
4. Test media downloads (covers and preview MP3s)

## 📝 Feedback

If you encounter any issues or have suggestions, please report them!

---

**Version**: 2.0.0  
**Status**: Ready for Testing  
**Python**: 3.8+