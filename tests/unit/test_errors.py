"""Tests for the SpotifyScraper exception hierarchy."""

from __future__ import annotations

import pytest

from spotify_scraper.errors import (
    AuthenticationError,
    MediaError,
    NetworkError,
    NotFoundError,
    ParsingError,
    RateLimitedError,
    SpotifyScraperError,
    TokenError,
    URLError,
)

ALL_ERRORS: tuple[type[SpotifyScraperError], ...] = (
    SpotifyScraperError,
    URLError,
    NetworkError,
    RateLimitedError,
    TokenError,
    AuthenticationError,
    NotFoundError,
    ParsingError,
    MediaError,
)

HIERARCHY: tuple[tuple[type[Exception], type[Exception]], ...] = (
    (SpotifyScraperError, Exception),
    (URLError, SpotifyScraperError),
    (NetworkError, SpotifyScraperError),
    (RateLimitedError, NetworkError),
    (RateLimitedError, SpotifyScraperError),
    (TokenError, SpotifyScraperError),
    (AuthenticationError, SpotifyScraperError),
    (NotFoundError, SpotifyScraperError),
    (ParsingError, SpotifyScraperError),
    (MediaError, SpotifyScraperError),
)


@pytest.mark.parametrize(("child", "parent"), HIERARCHY)
def test_hierarchy(child: type[Exception], parent: type[Exception]) -> None:
    assert issubclass(child, parent)


@pytest.mark.parametrize("error_type", ALL_ERRORS)
def test_every_error_is_spotify_scraper_error(error_type: type[SpotifyScraperError]) -> None:
    assert issubclass(error_type, SpotifyScraperError)


def test_network_error_request_url() -> None:
    error = NetworkError("boom", request_url="https://open.spotify.com/track/x")
    assert error.request_url == "https://open.spotify.com/track/x"
    assert str(error) == "boom"


def test_network_error_request_url_defaults_to_none() -> None:
    assert NetworkError("boom").request_url is None


def test_network_error_request_url_is_keyword_only() -> None:
    with pytest.raises(TypeError):
        NetworkError("boom", "https://open.spotify.com")  # type: ignore[misc]


def test_rate_limited_error_retry_after() -> None:
    error = RateLimitedError(
        "slow down",
        request_url="https://api.spotify.com/pathfinder",
        retry_after=2.5,
    )
    assert error.retry_after == 2.5
    assert error.request_url == "https://api.spotify.com/pathfinder"
    assert str(error) == "slow down"


def test_rate_limited_error_defaults() -> None:
    error = RateLimitedError("slow down")
    assert error.retry_after is None
    assert error.request_url is None


def test_rate_limited_error_caught_as_network_error() -> None:
    with pytest.raises(NetworkError):
        raise RateLimitedError("slow down", retry_after=1.0)


def test_any_error_caught_as_base() -> None:
    with pytest.raises(SpotifyScraperError):
        raise ParsingError("payload shape changed; check for a library update")
