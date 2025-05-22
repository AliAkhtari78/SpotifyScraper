# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-05-22

### 🚀 Major Release - Complete Modernization

This is a major release that completely modernizes the SpotifyScraper library with breaking changes for better performance, security, and maintainability.

### ✨ Added

- **Modern Architecture**: Complete rewrite with modular, type-hinted code structure
- **Multi-Browser Support**: Both requests-based and Selenium browser backends
- **Enhanced Client API**: New `SpotifyClient` class with simplified, intuitive interface
- **Comprehensive Type Support**: Full TypeScript-style type hints for better IDE support
- **Advanced Configuration**: Flexible configuration system with environment variable support
- **Media Downloads**: Built-in support for downloading preview audio and cover images
- **Session Management**: Robust authentication and session handling
- **Error Handling**: Comprehensive exception hierarchy with detailed error messages
- **Logging System**: Configurable logging with multiple output options
- **Performance Optimizations**: Async support and connection pooling
- **Security Enhancements**: Updated to latest security standards

### 🔧 Updated Dependencies

- **lxml**: Updated from 4.5.0 → 5.4.0 (Python 3.12 compatibility)
- **beautifulsoup4**: Updated from 4.9.0 → 4.13.0
- **requests**: Updated from 2.23.0 → 2.32.3 (security fixes)
- **urllib3**: Updated from 1.25.9 → 2.4.0 (HTTP/2 support)
- **selenium**: Added support for 4.30.0+ (modern WebDriver)
- **PyYAML**: Updated from 5.3.1 → 6.0.1 (security fixes)

### 🛠️ Technical Improvements

- **Python 3.8-3.12 Support**: Full compatibility across modern Python versions
- **CI/CD Pipeline**: Modern GitHub Actions workflow with matrix testing
- **Package Structure**: PEP 518 compliant with both setup.py and pyproject.toml
- **Code Quality**: Black formatting, isort imports, mypy type checking
- **Documentation**: Comprehensive README with examples and API reference
- **Testing**: Improved test suite with pytest and coverage reporting

### 🔄 Migration from 1.x

#### New API (Recommended)
```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()
track = client.get_track("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
```

#### Backward Compatibility (Legacy)
```python
from spotify_scraper.compat import Scraper, Request

request = Request().request()
scraper = Scraper(session=request)
track = scraper.get_track_url_info(url='https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6')
```

### 💥 Breaking Changes

- **Minimum Python Version**: Now requires Python 3.8+ (dropped 3.6-3.7 support)
- **Import Structure**: Main classes moved to new locations
- **API Methods**: Some method names and signatures have changed
- **Configuration**: New configuration system replaces old approach
- **Dependencies**: Updated to modern versions with potential compatibility impacts

### 🐛 Fixed

- **Python 3.12 Compatibility**: Fixed lxml compilation errors on Python 3.12
- **Security Vulnerabilities**: Updated all dependencies to secure versions
- **Memory Leaks**: Fixed session and browser resource management
- **Unicode Handling**: Improved text encoding/decoding across all modules
- **Error Messages**: More descriptive error messages with troubleshooting hints
- **Rate Limiting**: Better handling of Spotify's anti-bot measures

### 🔒 Security

- **Dependency Updates**: All dependencies updated to latest secure versions
- **Input Validation**: Enhanced validation for all user inputs
- **Authentication**: Secure session token handling
- **Network Security**: Improved SSL/TLS certificate verification

### 📚 Documentation

- **Complete Rewrite**: New comprehensive documentation
- **Code Examples**: Extensive examples for all major features
- **API Reference**: Detailed API documentation with type annotations
- **Migration Guide**: Step-by-step migration instructions from 1.x
- **Troubleshooting**: Common issues and solutions

### 🎯 Performance

- **Faster Requests**: Optimized HTTP requests with connection pooling
- **Memory Usage**: Reduced memory footprint through better resource management
- **Async Support**: Optional async/await support for concurrent operations
- **Caching**: Intelligent caching of commonly accessed data

## [1.0.5] - 2021-03-15

### Fixed
- Minor bug fixes and improvements
- Updated user agents for better compatibility

## [1.0.0] - 2020-01-15

### Added
- Initial release of SpotifyScraper
- Basic track, album, artist, and playlist extraction
- Support for downloading preview MP3s
- Simple web scraping with requests and BeautifulSoup

---

## Migration Notes

### From 1.x to 2.0

1. **Update Python Version**: Ensure you're using Python 3.8 or later
2. **Install New Version**: `pip install -U spotifyscraper`
3. **Update Imports**: Use new import structure (see examples above)
4. **Update Method Calls**: Some method names have changed for consistency
5. **Test Thoroughly**: Run your tests to ensure compatibility

### Recommended Upgrade Path

1. Test with new API in a separate environment
2. Update imports gradually
3. Migrate to new method signatures
4. Remove deprecated code
5. Enjoy improved performance and features!

For detailed migration assistance, see our [Migration Guide](docs/migration.md).
