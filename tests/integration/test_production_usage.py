#!/usr/bin/env python3
"""
Comprehensive test suite for production SpotifyScraper usage.

This module provides extensive testing for all SpotifyScraperWrapper features,
including error handling, caching, batch processing, and media downloads.

Author: SpotifyScraper Development Team
Date: 2025-01-22
Version: 2.0.0
"""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, Any, List

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.production_usage import (
    SpotifyScraperWrapper,
    create_authenticated_client,
    analyze_spotify_url,
    spotify_scraper_session
)
from spotify_scraper.exceptions import (
    SpotifyScraperError,
    URLError,
    NetworkError,
    ScrapingError,
    AuthenticationRequiredError
)


class TestSpotifyScraperWrapper:
    """Test suite for SpotifyScraperWrapper class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock SpotifyClient."""
        client = Mock()
        client.get_track_info = Mock()
        client.get_track_lyrics = Mock()
        client.get_album_info = Mock()
        client.get_artist_info = Mock()
        client.get_playlist_info = Mock()
        client.get_all_info = Mock()
        client.download_preview_mp3 = Mock()
        client.download_cover = Mock()
        client.close = Mock()
        return client
    
    @pytest.fixture
    def wrapper(self, temp_dir, mock_client):
        """Create a SpotifyScraperWrapper instance with mocked client."""
        with patch('examples.production_usage.SpotifyClient', return_value=mock_client):
            wrapper = SpotifyScraperWrapper(
                cache_dir=temp_dir / "cache",
                log_level="DEBUG",
                max_retries=3,
                retry_delay=0.1  # Short delay for testing
            )
            wrapper.client = mock_client
            yield wrapper
    
    def test_initialization(self, temp_dir):
        """Test wrapper initialization with various parameters."""
        with patch('examples.production_usage.SpotifyClient') as mock_client_class:
            wrapper = SpotifyScraperWrapper(
                cookie_file="cookies.txt",
                cookies={"session": "token"},
                headers={"User-Agent": "Test"},
                proxy={"http": "proxy.example.com"},
                browser_type="selenium",
                log_level="DEBUG",
                log_file=str(temp_dir / "test.log"),
                cache_dir=temp_dir / "cache",
                max_retries=5,
                retry_delay=2.0
            )
            
            # Verify initialization
            assert wrapper.max_retries == 5
            assert wrapper.retry_delay == 2.0
            assert wrapper.cache_dir == temp_dir / "cache"
            assert wrapper.cache_dir.exists()
            
            # Verify client was initialized with correct parameters
            mock_client_class.assert_called_once_with(
                cookie_file="cookies.txt",
                cookies={"session": "token"},
                headers={"User-Agent": "Test"},
                proxy={"http": "proxy.example.com"},
                browser_type="selenium",
                log_level="DEBUG",
                log_file=str(temp_dir / "test.log")
            )
    
    def test_cache_key_generation(self, wrapper):
        """Test cache key generation for different URL types."""
        test_cases = [
            (
                "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
                "track_info",
                "track_6rqhFgbbKwnb9MLmUQDhG6_track_info.json"
            ),
            (
                "https://open.spotify.com/album/1234567890abcdef",
                "album_info",
                "album_1234567890abcdef_album_info.json"
            ),
            (
                "https://open.spotify.com/artist/abcdef1234567890",
                "artist_info",
                "artist_abcdef1234567890_artist_info.json"
            ),
            (
                "https://open.spotify.com/playlist/xyz123",
                "playlist_info",
                "playlist_xyz123_playlist_info.json"
            )
        ]
        
        for url, operation, expected_filename in test_cases:
            cache_key = wrapper._get_cache_key(url, operation)
            assert cache_key.name == expected_filename
    
    def test_cache_operations(self, wrapper, temp_dir):
        """Test cache save and load operations."""
        # Test data
        test_data = {
            "id": "123",
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}]
        }
        
        cache_key = temp_dir / "cache" / "test_cache.json"
        
        # Test saving to cache
        wrapper._save_to_cache(cache_key, test_data)
        assert cache_key.exists()
        
        # Test loading from cache (fresh)
        loaded_data = wrapper._load_from_cache(cache_key)
        assert loaded_data == test_data
        
        # Test expired cache
        # Manually modify the timestamp to be old
        with open(cache_key, 'r') as f:
            cache_content = json.load(f)
        
        old_timestamp = (datetime.now() - timedelta(days=2)).isoformat()
        cache_content['timestamp'] = old_timestamp
        
        with open(cache_key, 'w') as f:
            json.dump(cache_content, f)
        
        # Should return None for expired cache
        loaded_data = wrapper._load_from_cache(cache_key)
        assert loaded_data is None
    
    def test_retry_operation_success(self, wrapper):
        """Test retry operation with successful execution."""
        mock_operation = Mock(return_value="success")
        
        result = wrapper._retry_operation(mock_operation, "arg1", kwarg="value")
        
        assert result == "success"
        mock_operation.assert_called_once_with("arg1", kwarg="value")
    
    def test_retry_operation_with_network_error(self, wrapper):
        """Test retry operation with network errors."""
        mock_operation = Mock(
            side_effect=[
                NetworkError("Network error 1"),
                NetworkError("Network error 2"),
                "success"
            ]
        )
        
        result = wrapper._retry_operation(mock_operation, "arg1")
        
        assert result == "success"
        assert mock_operation.call_count == 3
    
    def test_retry_operation_max_retries_exceeded(self, wrapper):
        """Test retry operation when max retries are exceeded."""
        mock_operation = Mock(side_effect=NetworkError("Persistent error"))
        
        with pytest.raises(NetworkError):
            wrapper._retry_operation(mock_operation)
        
        assert mock_operation.call_count == wrapper.max_retries
    
    def test_retry_operation_non_retryable_error(self, wrapper):
        """Test retry operation with non-retryable errors."""
        mock_operation = Mock(side_effect=ValueError("Invalid value"))
        
        with pytest.raises(ValueError):
            wrapper._retry_operation(mock_operation)
        
        # Should not retry for non-network errors
        assert mock_operation.call_count == 1
    
    def test_get_track_info_success(self, wrapper, mock_client):
        """Test successful track info retrieval."""
        expected_data = {
            "id": "6rqhFgbbKwnb9MLmUQDhG6",
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}]
        }
        mock_client.get_track_info.return_value = expected_data
        
        result = wrapper.get_track_info("https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6")
        
        assert result == expected_data
        mock_client.get_track_info.assert_called_once()
    
    def test_get_track_info_with_cache(self, wrapper, mock_client):
        """Test track info retrieval with caching."""
        url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
        expected_data = {
            "id": "6rqhFgbbKwnb9MLmUQDhG6",
            "name": "Test Track"
        }
        mock_client.get_track_info.return_value = expected_data
        
        # First call - should hit the API
        result1 = wrapper.get_track_info(url, use_cache=True)
        assert result1 == expected_data
        assert mock_client.get_track_info.call_count == 1
        
        # Second call - should use cache
        result2 = wrapper.get_track_info(url, use_cache=True)
        assert result2 == expected_data
        assert mock_client.get_track_info.call_count == 1  # No additional calls
    
    def test_get_track_info_without_cache(self, wrapper, mock_client):
        """Test track info retrieval without caching."""
        url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
        expected_data = {"id": "6rqhFgbbKwnb9MLmUQDhG6"}
        mock_client.get_track_info.return_value = expected_data
        
        # Multiple calls without cache should all hit the API
        wrapper.get_track_info(url, use_cache=False)
        wrapper.get_track_info(url, use_cache=False)
        
        assert mock_client.get_track_info.call_count == 2
    
    def test_get_track_lyrics_success(self, wrapper, mock_client):
        """Test successful lyrics retrieval."""
        expected_lyrics = "Test lyrics\nLine 2\nLine 3"
        mock_client.get_track_lyrics.return_value = expected_lyrics
        
        result = wrapper.get_track_lyrics(
            "https://open.spotify.com/track/123",
            require_auth=False
        )
        
        assert result == expected_lyrics
    
    def test_get_track_lyrics_auth_required(self, wrapper, mock_client):
        """Test lyrics retrieval with authentication required."""
        mock_client.get_track_lyrics.side_effect = AuthenticationRequiredError("Auth required")
        
        with pytest.raises(AuthenticationRequiredError):
            wrapper.get_track_lyrics(
                "https://open.spotify.com/track/123",
                require_auth=True
            )
    
    def test_batch_process_success(self, wrapper, mock_client):
        """Test successful batch processing."""
        urls = [
            "https://open.spotify.com/track/123",
            "https://open.spotify.com/album/456",
            "https://open.spotify.com/artist/789"
        ]
        
        mock_client.get_all_info.side_effect = [
            {"id": "123", "type": "track"},
            {"id": "456", "type": "album"},
            {"id": "789", "type": "artist"}
        ]
        
        results = wrapper.batch_process(urls, operation="all_info")
        
        assert len(results) == 3
        assert all(not isinstance(r, Exception) for r in results.values())
        assert mock_client.get_all_info.call_count == 3
    
    def test_batch_process_with_errors(self, wrapper, mock_client):
        """Test batch processing with some errors."""
        urls = [
            "https://open.spotify.com/track/123",
            "https://open.spotify.com/track/456"
        ]
        
        mock_client.get_all_info.side_effect = [
            {"id": "123", "type": "track"},
            NetworkError("Network error")
        ]
        
        results = wrapper.batch_process(
            urls,
            operation="all_info",
            continue_on_error=True
        )
        
        assert len(results) == 2
        assert not isinstance(results[urls[0]], Exception)
        assert isinstance(results[urls[1]], Exception)
    
    def test_batch_process_stop_on_error(self, wrapper, mock_client):
        """Test batch processing that stops on error."""
        urls = [
            "https://open.spotify.com/track/123",
            "https://open.spotify.com/track/456",
            "https://open.spotify.com/track/789"
        ]
        
        mock_client.get_all_info.side_effect = [
            {"id": "123"},
            NetworkError("Error"),
            {"id": "789"}  # This shouldn't be called
        ]
        
        results = wrapper.batch_process(
            urls,
            operation="all_info",
            continue_on_error=False
        )
        
        assert len(results) == 2  # Only processed first two
        assert mock_client.get_all_info.call_count == 2
    
    def test_download_media_success(self, wrapper, mock_client, temp_dir):
        """Test successful media download."""
        mock_client.download_preview_mp3.return_value = str(temp_dir / "audio.mp3")
        mock_client.download_cover.return_value = str(temp_dir / "cover.jpg")
        
        results = wrapper.download_media(
            "https://open.spotify.com/track/123",
            output_dir=temp_dir
        )
        
        assert results["audio_path"] == str(temp_dir / "audio.mp3")
        assert results["cover_path"] == str(temp_dir / "cover.jpg")
    
    def test_download_media_partial_failure(self, wrapper, mock_client, temp_dir):
        """Test media download with partial failure."""
        mock_client.download_preview_mp3.side_effect = Exception("Download failed")
        mock_client.download_cover.return_value = str(temp_dir / "cover.jpg")
        
        results = wrapper.download_media(
            "https://open.spotify.com/track/123",
            output_dir=temp_dir
        )
        
        assert results["audio_path"] is None
        assert results["cover_path"] == str(temp_dir / "cover.jpg")
    
    def test_export_results_json(self, wrapper, temp_dir):
        """Test exporting results to JSON."""
        data = {"id": "123", "name": "Test"}
        output_file = temp_dir / "output.json"
        
        wrapper.export_results(data, output_file, format="json")
        
        assert output_file.exists()
        with open(output_file) as f:
            loaded_data = json.load(f)
        assert loaded_data == data
    
    def test_export_results_csv(self, wrapper, temp_dir):
        """Test exporting results to CSV."""
        data = [
            {"id": "1", "name": "Track 1"},
            {"id": "2", "name": "Track 2"}
        ]
        output_file = temp_dir / "output.csv"
        
        wrapper.export_results(data, output_file, format="csv")
        
        assert output_file.exists()
        # Verify CSV content
        import csv
        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["id"] == "1"
        assert rows[1]["name"] == "Track 2"
    
    def test_export_results_txt(self, wrapper, temp_dir):
        """Test exporting results to text file."""
        data = {"id": "123", "name": "Test Track"}
        output_file = temp_dir / "output.txt"
        
        wrapper.export_results(data, output_file, format="txt")
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "id: 123" in content
        assert "name: Test Track" in content
    
    def test_clear_cache(self, wrapper):
        """Test cache clearing functionality."""
        # Create some cache files
        cache_files = []
        for i in range(5):
            cache_file = wrapper.cache_dir / f"test_{i}.json"
            wrapper._save_to_cache(cache_file, {"data": i})
            cache_files.append(cache_file)
        
        # Clear all cache
        cleared = wrapper.clear_cache()
        assert cleared == 5
        assert not any(f.exists() for f in cache_files)
    
    def test_clear_cache_with_age_filter(self, wrapper):
        """Test cache clearing with age filter."""
        import time
        
        # Create old cache file
        old_cache = wrapper.cache_dir / "old.json"
        wrapper._save_to_cache(old_cache, {"data": "old"})
        
        # Modify its timestamp to be 2 days old
        old_time = time.time() - (2 * 24 * 60 * 60)
        import os
        os.utime(old_cache, (old_time, old_time))
        
        # Create new cache file
        new_cache = wrapper.cache_dir / "new.json"
        wrapper._save_to_cache(new_cache, {"data": "new"})
        
        # Clear only old cache
        cleared = wrapper.clear_cache(older_than_days=1)
        
        assert cleared == 1
        assert not old_cache.exists()
        assert new_cache.exists()
    
    def test_context_manager(self, mock_client):
        """Test wrapper as context manager."""
        with patch('examples.production_usage.SpotifyClient', return_value=mock_client):
            with SpotifyScraperWrapper() as wrapper:
                assert wrapper.client is not None
            
            # Verify cleanup was called
            mock_client.close.assert_called_once()
    
    def test_error_handling_invalid_url(self, wrapper, mock_client):
        """Test error handling for invalid URLs."""
        mock_client.get_track_info.side_effect = URLError("Invalid URL")
        
        with pytest.raises(URLError):
            wrapper.get_track_info("invalid-url")
    
    def test_comprehensive_workflow(self, wrapper, mock_client, temp_dir):
        """Test a comprehensive workflow with multiple operations."""
        # Setup mock responses
        track_data = {
            "id": "123",
            "name": "Test Track",
            "artists": [{"name": "Artist"}],
            "album": {"name": "Album"}
        }
        album_data = {
            "id": "456",
            "name": "Test Album",
            "total_tracks": 10
        }
        
        mock_client.get_track_info.return_value = track_data
        mock_client.get_album_info.return_value = album_data
        mock_client.download_preview_mp3.return_value = str(temp_dir / "audio.mp3")
        
        # 1. Get track info
        track = wrapper.get_track_info("https://open.spotify.com/track/123")
        assert track["name"] == "Test Track"
        
        # 2. Get album info
        album = wrapper.get_album_info("https://open.spotify.com/album/456")
        assert album["total_tracks"] == 10
        
        # 3. Download media
        media = wrapper.download_media(
            "https://open.spotify.com/track/123",
            output_dir=temp_dir,
            download_audio=True,
            download_cover=False
        )
        assert media["audio_path"] is not None
        
        # 4. Export results
        all_results = {
            "track": track,
            "album": album,
            "media": media
        }
        wrapper.export_results(
            all_results,
            temp_dir / "results.json",
            format="json"
        )
        
        # Verify export
        assert (temp_dir / "results.json").exists()


