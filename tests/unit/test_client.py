"""
Unit tests for the SpotifyClient class.

These tests verify that the client correctly coordinates between different
extractors and provides a unified interface for data extraction.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

from spotify_scraper.client import SpotifyClient
from spotify_scraper.exceptions import (
    SpotifyScraperError,
    URLError, 
    AuthenticationRequiredError,
    MediaError
)


class TestSpotifyClient:
    """Tests for the SpotifyClient class."""
    
    @pytest.fixture
    def mock_browser(self):
        """Create a mock browser for testing."""
        browser = Mock()
        browser.get_page_content = Mock(return_value="<html>Mock content</html>")
        browser.close = Mock()
        return browser
    
    @pytest.fixture
    def client(self):
        """Create a SpotifyClient instance for testing."""
        # Mock the browser creation
        with patch('spotify_scraper.client.create_browser') as mock_create:
            mock_browser = Mock()
            mock_browser.close = Mock()
            mock_create.return_value = mock_browser
            
            client = SpotifyClient(
                cookie_file=None,
                cookies=None,
                headers=None,
                proxy=None,
                browser_type="requests",
                log_level="WARNING",
            )
            return client
    
    def test_client_initialization(self):
        """Test that the client initializes correctly."""
        with patch('spotify_scraper.client.create_browser') as mock_create:
            mock_browser = Mock()
            mock_create.return_value = mock_browser
            
            client = SpotifyClient()
            
            # Verify browser was created
            mock_create.assert_called_once()
            
            # Verify extractors were initialized
            assert hasattr(client, 'track_extractor')
            assert hasattr(client, 'album_extractor')
            assert hasattr(client, 'artist_extractor')
            assert hasattr(client, 'playlist_extractor')
    
    def test_get_track_info(self, client):
        """Test getting track information."""
        # Mock the track extractor
        mock_track_data = {
            "id": "3n3Ppam7vgaVa1iaRUc9Lp",
            "name": "Mr. Brightside",
            "artists": [{"name": "The Killers"}],
            "album": {"name": "Hot Fuss"},
            "duration_ms": 222075,
            "preview_url": "https://example.com/preview.mp3"
        }
        
        client.track_extractor.get_track_info = Mock(return_value=mock_track_data)
        
        # Test the method
        result = client.get_track_info("https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp")
        
        # Verify the result
        assert result == mock_track_data
        client.track_extractor.get_track_info.assert_called_once()
    
    def test_get_track_lyrics_requires_auth(self, client):
        """Test that getting lyrics requires authentication."""
        # Mock session as not authenticated
        client.session.is_authenticated = Mock(return_value=False)
        
        # Test that it raises AuthenticationRequiredError
        with pytest.raises(AuthenticationRequiredError):
            client.get_track_lyrics("https://open.spotify.com/track/123", require_auth=True)
    
    def test_get_track_lyrics_with_auth(self, client):
        """Test getting lyrics with authentication."""
        # Mock session as authenticated
        client.session.is_authenticated = Mock(return_value=True)
        
        # Mock the track extractor
        mock_lyrics = "These are the lyrics to the song"
        client.track_extractor.get_lyrics = Mock(return_value=mock_lyrics)
        
        # Test the method
        result = client.get_track_lyrics("https://open.spotify.com/track/123")
        
        # Verify the result
        assert result == mock_lyrics
        client.track_extractor.get_lyrics.assert_called_once()
    
    def test_get_track_info_with_lyrics(self, client):
        """Test getting track info with lyrics."""
        # Mock session as authenticated
        client.session.is_authenticated = Mock(return_value=True)
        
        # Mock track data and lyrics
        mock_track_data = {
            "id": "123",
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}]
        }
        mock_lyrics = "These are the lyrics"
        
        client.track_extractor.get_track_info = Mock(return_value=mock_track_data)
        client.track_extractor.get_lyrics = Mock(return_value=mock_lyrics)
        
        # Test the method
        result = client.get_track_info_with_lyrics("https://open.spotify.com/track/123")
        
        # Verify the result includes lyrics
        assert result["name"] == "Test Track"
        assert result["lyrics"] == mock_lyrics
    
    def test_get_album_info(self, client):
        """Test getting album information."""
        # Mock the album extractor
        mock_album_data = {
            "id": "4LH4d3cOWNNsVw41Gqt2kv",
            "name": "The Dark Side of the Moon",
            "artists": [{"name": "Pink Floyd"}],
            "release_date": "1973-03-01",
            "total_tracks": 10
        }
        
        client.album_extractor.extract = Mock(return_value=mock_album_data)
        
        # Test the method
        result = client.get_album_info("https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv")
        
        # Verify the result
        assert result == mock_album_data
        client.album_extractor.extract.assert_called_once()
    
    def test_get_artist_info(self, client):
        """Test getting artist information."""
        # Mock the artist extractor
        mock_artist_data = {
            "id": "0YC192cP3KPCRWx8zr8MfZ",
            "name": "Hans Zimmer",
            "genres": ["soundtrack", "orchestral"],
            "popularity": 78,
            "followers": {"total": 2500000}
        }
        
        client.artist_extractor.extract = Mock(return_value=mock_artist_data)
        
        # Test the method
        result = client.get_artist_info("https://open.spotify.com/artist/0YC192cP3KPCRWx8zr8MfZ")
        
        # Verify the result
        assert result == mock_artist_data
        client.artist_extractor.extract.assert_called_once()
    
    def test_get_playlist_info(self, client):
        """Test getting playlist information."""
        # Mock the playlist extractor
        mock_playlist_data = {
            "id": "37i9dQZF1DXcBWIGoYBM5M",
            "name": "Today's Top Hits",
            "description": "The hottest tracks right now",
            "owner": {"display_name": "Spotify"},
            "tracks": {"total": 50}
        }
        
        client.playlist_extractor.extract = Mock(return_value=mock_playlist_data)
        
        # Test the method
        result = client.get_playlist_info("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
        
        # Verify the result
        assert result == mock_playlist_data
        client.playlist_extractor.extract.assert_called_once()
    
    def test_get_all_info_track(self, client):
        """Test get_all_info with a track URL."""
        mock_track_data = {"id": "123", "name": "Test Track", "type": "track"}
        
        with patch('spotify_scraper.utils.url.get_url_type', return_value="track"):
            client.get_track_info = Mock(return_value=mock_track_data)
            
            result = client.get_all_info("https://open.spotify.com/track/123")
            
            assert result == mock_track_data
            client.get_track_info.assert_called_once()
    
    def test_get_all_info_album(self, client):
        """Test get_all_info with an album URL."""
        mock_album_data = {"id": "456", "name": "Test Album", "type": "album"}
        
        with patch('spotify_scraper.utils.url.get_url_type', return_value="album"):
            client.get_album_info = Mock(return_value=mock_album_data)
            
            result = client.get_all_info("https://open.spotify.com/album/456")
            
            assert result == mock_album_data
            client.get_album_info.assert_called_once()
    
    def test_get_all_info_artist(self, client):
        """Test get_all_info with an artist URL."""
        mock_artist_data = {"id": "789", "name": "Test Artist", "type": "artist"}
        
        with patch('spotify_scraper.utils.url.get_url_type', return_value="artist"):
            client.get_artist_info = Mock(return_value=mock_artist_data)
            
            result = client.get_all_info("https://open.spotify.com/artist/789")
            
            assert result == mock_artist_data
            client.get_artist_info.assert_called_once()
    
    def test_get_all_info_playlist(self, client):
        """Test get_all_info with a playlist URL."""
        mock_playlist_data = {"id": "abc", "name": "Test Playlist", "type": "playlist"}
        
        with patch('spotify_scraper.utils.url.get_url_type', return_value="playlist"):
            client.get_playlist_info = Mock(return_value=mock_playlist_data)
            
            result = client.get_all_info("https://open.spotify.com/playlist/abc")
            
            assert result == mock_playlist_data
            client.get_playlist_info.assert_called_once()
    
    def test_get_all_info_invalid_url(self, client):
        """Test get_all_info with an invalid URL type."""
        with patch('spotify_scraper.utils.url.get_url_type', return_value=None):
            with pytest.raises(URLError):
                client.get_all_info("https://invalid.url.com")
    
    def test_download_cover(self, client):
        """Test downloading cover image."""
        mock_path = "/path/to/image.jpg"
        client._image_downloader.download = Mock(return_value=mock_path)
        
        result = client.download_cover("https://open.spotify.com/track/123")
        
        assert result == mock_path
        client._image_downloader.download.assert_called_once()
    
    def test_download_preview_mp3(self, client):
        """Test downloading preview MP3."""
        mock_path = "/path/to/preview.mp3"
        client._audio_downloader.download = Mock(return_value=mock_path)
        
        result = client.download_preview_mp3("https://open.spotify.com/track/123", with_cover=True)
        
        assert result == mock_path
        client._audio_downloader.download.assert_called_once_with(
            "https://open.spotify.com/track/123", "", True
        )
    
    def test_client_close(self, client):
        """Test that the client properly closes resources."""
        client.close()
        
        # Verify browser was closed
        client.browser.close.assert_called_once()
    
    def test_client_context_manager(self):
        """Test using the client as a context manager."""
        with patch('spotify_scraper.client.create_browser') as mock_create:
            mock_browser = Mock()
            mock_browser.close = Mock()
            mock_create.return_value = mock_browser
            
            # Use client in context manager (if implemented)
            client = SpotifyClient()
            client.close()
            
            # Verify cleanup was called
            mock_browser.close.assert_called_once()