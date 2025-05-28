# Installation Guide

This guide covers all installation methods for SpotifyScraper.

## Requirements

- **Python:** 3.8 or higher
- **Operating System:** Windows, macOS, Linux, BSD
- **Memory:** 100MB minimum
- **Disk Space:** 50MB for full installation

## Installation Methods

### 🚀 Quick Install (Recommended)

```bash
pip install spotifyscraper
```

This installs the core library with essential dependencies.

### 📦 Installation Options

#### With Selenium Support
For JavaScript-heavy pages and advanced browser automation:

```bash
pip install "spotifyscraper[selenium]"
```

#### With Development Tools
For contributing or development work:

```bash
pip install "spotifyscraper[dev]"
```

Includes:
- pytest (testing framework)
- black (code formatter)
- flake8 (linter)
- mypy (type checker)
- pre-commit hooks

#### Full Installation
Everything included:

```bash
pip install "spotifyscraper[all]"
```

### 🐍 Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install SpotifyScraper
pip install spotifyscraper
```

### 📦 From Source

```bash
# Clone the repository
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper

# Install in development mode
pip install -e ".[dev]"
```

### 🐳 Using Docker

```bash
# Pull the image
docker pull aliakhtari78/spotifyscraper

# Run a command
docker run aliakhtari78/spotifyscraper track https://open.spotify.com/track/...
```

## Dependency Details

### Core Dependencies
- `requests` - HTTP library for web requests
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast XML/HTML parser
- `click` - CLI framework
- `rich` - Terminal formatting

### Optional Dependencies

#### Selenium Bundle
- `selenium` - Browser automation
- `webdriver-manager` - Automatic driver management

#### Development Bundle
- `pytest` - Testing framework
- `black` - Code formatter
- `flake8` - Style checker
- `mypy` - Type checker
- `coverage` - Code coverage

## Post-Installation

### Verify Installation

```bash
# Check version
spotify-scraper --version

# Run help
spotify-scraper --help

# Test with a track
spotify-scraper track https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
```

### Python Verification

```python
import spotify_scraper
print(spotify_scraper.__version__)
# Output: 2.0.19
```

## Selenium Setup

If using Selenium, you'll need a browser driver:

### Automatic Setup (Recommended)
The library uses `webdriver-manager` to automatically download drivers:

```python
from spotify_scraper import SpotifyClient

# Driver will be downloaded automatically
client = SpotifyClient(browser_type="selenium")
```

### Manual Setup
1. Download the appropriate driver:
   - [ChromeDriver](https://chromedriver.chromium.org/)
   - [GeckoDriver](https://github.com/mozilla/geckodriver/releases) (Firefox)

2. Add to PATH or specify location:
```python
client = SpotifyClient(
    browser_type="selenium",
    driver_path="/path/to/chromedriver"
)
```

## Troubleshooting

### Common Issues

#### 1. pip not found
```bash
# Install pip
python -m ensurepip --upgrade
```

#### 2. Permission denied
```bash
# Use user installation
pip install --user spotifyscraper
```

#### 3. SSL Certificate errors
```bash
# Upgrade certificates
pip install --upgrade certifi
```

#### 4. Incompatible Python version
```bash
# Check Python version
python --version

# Use pyenv to install Python 3.8+
pyenv install 3.11.0
pyenv global 3.11.0
```

### Platform-Specific Notes

#### Windows
- Use Command Prompt or PowerShell as Administrator
- Install Visual C++ Build Tools if compilation errors occur

#### macOS
- Install Xcode Command Line Tools: `xcode-select --install`
- Use Homebrew for Python: `brew install python@3.11`

#### Linux
- Install python3-dev: `sudo apt-get install python3-dev`
- Install build essentials: `sudo apt-get install build-essential`

## Upgrading

### Upgrade to Latest Version

```bash
pip install --upgrade spotifyscraper
```

### Check for Updates

```python
import requests
import spotify_scraper

response = requests.get("https://pypi.org/pypi/spotifyscraper/json")
latest_version = response.json()["info"]["version"]
current_version = spotify_scraper.__version__

if latest_version != current_version:
    print(f"Update available: {latest_version}")
```

## Uninstallation

```bash
pip uninstall spotifyscraper
```

## Next Steps

- 📖 Read the [Quick Start Guide](Quick-Start)
- 🎯 Check out [Examples](Examples)
- 📚 Browse the [API Reference](API-Reference)

---

Need help? Check our [FAQ](FAQ) or [open an issue](https://github.com/AliAkhtari78/SpotifyScraper/issues).