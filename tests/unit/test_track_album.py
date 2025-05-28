"""
Unit tests for the track album field functionality.

These tests verify that the track extractor correctly includes album
information in the track data, as per Spotify's API contract.
"""

import json
from pathlib import Path

import pytest

from spotify_scraper.client import SpotifyClient

# Import the TrackExtractor
from spotify_scraper.extractors.track import TrackExtractor


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

    def close(self):
        """Mock the close method."""
        pass


class TestTrackAlbumField:
    """Tests for the album field in track data."""

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

    def test_track_album_field_present(self, track_html, expected_track_data):
        """Test that the album field is present in track data."""
        mock_browser = MockBrowser(track_html)

        # Create the extractor and extract track data
        extractor = TrackExtractor(browser=mock_browser)
        track_data = extractor.extract(url="https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv")

        # Verify album field is present
        assert "album" in track_data
        assert track_data["album"] is not None
        assert "name" in track_data["album"]
        assert track_data["album"]["name"] == expected_track_data["album"]["name"]

    def test_client_get_track_info_album_field(self, track_html, monkeypatch):
        """Test that client.get_track_info() returns data with album field."""
        # We need to patch both the create_browser function AND the extract method
        # of the TrackExtractor to ensure we test our actual implementation

        mock_browser = MockBrowser(track_html)

        # First test that the album is correctly extracted by the TrackExtractor
        extractor = TrackExtractor(browser=mock_browser)
        track_data = extractor.extract(url="https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv")

        # Then verify it's correctly returned by get_track_info
        monkeypatch.setattr(
            "spotify_scraper.extractors.track.TrackExtractor.extract", lambda self, url: track_data
        )

        # Create client - it doesn't matter what browser it has since we mocked the extract method
        client = SpotifyClient()

        # Get track info
        track = client.get_track_info("https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv")

        # Verify album field is present
        assert "album" in track
        assert track["album"] is not None
        assert "name" in track["album"]
        assert track["album"]["name"] == "A Night At The Opera (2011 Remaster)"
