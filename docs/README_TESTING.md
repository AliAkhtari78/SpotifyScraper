# Testing Documentation for SpotifyScraper

This document provides comprehensive guidance on testing SpotifyScraper, including running tests, writing new tests, and understanding the testing architecture.

## Table of Contents
- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Test Data and Fixtures](#test-data-and-fixtures)
- [Mocking and Stubbing](#mocking-and-stubbing)
- [Integration Testing](#integration-testing)
- [Performance Testing](#performance-testing)
- [CI/CD Testing](#cicd-testing)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

```bash
# Install development dependencies
pip install -e ".[dev]"

# Or install test dependencies only
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/spotify_scraper --cov-report=html

# Run specific test categories
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only
pytest -m "not slow"  # Skip slow tests
```

### Quick Test Verification

```bash
# Verify your setup with a quick test
python -m pytest tests/unit/test_client.py::TestSpotifyClient::test_init -v
```

---

## Test Structure

### Directory Layout

```
tests/
├── conftest.py              # Global pytest configuration and fixtures
├── unit/                    # Unit tests (isolated, fast)
│   ├── __init__.py
│   ├── test_client.py       # SpotifyClient tests
│   ├── extractors/          # Extractor module tests
│   │   ├── test_track.py
│   │   ├── test_album.py
│   │   ├── test_artist.py
│   │   └── test_playlist.py
│   ├── parsers/             # Parser module tests
│   │   └── test_json_parser.py
│   ├── media/               # Media handling tests
│   │   ├── test_downloader.py
│   │   └── test_audio.py
│   └── utils/               # Utility function tests
│       ├── test_url_parser.py
│       └── test_cache.py
├── integration/             # Integration tests (with external deps)
│   ├── test_end_to_end.py   # Complete workflow tests
│   ├── test_network.py      # Network-dependent tests
│   └── test_authentication.py # Auth flow tests
├── performance/             # Performance and load tests
│   ├── test_bulk_operations.py
│   └── test_memory_usage.py
├── fixtures/                # Test data and mock responses
│   ├── html/               # Sample HTML responses
│   ├── json/               # Sample JSON data
│   └── audio/              # Sample audio files
└── helpers/                 # Test utilities and helpers
    ├── mock_server.py       # Mock HTTP server
    └── test_utils.py        # Common test utilities
```

### Test Naming Conventions

```python
# Test file naming
test_[module_name].py        # Unit tests for a module
test_[feature_name]_integration.py  # Integration tests

# Test function naming
def test_[function_name]_[condition]_[expected_result]():
    # Examples:
    def test_get_track_info_valid_url_returns_track_data():
    def test_get_track_info_invalid_url_raises_invalid_url_error():
    def test_download_preview_no_preview_available_returns_none():
```

---

## Running Tests

### Basic Test Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_client.py

# Run specific test class
pytest tests/unit/test_client.py::TestSpotifyClient

# Run specific test method
pytest tests/unit/test_client.py::TestSpotifyClient::test_get_track_info

# Run tests matching pattern
pytest -k "test_track"
pytest -k "test_get and not test_get_album"
```

### Test Categories and Markers

```bash
# Run by markers (defined in pytest.ini)
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m "unit and not slow"     # Fast unit tests only
pytest -m network                 # Tests requiring internet
pytest -m authenticated           # Tests requiring authentication

# Run excluding categories
pytest -m "not integration"       # Skip integration tests
pytest -m "not slow"              # Skip slow tests
pytest -m "not network"           # Skip network-dependent tests
```

### Coverage Testing

```bash
# Run with coverage
pytest --cov=src/spotify_scraper

# Coverage with HTML report
pytest --cov=src/spotify_scraper --cov-report=html

# Coverage with specific threshold
pytest --cov=src/spotify_scraper --cov-fail-under=85

# Coverage for specific modules
pytest --cov=src/spotify_scraper.client --cov-report=term-missing
```

### Parallel Testing

```bash
# Install pytest-xdist for parallel execution
pip install pytest-xdist

# Run tests in parallel
pytest -n auto               # Auto-detect CPU count
pytest -n 4                  # Use 4 processes
pytest -n 2 tests/unit/      # Parallel unit tests only
```

---

## Test Categories

### Unit Tests

Fast, isolated tests that mock external dependencies:

```python
# tests/unit/test_client.py
import pytest
from unittest.mock import Mock, patch
from spotify_scraper import SpotifyClient
from spotify_scraper import InvalidURLError

class TestSpotifyClient:
    """Unit tests for SpotifyClient."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        self.client = SpotifyClient()
    
    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self.client, 'close'):
            self.client.close()
    
    @patch('spotify_scraper.client.requests.Session.get')
    def test_get_track_info_valid_url_returns_track_data(self, mock_get):
        """Test successful track info extraction."""
        # Arrange
        mock_response = Mock()
        mock_response.text = self.load_fixture('track_page.html')
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Act
        result = self.client.get_track_info('https://open.spotify.com/track/123')
        
        # Assert
        assert result is not None
        assert 'name' in result
        assert 'artists' in result
        mock_get.assert_called_once()
    
    def test_get_track_info_invalid_url_raises_error(self):
        """Test that invalid URLs raise appropriate error."""
        with pytest.raises(InvalidURLError):
            self.client.get_track_info('invalid-url')
    
    @staticmethod
    def load_fixture(filename):
        """Load test fixture file."""
        import os
        fixture_path = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'html', filename)
        with open(fixture_path, 'r') as f:
            return f.read()
```

### Integration Tests

Tests that verify interaction between components:

```python
# tests/integration/test_end_to_end.py
import pytest
from spotify_scraper import SpotifyClient

@pytest.mark.integration
class TestEndToEnd:
    """End-to-end integration tests."""
    
    def setup_method(self):
        """Set up integration test environment."""
        self.client = SpotifyClient()
        # Known stable test URLs
        self.test_track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        self.test_album_url = "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy"
    
    def teardown_method(self):
        """Clean up integration test environment."""
        self.client.close()
    
    @pytest.mark.network
    def test_full_track_extraction_workflow(self):
        """Test complete track extraction workflow."""
        # Extract track info
        track = self.client.get_track_info(self.test_track_url)
        
        assert track is not None
        assert 'id' in track
        assert 'name' in track
        assert 'artists' in track
        assert len(track['artists']) > 0
        
        # Verify we can download preview if available
        if track.get('preview_url'):
            preview_path = self.client.download_preview_mp3(
                self.test_track_url,
                path='/tmp/'
            )
            assert preview_path is not None
    
    @pytest.mark.network
    @pytest.mark.slow
    def test_bulk_extraction_performance(self):
        """Test bulk extraction performance."""
        import time
        
        urls = [self.test_track_url] * 5  # Test with 5 identical URLs
        
        start_time = time.time()
        results = []
        
        for url in urls:
            track = self.client.get_track_info(url)
            results.append(track)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert len(results) == len(urls)
        assert all(result is not None for result in results)
        assert duration < 30  # Should complete within 30 seconds
```

### Performance Tests

Tests that verify performance characteristics:

```python
# tests/performance/test_bulk_operations.py
import pytest
import time
import memory_profiler
from spotify_scraper import SpotifyClient

@pytest.mark.performance
class TestPerformance:
    """Performance tests for SpotifyScraper."""
    
    def setup_method(self):
        """Set up performance test environment."""
        self.client = SpotifyClient()
    
    def teardown_method(self):
        """Clean up performance test environment."""
        self.client.close()
    
    @pytest.mark.slow
    def test_bulk_track_extraction_speed(self):
        """Test speed of bulk track extraction."""
        # Use a playlist with known tracks
        playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
        
        start_time = time.time()
        
        playlist = self.client.get_playlist_info(playlist_url)
        track_count = min(10, len(playlist['tracks']['items']))  # Limit for testing
        
        for i, item in enumerate(playlist['tracks']['items'][:track_count]):
            if item['track']:
                track = self.client.get_track_info(item['track']['external_urls']['spotify'])
                assert track is not None
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        avg_time_per_track = duration / track_count
        assert avg_time_per_track < 3.0  # Should be less than 3 seconds per track
    
    @memory_profiler.profile
    def test_memory_usage_bulk_extraction(self):
        """Test memory usage during bulk extraction."""
        # This test uses memory_profiler to track memory usage
        track_urls = [
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        ] * 20
        
        tracks = []
        for url in track_urls:
            track = self.client.get_track_info(url)
            tracks.append(track)
        
        # Memory usage is tracked by the @memory_profiler.profile decorator
        assert len(tracks) == len(track_urls)
```

---

## Writing Tests

### Test Structure Template

```python
# Standard test structure
import pytest
from unittest.mock import Mock, patch, MagicMock
from spotify_scraper import SpotifyClient
from spotify_scraper import SpotifyScraperError

class TestYourFeature:
    """Test class for your feature."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = SpotifyClient()
        self.mock_data = self.create_mock_data()
    
    def teardown_method(self):
        """Clean up after each test method."""
        if hasattr(self.client, 'close'):
            self.client.close()
    
    def create_mock_data(self):
        """Create mock data for tests."""
        return {
            'track': {
                'id': 'test_track_id',
                'name': 'Test Track',
                'artists': [{'name': 'Test Artist'}]
            }
        }
    
    def test_feature_success_case(self):
        """Test successful operation."""
        # Arrange
        expected_result = {'name': 'Test Track'}
        
        # Act
        result = self.client.some_method('test_input')
        
        # Assert
        assert result == expected_result
    
    def test_feature_error_case(self):
        """Test error handling."""
        with pytest.raises(SpotifyScraperError):
            self.client.some_method('invalid_input')
    
    @pytest.mark.parametrize("input_value,expected_output", [
        ("input1", "output1"),
        ("input2", "output2"),
        ("input3", "output3"),
    ])
    def test_feature_multiple_inputs(self, input_value, expected_output):
        """Test with multiple input/output combinations."""
        result = self.client.some_method(input_value)
        assert result == expected_output
```

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("url,expected_type", [
    ("https://open.spotify.com/track/123", "track"),
    ("https://open.spotify.com/album/456", "album"),
    ("https://open.spotify.com/artist/789", "artist"),
    ("https://open.spotify.com/playlist/abc", "playlist"),
])
def test_url_parsing(url, expected_type):
    """Test URL parsing for different content types."""
    from spotify_scraper.utils.url_parser import parse_spotify_url
    
    result = parse_spotify_url(url)
    assert result['type'] == expected_type

@pytest.mark.parametrize("invalid_url", [
    "not-a-url",
    "https://example.com",
    "https://open.spotify.com/invalid/123",
    "",
    None,
])
def test_invalid_url_handling(invalid_url):
    """Test handling of invalid URLs."""
    from spotify_scraper import InvalidURLError
    from spotify_scraper.utils.url_parser import parse_spotify_url
    
    with pytest.raises(InvalidURLError):
        parse_spotify_url(invalid_url)
```

### Async Tests

```python
import pytest
import asyncio

@pytest.mark.asyncio
class TestAsyncFeatures:
    """Tests for async functionality."""
    
    async def test_async_track_extraction(self):
        """Test async track extraction."""
        from spotify_scraper import AsyncSpotifyClient
        
        async with AsyncSpotifyClient() as client:
            track = await client.get_track_info_async(
                "https://open.spotify.com/track/123"
            )
            assert track is not None
    
    async def test_concurrent_requests(self):
        """Test concurrent request handling."""
        from spotify_scraper import AsyncSpotifyClient
        
        urls = [
            "https://open.spotify.com/track/123",
            "https://open.spotify.com/track/456",
            "https://open.spotify.com/track/789",
        ]
        
        async with AsyncSpotifyClient() as client:
            tasks = [client.get_track_info_async(url) for url in urls]
            results = await asyncio.gather(*tasks)
            
            assert len(results) == len(urls)
            assert all(result is not None for result in results)
```

---

## Test Data and Fixtures

### Global Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
import json
import os
from pathlib import Path
from unittest.mock import Mock

@pytest.fixture(scope="session")
def test_data_dir():
    """Get test data directory path."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def sample_track_data(test_data_dir):
    """Load sample track data."""
    with open(test_data_dir / "json" / "track_data.json", 'r') as f:
        return json.load(f)

@pytest.fixture(scope="session")
def sample_album_data(test_data_dir):
    """Load sample album data."""
    with open(test_data_dir / "json" / "album_data.json", 'r') as f:
        return json.load(f)

@pytest.fixture
def mock_spotify_client():
    """Create a mock SpotifyClient."""
    client = Mock()
    client.get_track_info.return_value = {
        'id': 'test_track',
        'name': 'Test Track',
        'artists': [{'name': 'Test Artist'}]
    }
    return client

@pytest.fixture
def mock_requests_session():
    """Create a mock requests session."""
    session = Mock()
    
    # Mock successful response
    response = Mock()
    response.status_code = 200
    response.text = "<html>Mock HTML content</html>"
    session.get.return_value = response
    
    return session

@pytest.fixture(autouse=True)
def isolate_tests(tmp_path, monkeypatch):
    """Isolate tests by using temporary directories."""
    # Change to temporary directory
    monkeypatch.chdir(tmp_path)
    
    # Set temporary cache directory
    monkeypatch.setenv("SPOTIFY_SCRAPER_CACHE_DIR", str(tmp_path / "cache"))
```

### File-Based Fixtures

```python
# Loading HTML fixtures
@pytest.fixture
def track_page_html():
    """Load sample track page HTML."""
    fixture_path = Path(__file__).parent / "fixtures" / "html" / "track_page.html"
    with open(fixture_path, 'r') as f:
        return f.read()

# Creating fixtures directory structure
def create_test_fixtures():
    """Create test fixture files."""
    fixtures_dir = Path("tests/fixtures")
    
    # Create directories
    (fixtures_dir / "html").mkdir(parents=True, exist_ok=True)
    (fixtures_dir / "json").mkdir(parents=True, exist_ok=True)
    (fixtures_dir / "audio").mkdir(parents=True, exist_ok=True)
    
    # Create sample JSON data
    track_data = {
        "id": "test_track_id",
        "name": "Sample Track",
        "artists": [{"name": "Sample Artist", "id": "artist_id"}],
        "album": {"name": "Sample Album", "id": "album_id"},
        "duration_ms": 210000,
        "preview_url": "https://example.com/preview.mp3"
    }
    
    with open(fixtures_dir / "json" / "track_data.json", 'w') as f:
        json.dump(track_data, f, indent=2)
```

---

## Mocking and Stubbing

### Network Request Mocking

```python
import pytest
from unittest.mock import patch, Mock
from spotify_scraper import SpotifyClient

class TestNetworkMocking:
    """Tests with mocked network requests."""
    
    @patch('spotify_scraper.client.requests.Session.get')
    def test_track_extraction_with_mocked_response(self, mock_get):
        """Test track extraction with mocked HTTP response."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.load_sample_html()
        mock_get.return_value = mock_response
        
        client = SpotifyClient()
        
        # Act
        track = client.get_track_info("https://open.spotify.com/track/123")
        
        # Assert
        assert track is not None
        assert mock_get.called
        mock_get.assert_called_with(
            "https://open.spotify.com/track/123",
            headers=client.headers,
            timeout=client.timeout
        )
    
    @patch('spotify_scraper.client.requests.Session.get')
    def test_network_error_handling(self, mock_get):
        """Test network error handling."""
        from requests.exceptions import ConnectionError
        from spotify_scraper import NetworkError
        
        # Arrange
        mock_get.side_effect = ConnectionError("Connection failed")
        client = SpotifyClient()
        
        # Act & Assert
        with pytest.raises(NetworkError):
            client.get_track_info("https://open.spotify.com/track/123")
    
    def load_sample_html(self):
        """Load sample HTML for testing."""
        return """
        <html>
        <script id="__NEXT_DATA__" type="application/json">
        {"props": {"pageProps": {"state": {"data": {"entity": {
            "name": "Test Track",
            "uri": "spotify:track:123",
            "artists": [{"name": "Test Artist"}]
        }}}}}}
        </script>
        </html>
        """
```

### File System Mocking

```python
import pytest
from unittest.mock import patch, mock_open
from spotify_scraper import SpotifyClient

@patch('builtins.open', new_callable=mock_open, read_data='{"sp_dc": "test_cookie"}')
@patch('os.path.exists', return_value=True)
def test_cookie_file_loading(mock_exists, mock_file):
    """Test loading cookies from file."""
    client = SpotifyClient(cookie_file="cookies.json")
    
    # Verify file was opened
    mock_file.assert_called_with("cookies.json", 'r')
    
    # Verify cookies were loaded
    assert 'sp_dc' in client.cookies
```

### Time and Date Mocking

```python
import pytest
from unittest.mock import patch
from datetime import datetime
from spotify_scraper.utils import cache

@patch('spotify_scraper.utils.cache.datetime')
def test_cache_expiration(mock_datetime):
    """Test cache expiration logic."""
    # Mock current time
    mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
    
    cache_manager = cache.CacheManager(expiry_hours=24)
    
    # Add item to cache
    cache_manager.set("key", "value")
    
    # Advance time by 25 hours
    mock_datetime.now.return_value = datetime(2023, 1, 2, 13, 0, 0)
    
    # Item should be expired
    assert cache_manager.get("key") is None
```

---

## Integration Testing

### Real Network Tests

```python
@pytest.mark.integration
@pytest.mark.network
class TestRealNetwork:
    """Integration tests with real network requests."""
    
    def setup_method(self):
        """Set up integration test environment."""
        self.client = SpotifyClient()
        # Use stable, public tracks for testing
        self.stable_urls = {
            'track': "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",  # Daft Punk
            'album': "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy",  # Random Access Memories
            'artist': "https://open.spotify.com/artist/4tZwfgrHOc3mvqYlEYSvVi"  # Daft Punk
        }
    
    def teardown_method(self):
        """Clean up integration test environment."""
        self.client.close()
    
    @pytest.mark.slow
    def test_real_track_extraction(self):
        """Test extraction from real Spotify track."""
        track = self.client.get_track_info(self.stable_urls['track'])
        
        # Verify essential fields
        assert track is not None
        assert 'id' in track
        assert 'name' in track
        assert 'artists' in track
        assert len(track['artists']) > 0
        assert 'album' in track
        
        # Verify data types
        assert isinstance(track.get('name', 'Unknown'), str)
        assert isinstance(track['artists'], list)
        assert isinstance(track.get('duration_ms'), int)
    
    @pytest.mark.slow
    def test_real_download(self):
        """Test downloading real preview."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            preview_path = self.client.download_preview_mp3(
                self.stable_urls['track'],
                path=temp_dir
            )
            
            if preview_path:  # Only test if preview is available
                assert os.path.exists(preview_path)
                assert os.path.getsize(preview_path) > 1000  # At least 1KB
```

### Database Integration Tests

```python
@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests with database storage."""
    
    def setup_method(self):
        """Set up database for testing."""
        import sqlite3
        
        self.db_path = ":memory:"  # Use in-memory database for testing
        self.conn = sqlite3.connect(self.db_path)
        
        # Create test tables
        self.conn.execute("""
            CREATE TABLE tracks (
                id TEXT PRIMARY KEY,
                name TEXT,
                artist TEXT,
                album TEXT,
                duration_ms INTEGER
            )
        """)
        self.conn.commit()
    
    def teardown_method(self):
        """Clean up database."""
        self.conn.close()
    
    def test_track_storage_workflow(self):
        """Test complete track extraction and storage workflow."""
        from unittest.mock import Mock
        
        # Mock track extraction
        mock_client = Mock()
        mock_client.get_track_info.return_value = {
            'id': 'test_track',
            'name': 'Test Track',
            'artists': [{'name': 'Test Artist'}],
            'album': {'name': 'Test Album'},
            'duration_ms': 210000
        }
        
        # Extract and store track
        track_data = mock_client.get_track_info("https://open.spotify.com/track/123")
        
        self.conn.execute(
            "INSERT INTO tracks (id, name, artist, album, duration_ms) VALUES (?, ?, ?, ?, ?)",
            (
                track_data['id'],
                track_data.get('name', 'Unknown'),
                track_data['artists'][0]['name'],
                track_data['album']['name'],
                track_data['duration_ms']
            )
        )
        self.conn.commit()
        
        # Verify storage
        cursor = self.conn.execute("SELECT * FROM tracks WHERE id = ?", (track_data['id'],))
        stored_track = cursor.fetchone()
        
        assert stored_track is not None
        assert stored_track[1] == track_data.get('name', 'Unknown')  # name column
```

---

## Performance Testing

### Memory Usage Tests

```python
import pytest
import psutil
import gc
from spotify_scraper import SpotifyClient

@pytest.mark.performance
class TestMemoryUsage:
    """Memory usage performance tests."""
    
    def test_memory_leak_detection(self):
        """Test for memory leaks during repeated operations."""
        initial_memory = psutil.Process().memory_info().rss
        
        # Perform repeated operations
        for i in range(100):
            client = SpotifyClient()
            # Simulate work
            client.close()
            
            # Force garbage collection
            gc.collect()
        
        final_memory = psutil.Process().memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (less than 10MB)
        assert memory_increase < 10 * 1024 * 1024
    
    def test_bulk_operation_memory_efficiency(self):
        """Test memory efficiency during bulk operations."""
        import tracemalloc
        
        tracemalloc.start()
        
        client = SpotifyClient()
        
        # Simulate bulk processing
        urls = ["https://open.spotify.com/track/test"] * 50
        
        # Mock the actual extraction to focus on memory usage
        with patch.object(client, 'get_track_info') as mock_get:
            mock_get.return_value = {'id': 'test', 'name': 'Test Track'}
            
            tracks = []
            for url in urls:
                track = client.get_track_info(url)
                tracks.append(track)
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        client.close()
        
        # Peak memory usage should be reasonable
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 100  # Less than 100MB peak usage
```

### Response Time Tests

```python
import pytest
import time
from spotify_scraper import SpotifyClient

@pytest.mark.performance
class TestResponseTimes:
    """Response time performance tests."""
    
    def setup_method(self):
        """Set up performance test client."""
        self.client = SpotifyClient()
    
    def teardown_method(self):
        """Clean up performance test client."""
        self.client.close()
    
    @pytest.mark.slow
    def test_track_extraction_response_time(self):
        """Test track extraction response time."""
        url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        
        start_time = time.time()
        track = self.client.get_track_info(url)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Should complete within 5 seconds
        assert response_time < 5.0
        assert track is not None
    
    def test_cached_request_performance(self):
        """Test performance improvement with caching."""
        from unittest.mock import patch
        
        # Mock network request to control timing
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = Mock(text="<html>mock</html>", status_code=200)
            
            url = "https://open.spotify.com/track/test"
            
            # First request (should be slower due to "network")
            start_time = time.time()
            self.client.get_track_info(url)
            first_time = time.time() - start_time
            
            # Second request (should use cache)
            start_time = time.time()
            self.client.get_track_info(url)
            second_time = time.time() - start_time
            
            # Cached request should be significantly faster
            # (This assumes caching is implemented)
            if hasattr(self.client, '_cache'):
                assert second_time < first_time * 0.5
```

---

## CI/CD Testing

### GitHub Actions Configuration

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.8, 3.9, '3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=src/spotify_scraper --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v -m "not network"
      env:
        PYTEST_TIMEOUT: 300
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true

  network-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'  # Only run on push, not PR
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Run network-dependent tests
      run: |
        pytest tests/integration/ -v -m "network" --maxfail=3
      env:
        PYTEST_TIMEOUT: 600
```

### Test Configuration Files

```ini
# pytest.ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra 
    --strict-markers 
    --strict-config 
    --disable-warnings
    --tb=short
python_files = tests/*.py
python_classes = Test*
python_functions = test_*
testpaths = tests
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (with external dependencies)
    network: Tests requiring network access
    slow: Slow tests (> 10 seconds)
    performance: Performance tests
    authenticated: Tests requiring authentication
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
timeout = 300

# coverage configuration
[coverage:run]
source = src/spotify_scraper
omit = 
    */tests/*
    */test_*
    */__pycache__/*
    */site-packages/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
precision = 2
show_missing = True
```

---

## Troubleshooting

### Common Test Issues

#### 1. Import Errors

```python
# Problem: Module not found
ModuleNotFoundError: No module named 'spotify_scraper'

# Solution: Install in development mode
pip install -e .

# Or add src to Python path in conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
```

#### 2. Fixture Not Found

```python
# Problem: Fixture not recognized
@pytest.fixture
def my_fixture():
    return "test_data"

# Solution: Ensure fixture is in conftest.py or properly imported
# Move to conftest.py or import in test file
```

#### 3. Network Test Failures

```python
# Problem: Network tests failing intermittently
def test_with_retry():
    """Test with automatic retry on network failure."""
    import time
    import requests
    
    for attempt in range(3):
        try:
            # Your network test here
            client = SpotifyClient()
            result = client.get_track_info(url)
            assert result is not None
            break
        except requests.RequestException:
            if attempt == 2:  # Last attempt
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

#### 4. Slow Test Performance

```python
# Problem: Tests running too slowly

# Solution 1: Use markers to skip slow tests in development
pytest -m "not slow"

# Solution 2: Parallel execution
pip install pytest-xdist
pytest -n auto

# Solution 3: Mock expensive operations
@patch('spotify_scraper.client.SpotifyClient._make_request')
def test_fast_version(mock_request):
    mock_request.return_value = Mock(text="mock_html", status_code=200)
    # Test logic here
```

#### 5. Flaky Tests

```python
# Problem: Tests pass sometimes, fail other times

# Solution: Add retry decorator
import pytest

@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_sometimes_fails():
    # Test that might fail due to timing, network, etc.
    pass

# Or use manual retry logic
def test_with_manual_retry():
    for attempt in range(3):
        try:
            # Test logic
            break
        except AssertionError:
            if attempt == 2:
                raise
            time.sleep(1)
```

### Debugging Tests

```python
# Add debugging output
def test_with_debug():
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    client = SpotifyClient(log_level="DEBUG")
    result = client.get_track_info(url)
    
    # Add debug prints
    print(f"Result: {result}")
    
    assert result is not None

# Use pytest debugging features
pytest --pdb           # Drop into debugger on failure
pytest --pdb-trace     # Drop into debugger on start
pytest -s              # Don't capture output
pytest -vv             # Very verbose output
```

### Test Data Management

```python
# Managing test data versions
class TestDataManager:
    """Manage test data consistency."""
    
    def __init__(self):
        self.data_version = "v1.0"
        self.data_path = Path("tests/fixtures")
    
    def validate_test_data(self):
        """Ensure test data is up to date."""
        version_file = self.data_path / "version.txt"
        
        if not version_file.exists():
            self.update_test_data()
            return
        
        current_version = version_file.read_text().strip()
        if current_version != self.data_version:
            self.update_test_data()
    
    def update_test_data(self):
        """Update test data to current version."""
        # Logic to refresh test fixtures
        pass

# Use in conftest.py
@pytest.fixture(scope="session", autouse=True)
def ensure_test_data():
    """Ensure test data is current before running tests."""
    manager = TestDataManager()
    manager.validate_test_data()
```

---

## Next Steps

Now that you understand SpotifyScraper testing:

1. 🧪 Run the existing test suite to ensure everything works
2. 📝 Write tests for any new features you develop
3. 🔧 Set up CI/CD pipeline for automated testing
4. 📊 Monitor test coverage and improve as needed
5. 🚀 Contribute tests back to the project

---

## Getting Help

For testing-related questions:

1. 📖 Review the [contributing guide](contributing.md) for development setup
2. 💬 Ask on [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
3. 🐛 Report test issues on [GitHub Issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)
4. 📚 Check [pytest documentation](https://docs.pytest.org/) for advanced testing techniques