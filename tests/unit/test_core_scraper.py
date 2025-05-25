"""Tests for core.scraper module."""

from typing import Any, Dict, Optional

import pytest

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import ScrapingError, URLError
from spotify_scraper.core.scraper import Scraper


class MockBrowser(Browser):
    """Mock browser for testing."""

    def __init__(self):
        super().__init__()
        self.closed = False

    def get_page_content(self, url: str) -> str:
        """Mock implementation of get_page_content."""
        return "<html><body>Mock content</body></html>"

    def get_json(self, url: str) -> Dict[str, Any]:
        """Mock implementation of get_json."""
        return {"status": "ok", "data": {}}

    def download_file(self, url: str, path: str) -> str:
        """Mock implementation of download_file."""
        return path

    def get_auth_token(self) -> Optional[str]:
        """Mock implementation of get_auth_token."""
        return None

    def close(self) -> None:
        """Mock implementation of close."""
        self.closed = True


class TestScraper:
    """Test Scraper class."""

    def test_init_with_browser(self):
        """Test initializing scraper with custom browser."""
        browser = MockBrowser()
        scraper = Scraper(browser=browser)

        assert scraper.browser is browser

    def test_init_with_log_level(self):
        """Test initializing scraper with custom log level."""
        browser = MockBrowser()

        # Valid log level
        scraper = Scraper(browser=browser, log_level="DEBUG")
        # Logger configuration happens internally

        # Invalid log level should default to INFO
        scraper = Scraper(browser=browser, log_level="INVALID")
        # Logger defaults to INFO internally

    def test_script_data_to_json_success(self):
        """Test converting script content to JSON."""
        script_content = '{"data": {"id": "123", "name": "Test"}}'

        result = Scraper._script_data_to_json(script_content)

        assert result == {"data": {"id": "123", "name": "Test"}}

    def test_script_data_to_json_invalid(self):
        """Test converting invalid script content to JSON."""
        script_content = "{invalid json content}"

        with pytest.raises(ScrapingError) as exc_info:
            Scraper._script_data_to_json(script_content)

        assert "Error parsing __NEXT_DATA__ JSON" in str(exc_info.value)

    def test_script_data_to_json_empty(self):
        """Test converting empty script content to JSON."""
        script_content = ""

        with pytest.raises(ScrapingError) as exc_info:
            Scraper._script_data_to_json(script_content)

        assert "Error parsing __NEXT_DATA__ JSON" in str(exc_info.value)

    def test_ms_to_readable_valid(self):
        """Test converting milliseconds to readable format."""
        # Test seconds only
        assert Scraper._ms_to_readable(30000) == "0:30"
        assert Scraper._ms_to_readable(45000) == "0:45"

        # Test minutes and seconds
        assert Scraper._ms_to_readable(90000) == "1:30"
        assert Scraper._ms_to_readable(270000) == "4:30"
        assert Scraper._ms_to_readable(605000) == "10:05"

        # Test hours
        assert Scraper._ms_to_readable(3600000) == "1:00:00"
        assert Scraper._ms_to_readable(5430000) == "1:30:30"
        assert Scraper._ms_to_readable(7265000) == "2:01:05"

    def test_ms_to_readable_invalid(self):
        """Test converting invalid milliseconds values."""
        # Negative values
        assert Scraper._ms_to_readable(-1000) == "0:00"

        # Non-integer values
        assert Scraper._ms_to_readable("not a number") == "0:00"
        assert Scraper._ms_to_readable(None) == "0:00"
        assert Scraper._ms_to_readable(3.14) == "0:00"

    def test_ms_to_readable_edge_cases(self):
        """Test edge cases for milliseconds conversion."""
        # Zero
        assert Scraper._ms_to_readable(0) == "0:00"

        # One second
        assert Scraper._ms_to_readable(1000) == "0:01"

        # 59 seconds
        assert Scraper._ms_to_readable(59000) == "0:59"

        # 59 minutes 59 seconds
        assert Scraper._ms_to_readable(3599000) == "59:59"

    def test_convert_to_embed_url_valid(self):
        """Test converting standard track URL to embed URL."""
        # Standard track URL
        url = "https://open.spotify.com/track/1234567890abcdef"
        expected = "https://open.spotify.com/embed/track/1234567890abcdef"

        assert Scraper.convert_to_embed_url(url) == expected

        # Track URL with query parameters
        url = "https://open.spotify.com/track/1234567890abcdef?si=xyz123"
        expected = "https://open.spotify.com/embed/track/1234567890abcdef"

        assert Scraper.convert_to_embed_url(url) == expected

    def test_convert_to_embed_url_invalid(self):
        """Test converting invalid URLs to embed URL."""
        # Not a track URL
        assert Scraper.convert_to_embed_url("https://open.spotify.com/album/123") is None
        assert Scraper.convert_to_embed_url("https://open.spotify.com/playlist/123") is None

        # Not a Spotify URL
        assert Scraper.convert_to_embed_url("https://example.com/track/123") is None

        # Invalid URL format
        assert Scraper.convert_to_embed_url("not a url") is None

    def test_get_track_id_from_url_standard(self):
        """Test extracting track ID from standard URLs."""
        # Standard track URL
        url = "https://open.spotify.com/track/1234567890abcdef"
        assert Scraper.get_track_id_from_url(url) == "1234567890abcdef"

        # Track URL with query parameters
        url = "https://open.spotify.com/track/1234567890abcdef?si=xyz123"
        assert Scraper.get_track_id_from_url(url) == "1234567890abcdef"

    def test_get_track_id_from_url_embed(self):
        """Test extracting track ID from embed URLs."""
        # Embed track URL
        url = "https://open.spotify.com/embed/track/1234567890abcdef"
        assert Scraper.get_track_id_from_url(url) == "1234567890abcdef"

        # Embed track URL with query parameters
        url = "https://open.spotify.com/embed/track/1234567890abcdef?utm_source=generator"
        assert Scraper.get_track_id_from_url(url) == "1234567890abcdef"

    def test_get_track_id_from_url_invalid(self):
        """Test extracting track ID from invalid URLs."""
        # Not a track URL
        assert Scraper.get_track_id_from_url("https://open.spotify.com/album/123") is None
        assert Scraper.get_track_id_from_url("https://open.spotify.com/playlist/123") is None

        # Not a Spotify URL
        assert Scraper.get_track_id_from_url("https://example.com/track/123") is None

        # Invalid URL format
        assert Scraper.get_track_id_from_url("not a url") is None

        # Empty or None
        assert Scraper.get_track_id_from_url("") is None

    def test_validate_spotify_url_valid(self):
        """Test validating valid Spotify URLs."""
        browser = MockBrowser()
        scraper = Scraper(browser=browser)

        # Valid track URL
        assert scraper.validate_spotify_url("https://open.spotify.com/track/123") is True

        # Valid album URL
        assert scraper.validate_spotify_url("https://open.spotify.com/album/123") is True

        # Valid playlist URL
        assert scraper.validate_spotify_url("https://open.spotify.com/playlist/123") is True

        # Valid artist URL
        assert scraper.validate_spotify_url("https://open.spotify.com/artist/123") is True

    def test_validate_spotify_url_with_expected_type(self):
        """Test validating URLs with expected type."""
        browser = MockBrowser()
        scraper = Scraper(browser=browser)

        # Correct type
        assert (
            scraper.validate_spotify_url(
                "https://open.spotify.com/track/123", expected_type="track"
            )
            is True
        )

        # Wrong type
        with pytest.raises(URLError) as exc_info:
            scraper.validate_spotify_url(
                "https://open.spotify.com/album/123", expected_type="track"
            )
        assert "is not a Spotify track URL" in str(exc_info.value)

    def test_validate_spotify_url_embed(self):
        """Test validating embed URLs."""
        browser = MockBrowser()
        scraper = Scraper(browser=browser)

        # Valid embed URL
        assert (
            scraper.validate_spotify_url(
                "https://open.spotify.com/embed/track/123", expected_type="embed/track"
            )
            is True
        )

        # Wrong embed type
        with pytest.raises(URLError) as exc_info:
            scraper.validate_spotify_url(
                "https://open.spotify.com/embed/album/123", expected_type="embed/track"
            )
        assert "is not a Spotify embed/track URL" in str(exc_info.value)

    def test_validate_spotify_url_invalid(self):
        """Test validating invalid URLs."""
        browser = MockBrowser()
        scraper = Scraper(browser=browser)

        # Empty URL
        with pytest.raises(URLError) as exc_info:
            scraper.validate_spotify_url("")
        assert "URL must be a non-empty string" in str(exc_info.value)

        # None URL
        with pytest.raises(URLError) as exc_info:
            scraper.validate_spotify_url(None)
        assert "URL must be a non-empty string" in str(exc_info.value)

        # Not a Spotify URL
        with pytest.raises(URLError) as exc_info:
            scraper.validate_spotify_url("https://example.com/track/123")
        assert "Must be from 'open.spotify.com'" in str(exc_info.value)

        # Invalid scheme
        with pytest.raises(URLError) as exc_info:
            scraper.validate_spotify_url("ftp://open.spotify.com/track/123")
        assert "Invalid Spotify URL" in str(exc_info.value)
