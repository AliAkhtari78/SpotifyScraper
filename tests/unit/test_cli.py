"""
Unit tests for the CLI module.

These tests verify that the CLI commands work correctly and handle
various input scenarios appropriately.
"""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path

from spotify_scraper.cli import cli
from spotify_scraper.cli.commands import track, album, artist, playlist, download
from spotify_scraper.exceptions import SpotifyScraperError, AuthenticationRequiredError


class TestCLI:
    """Tests for the main CLI interface."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    def test_cli_help(self, runner):
        """Test that the CLI shows help when no command is provided."""
        result = runner.invoke(cli)
        assert result.exit_code == 0
        assert "SpotifyScraper - Extract data from Spotify's web interface" in result.output
        assert "Commands:" in result.output
    
    def test_cli_version(self, runner):
        """Test the --version flag."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "version" in result.output.lower()
    
    def test_cli_with_log_level(self, runner):
        """Test setting log level."""
        with patch('spotify_scraper.utils.logger.configure_logging') as mock_config:
            result = runner.invoke(cli, ['--log-level', 'DEBUG', 'track', 'https://example.com'])
            mock_config.assert_called_with(level='DEBUG')


class TestTrackCommand:
    """Tests for the track command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock SpotifyClient."""
        client = Mock()
        client.get_track_info = Mock(return_value={
            "id": "123",
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}],
            "album": {"name": "Test Album"},
            "duration_ms": 180000
        })
        client.get_track_info_with_lyrics = Mock(return_value={
            "id": "123",
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}],
            "album": {"name": "Test Album"},
            "duration_ms": 180000,
            "lyrics": "Test lyrics here"
        })
        client.close = Mock()
        return client
    
    def test_track_basic(self, runner, mock_client):
        """Test basic track extraction."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(track.track, ['https://open.spotify.com/track/123'])
            
            assert result.exit_code == 0
            assert "Test Track" in result.output
            mock_client.get_track_info.assert_called_once()
    
    def test_track_with_output_file(self, runner, mock_client):
        """Test track extraction with output to file."""
        with runner.isolated_filesystem():
            with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
                result = runner.invoke(track.track, [
                    'https://open.spotify.com/track/123',
                    '-o', 'track.json'
                ])
                
                assert result.exit_code == 0
                assert Path('track.json').exists()
                
                # Verify JSON content
                with open('track.json') as f:
                    data = json.load(f)
                    assert data['name'] == 'Test Track'
    
    def test_track_with_lyrics(self, runner, mock_client):
        """Test track extraction with lyrics."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(track.track, [
                'https://open.spotify.com/track/123',
                '--with-lyrics'
            ])
            
            assert result.exit_code == 0
            mock_client.get_track_info_with_lyrics.assert_called_once()
    
    def test_track_pretty_format(self, runner, mock_client):
        """Test track extraction with pretty formatting."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(track.track, [
                'https://open.spotify.com/track/123',
                '--pretty'
            ])
            
            assert result.exit_code == 0
            # Pretty format should have indentation
            assert '  ' in result.output or '\n' in result.output
    
    def test_track_table_format(self, runner, mock_client):
        """Test track extraction with table format."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            with patch('spotify_scraper.cli.utils.format_as_table', return_value="Table output"):
                result = runner.invoke(track.track, [
                    'https://open.spotify.com/track/123',
                    '--format', 'table'
                ])
                
                assert result.exit_code == 0
                assert "Table output" in result.output
    
    def test_track_error_handling(self, runner):
        """Test track command error handling."""
        mock_client = Mock()
        mock_client.get_track_info = Mock(side_effect=SpotifyScraperError("Network error"))
        mock_client.close = Mock()
        
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(track.track, ['https://open.spotify.com/track/123'])
            
            assert result.exit_code == 1
            assert "Scraping error" in result.output


class TestAlbumCommand:
    """Tests for the album command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock SpotifyClient."""
        client = Mock()
        client.get_album_info = Mock(return_value={
            "id": "456",
            "name": "Test Album",
            "artists": [{"name": "Test Artist"}],
            "release_date": "2023-01-01",
            "total_tracks": 10,
            "tracks": {
                "items": [
                    {"name": "Track 1", "duration_ms": 180000},
                    {"name": "Track 2", "duration_ms": 200000}
                ]
            }
        })
        client.close = Mock()
        return client
    
    def test_album_basic(self, runner, mock_client):
        """Test basic album extraction."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(album.album, ['https://open.spotify.com/album/456'])
            
            assert result.exit_code == 0
            assert "Test Album" in result.output
            mock_client.get_album_info.assert_called_once()
    
    def test_album_tracks_only(self, runner, mock_client):
        """Test album extraction with tracks only."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(album.album, [
                'https://open.spotify.com/album/456',
                '--tracks-only'
            ])
            
            assert result.exit_code == 0
            # Should show track listing
            assert "Track 1" in result.output or "tracks" in result.output