class TestUtilityFunctions:
    """Test suite for utility functions."""
    
    def test_create_authenticated_client(self):
        """Test authenticated client creation."""
        with patch('examples.production_usage.SpotifyScraperWrapper') as mock_wrapper:
            client = create_authenticated_client(
                "cookies.txt",
                log_level="DEBUG"
            )
            
            mock_wrapper.assert_called_once_with(
                cookie_file="cookies.txt",
                log_level="DEBUG"
            )
    
    def test_analyze_spotify_url(self):
        """Test URL analysis function."""
        test_cases = [
            (
                "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
                {
                    "url": "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
                    "type": "track",
                    "id": "6rqhFgbbKwnb9MLmUQDhG6",
                    "is_valid": True
                }
            ),
            (
                "invalid-url",
                {
                    "url": "invalid-url",
                    "type": None,
                    "id": None,
                    "is_valid": False
                }
            )
        ]
        
        for url, expected in test_cases:
            result = analyze_spotify_url(url)
            assert result == expected
    
    def test_spotify_scraper_session(self):
        """Test session context manager."""
        mock_client = Mock()
        
        with patch('examples.production_usage.SpotifyScraperWrapper') as mock_wrapper_class:
            mock_wrapper_instance = Mock()
            mock_wrapper_class.return_value = mock_wrapper_instance
            
            with spotify_scraper_session(log_level="INFO") as session:
                assert session == mock_wrapper_instance
            
            # Verify close was called
            mock_wrapper_instance.close.assert_called_once()


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple features."""
    
    @pytest.fixture
    def integration_wrapper(self, temp_dir):
        """Create wrapper for integration testing."""
        with patch('examples.production_usage.SpotifyClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            wrapper = SpotifyScraperWrapper(
                cache_dir=temp_dir / "cache",
                log_level="INFO",
                max_retries=2,
                retry_delay=0.1
            )
            wrapper.client = mock_client
            yield wrapper, mock_client
    
    def test_full_playlist_processing(self, integration_wrapper, temp_dir):
        """Test processing a full playlist with caching and export."""
        wrapper, mock_client = integration_wrapper
        
        # Mock playlist data
        playlist_data = {
            "id": "playlist123",
            "name": "Test Playlist",
            "tracks": {
                "total": 3,
                "items": [
                    {"track": {"id": "1", "name": "Track 1"}},
                    {"track": {"id": "2", "name": "Track 2"}},
                    {"track": {"id": "3", "name": "Track 3"}}
                ]
            }
        }
        
        mock_client.get_playlist_info.return_value = playlist_data
        mock_client.get_track_info.side_effect = [
            {"id": "1", "name": "Track 1", "preview_url": "url1"},
            {"id": "2", "name": "Track 2", "preview_url": "url2"},
            {"id": "3", "name": "Track 3", "preview_url": "url3"}
        ]
        
        # Process playlist
        playlist = wrapper.get_playlist_info("https://open.spotify.com/playlist/123")
        
        # Process each track
        track_urls = [
            f"https://open.spotify.com/track/{item['track']['id']}"
            for item in playlist['tracks']['items']
        ]
        
        track_results = wrapper.batch_process(
            track_urls,
            operation="track_info"
        )
        
        # Export everything
        export_data = {
            "playlist": playlist,
            "tracks": track_results
        }
        
        wrapper.export_results(
            export_data,
            temp_dir / "playlist_export.json",
            format="json"
        )
        
        # Verify
        assert (temp_dir / "playlist_export.json").exists()
        assert len(track_results) == 3
        assert all(not isinstance(r, Exception) for r in track_results.values())
    
    def test_error_recovery_workflow(self, integration_wrapper):
        """Test workflow with error recovery."""
        wrapper, mock_client = integration_wrapper
        
        # Setup mock to fail initially then succeed
        mock_client.get_track_info.side_effect = [
            NetworkError("Temporary network issue"),
            {"id": "123", "name": "Success after retry"}
        ]
        
        # Should succeed after retry
        result = wrapper.get_track_info("https://open.spotify.com/track/123")
        
        assert result["name"] == "Success after retry"
        assert mock_client.get_track_info.call_count == 2
    
    def test_parallel_processing_simulation(self, integration_wrapper):
        """Test processing multiple items efficiently."""
        wrapper, mock_client = integration_wrapper
        
        # Setup different response times
        def mock_response(url):
            if "track" in url:
                return {"type": "track", "id": url.split("/")[-1]}
            elif "album" in url:
                return {"type": "album", "id": url.split("/")[-1]}
            elif "artist" in url:
                return {"type": "artist", "id": url.split("/")[-1]}
            else:
                return {"type": "playlist", "id": url.split("/")[-1]}
        
        mock_client.get_all_info.side_effect = mock_response
        
        # Process multiple URLs of different types
        urls = [
            "https://open.spotify.com/track/123",
            "https://open.spotify.com/album/456",
            "https://open.spotify.com/artist/789",
            "https://open.spotify.com/playlist/abc",
            "https://open.spotify.com/track/def"
        ]
        
        results = wrapper.batch_process(urls, operation="all_info")
        
        # Verify all processed successfully
        assert len(results) == 5
        assert all(not isinstance(r, Exception) for r in results.values())
        
        # Verify correct types
        assert results[urls[0]]["type"] == "track"
        assert results[urls[1]]["type"] == "album"
        assert results[urls[2]]["type"] == "artist"
        assert results[urls[3]]["type"] == "playlist"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])