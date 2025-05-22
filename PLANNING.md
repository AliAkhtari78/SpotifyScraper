# SpotifyScraper Library Modernization Project

## 📊 Project Dashboard

| Project Information |  |
|---------------------|----------------------|
| **Original Repository** | [AliAkhtari78/SpotifyScraper](https://github.com/AliAkhtari78/SpotifyScraper) |
| **Current Version** | 1.0.5 |
| **Target Version** | 2.0.0 |
| **Overall Progress** | ![Progress](https://progress-bar.dev/60/?width=200&title=60%) |

## 🎯 Project Overview

The SpotifyScraper library, originally created in 2020, is being completely modernized to work with the current Spotify web player architecture. This project involves updating all scraping methods, improving code quality, adding new features, and ensuring backward compatibility.

Key objectives:
- Update scraping methods to work with Spotify's React-based interface
- Adopt modern Python practices (type hints, modular architecture)
- Add Selenium support for more robust scraping
- Improve error handling and logging
- Provide better documentation and examples

## 📝 Task Board

### Phase 1: Project Setup and Core Architecture
| ID | Task | Status | Assignee | Priority | Difficulty | Dependencies |
|----|------|--------|----------|----------|------------|--------------|
| 1.1 | Create Project Structure | ✅ Complete | LLM Agent 1 | High | Easy | None |
| 1.2 | Define Core Types | ✅ Complete | LLM Agent 1 | Medium | Medium | 1.1 |
| 1.3 | Define Constants | ✅ Complete | LLM Agent 1 | Medium | Easy | 1.1 |
| 1.4 | Implement Exception Hierarchy | ✅ Complete | LLM Agent 1 | Medium | Easy | 1.1 |
| 1.5 | Implement Configuration System | ✅ Complete | LLM Agent 1 | Medium | Medium | 1.3, 1.4 |

### Phase 2: Authentication and Browser Implementation
| ID | Task | Status | Assignee | Priority | Difficulty | Dependencies |
|----|------|--------|----------|----------|------------|--------------|
| 2.1 | Implement Session Management | ✅ Complete | LLM Agent 1 | High | Medium | 1.4, 1.5 |
| 2.2 | Implement Browser Interface | ✅ Complete | LLM Agent 1 | High | Easy | 1.4 |
| 2.3 | Implement Requests-based Browser | ✅ Complete | LLM Agent 1 | High | Medium | 2.2 |
| 2.4 | Implement Selenium-based Browser | ✅ Complete | LLM Agent 1 | Medium | Medium | 2.2 |
| 2.5 | Implement Browser Factory | ✅ Complete | LLM Agent 1 | Medium | Easy | 2.3, 2.4 |

### Phase 3: Data Parsing and Extraction
| ID | Task | Status | Assignee | Priority | Difficulty | Dependencies |
|----|------|--------|----------|----------|------------|--------------|
| 3.1 | Implement URL Utilities | ✅ Complete | LLM Agent 1 | High | Easy | 1.3, 1.4 |
| 3.2 | Implement JSON Parser | ✅ Complete | LLM Agent 1 | High | Hard | 1.2, 1.3, 1.4 |
| 3.3 | Implement Track Extractor | ✅ Complete | LLM Agent 1 | High | Medium | 2.5, 3.1, 3.2 |
| 3.4 | Implement Album Extractor | ✅ Complete | LLM Agent 2 | Medium | Medium | 2.5, 3.1, 3.2 |
| 3.5 | Implement Artist Extractor | ✅ Complete | LLM Agent 2 | Medium | Medium | 2.5, 3.1, 3.2 |
| 3.6 | Implement Playlist Extractor | ✅ Complete | LLM Agent 2 | Medium | Medium | 2.5, 3.1, 3.2 |

### Phase 4: Media Handling
| ID | Task | Status | Assignee | Priority | Difficulty | Dependencies |
|----|------|--------|----------|----------|------------|--------------|
| 4.1 | Implement Logging Utilities | ✅ Complete | LLM Agent 1 | Medium | Easy | 1.4, 1.5 |
| 4.2 | Implement Image Downloader | ✅ Complete | LLM Agent 1 | Medium | Medium | 2.5, 3.3 |
| 4.3 | Implement Audio Downloader | ✅ Complete | LLM Agent 1 | Medium | Medium | 2.5, 3.3, 4.2 |

### Phase 5: Client Implementation
| ID | Task | Status | Assignee | Priority | Difficulty | Dependencies |
|----|------|--------|----------|----------|------------|--------------|
| 5.1 | Implement Client Interface | 🔄 In Progress | LLM Agent 2 | High | Medium | 2.1, 2.5, 3.3-3.6, 4.2, 4.3 |
| 5.2 | Implement Package Initialization | ⏳ Pending | | High | Easy | 5.1 |

### Phase 6: Testing and Documentation
| ID | Task | Status | Assignee | Priority | Difficulty | Dependencies |
|----|------|--------|----------|----------|------------|--------------|
| 6.1 | Create Test Fixtures | ⏳ Pending | | Medium | Easy | 1.1 |
| 6.2 | Implement Unit Tests | ⏳ Pending | | Medium | Medium | 6.1 |
| 6.3 | Update Documentation | ✅ Complete | LLM Agent 2 | High | Easy | 5.2 |
| 6.4 | Update Packaging Configuration | ⏳ Pending | | High | Easy | 5.2 |

## 📈 Progress Tracking

| Phase | Progress | Tasks Completed | Total Tasks | Status |
|-------|----------|----------------|------------|--------|
| 1: Project Setup and Core Architecture | ![Progress](https://progress-bar.dev/100) | 5 | 5 | ✅ Complete |
| 2: Authentication and Browser Implementation | ![Progress](https://progress-bar.dev/100) | 5 | 5 | ✅ Complete |
| 3: Data Parsing and Extraction | ![Progress](https://progress-bar.dev/100) | 6 | 6 | ✅ Complete |
| 4: Media Handling | ![Progress](https://progress-bar.dev/100) | 3 | 3 | ✅ Complete |
| 5: Client Implementation | ![Progress](https://progress-bar.dev/50) | 1 | 2 | 🔄 In Progress |
| 6: Testing and Documentation | ![Progress](https://progress-bar.dev/25) | 1 | 4 | 🔄 In Progress |
| **Overall Progress** | ![Progress](https://progress-bar.dev/60) | **21** | **25** | **🔄 In Progress** |

## 📝 Implementation Details

### Phase 1: Project Setup and Core Architecture

#### Core Types (Task 1.2)
The core types are implemented in `src/spotify_scraper/core/types.py` using TypedDict classes for all data structures. This provides strong typing support for IDE autocompletion and helps with data validation. The types include:

- `TrackData`: Track information including name, artists, duration, etc.
- `AlbumData`: Album information including name, artist, release date, etc.
- `ArtistData`: Artist information including name, bio, popularity, etc.
- `PlaylistData`: Playlist information including name, tracks, description, etc.
- `ImageData`: Image information including URL, dimensions, etc.
- `LyricsData`: Lyrics information including synced lines, provider, etc.

#### Exception Hierarchy (Task 1.4)
A comprehensive exception hierarchy is implemented in `src/spotify_scraper/core/exceptions.py`, with specialized exceptions for different error types:

- `SpotifyScraperError`: Base exception for all errors
- `URLError`: Invalid or malformed URLs
- `ParsingError`: Errors during HTML or JSON parsing
- `ExtractionError`: Errors during data extraction
- `NetworkError`: Network communication errors
- `AuthenticationError`: Authentication failures
- `BrowserError`: Browser-related errors
- `MediaError`: Media processing errors

#### Configuration System (Task 1.5)
The configuration system is implemented in `src/spotify_scraper/core/config.py`, providing a flexible way to configure the library:

- Default values for all configuration options
- Environment variable support (with `SPOTIFY_SCRAPER_` prefix)
- Configuration file support (JSON format)
- Dynamic configuration updates

### Phase 2: Authentication and Browser Implementation

#### Session Management (Task 2.1)
Session management is implemented in `src/spotify_scraper/auth/session.py`, supporting different authentication methods:

- Cookie-based authentication (from browser sessions)
- Token-based authentication (using API tokens)
- Session persistence and renewal
- Headers and proxy support

#### Browser Abstraction (Tasks 2.2-2.5)
A flexible browser abstraction is implemented to support different methods of accessing Spotify:

- Abstract `Browser` interface in `src/spotify_scraper/browsers/base.py`
- `RequestsBrowser` implementation using the requests library
- `SeleniumBrowser` implementation using Selenium for dynamic content
- Browser factory for automatic selection based on requirements

### Phase 3: Data Parsing and Extraction

#### URL Utilities (Task 3.1)
URL utilities are implemented in `src/spotify_scraper/utils/url.py`, providing functions for:

- URL validation and cleaning
- URL type detection (track, album, artist, playlist)
- ID extraction
- Conversion between regular and embed URLs

#### JSON Parser (Task 3.2)
JSON parsing is implemented in `src/spotify_scraper/parsers/json_parser.py`, with functions for:

- Extracting JSON data from HTML
- Parsing different entity types (track, album, artist, playlist)
- Handling different Spotify page structures
- Fallback mechanisms for structure changes

#### Data Extractors (Tasks 3.3-3.6)
Extractors are implemented for different entity types:

- `TrackExtractor` in `src/spotify_scraper/extractors/track.py`
- `AlbumExtractor` in `src/spotify_scraper/extractors/album.py`
- `ArtistExtractor` in `src/spotify_scraper/extractors/artist.py`
- `PlaylistExtractor` in `src/spotify_scraper/extractors/playlist.py`

Each extractor provides methods for extracting data from URLs or IDs, with support for different page structures and fallback mechanisms.

### Phase 4: Media Handling

#### Logging Utilities (Task 4.1)
Logging utilities are implemented in `src/spotify_scraper/utils/logger.py`, providing:

- Configurable logging levels
- File and console logging
- Context manager for temporary log level changes
- Module-specific loggers

#### Media Downloaders (Tasks 4.2-4.3)
Media downloaders are implemented for images and audio:

- `ImageDownloader` in `src/spotify_scraper/media/image.py`
- `AudioDownloader` in `src/spotify_scraper/media/audio.py`

These classes provide methods for downloading cover images and preview audio, with support for different sizes, formats, and metadata embedding.

### Phase 5: Client Implementation

#### Client Interface (Task 5.1)
The client interface is implemented in `src/spotify_scraper/client.py`, providing a high-level API for:

- Extracting track, album, artist, and playlist information
- Downloading cover images and preview audio
- Fetching lyrics (with authentication)
- Session management

The client integrates all components into a cohesive API, with sensible defaults and backward compatibility.

## 🔍 Technical Notes

### Spotify Web Player Structure

The current Spotify web player uses a React-based architecture with data embedded in a `__NEXT_DATA__` script tag. This modernization project updates the scraping methods to work with this structure while maintaining backward compatibility with older structures.

### Authentication Methods

Two authentication methods are supported:

1. **Cookie-based Authentication**:
   - Uses cookies from a browser session
   - Simpler implementation but limited lifetime
   - Good for quick access but harder to automate

2. **Token-based Authentication**:
   - Uses Spotify API tokens
   - More reliable and longer-lasting
   - Requires proper OAuth flow
   - Tokens require periodic refreshing

### Fallback Mechanisms

The library implements multiple fallback mechanisms to handle different page structures and changes to the Spotify web player:

1. Modern structure with `__NEXT_DATA__` script tag
2. Legacy structure with `resource` script tag
3. Embed URL fallback when regular URLs fail
4. Error handling and retries for network issues

### Backward Compatibility

Backward compatibility is maintained through the `compat` module, which provides the same API as version 1.x:

```python
# Old way (v1.x)
from SpotifyScraper.scraper import Scraper, Request

# New backward compatibility
from spotify_scraper.compat import Scraper, Request
```

This allows existing code to work with minimal changes while benefiting from the improved internals.

## 📆 Next Steps

1. Complete the client implementation (Task 5.1)
2. Implement package initialization (Task 5.2)
3. Create test fixtures and implement unit tests (Tasks 6.1-6.2)
4. Update packaging configuration (Task 6.4)
5. Prepare for release on PyPI

## 🤝 Contributing

See the [Contributing Guide](CONTRIBUTING.md) for details on how to contribute to this project.
