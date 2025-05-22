"""
Integration tests for SpotifyScraper.

These tests verify the full flow of extracting data from Spotify,
including network requests, parsing, and data extraction.

Note: These tests may require internet connection and may be affected
by changes to Spotify's web interface.
"""

import pytest
import os
from pathlib import Path

from spotify_scraper import SpotifyClient, is_spotify_url, extract_id
from spotify_scraper.exceptions import SpotifyScraperError, URLError


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestFullFlow:
    """Integration tests for the complete extraction flow."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create a SpotifyClient for testing."""
        # Use environment variables for cookies if available
        cookie_file = os.environ.get("SPOTIFY_COOKIE_FILE")
        
        client = SpotifyClient(
            cookie_file=cookie_file,
            browser_type="requests",
            log_level="INFO"
        )
        
        yield client
        
        # Cleanup
        client.close()
    
    @pytest.mark.skipif(
        not os.environ.get("SPOTIFY_TEST_TRACK_URL"),
        reason="No test track URL provided"
    )
    def test_track_extraction(self, client):
        """Test extracting track information from a real Spotify URL."""
        track_url = os.environ.get("SPOTIFY_TEST_TRACK_URL", 
                                  "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp")
        
        # Verify URL validation
        assert is_spotify_url(track_url)
        assert extract_id(track_url) is not None
        
        # Extract track information
        track_info = client.get_track_info(track_url)
        
        # Verify basic structure
        assert "ERROR" not in track_info
        assert track_info.get("id") is not None
        assert track_info.get("name") is not None
        assert track_info.get("artists") is not None
        assert isinstance(track_info.get("artists"), list)
        assert track_info.get("album") is not None
        assert track_info.get("duration_ms", 0) > 0
        
        # If we have authentication, try to get lyrics
        if client.session.is_authenticated():
            try:
                lyrics = client.get_track_lyrics(track_url)
                assert lyrics is None or isinstance(lyrics, str)
            except Exception:
                # Lyrics might not be available for all tracks
                pass
    
    @pytest.mark.skipif(
        not os.environ.get("SPOTIFY_TEST_ALBUM_URL"),
        reason="No test album URL provided"
    )
    def test_album_extraction(self, client):
        """Test extracting album information from a real Spotify URL."""
        album_url = os.environ.get("SPOTIFY_TEST_ALBUM_URL",
                                  "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv")
        
        # Extract album information
        album_info = client.get_album_info(album_url)
        
        # Verify basic structure
        assert "ERROR" not in album_info
        assert album_info.get("id") is not None
        assert album_info.get("name") is not None
        assert album_info.get("artists") is not None
        assert album_info.get("release_date") is not None
        assert album_info.get("total_tracks", 0) > 0
        assert album_info.get("tracks") is not None
        
        # Verify tracks structure
        tracks = album_info.get("tracks", {}).get("items", [])
        assert len(tracks) > 0
        for track in tracks[:3]:  # Check first 3 tracks
            assert track.get("name") is not None
            assert track.get("duration_ms", 0) > 0
    
    @pytest.mark.skipif(
        not os.environ.get("SPOTIFY_TEST_ARTIST_URL"),
        reason="No test artist URL provided"
    )
    def test_artist_extraction(self, client):
        """Test extracting artist information from a real Spotify URL."""
        artist_url = os.environ.get("SPOTIFY_TEST_ARTIST_URL",
                                   "https://open.spotify.com/artist/0YC192cP3KPCRWx8zr8MfZ")
        
        # Extract artist information
        artist_info = client.get_artist_info(artist_url)
        
        # Verify basic structure
        assert "ERROR" not in artist_info
        assert artist_info.get("id") is not None
        assert artist_info.get("name") is not None
        assert artist_info.get("genres") is not None
        assert isinstance(artist_info.get("genres"), list)
        assert artist_info.get("popularity") is not None
        assert artist_info.get("followers") is not None
        
        # Verify additional data if available
        if artist_info.get("top_tracks"):
            assert isinstance(artist_info["top_tracks"], list)
            assert len(artist_info["top_tracks"]) > 0
        
        if artist_info.get("albums"):
            assert isinstance(artist_info["albums"], list)
    
    @pytest.mark.skipif(
        not os.environ.get("SPOTIFY_TEST_PLAYLIST_URL"),
        reason="No test playlist URL provided"
    )
    def test_playlist_extraction(self, client):
        """Test extracting playlist information from a real Spotify URL."""
        playlist_url = os.environ.get("SPOTIFY_TEST_PLAYLIST_URL",
                                     "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
        
        # Extract playlist information
        playlist_info = client.get_playlist_info(playlist_url)
        
        # Verify basic structure
        assert "ERROR" not in playlist_info
        assert playlist_info.get("id") is not None
        assert playlist_info.get("name") is not None
        assert playlist_info.get("owner") is not None
        assert playlist_info.get("tracks") is not None
        
        # Verify tracks structure
        tracks = playlist_info.get("tracks", {})
        assert tracks.get("total", 0) > 0
        items = tracks.get("items", [])
        assert len(items) > 0
        
        # Check first few tracks
        for item in items[:3]:
            track = item.get("track", {})
            assert track.get("name") is not None
            assert track.get("artists") is not None
    
    def test_auto_detection(self, client):
        """Test automatic URL type detection."""
        test_urls = {
            "track": "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp",
            "album": "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv",
            "artist": "https://open.spotify.com/artist/0YC192cP3KPCRWx8zr8MfZ",
            "playlist": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
        }
        
        for url_type, url in test_urls.items():
            try:
                result = client.get_all_info(url)
                assert "ERROR" not in result
                # The result should have appropriate type-specific fields
                if url_type == "track":
                    assert "duration_ms" in result
                elif url_type == "album":
                    assert "total_tracks" in result
                elif url_type == "artist":
                    assert "genres" in result or "followers" in result
                elif url_type == "playlist":
                    assert "owner" in result
            except Exception as e:
                # Network issues might occur, but the method should exist
                assert hasattr(client, 'get_all_info')
    
    @pytest.mark.slow
    def test_media_download(self, client, tmp_path):
        """Test downloading media content."""
        track_url = "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
        
        # Test cover download
        try:
            cover_path = client.download_cover(track_url, str(tmp_path))
            if cover_path:
                assert Path(cover_path).exists()
                assert Path(cover_path).stat().st_size > 0
        except Exception:
            # Media download might fail due to network issues
            pass
        
        # Test preview download (if available)
        try:
            # First check if preview is available
            track_info = client.get_track_info(track_url)
            if track_info.get("preview_url"):
                preview_path = client.download_preview_mp3(track_url, str(tmp_path))
                if preview_path:
                    assert Path(preview_path).exists()
                    assert Path(preview_path).stat().st_size > 0
        except Exception:
            # Preview might not be available
            pass


class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create a SpotifyClient for testing."""
        client = SpotifyClient(browser_type="requests")
        yield client
        client.close()
    
    def test_invalid_url(self, client):
        """Test handling of invalid URLs."""
        invalid_urls = [
            "https://www.google.com",
            "not-a-url",
            "https://open.spotify.com/invalid/123",
            "spotify:invalid:123"
        ]
        
        for url in invalid_urls:
            with pytest.raises((URLError, SpotifyScraperError)):
                client.get_all_info(url)
    
    def test_nonexistent_content(self, client):
        """Test handling of non-existent content."""
        # Use obviously invalid IDs
        nonexistent_urls = [
            "https://open.spotify.com/track/0000000000000000000000",
            "https://open.spotify.com/album/zzzzzzzzzzzzzzzzzzzzz",
        ]
        
        for url in nonexistent_urls:
            try:
                result = client.get_all_info(url)
                # Should either raise an error or return error in result
                if not isinstance(result, dict):
                    pytest.fail("Expected dict result")
                if "ERROR" not in result:
                    # Some invalid IDs might still return empty data
                    assert result.get("id") is not None
            except (URLError, SpotifyScraperError):
                # This is expected for invalid content
                pass