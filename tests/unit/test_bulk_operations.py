"""Unit tests for SpotifyBulkOperations class."""

import csv
import json
from unittest.mock import Mock, patch

import pytest

from spotify_scraper.utils.common import SpotifyBulkOperations


class TestSpotifyBulkOperations:
    """Test cases for SpotifyBulkOperations class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock SpotifyClient."""
        client = Mock()
        client.get_track_info = Mock(
            return_value={
                "id": "track123",
                "name": "Test Track",
                "artists": [{"name": "Test Artist"}],
                "album": {"name": "Test Album"},
                "duration_ms": 180000,
                "popularity": 75,
            }
        )
        client.get_album_info = Mock(
            return_value={
                "id": "album123",
                "name": "Test Album",
                "artists": [{"name": "Test Artist"}],
                "release_date": "2023-01-01",
                "total_tracks": 10,
            }
        )
        client.get_artist_info = Mock(
            return_value={
                "id": "artist123",
                "name": "Test Artist",
                "genres": ["pop", "rock"],
                "followers": {"total": 100000},
                "popularity": 80,
            }
        )
        client.get_track_lyrics = Mock(return_value="Test lyrics")
        client.download_preview_mp3 = Mock(return_value="/path/to/audio.mp3")
        client.download_cover = Mock(return_value="/path/to/cover.jpg")
        return client

    @pytest.fixture
    def bulk_ops(self, mock_client):
        """Create SpotifyBulkOperations instance with mock client."""
        with patch("spotify_scraper.utils.common.SpotifyClient", return_value=mock_client):
            return SpotifyBulkOperations()

    def test_process_urls_info_operation(self, bulk_ops, mock_client):
        """Test process_urls with info operation."""
        urls = [
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            "https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp",
            "https://open.spotify.com/artist/00FQb4jTyendYWaN8pK0wa",
        ]

        results = bulk_ops.process_urls(urls, operation="info")

        assert results["total_urls"] == 3
        assert results["processed"] == 3
        assert results["failed"] == 0
        assert len(results["results"]) == 3

        # Check that appropriate methods were called
        mock_client.get_track_info.assert_called_once()
        mock_client.get_album_info.assert_called_once()
        mock_client.get_artist_info.assert_called_once()

    def test_process_urls_all_info_operation(self, bulk_ops, mock_client):
        """Test process_urls with all_info operation (includes lyrics)."""
        urls = ["https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"]

        results = bulk_ops.process_urls(urls, operation="all_info")

        assert results["processed"] == 1
        assert results["failed"] == 0

        # Check that lyrics were fetched
        mock_client.get_track_lyrics.assert_called_once()
        track_result = results["results"][urls[0]]
        assert track_result["info"]["lyrics"] == "Test lyrics"

    def test_process_urls_download_operation(self, bulk_ops, mock_client, tmp_path):
        """Test process_urls with download operation."""
        urls = ["https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"]

        results = bulk_ops.process_urls(urls, operation="download", output_dir=tmp_path)

        assert results["processed"] == 1
        assert results["failed"] == 0

        # Check downloads were attempted
        mock_client.download_preview_mp3.assert_called_once()
        mock_client.download_cover.assert_called_once()

        track_result = results["results"][urls[0]]
        assert "downloads" in track_result
        assert track_result["downloads"]["audio"] == "/path/to/audio.mp3"
        assert track_result["downloads"]["cover"] == "/path/to/cover.jpg"

    def test_process_urls_with_invalid_url(self, bulk_ops):
        """Test process_urls with invalid URL."""
        urls = ["https://invalid.url/test"]

        with patch("spotify_scraper.utils.common.get_url_type", return_value="unknown"):
            results = bulk_ops.process_urls(urls, operation="info")

        assert results["processed"] == 1
        assert results["failed"] == 0
        assert "error" in results["results"][urls[0]]["info"]

    def test_export_to_json(self, bulk_ops, tmp_path):
        """Test export_to_json method."""
        data = {
            "results": {
                "url1": {"info": {"name": "Test1"}},
                "url2": {"info": {"name": "Test2"}},
            }
        }

        output_file = tmp_path / "test_export.json"
        result_path = bulk_ops.export_to_json(data, output_file)

        assert result_path == output_file
        assert output_file.exists()

        # Verify content
        with open(output_file, "r") as f:
            loaded_data = json.load(f)
        assert loaded_data == data

    def test_export_to_csv(self, bulk_ops, tmp_path):
        """Test export_to_csv method."""
        data = {
            "results": {
                "https://open.spotify.com/track/123": {
                    "type": "track",
                    "info": {
                        "id": "123",
                        "name": "Test Track",
                        "artists": [{"name": "Artist1"}, {"name": "Artist2"}],
                        "album": {"name": "Test Album"},
                        "duration_ms": 180000,
                        "popularity": 75,
                    },
                }
            }
        }

        output_file = tmp_path / "test_export.csv"
        result_path = bulk_ops.export_to_csv(data, output_file)

        assert result_path == output_file
        assert output_file.exists()

        # Verify content
        with open(output_file, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["name"] == "Test Track"
        assert rows[0]["artists"] == "Artist1, Artist2"
        assert rows[0]["album"] == "Test Album"

    def test_export_to_csv_with_errors(self, bulk_ops, tmp_path):
        """Test export_to_csv with error results."""
        data = {
            "results": {
                "url1": {"error": "Failed to process"},
                "url2": {"type": "track", "info": {"name": "Test"}},
            }
        }

        output_file = tmp_path / "test_errors.csv"
        result_path = bulk_ops.export_to_csv(data, output_file)

        assert output_file.exists()

        with open(output_file, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert any(row.get("error") == "Failed to process" for row in rows)

    def test_batch_download(self, bulk_ops, mock_client, tmp_path):
        """Test batch_download method."""
        urls = [
            "https://open.spotify.com/track/123",
            "https://open.spotify.com/album/456",
        ]

        results = bulk_ops.batch_download(urls, tmp_path, media_types=["cover"])

        assert results["total"] == 2
        assert results["successful"] == 2
        assert results["failed"] == 0

        # Verify download was called for both URLs
        assert mock_client.download_cover.call_count == 2

    def test_batch_download_with_errors(self, bulk_ops, mock_client, tmp_path):
        """Test batch_download with download errors."""
        urls = ["https://open.spotify.com/track/123"]

        # Make download fail
        mock_client.download_cover.side_effect = Exception("Download failed")

        results = bulk_ops.batch_download(urls, tmp_path, skip_errors=True)

        assert results["successful"] == 1  # Still counts as successful processing
        assert "cover_error" in results["downloads"][urls[0]]

    def test_extract_urls_from_text(self, bulk_ops):
        """Test extract_urls_from_text method."""
        text = """
        Check out this track: https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
        And this album: spotify:album:0JGOiO34nwfUdDrD612dOp
        Also: https://open.spotify.com/artist/00FQb4jTyendYWaN8pK0wa
        """

        urls = bulk_ops.extract_urls_from_text(text)

        assert len(urls) == 3
        assert "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh" in urls
        assert "https://open.spotify.com/album/0JGOiO34nwfUdDrD612dOp" in urls
        assert "https://open.spotify.com/artist/00FQb4jTyendYWaN8pK0wa" in urls

    def test_process_url_file(self, bulk_ops, tmp_path, mock_client):
        """Test process_url_file method."""
        # Create a test file with URLs
        url_file = tmp_path / "urls.txt"
        url_file.write_text(
            """
        # Test URLs
        https://open.spotify.com/track/123
        https://open.spotify.com/album/456

        # This is a comment
        spotify:artist:789
        """
        )

        results = bulk_ops.process_url_file(url_file, operation="info")

        assert results["total_urls"] == 3
        assert results["processed"] == 3
        assert results["failed"] == 0

    def test_process_urls_handles_none_lyrics_gracefully(self, bulk_ops, mock_client):
        """Test that process_urls handles None lyrics without crashing."""
        urls = ["https://open.spotify.com/track/123"]

        # Make get_track_lyrics raise an exception
        mock_client.get_track_lyrics.side_effect = Exception("Auth required")

        results = bulk_ops.process_urls(urls, operation="all_info")

        assert results["processed"] == 1
        assert results["failed"] == 0

        track_info = results["results"][urls[0]]["info"]
        assert track_info["lyrics"] is None  # Should be None, not crash
