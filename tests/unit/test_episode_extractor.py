"""Unit tests for the episode extractor module."""

import json
import pytest
from unittest.mock import Mock, patch

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import URLError
from spotify_scraper.extractors.episode import EpisodeExtractor
from spotify_scraper.core.types import EpisodeData


class TestEpisodeExtractor:
    """Test cases for EpisodeExtractor class."""

    @pytest.fixture
    def mock_browser(self):
        """Create a mock browser instance."""
        return Mock(spec=Browser)

    @pytest.fixture
    def extractor(self, mock_browser):
        """Create an EpisodeExtractor instance with mock browser."""
        return EpisodeExtractor(browser=mock_browser)

    @pytest.fixture
    def sample_episode_embed_html(self):
        """Sample HTML content from episode embed page."""
        return '''
        <html>
        <head><title>Spotify Embed</title></head>
        <body>
        <script id="__NEXT_DATA__" type="application/json">
        {
            "props": {
                "pageProps": {
                    "state": {
                        "data": {
                            "entity": {
                                "type": "episode",
                                "id": "5Q2dkZHfnGb2Y4BzzoBu2G",
                                "name": "#2333 - Protect Our Parks 15",
                                "uri": "spotify:episode:5Q2dkZHfnGb2Y4BzzoBu2G",
                                "duration": 11476329,
                                "isExplicit": true,
                                "isPlayable": true,
                                "isTrailer": false,
                                "isAudiobook": false,
                                "hasVideo": true,
                                "releaseDate": {
                                    "isoString": "2025-06-05T17:00:00Z"
                                },
                                "subtitle": "The Joe Rogan Experience",
                                "title": "#2333 - Protect Our Parks 15",
                                "audioPreview": {
                                    "url": "https://podz-content.spotifycdn.com/audio/clips/preview.mp3"
                                },
                                "videoPreview": {
                                    "url": "https://smart-preview-clips.spotifycdn.com/preview.mp4"
                                },
                                "relatedEntityUri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk",
                                "relatedEntityCoverArt": [
                                    {
                                        "url": "https://image-cdn.spotifycdn.com/image/show-image.jpg",
                                        "maxHeight": 640,
                                        "maxWidth": 640
                                    }
                                ],
                                "visualIdentity": {
                                    "backgroundBase": {"alpha": 255, "blue": 0, "green": 48, "red": 145},
                                    "image": [
                                        {
                                            "url": "https://image-cdn.spotifycdn.com/image/episode-image.jpg",
                                            "maxHeight": 640,
                                            "maxWidth": 640
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }
        </script>
        </body>
        </html>
        '''

    def test_extract_valid_episode_url(
        self, extractor, mock_browser, sample_episode_embed_html
    ):
        """Test extracting episode data from a valid URL."""
        mock_browser.get_page_content.return_value = sample_episode_embed_html

        result = extractor.extract(
            "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
        )

        assert result["id"] == "5Q2dkZHfnGb2Y4BzzoBu2G"
        assert result["name"] == "#2333 - Protect Our Parks 15"
        assert result["type"] == "episode"
        assert result["duration_ms"] == 11476329
        assert result["explicit"] == True
        assert result["has_video"] == True
        assert (
            result["audio_preview_url"]
            == "https://podz-content.spotifycdn.com/audio/clips/preview.mp3"
        )
        assert result["show"]["id"] == "4rOoJ6Egrf8K2IrywzwOMk"
        assert result["show"]["name"] == "The Joe Rogan Experience"

    def test_extract_invalid_url(self, extractor):
        """Test extraction with invalid URL."""
        result = extractor.extract("https://open.spotify.com/track/invalid")

        assert "ERROR" in result
        assert "not a Spotify episode URL" in result["ERROR"]

    def test_extract_by_id(self, extractor, mock_browser, sample_episode_embed_html):
        """Test extracting episode by ID."""
        mock_browser.get_page_content.return_value = sample_episode_embed_html

        result = extractor.extract_by_id("5Q2dkZHfnGb2Y4BzzoBu2G")

        assert result["id"] == "5Q2dkZHfnGb2Y4BzzoBu2G"
        assert result["name"] == "#2333 - Protect Our Parks 15"
        mock_browser.get_page_content.assert_called_with(
            "https://open.spotify.com/embed/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
        )

    def test_extract_preview_url(
        self, extractor, mock_browser, sample_episode_embed_html
    ):
        """Test extracting preview URL only."""
        mock_browser.get_page_content.return_value = sample_episode_embed_html

        preview_url = extractor.extract_preview_url(
            "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
        )

        assert (
            preview_url == "https://podz-content.spotifycdn.com/audio/clips/preview.mp3"
        )

    def test_extract_cover_url(self, extractor, mock_browser, sample_episode_embed_html):
        """Test extracting cover image URL."""
        mock_browser.get_page_content.return_value = sample_episode_embed_html

        cover_url = extractor.extract_cover_url(
            "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
        )

        assert cover_url == "https://image-cdn.spotifycdn.com/image/episode-image.jpg"

    def test_extract_no_preview_available(self, extractor, mock_browser):
        """Test extraction when no preview is available."""
        html = '''
        <html>
        <script id="__NEXT_DATA__" type="application/json">
        {
            "props": {
                "pageProps": {
                    "state": {
                        "data": {
                            "entity": {
                                "type": "episode",
                                "id": "test123",
                                "name": "Test Episode",
                                "uri": "spotify:episode:test123"
                            }
                        }
                    }
                }
            }
        }
        </script>
        </html>
        '''
        mock_browser.get_page_content.return_value = html

        result = extractor.extract("https://open.spotify.com/episode/test123")

        assert result["id"] == "test123"
        assert "audio_preview_url" not in result or result["audio_preview_url"] == ""

    def test_extract_malformed_html(self, extractor, mock_browser):
        """Test extraction with malformed HTML."""
        mock_browser.get_page_content.return_value = "<html>No data here</html>"

        result = extractor.extract("https://open.spotify.com/episode/test")

        assert "ERROR" in result
        assert "Could not find episode data" in result["ERROR"]

    def test_extract_network_error(self, extractor, mock_browser):
        """Test extraction when network error occurs."""
        mock_browser.get_page_content.side_effect = Exception("Network error")

        result = extractor.extract("https://open.spotify.com/episode/test")

        assert "ERROR" in result
        assert "Network error" in result["ERROR"]

    def test_spotify_uri_support(
        self, extractor, mock_browser, sample_episode_embed_html
    ):
        """Test extraction with Spotify URI."""
        mock_browser.get_page_content.return_value = sample_episode_embed_html

        result = extractor.extract("spotify:episode:5Q2dkZHfnGb2Y4BzzoBu2G")

        assert result["id"] == "5Q2dkZHfnGb2Y4BzzoBu2G"
        assert result["uri"] == "spotify:episode:5Q2dkZHfnGb2Y4BzzoBu2G"

    def test_extract_full_audio_url(self, extractor, mock_browser):
        """Test extracting full audio URLs (requires Premium)."""
        html = '''
        <html>
        <script id="__NEXT_DATA__" type="application/json">
        {
            "props": {
                "pageProps": {
                    "state": {
                        "data": {
                            "entity": {
                                "type": "episode",
                                "id": "test",
                                "name": "Test",
                                "uri": "spotify:episode:test"
                            },
                            "defaultAudioFileObject": {
                                "url": [
                                    "https://audio4-ak.spotifycdn.com/audio/full-episode.mp4"
                                ],
                                "format": "MP4_128_CBCS",
                                "fileId": "abc123"
                            }
                        }
                    }
                }
            }
        }
        </script>
        </html>
        '''
        mock_browser.get_page_content.return_value = html

        full_urls = extractor.extract_full_audio_url(
            "https://open.spotify.com/episode/test"
        )

        assert full_urls == ["https://audio4-ak.spotifycdn.com/audio/full-episode.mp4"]