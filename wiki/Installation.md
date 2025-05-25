# Installation Guide

## Prerequisites

Before installing SpotifyScraper, ensure you have:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (usually comes with Python)
- **Internet connection** for downloading packages

You can verify your Python installation:
```bash
python --version  # Should show Python 3.8+
pip --version     # Should show pip version
```

## Installation Methods

### Method 1: Install from PyPI (Recommended)

The easiest way to install SpotifyScraper is via pip:

```bash
pip install spotifyscraper
```

To upgrade to the latest version:
```bash
pip install --upgrade spotifyscraper
```

### Method 2: Install from GitHub

For the latest development version:

```bash
# Clone the repository
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper

# Install in development mode
pip install -e .
```

### Method 3: Install from Source Distribution

```bash
# Download and extract the source
wget https://github.com/AliAkhtari78/SpotifyScraper/archive/master.zip
unzip master.zip
cd SpotifyScraper-master

# Install
python setup.py install
```

## Optional Dependencies

### For Selenium Support

If you need JavaScript rendering (for some dynamic content):

```bash
pip install spotifyscraper[selenium]
```

You'll also need a WebDriver:
- **Chrome**: [ChromeDriver](https://chromedriver.chromium.org/)
- **Firefox**: [GeckoDriver](https://github.com/mozilla/geckodriver/releases)

### For MP3 Metadata Support

To embed cover art in downloaded MP3 files:

```bash
pip install eyeD3
```

### For Development

If you're contributing to SpotifyScraper:

```bash
pip install spotifyscraper[dev]
# or
pip install -r requirements-dev.txt
```

## Verification

After installation, verify everything is working:

```python
>>> import spotify_scraper
>>> spotify_scraper.__version__
'2.0.0'

>>> from spotify_scraper import SpotifyClient
>>> client = SpotifyClient()
>>> print("Installation successful!")
```

## Virtual Environment (Recommended)

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv spotify_env

# Activate it
# On Windows:
spotify_env\Scripts\activate
# On macOS/Linux:
source spotify_env/bin/activate

# Install SpotifyScraper
pip install spotifyscraper
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'spotify_scraper'**
   - Ensure you've installed the package: `pip install spotifyscraper`
   - Check you're in the right environment: `pip list | grep spotify`

2. **SSL Certificate errors**
   - Update certificates: `pip install --upgrade certifi`
   - Or use: `pip install --trusted-host pypi.org spotifyscraper`

3. **Permission denied errors**
   - Use `pip install --user spotifyscraper`
   - Or use sudo (Linux/macOS): `sudo pip install spotifyscraper`

4. **Version conflicts**
   - Create a fresh virtual environment
   - Or use: `pip install --force-reinstall spotifyscraper`

### Getting Help

If you encounter issues:
1. Check the [FAQ](FAQ)
2. Search [existing issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
3. Create a [new issue](https://github.com/AliAkhtari78/SpotifyScraper/issues/new) with:
   - Python version (`python --version`)
   - SpotifyScraper version (`pip show spotifyscraper`)
   - Full error message
   - Steps to reproduce

## Next Steps

Once installed, check out:
- [Quick Start Guide](Quick-Start) - Get up and running quickly
- [API Reference](API-Reference) - Detailed API documentation
- [Examples](Examples) - Code examples and use cases