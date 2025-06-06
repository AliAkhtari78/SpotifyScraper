"""Unit tests for the show extractor module."""

import json
import pytest
from unittest.mock import Mock, patch

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import URLError
from spotify_scraper.extractors.show import ShowExtractor
from spotify_scraper.core.types import ShowData


class TestShowExtractor:
    """Test cases for ShowExtractor class."""

    @pytest.fixture
    def mock_browser(self):
        """Create a mock browser instance."""
        return Mock(spec=Browser)

    @pytest.fixture
    def extractor(self, mock_browser):
        """Create a ShowExtractor instance with mock browser."""
        return ShowExtractor(browser=mock_browser)

    @pytest.fixture
    def sample_show_embed_html(self):
        """Sample HTML content from show embed page (returns episode data)."""
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
                                "name": "Latest Episode",
                                "uri": "spotify:episode:5Q2dkZHfnGb2Y4BzzoBu2G",
                                "subtitle": "The Joe Rogan Experience",
                                "relatedEntityUri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk",
                                "relatedEntityCoverArt": [
                                    {
                                        "url": "https://image-cdn.spotifycdn.com/image/show-cover.jpg",
                                        "maxHeight": 640,
                                        "maxWidth": 640
                                    }
                                ],
                                "visualIdentity": {
                                    "backgroundBase": {"alpha": 255, "blue": 0, "green": 48, "red": 145}
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

    @pytest.fixture
    def sample_regular_show_html(self):
        """Sample HTML content from regular show page for enrichment."""
        return '''
        <html>
        <head>
            <meta property="og:description" content="The official podcast of comedian Joe Rogan." />
            <script type="application/ld+json">
            {
                "@type": "PodcastSeries",
                "name": "The Joe Rogan Experience",
                "description": "The official podcast of comedian Joe Rogan.",
                "publisher": {
                    "@type": "Organization",
                    "name": "Joe Rogan"
                }
            }
            </script>
        </head>
        <body></body>
        </html>
        '''

    def test_extract_valid_show_url(
        self, extractor, mock_browser, sample_show_embed_html, sample_regular_show_html
    ):
        """Test extracting show data from a valid URL."""
        # Mock both embed and regular page requests
        mock_browser.get_page_content.side_effect = [
            sample_show_embed_html,  # First call for embed
            sample_regular_show_html,  # Second call for enrichment
        ]

        result = extractor.extract(
            "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"
        )

        assert result["id"] == "4rOoJ6Egrf8K2IrywzwOMk"
        assert result["name"] == "The Joe Rogan Experience"
        assert result["type"] == "show"
        assert result["uri"] == "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
        assert result["publisher"] == "Joe Rogan"
        assert result["description"] == "The official podcast of comedian Joe Rogan."
        assert len(result["images"]) > 0
        assert (
            result["images"][0]["url"]
            == "https://image-cdn.spotifycdn.com/image/show-cover.jpg"
        )

    def test_extract_invalid_url(self, extractor):
        """Test extraction with invalid URL."""
        result = extractor.extract("https://open.spotify.com/track/invalid")

        assert "ERROR" in result
        assert "not a Spotify show URL" in result["ERROR"]

    def test_extract_by_id(
        self, extractor, mock_browser, sample_show_embed_html, sample_regular_show_html
    ):
        """Test extracting show by ID."""
        mock_browser.get_page_content.side_effect = [
            sample_show_embed_html,
            sample_regular_show_html,
        ]

        result = extractor.extract_by_id("4rOoJ6Egrf8K2IrywzwOMk")

        assert result["id"] == "4rOoJ6Egrf8K2IrywzwOMk"
        assert result["name"] == "The Joe Rogan Experience"

        # Should call embed URL
        first_call = mock_browser.get_page_content.call_args_list[0]
        assert "https://open.spotify.com/embed/show/4rOoJ6Egrf8K2IrywzwOMk" in str(
            first_call
        )

    def test_extract_cover_url(
        self, extractor, mock_browser, sample_show_embed_html, sample_regular_show_html
    ):
        """Test extracting cover image URL."""
        mock_browser.get_page_content.side_effect = [
            sample_show_embed_html,
            sample_regular_show_html,
        ]

        cover_url = extractor.extract_cover_url(
            "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"
        )

        assert cover_url == "https://image-cdn.spotifycdn.com/image/show-cover.jpg"

    def test_extract_episodes_list(self, extractor, mock_browser):
        """Test extracting episodes list from show."""
        html_with_episodes = '''
        <html>
        <script id="__NEXT_DATA__" type="application/json">
        {
            "props": {
                "pageProps": {
                    "state": {
                        "data": {
                            "entity": {
                                "type": "episode",
                                "subtitle": "Test Show",
                                "relatedEntityUri": "spotify:show:test123"
                            },
                            "episodeList": {
                                "items": [
                                    {
                                        "id": "ep1",
                                        "name": "Episode 1",
                                        "uri": "spotify:episode:ep1",
                                        "duration": 1800000,
                                        "releaseDate": {"isoString": "2025-06-01T00:00:00Z"}
                                    },
                                    {
                                        "id": "ep2",
                                        "name": "Episode 2",
                                        "uri": "spotify:episode:ep2",
                                        "duration": 2400000,
                                        "releaseDate": {"isoString": "2025-06-02T00:00:00Z"}
                                    }
                                ],
                                "totalCount": 2
                            }
                        }
                    }
                }
            }
        }
        </script>
        </html>
        '''
        mock_browser.get_page_content.return_value = html_with_episodes

        episodes = extractor.extract_episodes_list(
            "https://open.spotify.com/show/test123"
        )

        assert len(episodes) == 2
        assert episodes[0]["id"] == "ep1"
        assert episodes[0]["name"] == "Episode 1"
        assert episodes[1]["id"] == "ep2"
        assert episodes[1]["name"] == "Episode 2"

    def test_extract_malformed_html(self, extractor, mock_browser):
        """Test extraction with malformed HTML."""
        mock_browser.get_page_content.return_value = "<html>No data here</html>"

        result = extractor.extract("https://open.spotify.com/show/test")

        assert "ERROR" in result
        assert "Could not find show data" in result["ERROR"]

    def test_extract_network_error(self, extractor, mock_browser):
        """Test extraction when network error occurs."""
        mock_browser.get_page_content.side_effect = Exception("Network error")

        result = extractor.extract("https://open.spotify.com/show/test")

        assert "ERROR" in result
        assert "Network error" in result["ERROR"]

    def test_spotify_uri_support(
        self, extractor, mock_browser, sample_show_embed_html, sample_regular_show_html
    ):
        """Test extraction with Spotify URI."""
        mock_browser.get_page_content.side_effect = [
            sample_show_embed_html,
            sample_regular_show_html,
        ]

        result = extractor.extract("spotify:show:4rOoJ6Egrf8K2IrywzwOMk")

        assert result["id"] == "4rOoJ6Egrf8K2IrywzwOMk"
        assert result["uri"] == "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"

    def test_direct_show_data_response(self, extractor, mock_browser):
        """Test when embed page returns actual show data (not episode)."""
        html_with_show_data = '''
        <html>
        <script id="__NEXT_DATA__" type="application/json">
        {
            "props": {
                "pageProps": {
                    "state": {
                        "data": {
                            "entity": {
                                "type": "show",
                                "id": "direct123",
                                "name": "Direct Show",
                                "uri": "spotify:show:direct123",
                                "publisher": {"name": "Direct Publisher"},
                                "htmlDescription": "A direct show description",
                                "topics": [{"title": "Comedy"}, {"title": "Talk"}]
                            }
                        }
                    }
                }
            }
        }
        </script>
        </html>
        '''
        mock_browser.get_page_content.return_value = html_with_show_data

        result = extractor.extract("https://open.spotify.com/show/direct123")

        assert result["id"] == "direct123"
        assert result["name"] == "Direct Show"
        assert result["publisher"] == "Direct Publisher"
        assert result["description"] == "A direct show description"
        assert "Comedy" in result["categories"]
        assert "Talk" in result["categories"]

    def test_enrichment_failure(self, extractor, mock_browser, sample_show_embed_html):
        """Test when enrichment from regular page fails."""
        # First call succeeds, second call (enrichment) fails
        mock_browser.get_page_content.side_effect = [
            sample_show_embed_html,
            Exception("Enrichment failed"),
        ]

        result = extractor.extract(
            "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"
        )

        # Should still have basic data from episode
        assert result["id"] == "4rOoJ6Egrf8K2IrywzwOMk"
        assert result["name"] == "The Joe Rogan Experience"
        assert result["type"] == "show"
        # But no enriched data - only default description
        assert result.get("description", "").startswith("Podcast show:")