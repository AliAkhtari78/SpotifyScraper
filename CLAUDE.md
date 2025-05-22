# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Installation
```bash
# Development install with all dependencies
pip install -e ".[dev]"

# Basic install for users
pip install -e .
```

### Testing
```bash
# Run tests with pytest
pytest

# Run tests with coverage
pytest --cov=spotify_scraper

# Run a single test file
pytest tests/unit/test_track_extractor.py

# Run tests in isolated environments (though tox.ini only has py36)
tox
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Run linting
flake8 src/ tests/

# Type checking
mypy src/

# Additional linting
pylint src/
```

### Build
```bash
# Traditional build
python setup.py build

# Modern build
python -m build
```

## High-Level Architecture

The SpotifyScraper library uses a modular architecture designed to extract data from Spotify's modern React-based web interface.

### Core Components

1. **Browser Abstraction Layer** (`src/spotify_scraper/browsers/`)
   - Provides a unified interface for web requests
   - Two implementations: `RequestsBrowser` (lightweight) and `SeleniumBrowser` (for complex scenarios)
   - Factory pattern for browser creation based on requirements

2. **Extractors** (`src/spotify_scraper/extractors/`)
   - Specialized classes for each Spotify entity type (track, album, artist, playlist)
   - Each extractor knows how to parse the specific data structure for its entity
   - Uses the JSON parser to extract data from Spotify's `__NEXT_DATA__` script tag

3. **JSON Parser** (`src/spotify_scraper/parsers/json_parser.py`)
   - Extracts structured data from Spotify's React-based pages
   - Handles the complex nested structure of Spotify's data
   - Provides graceful fallbacks for missing fields

4. **Media Handlers** (`src/spotify_scraper/media/`)
   - `AudioDownloader`: Downloads preview MP3s with metadata embedding
   - `ImageDownloader`: Downloads cover art in various sizes
   - Both support custom filenames and paths

5. **Client Interface** (`src/spotify_scraper/core/client.py`)
   - High-level API that coordinates all components
   - Handles URL validation, browser selection, and data extraction
   - Provides convenience methods for common operations

### Data Flow

1. User provides a Spotify URL to the client
2. URL utilities validate and parse the URL to extract entity type and ID
3. Browser fetches the page content (with optional authentication)
4. JSON parser extracts the `__NEXT_DATA__` data from the page
5. Appropriate extractor processes the raw data into structured format
6. Client optionally downloads media (preview audio, cover images)
7. Structured data is returned to the user

### Key Design Patterns

- **Strategy Pattern**: Different browser implementations for different use cases
- **Factory Pattern**: Browser creation based on authentication needs
- **Template Method**: Base extractor defines common behavior, subclasses specialize
- **Type Safety**: Extensive use of TypedDict for all data structures

### Important Notes

- The library is currently at version 2.0.0, a major rewrite from 1.x
- Backward compatibility is maintained through the `compat` module
- The project is approximately 60% complete according to PLANNING.md
- Authentication support allows access to additional content (e.g., lyrics)
- The library handles Spotify's React-based architecture by parsing the `__NEXT_DATA__` JSON