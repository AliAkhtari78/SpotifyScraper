# SpotifyScraper Library Modernization Project

## 📊 Project Dashboard

| Project Information |  |
|---------------------|----------------------|
| **Original Repository** | [AliAkhtari78/SpotifyScraper](https://github.com/AliAkhtari78/SpotifyScraper) |
| **Current Version** | 1.0.5 |
| **Target Version** | 2.0.0 |
| **Overall Progress** | ![Progress](https://progress-bar.dev/0/?width=200&title=0%) |

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
| 1.1 | Create Project Structure | 🔄 In Progress | LLM Agent 1 | High | Easy | None |
| 1.2 | Define Core Types | ⏳ Pending | | Medium | Medium | 1.1 |
| 1.3 | Define Constants | ⏳ Pending | | Medium | Easy | 1.1 |
| 1.4 | Implement Exception Hierarchy | ⏳ Pending | | Medium | Easy | 1.1 |
| 1.5 | Implement Configuration System | ⏳ Pending | | Medium | Medium | 1.3, 1.4 |

### Phase 2: Authentication and Browser Implementation
| ID | Task | Status | Assignee | Priority | Difficulty | Dependencies |
|----|------|--------|----------|----------|------------|--------------|
| 2.1 | Implement Session Management | ⏳ Pending | | High | Medium | 1.4, 1.5 |
| 2.2 | Implement Browser Interface | ⏳ Pending | | High | Easy | 1.4 |
| 2.3 | Implement Requests-based Browser | ⏳ Pending | | High | Medium | 2.2 |
| 2.4 | Implement Selenium-based Browser | ⏳ Pending | | Medium | Medium | 2.2 |
| 2.5 | Implement Browser Factory | ⏳ Pending | | Medium | Easy | 2.3, 2.4 |

### Phase 3: Data Parsing and Extraction
| ID | Task | Status | Assignee | Priority | Difficulty | Dependencies |
|----|------|--------|----------|----------|------------|--------------|
| 3.1 | Implement URL Utilities | ⏳ Pending | | High | Easy | 1.3, 1.4 |
| 3.2 | Implement JSON Parser | ⏳ Pending | | High | Hard | 1.2, 1.3, 1.4 |
| 3.3 | Implement Track Extractor | ⏳ Pending | | High | Medium | 2.5, 3.1, 3.2 |
| 3.4 | Implement Album Extractor | ⏳ Pending | | Medium | Medium | 2.5, 3.1, 3.2 |
| 3.5 | Implement Artist Extractor | ⏳ Pending | | Medium | Medium | 2.5, 3.1, 3.2 |
| 3.6 | Implement Playlist Extractor | ⏳ Pending | | Medium | Medium | 2.5, 3.1, 3.2 |

### Phase 4: Media Handling
| ID | Task | Status | Assignee | Priority | Difficulty | Dependencies |
|----|------|--------|----------|----------|------------|--------------|
| 4.1 | Implement Logging Utilities | ⏳ Pending | | Medium | Easy | 1.4, 1.5 |
| 4.2 | Implement Image Downloader | ⏳ Pending | | Medium | Medium | 2.5, 3.3 |
| 4.3 | Implement Audio Downloader | ⏳ Pending | | Medium | Medium | 2.5, 3.3, 4.2 |

### Phase 5: Client Implementation
| ID | Task | Status | Assignee | Priority | Difficulty | Dependencies |
|----|------|--------|----------|----------|------------|--------------|
| 5.1 | Implement Client Interface | ⏳ Pending | | High | Medium | 2.1, 2.5, 3.3-3.6, 4.2, 4.3 |
| 5.2 | Implement Package Initialization | ⏳ Pending | | High | Easy | 5.1 |

### Phase 6: Testing and Documentation
| ID | Task | Status | Assignee | Priority | Difficulty | Dependencies |
|----|------|--------|----------|----------|------------|--------------|
| 6.1 | Create Test Fixtures | ⏳ Pending | | Medium | Easy | 1.1 |
| 6.2 | Implement Unit Tests | ⏳ Pending | | Medium | Medium | 6.1 |
| 6.3 | Update Documentation | ⏳ Pending | | High | Easy | 5.2 |
| 6.4 | Update Packaging Configuration | ⏳ Pending | | High | Easy | 5.2 |

## 📈 Progress Tracking

| Phase | Progress | Tasks Completed | Total Tasks | Status |
|-------|----------|----------------|------------|--------|
| 1: Project Setup and Core Architecture | ![Progress](https://progress-bar.dev/0) | 0 | 5 | 🔄 In Progress |
| 2: Authentication and Browser Implementation | ![Progress](https://progress-bar.dev/0) | 0 | 5 | ⏳ Waiting |
| 3: Data Parsing and Extraction | ![Progress](https://progress-bar.dev/0) | 0 | 6 | ⏳ Waiting |
| 4: Media Handling | ![Progress](https://progress-bar.dev/0) | 0 | 3 | ⏳ Waiting |
| 5: Client Implementation | ![Progress](https://progress-bar.dev/0) | 0 | 2 | ⏳ Waiting |
| 6: Testing and Documentation | ![Progress](https://progress-bar.dev/0) | 0 | 4 | ⏳ Waiting |
| **Overall Progress** | ![Progress](https://progress-bar.dev/0) | **0** | **25** | **🔄 In Progress** |

## 📑 Task Details

### Phase 1: Project Setup and Core Architecture

#### Task 1.1: Create Project Structure
- **Description**: Set up the directory structure for the modernized library
- **Steps**:
  1. Create all directories as per the project structure
  2. Initialize Python package files
  3. Set up packaging configuration (setup.py, pyproject.toml)
- **Acceptance Criteria**: All directories and basic __init__.py files are created
- **Files to Modify**: 
  - Create src/spotify_scraper/ and all subdirectories
  - Create tests/ and subdirectories
  - Create or update setup.py, pyproject.toml, setup.cfg
- **Dependencies**: None
- **Estimated Time**: 2 hours

#### Task 1.2: Define Core Types
- **Description**: Create TypedDict definitions for all data structures
- **Steps**:
  1. Analyze the JSON structure from Spotify embeds
  2. Define TypedDict classes for Track, Album, Artist, Playlist
  3. Include additional types for auth, configuration, etc.
- **Acceptance Criteria**: Complete types.py file with comprehensive TypedDict definitions
- **Files to Modify**: src/spotify_scraper/core/types.py
- **Dependencies**: 1.1
- **Estimated Time**: 3 hours
- **Reference**: See the JSON structure in `__NEXT_DATA__` from a Spotify embed page

#### Task 1.3: Define Constants
- **Description**: Define all constants used throughout the library
- **Steps**:
  1. Define URL patterns, selectors, and paths
  2. Define default values for configuration
  3. Define error messages
- **Acceptance Criteria**: Complete constants.py file with all necessary constants
- **Files to Modify**: src/spotify_scraper/core/constants.py
- **Dependencies**: 1.1
- **Estimated Time**: 2 hours
- **Reference**: Current Spotify URLs and selectors

#### Task 1.4: Implement Exception Hierarchy
- **Description**: Create a comprehensive exception hierarchy
- **Steps**:
  1. Define base exception class
  2. Define specific exception types for different error scenarios
  3. Include helpful error messages and context
- **Acceptance Criteria**: Complete exceptions.py file with all exception classes
- **Files to Modify**: src/spotify_scraper/core/exceptions.py
- **Dependencies**: 1.1
- **Estimated Time**: 2 hours

#### Task 1.5: Implement Configuration System
- **Description**: Create a flexible configuration system
- **Steps**:
  1. Define configuration class with default values
  2. Implement loading from file, environment, and parameters
  3. Support validation and serialization
- **Acceptance Criteria**: Complete config.py file with Config class
- **Files to Modify**: src/spotify_scraper/core/config.py
- **Dependencies**: 1.3, 1.4
- **Estimated Time**: 4 hours

### Phase 2: Authentication and Browser Implementation

#### Task 2.1: Implement Session Management
- **Description**: Create a session management system for authentication
- **Steps**:
  1. Implement cookie-based authentication
  2. Implement token-based authentication
  3. Support session persistence and renewal
- **Acceptance Criteria**: Complete session.py file with Session class
- **Files to Modify**: src/spotify_scraper/auth/session.py
- **Dependencies**: 1.4, 1.5
- **Estimated Time**: 5 hours
- **Reference**: Examine how Spotify's authentication works in the browser

#### Task 2.2: Implement Browser Interface
- **Description**: Define abstract browser interface
- **Steps**:
  1. Define Browser abstract base class
  2. Define methods for getting pages, extracting data, etc.
- **Acceptance Criteria**: Complete base.py file with Browser ABC
- **Files to Modify**: src/spotify_scraper/browsers/base.py
- **Dependencies**: 1.4
- **Estimated Time**: 2 hours

#### Task 2.3: Implement Requests-based Browser
- **Description**: Implement browser using requests library
- **Steps**:
  1. Implement RequestsBrowser class
  2. Support headers, cookies, proxies
  3. Implement retry and error handling
- **Acceptance Criteria**: Complete requests_browser.py file with RequestsBrowser class
- **Files to Modify**: src/spotify_scraper/browsers/requests_browser.py
- **Dependencies**: 2.2
- **Estimated Time**: 4 hours
- **Reference**: Current request.py file from old implementation

#### Task 2.4: Implement Selenium-based Browser
- **Description**: Implement browser using Selenium for dynamic content
- **Steps**:
  1. Implement SeleniumBrowser class
  2. Support headless mode, various options
  3. Implement waiting for content, etc.
- **Acceptance Criteria**: Complete selenium_browser.py file with SeleniumBrowser class
- **Files to Modify**: src/spotify_scraper/browsers/selenium_browser.py
- **Dependencies**: 2.2
- **Estimated Time**: 5 hours

#### Task 2.5: Implement Browser Factory
- **Description**: Create factory for browser selection and creation
- **Steps**:
  1. Implement create_browser function
  2. Support auto-detection and fallback
- **Acceptance Criteria**: Complete __init__.py file in browsers module with factory function
- **Files to Modify**: src/spotify_scraper/browsers/__init__.py
- **Dependencies**: 2.3, 2.4
- **Estimated Time**: 2 hours

### Phase 3: Data Parsing and Extraction

#### Task 3.1: Implement URL Utilities
- **Description**: Create utilities for URL manipulation
- **Steps**:
  1. Implement functions for URL validation, cleaning
  2. Implement functions for URL type detection
  3. Implement functions for URL conversion (regular/embed)
- **Acceptance Criteria**: Complete url.py file with URL utility functions
- **Files to Modify**: src/spotify_scraper/utils/url.py
- **Dependencies**: 1.3, 1.4
- **Estimated Time**: 3 hours
- **Reference**: Regular and embed URL patterns from Spotify

#### Task 3.2: Implement JSON Parser
- **Description**: Create parser for Spotify JSON data
- **Steps**:
  1. Implement extraction from HTML
  2. Implement parsing for different entity types
  3. Include fallbacks for different structures
- **Acceptance Criteria**: Complete json_parser.py file with parser functions
- **Files to Modify**: src/spotify_scraper/parsers/json_parser.py
- **Dependencies**: 1.2, 1.3, 1.4
- **Estimated Time**: 6 hours
- **Reference**: JSON structure in `__NEXT_DATA__` script tag

#### Task 3.3: Implement Track Extractor
- **Description**: Create extractor for track data
- **Steps**:
  1. Implement TrackExtractor class
  2. Support both regular and embed URLs
  3. Include fallbacks and error handling
- **Acceptance Criteria**: Complete track.py file with TrackExtractor class
- **Files to Modify**: src/spotify_scraper/extractors/track.py
- **Dependencies**: 2.5, 3.1, 3.2
- **Estimated Time**: 4 hours
- **Reference**: Current scraper.py get_track_url_info method

#### Task 3.4: Implement Album Extractor
- **Description**: Create extractor for album data
- **Steps**:
  1. Implement AlbumExtractor class
  2. Support track list extraction
  3. Include fallbacks and error handling
- **Acceptance Criteria**: Complete album.py file with AlbumExtractor class
- **Files to Modify**: src/spotify_scraper/extractors/album.py
- **Dependencies**: 2.5, 3.1, 3.2
- **Estimated Time**: 4 hours

#### Task 3.5: Implement Artist Extractor
- **Description**: Create extractor for artist data
- **Steps**:
  1. Implement ArtistExtractor class
  2. Support discography extraction
  3. Include fallbacks and error handling
- **Acceptance Criteria**: Complete artist.py file with ArtistExtractor class
- **Files to Modify**: src/spotify_scraper/extractors/artist.py
- **Dependencies**: 2.5, 3.1, 3.2
- **Estimated Time**: 4 hours

#### Task 3.6: Implement Playlist Extractor
- **Description**: Create extractor for playlist data
- **Steps**:
  1. Implement PlaylistExtractor class
  2. Support track list extraction with pagination
  3. Include fallbacks and error handling
- **Acceptance Criteria**: Complete playlist.py file with PlaylistExtractor class
- **Files to Modify**: src/spotify_scraper/extractors/playlist.py
- **Dependencies**: 2.5, 3.1, 3.2
- **Estimated Time**: 4 hours
- **Reference**: Current scraper.py get_playlist_url_info method

### Phase 4: Media Handling

#### Task 4.1: Implement Logging Utilities
- **Description**: Create utilities for logging
- **Steps**:
  1. Implement logging configuration
  2. Add context managers and helpers
- **Acceptance Criteria**: Complete logger.py file with logging utilities
- **Files to Modify**: src/spotify_scraper/utils/logger.py
- **Dependencies**: 1.4, 1.5
- **Estimated Time**: 2 hours

#### Task 4.2: Implement Image Downloader
- **Description**: Create downloader for images
- **Steps**:
  1. Implement ImageDownloader class
  2. Support different sizes and formats
  3. Include error handling and retries
- **Acceptance Criteria**: Complete image.py file with ImageDownloader class
- **Files to Modify**: src/spotify_scraper/media/image.py
- **Dependencies**: 2.5, 3.3
- **Estimated Time**: 3 hours
- **Reference**: Current scraper.py download_cover method

#### Task 4.3: Implement Audio Downloader
- **Description**: Create downloader for audio previews
- **Steps**:
  1. Implement AudioDownloader class
  2. Support metadata embedding
  3. Include error handling and retries
- **Acceptance Criteria**: Complete audio.py file with AudioDownloader class
- **Files to Modify**: src/spotify_scraper/media/audio.py
- **Dependencies**: 2.5, 3.3, 4.2
- **Estimated Time**: 4 hours
- **Reference**: Current scraper.py download_preview_mp3 method

### Phase 5: Client Implementation

#### Task 5.1: Implement Client Interface
- **Description**: Create main client interface
- **Steps**:
  1. Implement SpotifyClient class
  2. Integrate all components
  3. Provide high-level API
- **Acceptance Criteria**: Complete client.py file with SpotifyClient class
- **Files to Modify**: src/spotify_scraper/core/client.py
- **Dependencies**: 2.1, 2.5, 3.3, 3.4, 3.5, 3.6, 4.2, 4.3
- **Estimated Time**: 5 hours

#### Task 5.2: Implement Package Initialization
- **Description**: Create package initialization
- **Steps**:
  1. Define version and metadata
  2. Import and expose public API
  3. Set up backward compatibility
- **Acceptance Criteria**: Complete __init__.py file in root package
- **Files to Modify**: src/spotify_scraper/__init__.py
- **Dependencies**: 5.1
- **Estimated Time**: 2 hours

### Phase 6: Testing and Documentation

#### Task 6.1: Create Test Fixtures
- **Description**: Create test fixtures for unit tests
- **Steps**:
  1. Create sample HTML responses
  2. Create sample JSON data
  3. Set up pytest configuration
- **Acceptance Criteria**: Complete fixture files and conftest.py
- **Files to Modify**: tests/fixtures/html/*, tests/conftest.py
- **Dependencies**: 1.1
- **Estimated Time**: 3 hours
- **Reference**: Sample Spotify embed HTML

#### Task 6.2: Implement Unit Tests
- **Description**: Create unit tests for all components
- **Steps**:
  1. Write tests for each module
  2. Use fixtures and mocks
  3. Ensure good coverage
- **Acceptance Criteria**: Complete test files for all modules
- **Files to Modify**: tests/unit/*.py
- **Dependencies**: 6.1
- **Estimated Time**: 6 hours

#### Task 6.3: Update Documentation
- **Description**: Update all documentation
- **Steps**:
  1. Update README.md
  2. Update docstrings
  3. Create usage examples
- **Acceptance Criteria**: Complete documentation files
- **Files to Modify**: README.md, docs/*, all docstrings
- **Dependencies**: 5.2
- **Estimated Time**: 4 hours

#### Task 6.4: Update Packaging Configuration
- **Description**: Update packaging configuration
- **Steps**:
  1. Update setup.py
  2. Create pyproject.toml
  3. Update setup.cfg
- **Acceptance Criteria**: Complete packaging files
- **Files to Modify**: setup.py, pyproject.toml, setup.cfg
- **Dependencies**: 5.2
- **Estimated Time**: 2 hours

## 🔄 Task Completion Workflow

After completing each task, the LLM Agent should follow this workflow:

1. **Self-review**:
   - Verify that the implementation meets all requirements
   - Check for errors, edge cases, and potential bugs
   - Ensure code is well-documented and follows best practices

2. **Implementation Report**:
   - Update the Task Board with the new status
   - Provide a detailed completion report in the comments
   - Update the Progress Tracking section

3. **Next Steps**:
   - Identify and assign the next tasks that can be started
   - Update dependencies as needed

### Task Completion Report Template

```markdown
## Task X.Y Completion Report

**Task**: [Task Name]

**Status**: ✅ Complete / ⚠️ Partially Complete / ❌ Incomplete

**Implementation Summary**:
[Brief description of what was implemented]

**Challenges and Decisions**:
[Any challenges faced and design decisions made]

**Open Questions**:
[Any questions or issues that need clarification]

**Next Tasks**:
[List of tasks that can be started next]

**Updated Files**:
- [List of files modified]
```

## 📚 Technical Reference

### Modern Spotify Web Player Structure

The current Spotify web player uses a React-based architecture with data embedded in a `__NEXT_DATA__` script tag:

```html
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "state": {
        "data": {
          "entity": {
            "type": "track",
            "name": "Track Name",
            "uri": "spotify:track:ID",
            "artists": [
              {
                "name": "Artist Name",
                "uri": "spotify:artist:ID"
              }
            ],
            "duration": 123456,
            "audioPreview": {
              "url": "https://p.scdn.co/mp3-preview/..."
            },
            "visualIdentity": {
              "image": [
                {
                  "url": "https://image-cdn-ak.spotifycdn.com/...",
                  "maxHeight": 300,
                  "maxWidth": 300
                }
              ]
            }
          }
        },
        "settings": {
          "session": {
            "accessToken": "...",
            "accessTokenExpirationTimestampMs": 1234567890
          }
        }
      }
    }
  }
}
</script>
```

### Authentication Options

1. **Cookie-based Authentication**:
   - Uses cookies from a browser session
   - Simpler implementation but limited lifetime
   - Good for quick access but harder to automate

2. **Token-based Authentication**:
   - Uses Spotify API tokens
   - More reliable and longer-lasting
   - Requires proper OAuth flow
   - Tokens require periodic refreshing

### URL Conversion Methods

Regular Spotify URLs can be converted to embed URLs for more reliable data extraction:

| Type | Regular URL | Embed URL |
|------|------------|-----------|
| Track | `https://open.spotify.com/track/ID` | `https://open.spotify.com/embed/track/ID` |
| Album | `https://open.spotify.com/album/ID` | `https://open.spotify.com/embed/album/ID` |
| Artist | `https://open.spotify.com/artist/ID` | `https://open.spotify.com/embed/artist/ID` |
| Playlist | `https://open.spotify.com/playlist/ID` | `https://open.spotify.com/embed/playlist/ID` |

### Backward Compatibility Plan

To maintain backward compatibility with v1.x:

```python
# Old way (v1.x)
from SpotifyScraper.scraper import Scraper, Request

request = Request().request()
track_info = Scraper(session=request).get_track_url_info(url='...')

# New way (v2.x) will use:
from spotify_scraper import SpotifyClient

client = SpotifyClient()
track_info = client.get_track(url='...')

# But will also support legacy interface:
from spotify_scraper.compat import Scraper, Request

request = Request().request()
track_info = Scraper(session=request).get_track_url_info(url='...')
```
