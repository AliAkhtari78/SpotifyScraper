#!/usr/bin/env python3
"""
Full system integration test for SpotifyScraper.

This test validates that all components work together correctly:
- Configuration management
- Client initialization
- Data extraction
- Utility functions
- Error handling

Author: SpotifyScraper Development Team
Date: 2025-01-22
Version: 2.0.0
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import json

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from spotify_scraper import SpotifyClient
from spotify_scraper.config_manager import ConfigurationManager, SpotifyScraperConfig
from spotify_scraper.utils.common import (
    SpotifyDataAnalyzer,
    SpotifyDataFormatter,
    SpotifyBulkOperations,
    format_duration,
    validate_spotify_urls
)
from examples.production_usage import SpotifyScraperWrapper


class TestFullSystemIntegration:
    """Test full system integration."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_track_data(self):
        """Sample track data for testing."""
        return {
            "id": "test123",
            "name": "Test Track",
            "uri": "spotify:track:test123",
            "artists": [{"name": "Test Artist", "id": "artist123"}],
            "album": {
                "name": "Test Album",
                "id": "album123",
                "release_date": "2024-01-01"
            },
            "duration_ms": 210000,
            "popularity": 75,
            "preview_url": "https://example.com/preview.mp3",
            "images": [
                {"url": "https://example.com/large.jpg", "height": 640, "width": 640},
                {"url": "https://example.com/medium.jpg", "height": 300, "width": 300},
                {"url": "https://example.com/small.jpg", "height": 64, "width": 64}
            ]
        }
    
    @pytest.fixture
    def mock_playlist_data(self):
        """Sample playlist data for testing."""
        return {
            "id": "playlist123",
            "name": "Test Playlist",
            "description": "A test playlist",
            "owner": {"display_name": "Test User"},
            "public": True,
            "collaborative": False,
            "tracks": {
                "total": 3,
                "items": [
                    {
                        "track": {
                            "id": "track1",
                            "name": "Track 1",
                            "artists": [{"name": "Artist A"}],
                            "album": {"name": "Album 1", "release_date": "2023-01-01"},
                            "duration_ms": 180000,
                            "popularity": 80
                        }
                    },
                    {
                        "track": {
                            "id": "track2",
                            "name": "Track 2",
                            "artists": [{"name": "Artist B"}],
                            "album": {"name": "Album 2", "release_date": "2023-06-01"},
                            "duration_ms": 200000,
                            "popularity": 65
                        }
                    },
                    {
                        "track": {
                            "id": "track3",
                            "name": "Track 3",
                            "artists": [{"name": "Artist A"}],
                            "album": {"name": "Album 3", "release_date": "2024-01-01"},
                            "duration_ms": 240000,
                            "popularity": 90
                        }
                    }
                ]
            }
        }
    
    def test_configuration_to_client_workflow(self, temp_dir):
        """Test workflow from configuration to client creation."""
        # Create configuration
        config = SpotifyScraperConfig(
            log_level=LogLevel.DEBUG,
            cache=CacheConfig(
                enabled=True,
                directory=str(temp_dir / "cache")
            ),
            output_directory=str(temp_dir / "output")
        )
        
        # Create manager
        manager = ConfigurationManager(config)
        
        # Save configuration
        config_file = temp_dir / "config.json"
        manager.save_to_file(config_file)
        
        # Load configuration
        new_manager = ConfigurationManager()
        new_manager.load_from_file(config_file)
        
        # Verify configuration was preserved
        assert new_manager.config.log_level == LogLevel.DEBUG
        assert new_manager.config.cache.directory == str(temp_dir / "cache")
        
        # Create client with configuration
        with patch('spotify_scraper.config_manager.SpotifyClient') as mock_client:
            client = new_manager.create_client()
            mock_client.assert_called_once()
    
    def test_wrapper_with_utilities(self, temp_dir, mock_track_data, mock_playlist_data):
        """Test SpotifyScraperWrapper with utility functions."""
        with patch('examples.production_usage.SpotifyClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Setup mock responses
            mock_client.get_track_info.return_value = mock_track_data
            mock_client.get_playlist_info.return_value = mock_playlist_data
            
            # Create wrapper
            wrapper = SpotifyScraperWrapper(
                cache_dir=temp_dir / "cache",
                log_level="INFO"
            )
            wrapper.client = mock_client
            
            # Test track operations
            track_info = wrapper.get_track_info("https://open.spotify.com/track/test123")
            assert track_info["name"] == "Test Track"
            
            # Test playlist operations
            playlist_info = wrapper.get_playlist_info("https://open.spotify.com/playlist/playlist123")
            assert playlist_info["name"] == "Test Playlist"
            
            # Use data analyzer
            analyzer = SpotifyDataAnalyzer()
            analysis = analyzer.analyze_playlist(playlist_info)
            
            assert analysis["basic_stats"]["total_tracks"] == 3
            assert analysis["artist_stats"]["unique_artists"] == 2
            assert "Artist A" in analysis["artist_stats"]["artist_distribution"]
            
            # Use data formatter
            formatter = SpotifyDataFormatter()
            track_summary = formatter.format_track_summary(track_info)
            assert "Test Track" in track_summary
            assert "Test Artist" in track_summary
            
            # Export results
            wrapper.export_results(
                {"track": track_info, "playlist": playlist_info},
                temp_dir / "results.json",
                format="json"
            )
            
            assert (temp_dir / "results.json").exists()
    
    def test_bulk_operations_integration(self, temp_dir, mock_track_data):
        """Test bulk operations with configuration."""
        with patch('spotify_scraper.utils.common.SpotifyClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Setup mock responses
            mock_client.get_track_info.return_value = mock_track_data
            mock_client.get_album_info.return_value = {"id": "album123", "name": "Test Album"}
            mock_client.get_artist_info.return_value = {"id": "artist123", "name": "Test Artist"}
            
            # Create bulk operations handler
            bulk_ops = SpotifyBulkOperations(mock_client)
            
            # Test URL extraction
            text = """
            Check out these tracks:
            https://open.spotify.com/track/track1
            https://open.spotify.com/album/album1
            spotify:artist:artist1
            """
            
            urls = bulk_ops.extract_urls_from_text(text)
            assert len(urls) == 3
            assert any("track" in url for url in urls)
            assert any("album" in url for url in urls)
            assert any("artist" in url for url in urls)
            
            # Test dataset creation
            dataset_file = temp_dir / "dataset.json"
            bulk_ops.create_dataset(
                ["https://open.spotify.com/track/test123"],
                dataset_file,
                format="json"
            )
            
            assert dataset_file.exists()
            with open(dataset_file) as f:
                dataset = json.load(f)
            assert len(dataset) == 1
            assert dataset[0]["name"] == "Test Track"
    
    def test_error_handling_integration(self, temp_dir):
        """Test error handling across components."""
        with patch('examples.production_usage.SpotifyClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Setup client to raise errors
            mock_client.get_track_info.side_effect = NetworkError("Network error")
            
            # Create wrapper with retry logic
            wrapper = SpotifyScraperWrapper(
                cache_dir=temp_dir / "cache",
                max_retries=2,
                retry_delay=0.1
            )
            wrapper.client = mock_client
            
            # Should raise after retries
            with pytest.raises(NetworkError):
                wrapper.get_track_info("https://open.spotify.com/track/test")
            
            # Verify retries were attempted
            assert mock_client.get_track_info.call_count == 2
    
    def test_cache_integration(self, temp_dir, mock_track_data):
        """Test caching across operations."""
        with patch('examples.production_usage.SpotifyClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.get_track_info.return_value = mock_track_data
            
            # Create wrapper with cache
            wrapper = SpotifyScraperWrapper(
                cache_dir=temp_dir / "cache"
            )
            wrapper.client = mock_client
            
            url = "https://open.spotify.com/track/test123"
            
            # First call - should hit API
            result1 = wrapper.get_track_info(url)
            assert mock_client.get_track_info.call_count == 1
            
            # Second call - should use cache
            result2 = wrapper.get_track_info(url)
            assert mock_client.get_track_info.call_count == 1
            assert result1 == result2
            
            # Verify cache file exists
            cache_files = list((temp_dir / "cache").glob("*.json"))
            assert len(cache_files) == 1
    
    def test_validation_utilities(self):
        """Test URL validation utilities."""
        test_urls = [
            "https://open.spotify.com/track/valid123",
            "https://open.spotify.com/album/valid456",
            "https://invalid-url.com",
            "not-a-url",
            "spotify:track:valid789"
        ]
        
        valid, invalid = validate_spotify_urls(test_urls)
        
        assert len(valid) == 3
        assert len(invalid) == 2
        assert "https://open.spotify.com/track/valid123" in valid
        assert "https://invalid-url.com" in invalid
    
    def test_format_utilities(self):
        """Test formatting utilities."""
        # Test duration formatting
        assert format_duration(0) == "0:00"
        assert format_duration(60000) == "1:00"
        assert format_duration(3723000) == "1:02:03"
        assert format_duration(183000) == "3:03"
    
    def test_end_to_end_workflow(self, temp_dir, mock_track_data, mock_playlist_data):
        """Test complete end-to-end workflow."""
        with patch('examples.production_usage.SpotifyClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Setup comprehensive mock data
            mock_client.get_track_info.return_value = mock_track_data
            mock_client.get_playlist_info.return_value = mock_playlist_data
            mock_client.get_all_info.side_effect = lambda url: (
                mock_track_data if "track" in url else mock_playlist_data
            )
            mock_client.download_preview_mp3.return_value = str(temp_dir / "audio.mp3")
            mock_client.download_cover.return_value = str(temp_dir / "cover.jpg")
            
            # 1. Create configuration
            config = SpotifyScraperConfig(
                output_directory=str(temp_dir / "output"),
                cache=CacheConfig(directory=str(temp_dir / "cache"))
            )
            
            manager = ConfigurationManager(config)
            
            # 2. Create wrapper with configuration
            wrapper = SpotifyScraperWrapper(
                cache_dir=config.cache.directory,
                log_level=config.log_level.value
            )
            wrapper.client = mock_client
            
            # 3. Process URLs
            urls = [
                "https://open.spotify.com/track/test123",
                "https://open.spotify.com/playlist/playlist123"
            ]
            
            results = wrapper.batch_process(urls, operation="all_info")
            
            # 4. Analyze results
            analyzer = SpotifyDataAnalyzer()
            playlist_analysis = analyzer.analyze_playlist(results[urls[1]])
            
            # 5. Format results
            formatter = SpotifyDataFormatter()
            markdown_output = formatter.format_playlist_markdown(results[urls[1]])
            
            # 6. Export everything
            final_output = {
                "configuration": config.to_dict(),
                "results": {url: result for url, result in results.items() if not isinstance(result, Exception)},
                "analysis": playlist_analysis,
                "formatted_output": markdown_output
            }
            
            output_file = temp_dir / "final_results.json"
            wrapper.export_results(final_output, output_file, format="json")
            
            # Verify everything worked
            assert output_file.exists()
            assert len(results) == 2
            assert all(not isinstance(r, Exception) for r in results.values())
            assert playlist_analysis["basic_stats"]["total_tracks"] == 3
            assert "Test Playlist" in markdown_output
            
            # 7. Clean up
            wrapper.clear_cache()
            wrapper.close()


# Import required enums for the test
from spotify_scraper.config_manager import LogLevel, CacheConfig
from spotify_scraper.exceptions import NetworkError


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])