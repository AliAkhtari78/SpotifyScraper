# Contributing to SpotifyScraper Development

This guide covers how to contribute to the SpotifyScraper project, set up a development environment, and understand our development workflow.

## Table of Contents
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Organization](#code-organization)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Development Tools](#development-tools)

---

## Development Setup

### Prerequisites

Ensure you have the required tools installed:

- **Python 3.8+** (3.10+ recommended)
- **Git** for version control
- **Make** for running development tasks
- **Node.js** (optional, for documentation)

### Clone and Setup

```bash
# Fork the repository on GitHub first, then clone your fork
git clone https://github.com/YOUR_USERNAME/SpotifyScraper.git
cd SpotifyScraper

# Add upstream repository
git remote add upstream https://github.com/AliAkhtari78/SpotifyScraper.git

# Create development environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```

### Development Dependencies

The development installation includes:

```bash
# Core development tools
pytest>=7.0.0          # Testing framework
pytest-cov>=4.0.0      # Coverage reporting
pytest-mock>=3.10.0    # Mocking for tests

# Code quality tools
black>=22.0.0           # Code formatting
isort>=5.0.0           # Import sorting
flake8>=5.0.0          # Linting
mypy>=0.900            # Type checking
bandit>=1.7.0          # Security linting

# Documentation tools
sphinx>=4.0.0          # Documentation generation
sphinx-rtd-theme>=1.0.0 # Documentation theme
myst-parser>=0.18.0    # Markdown support in Sphinx

# Optional tools
pre-commit>=2.20.0     # Git hooks
tox>=3.25.0           # Multi-environment testing
```

### Verify Setup

```bash
# Run tests to verify setup
make test

# Check code style
make lint

# Build documentation
make docs

# Run all checks
make check-all
```

---

## Development Workflow

### Branch Management

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Keep your branch updated
git fetch upstream
git rebase upstream/master

# Push your branch
git push origin feature/your-feature-name
```

### Making Changes

1. **Write Tests First** (TDD approach recommended)
2. **Implement Changes** in small, focused commits
3. **Run Tests** continuously during development
4. **Update Documentation** for user-facing changes
5. **Check Code Quality** before submitting

### Pre-commit Hooks (Recommended)

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

The hooks will automatically:
- Format code with Black
- Sort imports with isort
- Run linting with flake8
- Check for security issues with bandit
- Validate commit messages

---

## Code Organization

### Project Structure

```
src/spotify_scraper/
├── __init__.py              # Package initialization
├── client.py                # Main SpotifyClient class
├── extractors/              # Data extraction modules
│   ├── __init__.py
│   ├── base.py             # Base extractor class
│   ├── track.py            # Track extraction
│   ├── album.py            # Album extraction
│   ├── artist.py           # Artist extraction
│   └── playlist.py         # Playlist extraction
├── media/                   # Media handling modules
│   ├── __init__.py
│   ├── downloader.py       # File download utilities
│   ├── audio.py            # Audio processing
│   └── images.py           # Image processing
├── utils/                   # Utility modules
│   ├── __init__.py
│   ├── url_parser.py       # URL parsing utilities
│   ├── cache.py            # Caching functionality
│   └── helpers.py          # General helpers
├── exceptions.py            # Custom exceptions
└── config.py               # Configuration management
```

### Coding Standards

#### Code Style

We use **Black** for code formatting:

```bash
# Format all code
black src/ tests/

# Check formatting
black --check src/ tests/
```

#### Import Organization

We use **isort** for import sorting:

```bash
# Sort imports
isort src/ tests/

# Check import sorting
isort --check-only src/ tests/
```

#### Type Hints

Use type hints for all public functions:

```python
from typing import Dict, List, Optional, Union

def get_track_info(self, url: str) -> Dict[str, Any]:
    """Get track information from Spotify URL.
    
    Args:
        url: Spotify track URL
        
    Returns:
        Dictionary containing track information
        
    Raises:
        InvalidURLError: If URL format is invalid
        NotFoundError: If track is not found
    """
    pass
```

#### Documentation Strings

Use Google-style docstrings:

```python
def extract_data(self, content: str, selector: str) -> Optional[str]:
    """Extract data from HTML content using CSS selector.
    
    Args:
        content: HTML content to parse
        selector: CSS selector string
        
    Returns:
        Extracted text content, or None if not found
        
    Raises:
        ParseError: If content cannot be parsed
        
    Example:
        >>> extractor = DataExtractor()
        >>> result = extractor.extract_data('<div>test</div>', 'div')
        >>> print(result)
        'test'
    """
    pass
```

### Architecture Guidelines

#### Single Responsibility

Each class should have a single, well-defined responsibility:

```python
# Good: Focused responsibility
class TrackExtractor:
    """Extracts track information from Spotify."""
    
    def extract_track_info(self, url: str) -> Dict[str, Any]:
        pass

# Avoid: Multiple responsibilities
class SpotifyHandler:  # Too broad
    def extract_track_info(self, url: str) -> Dict[str, Any]:
        pass
    
    def download_audio(self, url: str) -> str:
        pass
    
    def send_email_notification(self, message: str) -> None:
        pass
```

#### Dependency Injection

Use dependency injection for better testability:

```python
# Good: Dependencies injected
class TrackExtractor:
    def __init__(self, http_client: HTTPClient, cache: Cache):
        self.http_client = http_client
        self.cache = cache

# Avoid: Hard-coded dependencies
class TrackExtractor:
    def __init__(self):
        self.http_client = requests.Session()  # Hard to test
        self.cache = FileCache()  # Hard to mock
```

#### Error Handling

Follow the established error handling patterns:

```python
from spotify_scraper import SpotifyScraperError, NotFoundError

def extract_track_info(self, url: str) -> Dict[str, Any]:
    """Extract track information."""
    try:
        response = self._make_request(url)
        return self._parse_response(response)
    except requests.RequestException as e:
        raise NetworkError(f"Failed to fetch track data: {e}") from e
    except ValueError as e:
        raise ParseError(f"Failed to parse track data: {e}") from e
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_client.py
│   ├── extractors/
│   │   ├── test_track.py
│   │   └── test_album.py
│   └── utils/
│       └── test_url_parser.py
├── integration/             # Integration tests
│   ├── test_end_to_end.py
│   └── test_api_integration.py
├── fixtures/               # Test data
│   ├── track_response.json
│   └── album_response.json
└── conftest.py            # Pytest configuration
```

### Writing Tests

#### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from spotify_scraper.extractors.track import TrackExtractor
from spotify_scraper import NotFoundError

class TestTrackExtractor:
    """Test cases for TrackExtractor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.http_client = Mock()
        self.cache = Mock()
        self.extractor = TrackExtractor(self.http_client, self.cache)
    
    def test_extract_track_info_success(self):
        """Test successful track extraction."""
        # Arrange
        url = "https://open.spotify.com/track/123"
        mock_response = Mock()
        mock_response.json.return_value = {"name": "Test Track"}
        self.http_client.get.return_value = mock_response
        
        # Act
        result = self.extractor.extract_track_info(url)
        
        # Assert
        assert result["name"] == "Test Track"
        self.http_client.get.assert_called_once_with(url)
    
    def test_extract_track_info_not_found(self):
        """Test track extraction when track not found."""
        # Arrange
        url = "https://open.spotify.com/track/nonexistent"
        self.http_client.get.side_effect = requests.HTTPError("404 Not Found")
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            self.extractor.extract_track_info(url)
    
    @pytest.mark.parametrize("invalid_url", [
        "not-a-url",
        "https://example.com",
        "https://open.spotify.com/invalid/123"
    ])
    def test_extract_track_info_invalid_url(self, invalid_url):
        """Test track extraction with invalid URLs."""
        with pytest.raises(InvalidURLError):
            self.extractor.extract_track_info(invalid_url)
```

#### Integration Tests

```python
import pytest
import requests
from spotify_scraper import SpotifyClient

class TestSpotifyClientIntegration:
    """Integration tests for SpotifyClient."""
    
    def setup_method(self):
        """Set up integration test client."""
        self.client = SpotifyClient()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.client.close()
    
    @pytest.mark.integration
    def test_get_track_info_real_track(self):
        """Test getting real track information."""
        # Use a known stable track for testing
        url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        
        track = self.client.get_track_info(url)
        
        assert "name" in track
        assert "artists" in track
        assert len(track["artists"]) > 0
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_bulk_extraction_performance(self):
        """Test bulk extraction performance."""
        urls = [
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
            # Add more test URLs
        ]
        
        import time
        start_time = time.time()
        
        results = []
        for url in urls:
            track = self.client.get_track_info(url)
            results.append(track)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert len(results) == len(urls)
        assert duration < 30  # Should complete within 30 seconds
```

### Test Data Management

#### Using Fixtures

```python
# conftest.py
import pytest
import json
from pathlib import Path

@pytest.fixture
def track_response_data():
    """Load track response test data."""
    fixture_path = Path(__file__).parent / "fixtures" / "track_response.json"
    with open(fixture_path, 'r') as f:
        return json.load(f)

@pytest.fixture
def mock_http_client():
    """Create mock HTTP client."""
    from unittest.mock import Mock
    return Mock()

@pytest.fixture
def spotify_client(mock_http_client):
    """Create SpotifyClient with mocked dependencies."""
    with patch('spotify_scraper.client.HTTPClient', return_value=mock_http_client):
        return SpotifyClient()
```

#### Test Categories

Use pytest markers to categorize tests:

```python
# pytest.ini or setup.cfg
[tool:pytest]
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests that take significant time
    network: Tests that require network access
    authenticated: Tests that require authentication
```

```bash
# Run specific test categories
pytest -m unit                    # Run only unit tests
pytest -m "not slow"              # Skip slow tests
pytest -m "integration and not network"  # Integration tests without network
```

### Code Coverage

```bash
# Run tests with coverage
pytest --cov=src/spotify_scraper --cov-report=html --cov-report=term

# Set coverage thresholds
pytest --cov=src/spotify_scraper --cov-fail-under=90
```

Coverage goals:
- **Overall**: 90%+ coverage
- **Core modules**: 95%+ coverage
- **Utility modules**: 85%+ coverage

---

## Documentation

### Docstring Standards

Follow Google-style docstrings with comprehensive examples:

```python
def get_album_info(self, url: str, include_tracks: bool = True) -> Dict[str, Any]:
    """Get comprehensive album information from Spotify.
    
    Extracts album metadata including tracks, artists, release information,
    and cover art URLs from a Spotify album URL.
    
    Args:
        url: Spotify album URL (e.g., 'https://open.spotify.com/album/123')
        include_tracks: Whether to include track listing in response.
            Defaults to True.
    
    Returns:
        Dictionary containing album information with the following structure:
        
        .. code-block:: python
        
            {
                'id': 'album_id',
                'name': 'Album Name',
                'artists': [{'name': 'Artist Name', 'id': 'artist_id'}],
                'release_date': '2023-01-01',
                'total_tracks': 12,
                'tracks': [...],  # If include_tracks=True
                'images': [{'url': 'cover_url', 'width': 640, 'height': 640}]
            }
    
    Raises:
        InvalidURLError: If the provided URL is not a valid Spotify album URL
        NotFoundError: If the album cannot be found or is not accessible
        NetworkError: If there's a network-related error during extraction
        ParseError: If the response cannot be parsed correctly
    
    Example:
        Basic album extraction:
        
        >>> client = SpotifyClient()
        >>> album = client.get_album_info('https://open.spotify.com/album/123')
        >>> print(album.get('name', 'Unknown'))
        'Album Name'
        >>> print(len(album['tracks']))
        12
        
        Extract album without tracks for faster response:
        
        >>> album = client.get_album_info(url, include_tracks=False)
        >>> print('tracks' in album)
        False
    
    Note:
        - Album extraction may take longer for albums with many tracks
        - Some albums may have regional restrictions
        - Premium-only albums require authentication
    
    See Also:
        :meth:`get_track_info`: Extract individual track information
        :meth:`get_artist_info`: Extract artist information
        :meth:`download_cover`: Download album cover art
    """
```

### Sphinx Documentation

#### Building Documentation

```bash
# Build HTML documentation
make docs

# Build and serve documentation locally
make docs-serve

# Clean documentation build
make docs-clean
```

#### Writing Documentation

Create documentation files in `docs/` directory:

```rst
# docs/advanced/custom-extractors.rst

Custom Extractors
=================

This guide shows how to create custom extractors for SpotifyScraper.

Creating a Custom Extractor
---------------------------

.. code-block:: python

    from spotify_scraper.extractors.base import BaseExtractor
    
    class CustomExtractor(BaseExtractor):
        """Custom data extractor."""
        
        def extract(self, url: str) -> Dict[str, Any]:
            """Extract custom data."""
            # Implementation here
            pass

API Reference
-------------

.. autoclass:: spotify_scraper.extractors.base.BaseExtractor
    :members:
    :undoc-members:
    :show-inheritance:
```

---

## Submitting Changes

### Pull Request Guidelines

1. **Fork and Branch**: Create a feature branch from `master`
2. **Descriptive Title**: Use clear, descriptive PR titles
3. **Detailed Description**: Explain what changes and why
4. **Link Issues**: Reference related issues using `Closes #123`
5. **Test Coverage**: Ensure new code is tested
6. **Documentation**: Update docs for user-facing changes

### PR Template

```markdown
## Summary
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Changes Made
- List of specific changes
- Include any new dependencies
- Mention any breaking changes

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated (if applicable)
- [ ] Tests added/updated
- [ ] No breaking changes (or marked as breaking change)
```

### Code Review Process

1. **Automated Checks**: CI must pass
2. **Peer Review**: At least one approval required
3. **Maintainer Review**: Final review by maintainer
4. **Merge**: Squash and merge (default)

### Commit Message Format

Use conventional commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(extractors): add playlist extraction support

- Implement PlaylistExtractor class
- Add support for public and private playlists
- Include comprehensive test coverage

Closes #45

fix(client): handle timeout errors gracefully

Previously, timeout errors would crash the client. Now they are
caught and wrapped in a TimeoutError exception.

Closes #67

docs: update authentication guide with cookie extraction methods

- Add browser-specific instructions
- Include security best practices
- Add troubleshooting section
```

---

## Development Tools

### Makefile Commands

```bash
# Development
make install-dev         # Install development dependencies
make test               # Run all tests
make test-unit          # Run unit tests only
make test-integration   # Run integration tests
make coverage           # Run tests with coverage

# Code Quality
make lint               # Run all linters
make format             # Format code with black and isort
make type-check         # Run mypy type checking
make security-check     # Run bandit security checks

# Documentation
make docs               # Build documentation
make docs-serve         # Serve documentation locally
make docs-check         # Check documentation for errors

# Release
make clean              # Clean build artifacts
make build              # Build package
make check-all          # Run all checks before release
```

### IDE Configuration

#### VS Code Settings

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests/"
    ]
}
```

#### PyCharm Configuration

1. Set Python interpreter to `./venv/bin/python`
2. Configure code style:
   - Tools → External Tools → Add Black formatter
   - Tools → External Tools → Add isort
3. Enable pytest as test runner
4. Configure type checking with mypy plugin

### Performance Profiling

```python
# profiling.py
import cProfile
import pstats
from spotify_scraper import SpotifyClient

def profile_extraction():
    """Profile track extraction performance."""
    client = SpotifyClient()
    
    urls = [
        "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
        # Add more URLs
    ]
    
    for url in urls:
        client.get_track_info(url)
    
    client.close()

if __name__ == "__main__":
    # Run profiler
    cProfile.run('profile_extraction()', 'profile_stats')
    
    # Analyze results
    stats = pstats.Stats('profile_stats')
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
```

```bash
# Run performance profiling
python profiling.py

# Memory profiling with memory_profiler
pip install memory_profiler
python -m memory_profiler your_script.py
```

---

## Next Steps

Now that you understand the development setup:

1. 🔧 Set up your [development environment](#development-setup)
2. 📝 Read the main [contributing guidelines](https://github.com/AliAkhtari78/SpotifyScraper/blob/master/CONTRIBUTING.md)
3. 🧪 Write your first [test](#testing-guidelines)
4. 📖 Check the [API reference](api/index.md)
5. 🚀 Submit your first [pull request](#submitting-changes)

---

## Getting Help

Development questions and support:

1. 💬 Join [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
2. 📋 Check [existing issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
3. 📧 Contact maintainers: [ali@aliakhtari.com](mailto:ali@aliakhtari.com)
4. 📚 Read the [full documentation](index.md)