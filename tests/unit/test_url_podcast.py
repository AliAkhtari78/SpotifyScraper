"""Unit tests for podcast URL utilities."""

import pytest

from spotify_scraper.core.exceptions import URLError
from spotify_scraper.utils.url import (
    build_url,
    convert_spotify_uri_to_url,
    convert_to_embed_url,
    convert_url_to_spotify_uri,
    extract_id,
    get_url_type,
    is_spotify_url,
    validate_url,
)


class TestPodcastURLUtilities:
    """Test cases for podcast URL handling in the url utilities module."""

    def test_is_spotify_url_podcast(self):
        """Test is_spotify_url with podcast URLs."""
        # Valid episode URLs
        assert is_spotify_url("https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G")
        assert is_spotify_url("https://open.spotify.com/embed/episode/5Q2dkZHfnGb2Y4BzzoBu2G")
        assert is_spotify_url("spotify:episode:5Q2dkZHfnGb2Y4BzzoBu2G")

        # Valid show URLs
        assert is_spotify_url("https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk")
        assert is_spotify_url("https://open.spotify.com/embed/show/4rOoJ6Egrf8K2IrywzwOMk")
        assert is_spotify_url("spotify:show:4rOoJ6Egrf8K2IrywzwOMk")

        # Invalid URLs
        assert not is_spotify_url("https://example.com/episode/123")
        assert not is_spotify_url("https://podcasts.apple.com/show/123")

    def test_get_url_type_podcast(self):
        """Test get_url_type with podcast URLs."""
        # Episode URLs
        assert get_url_type("https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G") == "episode"
        assert (
            get_url_type("https://open.spotify.com/embed/episode/5Q2dkZHfnGb2Y4BzzoBu2G")
            == "episode"
        )
        assert get_url_type("spotify:episode:5Q2dkZHfnGb2Y4BzzoBu2G") == "episode"

        # Show URLs
        assert get_url_type("https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk") == "show"
        assert get_url_type("https://open.spotify.com/embed/show/4rOoJ6Egrf8K2IrywzwOMk") == "show"
        assert get_url_type("spotify:show:4rOoJ6Egrf8K2IrywzwOMk") == "show"

        # With query parameters
        assert (
            get_url_type("https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G?si=abcd")
            == "episode"
        )
        assert (
            get_url_type("https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk?si=efgh") == "show"
        )

    def test_extract_id_podcast(self):
        """Test extract_id with podcast URLs."""
        # Episode IDs
        assert (
            extract_id("https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G")
            == "5Q2dkZHfnGb2Y4BzzoBu2G"
        )
        assert (
            extract_id("https://open.spotify.com/embed/episode/5Q2dkZHfnGb2Y4BzzoBu2G")
            == "5Q2dkZHfnGb2Y4BzzoBu2G"
        )
        assert extract_id("spotify:episode:5Q2dkZHfnGb2Y4BzzoBu2G") == "5Q2dkZHfnGb2Y4BzzoBu2G"

        # Show IDs
        assert (
            extract_id("https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk")
            == "4rOoJ6Egrf8K2IrywzwOMk"
        )
        assert (
            extract_id("https://open.spotify.com/embed/show/4rOoJ6Egrf8K2IrywzwOMk")
            == "4rOoJ6Egrf8K2IrywzwOMk"
        )
        assert extract_id("spotify:show:4rOoJ6Egrf8K2IrywzwOMk") == "4rOoJ6Egrf8K2IrywzwOMk"

        # With query parameters
        assert (
            extract_id(
                "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G?si=abcd&utm_source=copy"
            )
            == "5Q2dkZHfnGb2Y4BzzoBu2G"
        )

    def test_convert_to_embed_url_podcast(self):
        """Test convert_to_embed_url with podcast URLs."""
        # Episode conversions
        assert (
            convert_to_embed_url("https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G")
            == "https://open.spotify.com/embed/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
        )
        assert (
            convert_to_embed_url("spotify:episode:5Q2dkZHfnGb2Y4BzzoBu2G")
            == "https://open.spotify.com/embed/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
        )

        # Show conversions
        assert (
            convert_to_embed_url("https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk")
            == "https://open.spotify.com/embed/show/4rOoJ6Egrf8K2IrywzwOMk"
        )
        assert (
            convert_to_embed_url("spotify:show:4rOoJ6Egrf8K2IrywzwOMk")
            == "https://open.spotify.com/embed/show/4rOoJ6Egrf8K2IrywzwOMk"
        )

        # Already embed URLs should remain unchanged
        assert (
            convert_to_embed_url("https://open.spotify.com/embed/episode/5Q2dkZHfnGb2Y4BzzoBu2G")
            == "https://open.spotify.com/embed/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
        )

    def test_validate_url_podcast(self):
        """Test validate_url with podcast URLs."""
        # Valid episode URLs
        assert validate_url(
            "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G",
            expected_type="episode",
        )
        assert validate_url("spotify:episode:5Q2dkZHfnGb2Y4BzzoBu2G", expected_type="episode")

        # Valid show URLs
        assert validate_url(
            "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk",
            expected_type="show",
        )
        assert validate_url("spotify:show:4rOoJ6Egrf8K2IrywzwOMk", expected_type="show")

        # Type mismatch should raise error
        with pytest.raises(URLError, match="not a Spotify episode URL"):
            validate_url(
                "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk",
                expected_type="episode",
            )

        with pytest.raises(URLError, match="not a Spotify show URL"):
            validate_url(
                "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G",
                expected_type="show",
            )

    def test_build_url_podcast(self):
        """Test build_url with podcast types."""
        # Build episode URL
        assert (
            build_url("episode", "5Q2dkZHfnGb2Y4BzzoBu2G")
            == "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
        )

        # Build show URL
        assert (
            build_url("show", "4rOoJ6Egrf8K2IrywzwOMk")
            == "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"
        )

        # Build embed URLs
        assert (
            build_url("episode", "5Q2dkZHfnGb2Y4BzzoBu2G", embed=True)
            == "https://open.spotify.com/embed/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
        )
        assert (
            build_url("show", "4rOoJ6Egrf8K2IrywzwOMk", embed=True)
            == "https://open.spotify.com/embed/show/4rOoJ6Egrf8K2IrywzwOMk"
        )

        # With query parameters
        assert (
            build_url("episode", "5Q2dkZHfnGb2Y4BzzoBu2G", query_params={"si": "abc123"})
            == "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G?si=abc123"
        )

    def test_spotify_uri_conversion_podcast(self):
        """Test URI to URL and URL to URI conversions for podcasts."""
        # Episode conversions
        episode_url = "https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
        episode_uri = "spotify:episode:5Q2dkZHfnGb2Y4BzzoBu2G"

        assert convert_spotify_uri_to_url(episode_uri) == episode_url
        assert convert_url_to_spotify_uri(episode_url) == episode_uri

        # Show conversions
        show_url = "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"
        show_uri = "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"

        assert convert_spotify_uri_to_url(show_uri) == show_url
        assert convert_url_to_spotify_uri(show_url) == show_uri

        # Embed URLs should also convert properly
        assert (
            convert_url_to_spotify_uri(
                "https://open.spotify.com/embed/episode/5Q2dkZHfnGb2Y4BzzoBu2G"
            )
            == episode_uri
        )
        assert (
            convert_url_to_spotify_uri("https://open.spotify.com/embed/show/4rOoJ6Egrf8K2IrywzwOMk")
            == show_uri
        )

    def test_edge_cases_podcast(self):
        """Test edge cases with podcast URLs."""
        # Very long IDs
        long_id = "a" * 50
        assert extract_id(f"https://open.spotify.com/episode/{long_id}") == long_id
        assert extract_id(f"https://open.spotify.com/show/{long_id}") == long_id

        # Mixed case in URL path (Spotify IDs are case-sensitive)
        assert get_url_type("https://open.spotify.com/Episode/abc") == "unknown"
        assert get_url_type("https://open.spotify.com/SHOW/def") == "unknown"

        # Trailing slashes
        assert (
            extract_id("https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G/")
            == "5Q2dkZHfnGb2Y4BzzoBu2G"
        )
        assert get_url_type("https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk/") == "show"
