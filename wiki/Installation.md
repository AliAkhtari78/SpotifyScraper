# Installation Guide

This guide will help you install SpotifyScraper on your system.

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection

## 🚀 Quick Installation

### Basic Installation

```bash
pip install spotifyscraper
```

### Installation with Optional Features

```bash
# With Selenium support for complex scenarios
pip install spotifyscraper[selenium]

# With enhanced media handling
pip install spotifyscraper[media]

# All features
pip install spotifyscraper[all]

# Development dependencies
pip install spotifyscraper[dev]
```

## 📦 Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install spotifyscraper
```

### Method 2: Install from GitHub

```bash
pip install git+https://github.com/AliAkhtari78/SpotifyScraper.git
```

### Method 3: Install from Source

```bash
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper
pip install -e .
```

## 🐳 Docker Installation

### Using Docker Hub

```bash
docker pull aliakhtari78/spotifyscraper:latest
```

### Building from Source

```bash
git clone https://github.com/AliAkhtari78/SpotifyScraper.git
cd SpotifyScraper
docker build -t spotifyscraper .
```

### Running with Docker

```bash
# Interactive shell
docker run -it spotifyscraper python

# Run a script
docker run -v $(pwd):/app spotifyscraper python /app/your_script.py
```

## 🔧 Virtual Environment Setup

It's recommended to use a virtual environment:

### Creating a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate

# Install SpotifyScraper
pip install spotifyscraper
```

## ✅ Verify Installation

```python
# Test installation
python -c "import spotify_scraper; print(spotify_scraper.__version__)"

# Should output: 2.0.0
```

## 🛠️ Platform-Specific Instructions

### Windows

1. Install Python from [python.org](https://python.org)
2. Open Command Prompt or PowerShell
3. Run: `pip install spotifyscraper`

### macOS

1. Install Python using Homebrew: `brew install python`
2. Open Terminal
3. Run: `pip3 install spotifyscraper`

### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip
pip3 install spotifyscraper

# Fedora
sudo dnf install python3 python3-pip
pip3 install spotifyscraper

# Arch Linux
sudo pacman -S python python-pip
pip install spotifyscraper
```

## 🔄 Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade spotifyscraper
```

## 🗑️ Uninstalling

To remove SpotifyScraper:

```bash
pip uninstall spotifyscraper
```

## ❓ Troubleshooting Installation

### Common Issues

1. **Permission Denied**
   ```bash
   pip install --user spotifyscraper
   ```

2. **SSL Certificate Error**
   ```bash
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org spotifyscraper
   ```

3. **Outdated pip**
   ```bash
   python -m pip install --upgrade pip
   ```

4. **Missing Dependencies**
   ```bash
   pip install --upgrade setuptools wheel
   ```

## 📚 Next Steps

- Read the [Quick Start Guide](Quick-Start)
- Explore [Basic Examples](Examples)
- Check the [API Reference](API-Reference)