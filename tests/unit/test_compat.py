"""
Unit tests for the backward compatibility module.

These tests verify that the compatibility layer correctly provides
the old v1.x interface while using the new v2.x implementation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from spotify_scraper.compat import Scraper, Request
from spotify_scraper.auth.session import Session


class TestCompatScraper:
    """Tests for the backward compatibility Scraper class."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock session for testing."""
        session = Mock(spec=Session)
        session.cookies = {"session_cookie": "test_value"}
        return session
    
    @pytest.fixture
    def scraper(self, mock_session):
        """Create a Scraper instance with mocked client."""
        with patch('spotify_scraper.compat.SpotifyClient') as MockClient:
            mock_client = Mock()
            MockClient.return_value = mock_client
            
            scraper = Scraper(session=mock_session, log=False)
            scraper.client = mock_client  # Ensure client is set
            return scraper
    
    def test_scraper_initialization(self, mock_session):
        """Test that Scraper initializes correctly."""
        with patch('spotify_scraper.compat.SpotifyClient') as MockClient:
            scraper = Scraper(session=mock_session, log=True)
            
            # Verify client was created with correct parameters
            MockClient.assert_called_once()
            assert scraper.session == mock_session
            assert scraper.log is True
    
    def test_get_track_url_info_success(self, scraper):
        """Test successful track extraction with legacy format."""
        # Mock new format response
        new_format_data = {
            "id": "123",
            "name": "Test Track",
            "duration_ms": 240000,
            "preview_url": "https://example.com/preview.mp3",
            "artists": [{"name": "Test Artist", "uri": "spotify:artist:456"}],
            "album": {
                "name": "Test Album",
                "release_date": "2023-01-01",
                "images": [
                    {"url": "https://example.com/cover.jpg", "height": 640, "width": 640}
                ]
            }
        }
        
        scraper.client.get_track_info = Mock(return_value=new_format_data)
        
        # Test the method
        result = scraper.get_track_url_info("https://open.spotify.com/track/123")
        
        # Verify legacy format conversion
        assert result["title"] == "Test Track"
        assert result["artist_name"] == "Test Artist"
        assert result["album_title"] == "Test Album"
        assert result["preview_mp3"] == "https://example.com/preview.mp3"
        assert result["duration"] == "4:00"
        assert result["release_date"] == "2023-01-01"
        assert result["album_cover_url"] == "https://example.com/cover.jpg"
        assert result["album_cover_height"] == 640
        assert result["album_cover_width"] == 640
        assert result["ERROR"] is None
    
    def test_get_track_url_info_error(self, scraper):
        """Test track extraction error handling."""
        scraper.client.get_track_info = Mock(return_value={"ERROR": "Track not found"})
        
        result = scraper.get_track_url_info("https://open.spotify.com/track/invalid")
        
        assert result["ERROR"] == "Track not found"
    
    def test_get_track_url_info_no_client(self, mock_session):
        """Test track extraction when client initialization fails."""
        scraper = Scraper(session=mock_session, log=False)
        scraper.client = None
        
        result = scraper.get_track_url_info("https://open.spotify.com/track/123")
        
        assert result["ERROR"] == "Client initialization failed"
    
    def test_get_playlist_url_info_success(self, scraper):
        """Test successful playlist extraction with legacy format."""
        # Mock new format response
        new_format_data = {
            "id": "playlist123",
            "name": "Test Playlist",
            "description": "A test playlist",
            "owner": {"display_name": "Test User", "uri": "spotify:user:testuser"},
            "followers": {"total": 1000},
            "public": True,
            "collaborative": False,
            "images": [
                {"url": "https://example.com/playlist_cover.jpg", "height": 300, "width": 300}
            ],
            "tracks": {
                "total": 2,
                "items": [
                    {
                        "track": {
                            "name": "Song 1",
                            "artists": [{"name": "Artist 1"}],
                            "album": {"name": "Album 1"},
                            "duration_ms": 180000,
                            "uri": "spotify:track:111",
                            "external_urls": {"spotify": "https://open.spotify.com/track/111"}
                        }
                    },
                    {
                        "track": {
                            "name": "Song 2",
                            "artists": [{"name": "Artist 2"}],
                            "album": {"name": "Album 2"},
                            "duration_ms": 200000,
                            "uri": "spotify:track:222",
                            "external_urls": {"spotify": "https://open.spotify.com/track/222"}
                        }
                    }
                ]
            }
        }
        
        scraper.client.get_playlist_info = Mock(return_value=new_format_data)
        
        # Test the method
        result = scraper.get_playlist_url_info("https://open.spotify.com/playlist/playlist123")
        
        # Verify legacy format conversion
        assert result["name"] == "Test Playlist"
        assert result["owner_name"] == "Test User"
        assert result["owner_url"] == "https://open.spotify.com/user/testuser"
        assert result["description"] == "A test playlist"
        assert result["followers"] == 1000
        assert result["is_public"] is True
        assert result["collaborative"] is False
        assert result["image_url"] == "https://example.com/playlist_cover.jpg"
        assert result["tracks_total"] == 2
        assert len(result["tracks"]) == 2
        assert result["tracks"][0]["name"] == "Song 1"
        assert result["tracks"][0]["artist"] == "Artist 1"
        assert result["ERROR"] is None
    
    def test_get_album_url_info_success(self, scraper):
        """Test successful album extraction with legacy format."""
        # Mock new format response
        new_format_data = {
            "id": "album123",
            "name": "Test Album",
            "artists": [{"name": "Test Artist"}],
            "release_date": "2023-06-15",
            "total_tracks": 12,
            "label": "Test Records",
            "popularity": 75,
            "album_type": "album",
            "uri": "spotify:album:album123",
            "images": [
                {"url": "https://example.com/album_cover.jpg", "height": 640, "width": 640}
            ],
            "tracks": {
                "items": [
                    {
                        "name": "Track 1",
                        "artists": [{"name": "Test Artist"}],
                        "duration_ms": 240000,
                        "track_number": 1,
                        "uri": "spotify:track:t1"
                    },
                    {
                        "name": "Track 2",
                        "artists": [{"name": "Test Artist"}],
                        "duration_ms": 200000,
                        "track_number": 2,
                        "uri": "spotify:track:t2"
                    }
                ]
            }
        }
        
        scraper.client.get_album_info = Mock(return_value=new_format_data)
        
        # Test the method
        result = scraper.get_album_url_info("https://open.spotify.com/album/album123")
        
        # Verify legacy format conversion
        assert result["name"] == "Test Album"
        assert result["artist"] == "Test Artist"
        assert result["release_date"] == "2023-06-15"
        assert result["total_tracks"] == 12
        assert result["label"] == "Test Records"
        assert result["popularity"] == 75
        assert result["cover_url"] == "https://example.com/album_cover.jpg"
        assert len(result["tracks"]) == 2
        assert result["tracks"][0]["name"] == "Track 1"
        assert result["ERROR"] is None
    
    def test_get_artist_url_info_success(self, scraper):
        """Test successful artist extraction with legacy format."""
        # Mock new format response
        new_format_data = {
            "id": "artist123",
            "name": "Test Artist",
            "genres": ["rock", "indie"],
            "popularity": 82,
            "followers": {"total": 500000},
            "monthly_listeners": 2000000,
            "bio": "A talented artist",
            "verified": True,
            "uri": "spotify:artist:artist123",
            "images": [
                {"url": "https://example.com/artist_photo.jpg", "height": 640, "width": 640}
            ],
            "top_tracks": [
                {
                    "name": "Hit Song",
                    "album": {"name": "Best Album"},
                    "duration_ms": 210000,
                    "popularity": 90,
                    "uri": "spotify:track:hit1"
                }
            ],
            "albums": [
                {
                    "name": "Latest Album",
                    "release_date": "2023-10-01",
                    "total_tracks": 10,
                    "album_type": "album",
                    "uri": "spotify:album:latest1"
                }
            ]
        }
        
        scraper.client.get_artist_info = Mock(return_value=new_format_data)
        
        # Test the method
        result = scraper.get_artist_url_info("https://open.spotify.com/artist/artist123")
        
        # Verify legacy format conversion
        assert result["name"] == "Test Artist"
        assert result["genres"] == ["rock", "indie"]
        assert result["popularity"] == 82
        assert result["followers"] == 500000
        assert result["monthly_listeners"] == 2000000
        assert result["verified"] is True
        assert result["image_url"] == "https://example.com/artist_photo.jpg"
        assert len(result["top_tracks"]) == 1
        assert result["top_tracks"][0]["name"] == "Hit Song"
        assert len(result["albums"]) == 1
        assert result["ERROR"] is None
    
    def test_download_cover(self, scraper):
        """Test cover download through compatibility layer."""
        scraper.client.download_cover = Mock(return_value="/path/to/cover.jpg")
        
        result = scraper.download_cover("https://open.spotify.com/track/123", path="/downloads")
        
        assert result == "/path/to/cover.jpg"
        scraper.client.download_cover.assert_called_once_with(
            "https://open.spotify.com/track/123", "/downloads"
        )
    
    def test_download_cover_error(self, scraper):
        """Test cover download error handling."""
        scraper.client.download_cover = Mock(side_effect=Exception("Network error"))
        
        result = scraper.download_cover("https://open.spotify.com/track/123")
        
        assert "Couldn't download the cover: Network error" in result
    
    def test_download_preview_mp3(self, scraper):
        """Test MP3 download through compatibility layer."""
        scraper.client.download_preview_mp3 = Mock(return_value="/path/to/preview.mp3")
        
        result = scraper.download_preview_mp3(
            "https://open.spotify.com/track/123", 
            path="/downloads",
            with_cover=True
        )
        
        assert result == "/path/to/preview.mp3"
        scraper.client.download_preview_mp3.assert_called_once_with(
            "https://open.spotify.com/track/123", "/downloads", True
        )
    
    def test_ms_to_readable(self):
        """Test milliseconds to readable time conversion."""
        assert Scraper._ms_to_readable(0) == "0:00"
        assert Scraper._ms_to_readable(60000) == "1:00"
        assert Scraper._ms_to_readable(90000) == "1:30"
        assert Scraper._ms_to_readable(222075) == "3:42"
        assert Scraper._ms_to_readable(3661000) == "1:01:01"
    
    def test_close(self, scraper):
        """Test that close properly cleans up resources."""
        scraper.close()
        
        scraper.client.close.assert_called_once()


class TestCompatRequest:
    """Tests for the backward compatibility Request class."""
    
    def test_request_class_exists(self):
        """Test that Request class is available for import."""
        assert Request is not None
        
    def test_request_initialization(self):
        """Test that Request can be initialized."""
        # Request class should be available from auth.session
        request = Request()
        assert hasattr(request, 'request') or hasattr(request, '__init__')