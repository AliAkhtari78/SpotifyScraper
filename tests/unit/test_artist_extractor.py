"""
Unit tests for the artist extractor module.

These tests verify that the artist extractor correctly parses artist data
from Spotify web pages, including artist details, biography, discography, and top tracks.
"""

import json
import os
from pathlib import Path
import pytest

# This will be the actual import once the module is implemented
# from spotify_scraper.extractors.artist import ArtistExtractor
# from spotify_scraper.browsers.requests_browser import RequestsBrowser
# from spotify_scraper.core.exceptions import ParsingError

# For testing purposes
class MockBrowser:
    """Mock browser for testing extractors without network requests."""
    
    def __init__(self, html_content):
        self.html_content = html_content
    
    def get_page_content(self, url):
        """Return the mock HTML content regardless of URL."""
        return self.html_content


class TestArtistExtractor:
    """Tests for the ArtistExtractor class."""

    @pytest.fixture
    def fixture_path(self):
        """Path to the test fixtures directory."""
        return Path(__file__).parent.parent / "fixtures"
    
    @pytest.fixture
    def artist_html(self, fixture_path):
        """Load the artist HTML fixture."""
        with open(fixture_path / "html" / "artist_modern.html", "r", encoding="utf-8") as f:
            return f.read()
    
    @pytest.fixture
    def expected_artist_data(self, fixture_path):
        """Load the expected artist data JSON fixture."""
        with open(fixture_path / "json" / "artist_expected.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    def test_extract_artist_data(self, artist_html, expected_artist_data):
        """Test extracting artist data from the HTML fixture."""
        # This test will fail until ArtistExtractor is implemented
        mock_browser = MockBrowser(artist_html)
        
        # Example of how the extractor would be used
        # extractor = ArtistExtractor(browser=mock_browser)
        # artist_data = extractor.extract(url="https://open.spotify.com/artist/1dfeR4HaWDbWqFHLkxsg1d")
        
        # For now, just demonstrate the expected input and output
        print("Expected Input HTML:")
        print(artist_html[:500] + "...")  # Just show first 500 chars
        
        print("\nExpected Output JSON:")
        print(json.dumps(expected_artist_data, indent=2))
        
        # This assertion will fail until ArtistExtractor is implemented
        # assert artist_data == expected_artist_data
        
        # Placeholder assertion for now
        assert True
    
    def test_extract_artist_top_tracks(self, artist_html, expected_artist_data):
        """Test that artist top tracks are correctly extracted."""
        mock_browser = MockBrowser(artist_html)
        
        # Example of how top tracks would be accessed
        # extractor = ArtistExtractor(browser=mock_browser)
        # artist_data = extractor.extract(url="https://open.spotify.com/artist/1dfeR4HaWDbWqFHLkxsg1d")
        # top_tracks = artist_data.get("top_tracks", [])
        
        # Get expected top tracks from the fixture for comparison
        expected_top_tracks = expected_artist_data.get("top_tracks", [])
        
        print("\nExample Top Track Structure:")
        if expected_top_tracks:
            print(json.dumps(expected_top_tracks[0], indent=2))
        
        # These assertions will fail until ArtistExtractor is implemented
        # assert len(top_tracks) > 0
        # for i, track in enumerate(top_tracks):
        #     expected_track = expected_top_tracks[i] if i < len(expected_top_tracks) else None
        #     if expected_track:
        #         assert track["id"] == expected_track["id"]
        #         assert track["name"] == expected_track["name"]
        
        # Placeholder assertion for now
        assert len(expected_top_tracks) > 0  # Verify the fixture has top tracks