class TestArtistCommand:
    """Tests for the artist command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock SpotifyClient."""
        client = Mock()
        client.get_artist_info = Mock(return_value={
            "id": "789",
            "name": "Test Artist",
            "genres": ["rock", "pop"],
            "popularity": 85,
            "followers": {"total": 1000000},
            "top_tracks": [
                {"name": "Hit Song 1"},
                {"name": "Hit Song 2"}
            ],
            "albums": [
                {"name": "Album 1"},
                {"name": "Album 2"}
            ]
        })
        client.close = Mock()
        return client
    
    def test_artist_basic(self, runner, mock_client):
        """Test basic artist extraction."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(artist.artist, ['https://open.spotify.com/artist/789'])
            
            assert result.exit_code == 0
            assert "Test Artist" in result.output
            mock_client.get_artist_info.assert_called_once()
    
    def test_artist_top_tracks_only(self, runner, mock_client):
        """Test artist extraction with top tracks only."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(artist.artist, [
                'https://open.spotify.com/artist/789',
                '--top-tracks-only'
            ])
            
            assert result.exit_code == 0
            # Should show only top tracks
            assert "Hit Song 1" in result.output or "top_tracks" in result.output


class TestPlaylistCommand:
    """Tests for the playlist command."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock SpotifyClient."""
        client = Mock()
        client.get_playlist_info = Mock(return_value={
            "id": "abc",
            "name": "Test Playlist",
            "owner": {"display_name": "Test User"},
            "description": "A test playlist",
            "tracks": {
                "total": 50,
                "items": [
                    {"track": {"name": "Song 1", "artists": [{"name": "Artist 1"}]}},
                    {"track": {"name": "Song 2", "artists": [{"name": "Artist 2"}]}}
                ]
            },
            "public": True,
            "collaborative": False
        })
        client.close = Mock()
        return client
    
    def test_playlist_basic(self, runner, mock_client):
        """Test basic playlist extraction."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(playlist.playlist, ['https://open.spotify.com/playlist/abc'])
            
            assert result.exit_code == 0
            assert "Test Playlist" in result.output
            mock_client.get_playlist_info.assert_called_once()
    
    def test_playlist_with_limit(self, runner, mock_client):
        """Test playlist extraction with track limit."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(playlist.playlist, [
                'https://open.spotify.com/playlist/abc',
                '--limit', '10'
            ])
            
            assert result.exit_code == 0
            # Limit info should be shown
            assert "10" in result.output or "limited" in result.output.lower()


class TestDownloadCommand:
    """Tests for the download commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock SpotifyClient."""
        client = Mock()
        client.download_cover = Mock(return_value="/path/to/cover.jpg")
        client.download_preview_mp3 = Mock(return_value="/path/to/preview.mp3")
        client.get_track_info = Mock(return_value={
            "name": "Test Track",
            "artists": [{"name": "Test Artist"}],
            "preview_url": "https://example.com/preview.mp3"
        })
        client.close = Mock()
        return client
    
    def test_download_cover(self, runner, mock_client):
        """Test downloading cover image."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(download.download, [
                'cover',
                'https://open.spotify.com/track/123'
            ])
            
            assert result.exit_code == 0
            assert "saved to" in result.output
            mock_client.download_cover.assert_called_once()
    
    def test_download_track(self, runner, mock_client):
        """Test downloading track preview."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(download.download, [
                'track',
                'https://open.spotify.com/track/123'
            ])
            
            assert result.exit_code == 0
            assert "saved to" in result.output
            mock_client.download_preview_mp3.assert_called_once()
    
    def test_download_track_with_cover(self, runner, mock_client):
        """Test downloading track with embedded cover."""
        with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
            result = runner.invoke(download.download, [
                'track',
                'https://open.spotify.com/track/123',
                '--with-cover'
            ])
            
            assert result.exit_code == 0
            mock_client.download_preview_mp3.assert_called_with(
                url='https://open.spotify.com/track/123',
                path='.',
                with_cover=True
            )
    
    def test_download_batch(self, runner, mock_client):
        """Test batch download from file."""
        with runner.isolated_filesystem():
            # Create a test URLs file
            with open('urls.txt', 'w') as f:
                f.write("https://open.spotify.com/track/123\n")
                f.write("https://open.spotify.com/track/456\n")
                f.write("# This is a comment\n")
                f.write("\n")  # Empty line
                f.write("https://open.spotify.com/album/789\n")
            
            with patch('spotify_scraper.cli.utils.create_client', return_value=mock_client):
                with patch('spotify_scraper.utils.url.get_url_type') as mock_get_type:
                    mock_get_type.side_effect = ['track', 'track', 'album']
                    
                    result = runner.invoke(download.download, [
                        'batch',
                        'urls.txt',
                        '--type', 'both'
                    ])
                    
                    assert result.exit_code == 0
                    assert "Found 3 URLs" in result.output
                    assert "Successful:" in result.output