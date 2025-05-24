# Changelog

All notable changes to SpotifyScraper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation with ReadTheDocs integration
- Advanced guides for scaling, performance optimization, and custom extractors
- Migration guide from v1.x to v2.0
- Extensive FAQ and troubleshooting sections

## [2.0.0] - 2024-01-15

### Added
- Complete rewrite with modern Python architecture
- Support for both embed and regular Spotify URLs
- Selenium browser option for JavaScript-heavy pages
- Comprehensive caching system with multiple backends
- CLI interface with rich command-line options
- Type hints throughout the codebase
- Extensive test coverage
- Configuration system with multiple sources
- Plugin architecture for extensibility
- Async support for concurrent operations

### Changed
- **BREAKING**: Renamed methods for consistency
  - `get_track_by_url()` → `get_track()`
  - `get_album_by_url()` → `get_album()`
  - `get_artist_by_url()` → `get_artist()`
  - `get_playlist_by_url()` → `get_playlist()`
- **BREAKING**: Unified data extraction from URL or ID
- Improved error handling with specific exception types
- Enhanced data extraction accuracy
- Better handling of embed URL data structures

### Fixed
- Album release date extraction with multiple date formats
- Artist extraction from embed URLs using subtitle field
- Playlist owner extraction from embed URLs
- Removed unnecessary fields from extracted data
- Config class export issue
- Missing ConfigurationError exception