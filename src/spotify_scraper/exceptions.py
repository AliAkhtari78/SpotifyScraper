"""
Custom exceptions for the SpotifyScraper package.

This module defines the exception hierarchy used throughout the package.
"""


class SpotifyScraperError(Exception):
    """Base exception for all SpotifyScraper errors."""



class AuthenticationError(SpotifyScraperError):
    """Raised when authentication fails."""



class AuthenticationRequiredError(AuthenticationError):
    """Raised when authentication is required but not provided."""



class NetworkError(SpotifyScraperError):
    """Raised when network communication fails."""



class ScrapingError(SpotifyScraperError):
    """Raised when data extraction fails."""



class ParsingError(SpotifyScraperError):
    """Raised when parsing HTML or JSON fails."""



class URLError(SpotifyScraperError):
    """Raised when a URL is invalid or malformed."""



class ResourceNotFoundError(SpotifyScraperError):
    """Raised when a requested resource is not found."""



class DownloadError(SpotifyScraperError):
    """Raised when downloading a file fails."""



class MediaError(SpotifyScraperError):
    """Raised when processing media files fails."""



class RateLimitError(SpotifyScraperError):
    """Raised when rate limiting is detected."""



class ConfigurationError(SpotifyScraperError):
    """Raised when there's an issue with the configuration."""



class BrowserError(SpotifyScraperError):
    """Raised when there's an issue with the browser."""



class SeleniumError(BrowserError):
    """Raised when there's an issue with Selenium."""



class RequestsError(BrowserError):
    """Raised when there's an issue with Requests."""

