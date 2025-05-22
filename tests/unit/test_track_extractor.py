"""
Unit tests for the track extractor module.

These tests verify that the track extractor correctly parses track data
from Spotify web pages, including track details, album information, and lyrics.
"""

import json
import os
from pathlib import Path
import pytest

# Import the needed exceptions only
from spotify_scraper.core.exceptions import ParsingError, URLError

# Simple mock browser for testing (avoid complex imports)
class MockBrowser:
    """Mock browser for testing extractors without network requests."""
    
    def __init__(self, html_content):
        self.html_content = html_content
    
    def get_page_content(self, url):
        """Return the mock HTML content regardless of URL."""
        return self.html_content
        
    def get(self, url):
        """Alias for get_page_content to match the real Browser interface."""
        return self.get_page_content(url)


# Import the TrackExtractor from the package
from spotify_scraper.extractors.track import TrackExtractor


class TestTrackExtractor:
    """Tests for the TrackExtractor class."""

    @pytest.fixture
    def fixture_path(self):
        """Path to the test fixtures directory."""
        return Path(__file__).parent.parent / "fixtures"
    
    @pytest.fixture
    def track_html(self, fixture_path):
        """Load the track HTML fixture."""
        with open(fixture_path / "html" / "track_modern.html", "r", encoding="utf-8") as f:
            return f.read()
    
    @pytest.fixture
    def expected_track_data(self, fixture_path):
        """Load the expected track data JSON fixture."""
        with open(fixture_path / "json" / "track_expected.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    def test_extract_track_data(self, track_html, expected_track_data):
        """Test extracting track data from the HTML fixture."""
        mock_browser = MockBrowser(track_html)
        
        # Create the extractor and extract track data
        extractor = TrackExtractor(browser=mock_browser)
        track_data = extractor.extract(url="https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv")
        
        # Print debug information
        print("\nExpected Output JSON:")
        print(json.dumps(expected_track_data, indent=2))
        
        print("\nActual Output JSON:")
        print(json.dumps(track_data, indent=2))
        
        # Compare the results
        assert track_data["id"] == expected_track_data["id"]
        assert track_data["name"] == expected_track_data["name"]
        assert track_data["uri"] == expected_track_data["uri"]
        assert track_data["type"] == expected_track_data["type"]
        assert track_data["duration_ms"] == expected_track_data["duration_ms"]
        
        # Check the album data
        assert track_data["album"]["name"] == expected_track_data["album"]["name"]
        assert track_data["album"]["id"] == expected_track_data["album"]["id"]
        assert track_data["album"]["uri"] == expected_track_data["album"]["uri"]
        
        # Check the artists
        assert len(track_data["artists"]) == len(expected_track_data["artists"])
        assert track_data["artists"][0]["name"] == expected_track_data["artists"][0]["name"]
        assert track_data["artists"][0]["id"] == expected_track_data["artists"][0]["id"]
    
    def test_extract_track_with_lyrics(self, track_html, expected_track_data):
        """Test that lyrics are correctly extracted when present."""
        mock_browser = MockBrowser(track_html)
        
        # Extract track data with lyrics
        extractor = TrackExtractor(browser=mock_browser)
        track_data = extractor.extract(url="https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv")
        lyrics = track_data.get("lyrics")
        
        print("\nExample Lyrics Structure:")
        print(json.dumps(expected_track_data["lyrics"], indent=2))
        
        print("\nActual Lyrics Structure:")
        print(json.dumps(lyrics, indent=2) if lyrics else "None")
        
        # Verify lyrics extraction
        assert lyrics is not None
        assert "lines" in lyrics
        assert len(lyrics["lines"]) > 0
        assert "sync_type" in lyrics
        assert lyrics["sync_type"] == expected_track_data["lyrics"]["sync_type"]
        
        # Check a few specific lyrics lines
        assert lyrics["lines"][0]["start_time_ms"] == expected_track_data["lyrics"]["lines"][0]["start_time_ms"]
        assert lyrics["lines"][1]["words"] == expected_track_data["lyrics"]["lines"][1]["words"]
        assert lyrics["lines"][2]["end_time_ms"] == expected_track_data["lyrics"]["lines"][2]["end_time_ms"]
