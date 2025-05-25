# Installation Guide

This guide covers all installation methods for SpotifyScraper, from basic setup to advanced configurations.

## Table of Contents
- [Requirements](#requirements)
- [Quick Install](#quick-install)
- [Installation Methods](#installation-methods)
- [Optional Dependencies](#optional-dependencies)
- [Platform-Specific Notes](#platform-specific-notes)
- [Troubleshooting](#troubleshooting)
- [Verifying Installation](#verifying-installation)

---

## Requirements

### System Requirements
- **Python**: 3.8 or higher (3.10+ recommended)
- **Memory**: 512MB RAM minimum
- **Storage**: 50MB for package and dependencies
- **Internet**: Required for downloading and operation

### Python Version Check
```bash
python --version
# or
python3 --version
```

If you need to install Python, visit [python.org](https://www.python.org/downloads/).

---

## Quick Install

### Basic Installation
```bash
pip install spotifyscraper
```

### Upgrade to Latest Version
```bash
pip install --upgrade spotifyscraper
```

### Specific Version
```bash
pip install spotifyscraper==2.0.0
```

---

## Installation Methods

### Method 1: pip (Recommended)

#### From PyPI
```bash
# Basic installation
pip install spotifyscraper

# With all optional dependencies
pip install spotifyscraper[all]

# User installation (if you don't have admin rights)
pip install --user spotifyscraper
```

#### From GitHub (Latest Development)
```bash
pip install git+https://github.com/AliAkhtari78/SpotifyScraper.git
```

### Method 2: pipenv

```bash
# Add to Pipfile
pipenv install spotifyscraper

# With dev dependencies
pipenv install --dev spotifyscraper[dev]
```

### Method 3: poetry

```bash
# Add to your project
poetry add spotifyscraper

# With specific extras
poetry add spotifyscraper[selenium,media]
```

### Method 4: conda

```bash
# Using conda-forge
conda install -c conda-forge spotifyscraper
```

### Method 5: From Source

```bash
# Clone the repository
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper

# Install in development mode
pip install -e .

# Install with all dependencies
pip install -e ".[all]"
```

---

## Optional Dependencies

SpotifyScraper offers several optional dependency groups for specific features:

### Selenium Support
For JavaScript-heavy pages and complex scenarios:
```bash
pip install spotifyscraper[selenium]
```

This installs:
- `selenium>=4.0.0`
- `webdriver-manager>=3.8.0`

### Enhanced Media Handling
For advanced audio and image processing:
```bash
pip install spotifyscraper[media]
```

This installs:
- `eyeD3>=0.9.0` - MP3 metadata handling
- `Pillow>=9.0.0` - Image processing

### Development Tools
For contributing to SpotifyScraper:
```bash
pip install spotifyscraper[dev]
```

This installs:
- `pytest>=7.0.0` - Testing framework
- `black>=22.0.0` - Code formatting
- `isort>=5.0.0` - Import sorting
- `mypy>=0.900` - Type checking
- `sphinx>=4.0.0` - Documentation

### All Features
Install everything:
```bash
pip install "spotifyscraper[all]"
```

---

## Platform-Specific Notes

### Windows

#### Installing on Windows 10/11
```powershell
# Using PowerShell
pip install spotifyscraper

# If pip is not in PATH
python -m pip install spotifyscraper
```

#### Common Windows Issues
1. **SSL Certificate Error**:
   ```bash
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org spotifyscraper
   ```

2. **Permission Error**:
   ```bash
   pip install --user spotifyscraper
   ```

### macOS

#### Installing on macOS
```bash
# Using Homebrew Python
brew install python3
pip3 install spotifyscraper

# Using system Python (not recommended)
pip install --user spotifyscraper
```

#### Apple Silicon (M1/M2) Notes
```bash
# Ensure you're using native Python
arch -arm64 pip install spotifyscraper
```

### Linux

#### Ubuntu/Debian
```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip

# Install SpotifyScraper
pip3 install spotifyscraper
```

#### Fedora/RHEL
```bash
# Install Python and pip
sudo dnf install python3 python3-pip

# Install SpotifyScraper
pip3 install spotifyscraper
```

#### Arch Linux
```bash
# Using pacman
sudo pacman -S python python-pip

# Install SpotifyScraper
pip install spotifyscraper
```

---

## Virtual Environments

### Why Use Virtual Environments?
Virtual environments isolate project dependencies and prevent conflicts.

### Using venv (Built-in)
```bash
# Create virtual environment
python -m venv spotify_env

# Activate it
# Windows
spotify_env\Scripts\activate
# macOS/Linux
source spotify_env/bin/activate

# Install SpotifyScraper
pip install spotifyscraper

# Deactivate when done
deactivate
```

### Using virtualenv
```bash
# Install virtualenv
pip install virtualenv

# Create environment
virtualenv spotify_env

# Activate and install
source spotify_env/bin/activate  # or spotify_env\Scripts\activate on Windows
pip install spotifyscraper
```

### Using conda
```bash
# Create conda environment
conda create -n spotify python=3.10

# Activate environment
conda activate spotify

# Install SpotifyScraper
pip install spotifyscraper
```

---

## Docker Installation

### Using Official Docker Image
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN pip install spotifyscraper

COPY . .

CMD ["python", "your_script.py"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  spotify-scraper:
    build: .
    volumes:
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
```

---

## Troubleshooting

### Common Installation Issues

#### 1. pip: command not found
```bash
# Install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

#### 2. Permission Denied
```bash
# Use user installation
pip install --user spotifyscraper

# Or use sudo (not recommended)
sudo pip install spotifyscraper
```

#### 3. SSL/TLS Certificate Error
```bash
# Upgrade certificates
pip install --upgrade certifi

# Or bypass (not recommended for production)
pip install --index-url=https://pypi.org/simple/ --trusted-host pypi.org spotifyscraper
```

#### 4. Dependency Conflicts
```bash
# Install in isolated environment
python -m venv clean_env
source clean_env/bin/activate  # or clean_env\Scripts\activate on Windows
pip install spotifyscraper
```

#### 5. Slow Installation
```bash
# Use faster mirror
pip install -i https://pypi.douban.com/simple spotifyscraper  # China
pip install -i https://pypi.org/simple spotifyscraper  # Global
```

### Platform-Specific Issues

#### Windows: Microsoft Visual C++ Error
Download and install Microsoft C++ Build Tools from [visualstudio.microsoft.com](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

#### macOS: Xcode Command Line Tools
```bash
xcode-select --install
```

#### Linux: Missing Python Headers
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev

# Fedora/RHEL
sudo dnf install python3-devel
```

---

## Verifying Installation

### Basic Verification
```python
# Check if SpotifyScraper is installed
import spotify_scraper
print(spotify_scraper.__version__)
```

### Complete Verification Script
```python
#!/usr/bin/env python3
"""Verify SpotifyScraper installation."""

import sys

def verify_installation():
    """Check if SpotifyScraper is properly installed."""
    try:
        # Check basic import
        import spotify_scraper
        print(f"✅ SpotifyScraper {spotify_scraper.__version__} installed")
        
        # Check main components
        from spotify_scraper import SpotifyClient
        print("✅ SpotifyClient available")
        
        # Check optional dependencies
        try:
            import selenium
            print("✅ Selenium support available")
        except ImportError:
            print("ℹ️ Selenium not installed (optional)")
        
        try:
            import eyed3
            print("✅ Enhanced media support available")
        except ImportError:
            print("ℹ️ eyeD3 not installed (optional)")
        
        # Test basic functionality
        client = SpotifyClient()
        print("✅ Client initialization successful")
        
        print("\n🎉 SpotifyScraper is ready to use!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nPlease install with: pip install spotifyscraper")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if verify_installation() else 1)
```

Save this as `verify_spotify_scraper.py` and run:
```bash
python verify_spotify_scraper.py
```

---

## Next Steps

Now that you have SpotifyScraper installed:

1. 📖 Read the [Quick Start Guide](../examples/quickstart.md)
2. 🔧 Configure your [environment](configuration.md)
3. 💡 Explore [code examples](../examples/index.md)
4. 🚀 Build your first project!

---

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](../troubleshooting.md)
2. Search [existing issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
3. Ask on [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
4. Report bugs on [Issue Tracker](https://github.com/AliAkhtari78/SpotifyScraper/issues/new)