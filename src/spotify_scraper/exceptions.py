"""
Custom exceptions for the SpotifyScraper package.

This module defines the exception hierarchy used throughout the package.
"""

class SpotifyScraperError(Exception):
    """Base exception for all SpotifyScraper errors."""
    pass


class AuthenticationError(SpotifyScraperError):
    """Raised when authentication fails."""
    pass


class AuthenticationRequiredError(AuthenticationError):
    """Raised when authentication is required but not provided."""
    pass


class NetworkError(SpotifyScraperError):
    """Raised when network communication fails."""
    pass


class ScrapingError(SpotifyScraperError):
    """Raised when data extraction fails."""
    pass


class ParsingError(SpotifyScraperError):
    """Raised when parsing HTML or JSON fails."""
    pass


class URLError(SpotifyScraperError):
    """Raised when a URL is invalid or malformed."""
    pass


class ResourceNotFoundError(SpotifyScraperError):
    """Raised when a requested resource is not found."""
    pass


class DownloadError(SpotifyScraperError):
    """Raised when downloading a file fails."""
    pass


class MediaError(SpotifyScraperError):
    """Raised when processing media files fails."""
    pass


class RateLimitError(SpotifyScraperError):
    """Raised when rate limiting is detected."""
    pass


class ConfigurationError(SpotifyScraperError):
    """Raised when there's an issue with the configuration."""
    pass


class BrowserError(SpotifyScraperError):
    """Raised when there's an issue with the browser."""
    pass


class SeleniumError(BrowserError):
    """Raised when there's an issue with Selenium."""
    pass


class RequestsError(BrowserError):
    """Raised when there's an issue with Requests."""
    pass
