import pytest
import json
import os
from unittest.mock import MagicMock

from spotify_scraper.extractors.track import TrackExtractor
from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.types import TrackData
from spotify_scraper.core.exceptions import URLValidationError, ContentExtractionError, TrackNotFoundError

# Paths to test fixtures
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures')
HTML_FIXTURES_DIR = os.path.join(FIXTURES_DIR, 'html')
JSON_FIXTURES_DIR = os.path.join(FIXTURES_DIR, 'json')

# Test URLs
VALID_TRACK_URL = "https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv"
VALID_EMBED_URL = "https://open.spotify.com/embed/track/4u7EnebtmKWzUH433cf5Qv"
INVALID_URL = "https://example.com/not-spotify"
NOT_FOUND_URL = "https://open.spotify.com/track/notfound"

class TestTrackExtractor:
    @pytest.fixture
    def mock_browser(self):
        """Create a mock browser that returns fixture HTML."""
        browser = MagicMock(spec=Browser)
        
        # Load fixture HTML
        with open(os.path.join(HTML_FIXTURES_DIR, 'track_modern.html'), 'r', encoding='utf-8') as f:
            fixture_html = f.read()
        
        # Configure mock to return the fixture for valid URLs
        def get_page_content(url):
            if VALID_EMBED_URL in url:
                return fixture_html
            elif "notfound" in url:
                return "<div class='content'>Sorry, couldn't find that.</div>"
            return ""
            
        browser.get_page_content.side_effect = get_page_content
        return browser
    
    @pytest.fixture
    def expected_track_data(self):
        """Load expected track data from JSON fixture."""
        with open(os.path.join(JSON_FIXTURES_DIR, 'track_expected.json'), 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_extract_valid_url(self, mock_browser, expected_track_data):
        """Test extraction with a valid Spotify track URL."""
        extractor = TrackExtractor(mock_browser)
        result = extractor.extract(VALID_TRACK_URL)
        
        # Verify result is a TrackData instance
        assert isinstance(result, TrackData)
        
        # Convert to dict for comparison with expected data
        result_dict = result.to_dict()
        
        # Check essential fields
        assert result_dict['name'] == expected_track_data['name']
        assert result_dict['id'] == expected_track_data['id']
        assert result_dict['uri'] == expected_track_data['uri']
        assert result_dict['duration_ms'] == expected_track_data['duration_ms']
        assert result_dict['preview_url'] == expected_track_data['preview_url']
        assert result_dict['is_playable'] == expected_track_data['is_playable']
        
        # Check artists
        assert len(result_dict['artists']) == len(expected_track_data['artists'])
        assert result_dict['artists'][0]['name'] == expected_track_data['artists'][0]['name']
        
        # Check album
        assert result_dict['album']['name'] == expected_track_data['album']['name']
        assert result_dict['album']['id'] == expected_track_data['album']['id']
        
        # Check lyrics if present
        if expected_track_data.get('lyrics'):
            assert result_dict['lyrics'] is not None
            assert len(result_dict['lyrics']) == len(expected_track_data['lyrics'])
            assert result_dict['lyrics'][0]['text'] == expected_track_data['lyrics'][0]['text']
    
    def test_extract_embed_url(self, mock_browser):
        """Test extraction with an embed URL."""
        extractor = TrackExtractor(mock_browser)
        result = extractor.extract(VALID_EMBED_URL)
        
        assert isinstance(result, TrackData)
        assert result.name == "Bohemian Rhapsody - Remastered 2011"
    
    def test_validate_url_invalid(self):
        """Test URL validation with invalid URL."""
        extractor = TrackExtractor(MagicMock())
        
        with pytest.raises(URLValidationError):
            extractor._validate_url(INVALID_URL)
    
    def test_track_not_found(self, mock_browser):
        """Test extraction with URL for non-existent track."""
        extractor = TrackExtractor(mock_browser)
        
        # For testing purposes, we'll use a valid-format ID that doesn't exist
        not_found_url = "https://open.spotify.com/track/1234567890123456789012"
        
        def get_page_content_not_found(url):
            return "<div class='content'>Sorry, couldn't find that.</div>"
            
        mock_browser.get_page_content.side_effect = get_page_content_not_found
        
        with pytest.raises(TrackNotFoundError):
            extractor.extract(not_found_url)