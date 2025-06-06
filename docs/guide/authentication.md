# Authentication Guide

This guide covers how to set up authentication with SpotifyScraper to access premium features and increase rate limits.

## Table of Contents
- [Overview](#overview)
- [Cookie-Based Authentication](#cookie-based-authentication)
- [Extracting Cookies](#extracting-cookies)
- [Setting Up Authentication](#setting-up-authentication)
- [Premium Features](#premium-features)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

---

## Overview

SpotifyScraper works without authentication, but authenticated access provides:

### Benefits of Authentication

- **Higher Rate Limits**: Reduce chances of being rate-limited
- **Premium Content**: Access to premium-only tracks and features
- **Better Reliability**: More stable access to Spotify's services
- **Extended Metadata**: Additional track and album information
- **Playlist Access**: Private and collaborative playlists

**Note**: Lyrics are NOT accessible via cookie authentication. Spotify's lyrics API requires OAuth Bearer tokens which are only available through the official Spotify Web API.

### Authentication Methods

SpotifyScraper uses **cookie-based authentication** - the same method your browser uses when you're logged into Spotify. No API keys or OAuth required.

---

## Cookie-Based Authentication

### How It Works

When you log into Spotify in your browser, Spotify sets authentication cookies. SpotifyScraper can use these same cookies to authenticate requests.

### Required Cookies

The two main cookies needed are:

- **`sp_dc`**: Your Spotify authentication token
- **`sp_key`**: Additional authentication key (optional but recommended)

### Authentication Flow

```python
from spotify_scraper import SpotifyClient

# Using authentication cookies
client = SpotifyClient(cookies={
    'sp_dc': 'AQBYourSpDcTokenHere...',
    'sp_key': 'AQAYourSpKeyHere...'
})

# Now you have authenticated access
track = client.get_track_info("https://open.spotify.com/track/...")
```

---

## Extracting Cookies

### Method 1: Browser Developer Tools

#### Chrome/Edge
1. Go to [open.spotify.com](https://open.spotify.com) and log in
2. Press **F12** to open Developer Tools
3. Go to **Application** tab
4. In the sidebar, expand **Cookies** and click **https://open.spotify.com**
5. Find and copy the values for `sp_dc` and `sp_key`

#### Firefox
1. Go to [open.spotify.com](https://open.spotify.com) and log in
2. Press **F12** to open Developer Tools
3. Go to **Storage** tab
4. In the sidebar, expand **Cookies** and click **https://open.spotify.com**
5. Find and copy the values for `sp_dc` and `sp_key`

#### Safari
1. Enable Developer Tools: Safari → Preferences → Advanced → Show Develop menu
2. Go to [open.spotify.com](https://open.spotify.com) and log in
3. Open Develop → Show Web Inspector
4. Go to **Storage** tab
5. Click **Cookies** → **https://open.spotify.com**
6. Find and copy the values for `sp_dc` and `sp_key`

### Method 2: Browser Extensions

#### Using "cookies.txt" Extension

1. Install the "cookies.txt" browser extension
2. Go to [open.spotify.com](https://open.spotify.com) and log in
3. Click the extension icon
4. Export cookies to a file
5. Use the file with SpotifyScraper

```python
# Using cookies.txt file
client = SpotifyClient(cookie_file="spotify_cookies.txt")
```

#### Using "EditThisCookie" Extension

1. Install the "EditThisCookie" extension
2. Go to [open.spotify.com](https://open.spotify.com) and log in
3. Click the extension icon
4. Export cookies as JSON
5. Use the JSON data with SpotifyScraper

### Method 3: Programmatic Extraction

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json

def extract_spotify_cookies(email, password):
    """Extract Spotify cookies using Selenium."""
    driver = webdriver.Chrome()
    
    try:
        # Go to Spotify login
        driver.get("https://accounts.spotify.com/login")
        
        # Fill in credentials
        driver.find_element(By.ID, "login-username").send_keys(email)
        driver.find_element(By.ID, "login-password").send_keys(password)
        driver.find_element(By.ID, "login-button").click()
        
        # Wait for login to complete
        time.sleep(5)
        
        # Navigate to Spotify Web Player
        driver.get("https://open.spotify.com")
        time.sleep(3)
        
        # Extract cookies
        cookies = driver.get_cookies()
        spotify_cookies = {}
        
        for cookie in cookies:
            if cookie['name'] in ['sp_dc', 'sp_key']:
                spotify_cookies[cookie['name']] = cookie['value']
        
        return spotify_cookies
        
    finally:
        driver.quit()

# Use the extracted cookies
cookies = extract_spotify_cookies("your_email@example.com", "your_password")
client = SpotifyClient(cookies=cookies)
```

---

## Setting Up Authentication

### Method 1: Direct Cookie Values

```python
from spotify_scraper import SpotifyClient

# Using cookie dictionary
cookies = {
    'sp_dc': 'AQBYourSpDcValueHere...',
    'sp_key': 'AQAYourSpKeyValueHere...'  # Optional but recommended
}

client = SpotifyClient(cookies=cookies)
```

### Method 2: Cookie String

```python
# Using cookie string (like browser format)
cookie_string = "sp_dc=AQBYourSpDcValueHere...; sp_key=AQAYourSpKeyValueHere..."

client = SpotifyClient(cookies=cookie_string)
```

### Method 3: Cookie File

```python
# Using Netscape cookie file format
client = SpotifyClient(cookie_file="spotify_cookies.txt")

# Using JSON cookie file
client = SpotifyClient(cookie_file="cookies.json")
```

### Method 4: Environment Variables

```bash
# Set environment variables
export SPOTIFY_COOKIES='{"sp_dc": "AQBYourSpDcValueHere...", "sp_key": "AQAYourSpKeyValueHere..."}'
```

```python
import os
import json

# Load from environment
cookies_str = os.getenv('SPOTIFY_COOKIES')
cookies = json.loads(cookies_str) if cookies_str else None

client = SpotifyClient(cookies=cookies)
```

---

## Premium Features

### What You Get with Authentication

#### Enhanced Track Information
```python
# Authenticated client gets more metadata
track = client.get_track_info(url)
print(f"Popularity: {track.get('popularity', 'N/A')}")
print(f"Explicit: {track.get('explicit', 'N/A')}")
print(f"Markets: {track.get('available_markets', [])}")
```

#### Access to Private Playlists
```python
# Access your private playlists
private_playlist = client.get_playlist_info("https://open.spotify.com/playlist/your_private_playlist")
```

#### Higher Rate Limits
```python
# Authenticated requests have higher rate limits
import asyncio

async def bulk_extract():
    urls = [...]  # List of track URLs
    
    # Process more URLs faster with authentication
    tasks = [client.get_track_info(url) for url in urls]
    tracks = await asyncio.gather(*tasks)
    
    return tracks
```

#### Premium-Only Content
```python
# Some tracks are only available to premium users
premium_track = client.get_track_info("https://open.spotify.com/track/premium_track_id")
# Will work with authentication, fail without
```

---

## Troubleshooting

### Common Authentication Issues

#### 1. Invalid Cookies

**Problem**: Authentication fails with valid-looking cookies

**Solution**:
```python
# Check cookie validity
def test_authentication(cookies):
    try:
        client = SpotifyClient(cookies=cookies)
        # Try a simple authenticated request
        result = client.get_user_profile()  # This requires authentication
        print("✅ Authentication successful")
        return True
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

# Test your cookies
cookies = {'sp_dc': 'your_sp_dc_value'}
test_authentication(cookies)
```

#### 2. Expired Cookies

**Problem**: Cookies worked before but now fail

**Solution**: Extract fresh cookies from your browser
```python
# Cookies typically expire after 1 year
# Re-extract if you get authentication errors
```

#### 3. Wrong Cookie Format

**Problem**: Cookies aren't being parsed correctly

**Solution**:
```python
# Ensure proper format
# ✅ Correct
cookies = {'sp_dc': 'AQB...'}

# ❌ Incorrect 
cookies = {'sp_dc': '"AQB..."'}  # Remove quotes
cookies = {'sp_dc': 'sp_dc=AQB...'}  # Remove key prefix
```

#### 4. Regional Restrictions

**Problem**: Content not available in your region

**Solution**:
```python
# Use proxy if content is geo-restricted
client = SpotifyClient(
    cookies=cookies,
    proxy="http://proxy.example.com:8080"  # Proxy in different region
)
```

### Debugging Authentication

```python
import logging

# Enable debug logging to see authentication attempts
logging.basicConfig(level=logging.DEBUG)

client = SpotifyClient(
    cookies=cookies,
    log_level="DEBUG"
)

# Check if cookies are being sent
track = client.get_track_info(url)
```

### Validation Script

```python
def validate_spotify_cookies(cookies):
    """Validate Spotify authentication cookies."""
    required_cookies = ['sp_dc']
    
    # Check format
    if isinstance(cookies, str):
        print("❌ Cookies should be a dictionary, not string")
        return False
    
    if not isinstance(cookies, dict):
        print("❌ Cookies must be a dictionary")
        return False
    
    # Check required cookies
    for cookie in required_cookies:
        if cookie not in cookies:
            print(f"❌ Missing required cookie: {cookie}")
            return False
        
        if not cookies[cookie]:
            print(f"❌ Empty value for cookie: {cookie}")
            return False
    
    # Check sp_dc format (should start with AQB)
    if not cookies['sp_dc'].startswith('AQB'):
        print("⚠️ sp_dc cookie format looks unusual")
    
    print("✅ Cookie format validation passed")
    return True

# Validate your cookies
cookies = {'sp_dc': 'AQBYourTokenHere...'}
validate_spotify_cookies(cookies)
```

---

## Security Best Practices

### Protecting Your Cookies

#### 1. Environment Variables
```python
import os

# Store cookies in environment variables, not in code
sp_dc = os.getenv('SPOTIFY_SP_DC')
sp_key = os.getenv('SPOTIFY_SP_KEY')

cookies = {'sp_dc': sp_dc, 'sp_key': sp_key}
client = SpotifyClient(cookies=cookies)
```

#### 2. Encrypted Storage
```python
from cryptography.fernet import Fernet
import json
import os

def encrypt_cookies(cookies, key):
    """Encrypt cookies for secure storage."""
    f = Fernet(key)
    cookies_json = json.dumps(cookies)
    encrypted = f.encrypt(cookies_json.encode())
    return encrypted

def decrypt_cookies(encrypted_cookies, key):
    """Decrypt cookies for use."""
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_cookies)
    return json.loads(decrypted.decode())

# Generate and store key securely
key = Fernet.generate_key()
# Store key in environment or secure key management

# Encrypt cookies before storing
encrypted = encrypt_cookies(cookies, key)

# Decrypt when needed
cookies = decrypt_cookies(encrypted, key)
client = SpotifyClient(cookies=cookies)
```

#### 3. Cookie Rotation
```python
import time
from datetime import datetime, timedelta

class CookieManager:
    def __init__(self):
        self.cookies = None
        self.expires_at = None
    
    def get_fresh_cookies(self):
        """Get fresh cookies if current ones are old."""
        if not self.cookies or datetime.now() > self.expires_at:
            self.cookies = self.extract_new_cookies()
            # Refresh cookies monthly
            self.expires_at = datetime.now() + timedelta(days=30)
        
        return self.cookies
    
    def extract_new_cookies(self):
        """Extract new cookies from browser."""
        # Implement your cookie extraction logic
        pass

# Use cookie manager
cookie_manager = CookieManager()
client = SpotifyClient(cookies=cookie_manager.get_fresh_cookies())
```

### Production Security

```python
# Production-ready authentication setup
import os
import logging
from pathlib import Path

def get_secure_cookies():
    """Get cookies securely for production."""
    
    # Try environment variables first
    sp_dc = os.getenv('SPOTIFY_SP_DC')
    if sp_dc:
        return {'sp_dc': sp_dc, 'sp_key': os.getenv('SPOTIFY_SP_KEY', '')}
    
    # Try encrypted file
    cookie_file = Path('~/.spotify_cookies_encrypted').expanduser()
    if cookie_file.exists():
        key = os.getenv('COOKIE_ENCRYPTION_KEY')
        if key:
            return decrypt_cookies(cookie_file.read_bytes(), key.encode())
    
    # Log warning if no cookies found
    logging.warning("No Spotify cookies found - running without authentication")
    return None

# Use in production
cookies = get_secure_cookies()
client = SpotifyClient(cookies=cookies)
```

---

## Next Steps

Now that you have authentication set up:

1. 🎵 Access [premium content](../guide/basic-usage.md#premium-features)
2. 📥 Download [media files](../guide/media-downloads.md)
3. 📊 Extract [detailed metadata](../api/extractors.md)
4. 🔍 Handle [authentication errors](../guide/error-handling.md)

---

## Getting Help

If you need help with authentication:

1. Check the [FAQ](../faq.md) for common authentication issues
2. Review [troubleshooting guide](../troubleshooting.md)
3. Ask on [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
4. Report authentication bugs on [Issue Tracker](https://github.com/AliAkhtari78/SpotifyScraper/issues)