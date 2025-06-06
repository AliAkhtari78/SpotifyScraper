"""Unit tests for the show extractor module."""

import pytest


# Simple mock browser for testing (avoid complex imports)
class MockBrowser:
    """Mock browser for testing extractors without network requests."""

    def __init__(self, html_content):
        self.html_content = html_content
        self._call_count = 0
        self._responses = []

    def get_page_content(self, url):
        """Return the mock HTML content regardless of URL."""
        if self._responses:
            # Return responses in order if multiple were set
            response = self._responses[self._call_count]
            self._call_count += 1
            return response
        return self.html_content

    def get(self, url):
        """Alias for get_page_content to match the real Browser interface."""
        return self.get_page_content(url)

    def set_responses(self, responses):
        """Set multiple responses for sequential calls."""
        self._responses = responses
        self._call_count = 0


# Import the ShowExtractor from the package
from spotify_scraper.extractors.show import ShowExtractor


class TestShowExtractor:
    """Test cases for ShowExtractor class."""

    @pytest.fixture
    def extractor(self):
        """Create a ShowExtractor instance with mock browser."""
        # Will be created with specific HTML content in each test
        return ShowExtractor

    @pytest.fixture
    def sample_show_embed_html(self):
        """Sample HTML content from show embed page (returns episode data)."""
        return """
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
        """

    @pytest.fixture
    def sample_regular_show_html(self):
        """Sample HTML content from regular show page for enrichment."""
        return """
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
        """

    def test_extract_valid_show_url(
        self, extractor, sample_show_embed_html, sample_regular_show_html
    ):
        """Test extracting show data from a valid URL."""
        # Mock both embed and regular page requests
        mock_browser = MockBrowser("")
        mock_browser.set_responses(
            [
                sample_show_embed_html,  # First call for embed
                sample_regular_show_html,  # Second call for enrichment
            ]
        )
        show_extractor = extractor(browser=mock_browser)

        result = show_extractor.extract("https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk")

        assert result["id"] == "4rOoJ6Egrf8K2IrywzwOMk"
        assert result["name"] == "The Joe Rogan Experience"
        assert result["type"] == "show"
        assert result["uri"] == "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
        assert result["publisher"] == "Joe Rogan"
        assert result["description"] == "The official podcast of comedian Joe Rogan."
        assert len(result["images"]) > 0
        assert result["images"][0]["url"] == "https://image-cdn.spotifycdn.com/image/show-cover.jpg"

    def test_extract_invalid_url(self, extractor):
        """Test extraction with invalid URL."""
        mock_browser = MockBrowser("")
        show_extractor = extractor(browser=mock_browser)
        result = show_extractor.extract("https://open.spotify.com/track/invalid")

        assert "ERROR" in result
        assert "not a Spotify show URL" in result["ERROR"]

    def test_extract_by_id(self, extractor, sample_show_embed_html, sample_regular_show_html):
        """Test extracting show by ID."""
        mock_browser = MockBrowser("")
        mock_browser.set_responses(
            [
                sample_show_embed_html,
                sample_regular_show_html,
            ]
        )
        show_extractor = extractor(browser=mock_browser)

        result = show_extractor.extract_by_id("4rOoJ6Egrf8K2IrywzwOMk")

        assert result["id"] == "4rOoJ6Egrf8K2IrywzwOMk"
        assert result["name"] == "The Joe Rogan Experience"

    def test_extract_cover_url(self, extractor, sample_show_embed_html, sample_regular_show_html):
        """Test extracting cover image URL."""
        mock_browser = MockBrowser("")
        mock_browser.set_responses(
            [
                sample_show_embed_html,
                sample_regular_show_html,
            ]
        )
        show_extractor = extractor(browser=mock_browser)

        cover_url = show_extractor.extract_cover_url(
            "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"
        )

        assert cover_url == "https://image-cdn.spotifycdn.com/image/show-cover.jpg"

    def test_extract_episodes_list(self, extractor):
        """Test extracting episodes list from show."""
        html_with_episodes = """
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
        """
        mock_browser = MockBrowser(html_with_episodes)
        show_extractor = extractor(browser=mock_browser)

        episodes = show_extractor.extract_episodes_list("https://open.spotify.com/show/test123")

        assert len(episodes) == 2
        assert episodes[0]["id"] == "ep1"
        assert episodes[0]["name"] == "Episode 1"
        assert episodes[1]["id"] == "ep2"
        assert episodes[1]["name"] == "Episode 2"

    def test_extract_malformed_html(self, extractor):
        """Test extraction with malformed HTML."""
        mock_browser = MockBrowser("<html>No data here</html>")
        show_extractor = extractor(browser=mock_browser)

        result = show_extractor.extract("https://open.spotify.com/show/test")

        assert "ERROR" in result
        assert "Could not find show data" in result["ERROR"]

    def test_extract_network_error(self, extractor):
        """Test extraction when network error occurs."""

        # Create a mock browser that raises an exception
        class ErrorBrowser(MockBrowser):
            def get_page_content(self, url):
                raise Exception("Network error")

        mock_browser = ErrorBrowser("")
        show_extractor = extractor(browser=mock_browser)

        result = show_extractor.extract("https://open.spotify.com/show/test")

        assert "ERROR" in result
        assert "Network error" in result["ERROR"]

    def test_spotify_uri_support(self, extractor, sample_show_embed_html, sample_regular_show_html):
        """Test extraction with Spotify URI."""
        mock_browser = MockBrowser("")
        mock_browser.set_responses(
            [
                sample_show_embed_html,
                sample_regular_show_html,
            ]
        )
        show_extractor = extractor(browser=mock_browser)

        result = show_extractor.extract("spotify:show:4rOoJ6Egrf8K2IrywzwOMk")

        assert result["id"] == "4rOoJ6Egrf8K2IrywzwOMk"
        assert result["uri"] == "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"

    def test_direct_show_data_response(self, extractor):
        """Test when embed page returns actual show data (not episode)."""
        html_with_show_data = """
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
        """
        mock_browser = MockBrowser(html_with_show_data)
        show_extractor = extractor(browser=mock_browser)

        result = show_extractor.extract("https://open.spotify.com/show/direct123")

        assert result["id"] == "direct123"
        assert result["name"] == "Direct Show"
        assert result["publisher"] == "Direct Publisher"
        assert result["description"] == "A direct show description"
        assert "Comedy" in result["categories"]
        assert "Talk" in result["categories"]

    def test_enrichment_failure(self, extractor, sample_show_embed_html):
        """Test when enrichment from regular page fails."""

        # Create a mock browser that fails on second call
        class PartialErrorBrowser(MockBrowser):
            def __init__(self, html_content):
                super().__init__(html_content)
                self._call_count_internal = 0

            def get_page_content(self, url):
                if self._call_count_internal == 0:
                    self._call_count_internal += 1
                    return self.html_content
                else:
                    raise Exception("Enrichment failed")

        mock_browser = PartialErrorBrowser(sample_show_embed_html)
        show_extractor = extractor(browser=mock_browser)

        result = show_extractor.extract("https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk")

        # Should still have basic data from episode
        assert result["id"] == "4rOoJ6Egrf8K2IrywzwOMk"
        assert result["name"] == "The Joe Rogan Experience"
        assert result["type"] == "show"
        # But no enriched data - only default description
        assert result.get("description", "").startswith("Podcast show:")
