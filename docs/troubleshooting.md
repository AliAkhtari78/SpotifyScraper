# Troubleshooting Guide

This guide helps you diagnose and fix common issues with SpotifyScraper.

## Table of Contents
- [Installation Problems](#installation-problems)
- [Import Errors](#import-errors)
- [Extraction Failures](#extraction-failures)
- [Authentication Issues](#authentication-issues)
- [Network Problems](#network-problems)
- [Media Download Issues](#media-download-issues)
- [Performance Problems](#performance-problems)
- [Platform-Specific Issues](#platform-specific-issues)
- [Debugging Techniques](#debugging-techniques)
- [Getting Help](#getting-help)

---

## Installation Problems

### Error: "pip: command not found"

**Problem**: pip is not installed or not in PATH

**Solutions**:
```bash
# Use Python module syntax
python -m pip install spotifyscraper
# or
python3 -m pip install spotifyscraper

# Install pip if missing
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

### Error: "Could not find a version that satisfies the requirement"

**Problem**: Python version incompatibility or network issues

**Solutions**:
```bash
# Check Python version (needs 3.8+)
python --version

# Upgrade pip
pip install --upgrade pip

# Try different index
pip install -i https://pypi.org/simple/ spotifyscraper

# Install specific version
pip install spotifyscraper==2.0.0
```

### Error: "Permission denied"

**Problem**: Insufficient permissions to install packages

**Solutions**:
```bash
# Install for current user only
pip install --user spotifyscraper

# Use virtual environment (recommended)
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate
pip install spotifyscraper
```

### Error: "Microsoft Visual C++ 14.0 is required"

**Problem**: Missing C++ compiler on Windows

**Solution**:
1. Download Microsoft C++ Build Tools from [visualstudio.microsoft.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Install with "Desktop development with C++" workload
3. Restart and retry installation

---

## Import Errors

### ImportError: No module named 'spotify_scraper'

**Problem**: Package not installed or wrong environment

**Diagnostic Steps**:
```python
# Check if installed
import sys
print(sys.executable)  # Which Python?
print(sys.path)        # Where does Python look?

# List installed packages
import pkg_resources
installed = [pkg.key for pkg in pkg_resources.working_set]
print('spotifyscraper' in installed)
```

**Solutions**:
```bash
# Ensure you're in the right environment
which python  # or `where python` on Windows

# Reinstall
pip uninstall spotifyscraper
pip install spotifyscraper

# Check installation
python -c "import spotify_scraper; print(spotify_scraper.__version__)"
```

### ImportError: cannot import name 'Config'

**Problem**: Config is not directly exported from main module

**Solution**:
```python
# Correct imports
from spotify_scraper import SpotifyClient  # ✓

# If you need to configure the client, use constructor parameters:
client = SpotifyClient(
    browser_type="selenium",
    log_level="DEBUG",
    cookie_file="cookies.txt"
)

# Note: The Config class mentioned in some examples is internal
```

---

## Extraction Failures

### ExtractionError: Failed to extract data

**Common Causes**:
1. Invalid URL format
2. Content not available in your region
3. Spotify structure changed
4. Network issues

**Diagnostic Script**:
```python
from spotify_scraper import SpotifyClient
from spotify_scraper.utils import is_spotify_url

def diagnose_url(url):
    """Diagnose URL issues."""
    print(f"Checking: {url}")
    
    # Validate URL
    if not is_spotify_url(url):
        print("❌ Invalid Spotify URL")
        return
    
    print("✓ Valid Spotify URL")
    
    # Try extraction
    client = SpotifyClient(log_level="DEBUG")
    try:
        data = client.get_track_info(url)
        print("✓ Extraction successful")
        print(f"  Track: {data.get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        print("\nPossible solutions:")
        print("1. Check if content is available in your region")
        print("2. Update SpotifyScraper: pip install --upgrade spotifyscraper")
        print("3. Try using a VPN")
        print("4. Report issue on GitHub if persists")

# Test
diagnose_url("https://open.spotify.com/track/...")
```

### Empty Album Names in Track Data

**This is not a bug!** Spotify's embed API doesn't provide album names for tracks.

**Workaround**:
```python
# If you need album names, extract the album separately
track = client.get_track_info(track_url)
if track.get('album') and track['album'].get('id'):
    album_url = f"https://open.spotify.com/album/{track['album']['id']}"
    album = client.get_album_info(album_url)
    track.get('album', {}).get('name', 'Unknown') = album.get('name', 'Unknown')
```

---

## Authentication Issues

### Lyrics Not Available

**Problem**: Spotify's lyrics API requires OAuth Bearer tokens, not cookie authentication

**Current Status**: SpotifyScraper cannot access lyrics as they require OAuth tokens from Spotify's official Web API.

```python
# This will NOT work - OAuth required
client = SpotifyClient(cookie_file="spotify_cookies.txt")
track = client.get_track_info_with_lyrics(url)
# track['lyrics'] will be None
```

**Alternative**: Use the official Spotify Web API with proper OAuth authentication if you need lyrics access.

### Getting Cookies

**Step-by-step**:
1. Install browser extension: "cookies.txt" or "Get cookies.txt"
2. Go to [open.spotify.com](https://open.spotify.com)
3. Log in to your account
4. Click extension and export cookies
5. Save as `spotify_cookies.txt`

### Cookie Validation Script
```python
def validate_cookies(cookie_file):
    """Check if cookies are valid."""
    try:
        client = SpotifyClient(cookie_file=cookie_file)
        # Try to get a private playlist (requires auth)
        # Note: Lyrics cannot be used for validation as they require OAuth
        
        # Instead, check if cookies work by trying authenticated actions
        print("✓ Cookies loaded successfully")
        # You can test with private playlists or other auth features
    except:
            print("❌ Cookies might be expired")
    except Exception as e:
        print(f"❌ Cookie error: {e}")

validate_cookies("spotify_cookies.txt")
```

---

## Network Problems

### ConnectionError or TimeoutError

**Common Causes**:
- No internet connection
- Firewall blocking requests
- Proxy configuration issues
- Spotify server issues

**Solutions**:

1. **Test basic connectivity**:
```python
import requests
try:
    response = requests.get("https://open.spotify.com", timeout=10)
    print(f"✓ Connected: {response.status_code}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

2. **Use proxy with requests**:
```python
# Note: Proxy configuration depends on browser type
# For requests browser, you would need to configure the session
# For selenium browser, you would configure the driver options
client = SpotifyClient(browser_type="requests")
# Proxy configuration is browser-specific
```

3. **Increase timeout**:
```python
# For Selenium browser
client = SpotifyClient(browser_type="selenium")
# Note: Timeout configuration varies by browser type
```

### SSL Certificate Errors

**Problem**: SSL verification failing

**Solutions**:
```bash
# Update certificates
pip install --upgrade certifi

# For corporate networks, you might need:
export REQUESTS_CA_BUNDLE=/path/to/corporate/cert.pem
export SSL_CERT_FILE=/path/to/corporate/cert.pem
```

---

## Media Download Issues

### Preview Not Available

**Problem**: Not all tracks have preview URLs

**Solution**:
```python
track = client.get_track_info(url)
if track.get('preview_url'):
    path = client.download_preview_mp3(url)
else:
    print("No preview available for this track")
```

### Download Fails Silently

**Problem**: Directory doesn't exist or permission issues

**Diagnostic**:
```python
import os

def safe_download(url, directory="downloads"):
    """Download with error checking."""
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Check write permissions
    test_file = os.path.join(directory, ".test")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✓ Directory is writable")
    except:
        print("❌ Cannot write to directory")
        return
    
    # Download
    try:
        path = client.download_preview_mp3(url, path=directory)
        print(f"✓ Downloaded to: {path}")
    except Exception as e:
        print(f"❌ Download failed: {e}")
```

### Metadata Not Embedding

**Problem**: eyeD3 not installed

**Solution**:
```bash
# Install media dependencies
pip install "spotifyscraper[media]"
# or
pip install eyeD3 mutagen
```

---

## Performance Problems

### Slow Extraction

**Common Causes**:
1. Using Selenium when not needed
2. Not reusing client instances
3. No caching implemented

**Solutions**:

1. **Use appropriate browser**:
```python
# Fast - for most cases
client = SpotifyClient(browser_type="requests")

# Slower - only when needed
client = SpotifyClient(browser_type="selenium")
```

2. **Reuse clients**:
```python
# Good
client = SpotifyClient()
for url in urls:
    data = client.get_track_info(url)

# Bad
for url in urls:
    client = SpotifyClient()  # Creating new instance each time
    data = client.get_track_info(url)
```

3. **Implement caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_track_cached(url):
    """Cache track data in memory."""
    return client.get_track_info(url)
```

### Memory Usage

**Problem**: High memory usage with Selenium

**Solution**:
```python
# Always close Selenium browsers
client = SpotifyClient(browser_type="selenium")
try:
    # Your code
    pass
finally:
    client.close()  # Important!
```

---

## Platform-Specific Issues

### Windows

#### Path Issues
```python
# Use raw strings or forward slashes
path = r"C:\Users\Name\Music"  # Raw string
path = "C:/Users/Name/Music"   # Forward slashes
```

#### Selenium Driver Issues
```bash
# Install driver manager
pip install webdriver-manager

# It will auto-download drivers
```

### macOS

#### Permission Errors
```bash
# On macOS Catalina+, you might need
pip install --user spotifyscraper
```

#### Apple Silicon (M1/M2)
```bash
# Ensure using ARM version
arch -arm64 pip install spotifyscraper
```

### Linux

#### Missing Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev

# For Selenium
sudo apt-get install chromium-chromedriver
```

#### Headless Selenium
```python
# Required for servers without display
client = SpotifyClient(browser_type="selenium")
# Selenium runs headless by default
```

---

## Debugging Techniques

### Enable Debug Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or use client parameter
client = SpotifyClient(log_level="DEBUG")
```

### Inspection Script

```python
def inspect_response(url):
    """Inspect what SpotifyScraper sees."""
    from spotify_scraper.browsers import create_browser
    
    browser = create_browser("requests")
    content = browser.get_page_content(url)
    
    # Save response for inspection
    with open("response.html", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("Response saved to response.html")
    print(f"Size: {len(content)} bytes")
    
    # Check for common issues
    if "404" in content:
        print("⚠️ Might be 404 error")
    if "not available" in content.lower():
        print("⚠️ Content might not be available")
```

### Version Information

```python
def print_version_info():
    """Print version information for debugging."""
    import sys
    import spotify_scraper
    
    print(f"Python: {sys.version}")
    print(f"SpotifyScraper: {spotify_scraper.__version__}")
    
    # Check optional dependencies
    try:
        import selenium
        print(f"Selenium: {selenium.__version__}")
    except:
        print("Selenium: Not installed")
    
    try:
        import eyed3
        print(f"eyeD3: {eyed3.version.version}")
    except:
        print("eyeD3: Not installed")
```

---

## Getting Help

### Before Asking for Help

1. **Check documentation**: Read relevant sections
2. **Search issues**: Look for similar problems on GitHub
3. **Try examples**: Run example code to isolate issue
4. **Update package**: `pip install --upgrade spotifyscraper`

### Creating a Good Bug Report

Include:
- SpotifyScraper version
- Python version
- Operating system
- Complete error message
- Minimal code to reproduce
- What you expected vs what happened

**Template**:
```markdown
## Environment
- SpotifyScraper version: 2.0.0
- Python version: 3.10.0
- OS: Windows 10

## Code
```python
from spotify_scraper import SpotifyClient
client = SpotifyClient()
# Minimal code that shows the problem
```

## Error
```
Full error message here
```

## Expected Behavior
What should happen

## Actual Behavior
What actually happens
```

### Where to Get Help

1. 📖 **Documentation**: [spotifyscraper.readthedocs.io](https://spotifyscraper.readthedocs.io)
2. 💬 **Discussions**: [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
3. 🐛 **Bug Reports**: [GitHub Issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
4. 📧 **Email**: See repository for maintainer contact

---

## Common Import Fixes

```python
# Correct imports
from spotify_scraper import (
    SpotifyClient,
    SpotifyScraperError,
    URLError,
    NetworkError,
    ExtractionError,
    AuthenticationError,
    MediaError
)

# Utility imports
from spotify_scraper.utils import (
    is_spotify_url,
    extract_id,
    convert_to_embed_url,
    get_url_type
)

# For bulk operations
from spotify_scraper.utils import (
    SpotifyBulkOperations,
    SpotifyDataAnalyzer
)
```

## Quick Fixes Reference

| Problem | Quick Fix |
| Import error | `pip install --upgrade spotifyscraper` |
| No preview URL | Check if track has preview: `track.get('preview_url')` |
| Empty album name | Known limitation, not a bug |
| Cookies expired | Re-export from browser |
| SSL error | `pip install --upgrade certifi` |
| Slow performance | Use `browser_type="requests"` |
| Memory leak | Call `client.close()` when done |
| Rate limited | Add delays: `time.sleep(1)` |