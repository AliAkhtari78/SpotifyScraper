# WebDriver Manager Integration

SpotifyScraper now includes built-in support for [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager), which automatically downloads and manages browser drivers for Selenium.

## Overview

When using the Selenium browser backend, SpotifyScraper can automatically download the appropriate ChromeDriver or GeckoDriver (Firefox) for your system. This eliminates the need to manually download and configure drivers.

## Installation

To use webdriver-manager, install SpotifyScraper with the selenium extras:

```bash
pip install spotifyscraper[selenium]
```

This installs both Selenium and webdriver-manager.

## Usage

### Basic Usage (Automatic Driver Management)

By default, SpotifyScraper will use webdriver-manager when creating a Selenium browser:

```python
from spotify_scraper import SpotifyClient

# Drivers are automatically downloaded if needed
client = SpotifyClient(browser_type="selenium")
track = client.get_track_info("https://open.spotify.com/track/...")
client.close()
```

### Disable Automatic Driver Management

If you prefer to use system-installed drivers (e.g., chromedriver in PATH):

```python
client = SpotifyClient(
    browser_type="selenium",
    use_webdriver_manager=False  # Use system drivers
)
```

### Using Firefox

The Selenium browser supports both Chrome and Firefox:

```python
from spotify_scraper.browsers.selenium_browser import SeleniumBrowser

# Chrome with webdriver-manager (default)
browser = SeleniumBrowser(browser_name="chrome", use_webdriver_manager=True)

# Firefox with webdriver-manager
browser = SeleniumBrowser(browser_name="firefox", use_webdriver_manager=True)
```

## How It Works

1. **First Run**: When you first use Selenium with `use_webdriver_manager=True`, the appropriate driver is downloaded and cached locally.

2. **Cached Drivers**: Drivers are stored in:
   - Linux/Mac: `~/.wdm/`
   - Windows: `%USERPROFILE%\.wdm\`

3. **Automatic Updates**: webdriver-manager checks for driver updates and downloads new versions as needed.

4. **Fallback**: If webdriver-manager is not installed or fails, SpotifyScraper falls back to using system-installed drivers.

## Benefits

- **No Manual Setup**: No need to download drivers manually
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Always Up-to-Date**: Automatically uses the latest compatible driver
- **Cached for Speed**: Drivers are cached locally for fast startup

## Troubleshooting

### webdriver-manager Not Available

If you see a warning about webdriver-manager not being available:

```
WARNING - webdriver-manager requested but not available. Install with: pip install webdriver-manager
```

Install it with:
```bash
pip install webdriver-manager
```

Or reinstall SpotifyScraper with selenium extras:
```bash
pip install spotifyscraper[selenium]
```

### System Driver Fallback

If you prefer using system drivers or encounter issues with webdriver-manager:

1. Download the appropriate driver:
   - [ChromeDriver](https://chromedriver.chromium.org/)
   - [GeckoDriver (Firefox)](https://github.com/mozilla/geckodriver/releases)

2. Add the driver to your system PATH

3. Use SpotifyScraper with `use_webdriver_manager=False`:
   ```python
   client = SpotifyClient(
       browser_type="selenium",
       use_webdriver_manager=False
   )
   ```

## Example Code

```python
import logging
from spotify_scraper import SpotifyClient

# Enable logging to see driver downloads
logging.basicConfig(level=logging.INFO)

# Example 1: Default behavior (with webdriver-manager)
client = SpotifyClient(browser_type="selenium")
track = client.get_track_info("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT")
print(f"Track: {track['name']} by {track['artists'][0]['name']}")
client.close()

# Example 2: Explicitly enable webdriver-manager
client = SpotifyClient(
    browser_type="selenium",
    use_webdriver_manager=True
)

# Example 3: Use system drivers instead
client = SpotifyClient(
    browser_type="selenium",
    use_webdriver_manager=False
)

# Example 4: Direct browser usage with Firefox
from spotify_scraper.browsers.selenium_browser import SeleniumBrowser

browser = SeleniumBrowser(
    browser_name="firefox",
    use_webdriver_manager=True
)
content = browser.get_page_content("https://open.spotify.com")
browser.close()
```