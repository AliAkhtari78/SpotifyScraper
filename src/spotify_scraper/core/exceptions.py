"""
Exception definitions for the SpotifyScraper library.

This module defines custom exceptions for error handling throughout the library.
Using specific exception types allows for more precise error handling.
"""

class SpotifyScraperError(Exception):
    """Base exception for all SpotifyScraper errors."""
    pass


# Alias for backward compatibility and common usage
ScrapingError = SpotifyScraperError


class URLError(SpotifyScraperError):
    """Exception raised for errors related to URLs."""
    
    def __init__(self, message="Invalid URL", url=None):
        """
        Initialize URLError.
        
        Args:
            message: Error message
            url: The problematic URL
        """
        self.url = url
        super().__init__(f"{message}: {url}" if url else message)


class ParsingError(SpotifyScraperError):
    """Exception raised for errors during parsing of HTML or JSON data."""
    
    def __init__(self, message="Failed to parse data", data_type=None, details=None):
        """
        Initialize ParsingError.
        
        Args:
            message: Error message
            data_type: Type of data that failed to parse (e.g., "HTML", "JSON")
            details: Additional details about the error
        """
        self.data_type = data_type
        self.details = details
        msg = f"{message}"
        if data_type:
            msg += f" ({data_type})"
        if details:
            msg += f": {details}"
        super().__init__(msg)


class ExtractionError(SpotifyScraperError):
    """Exception raised for errors during data extraction."""
    
    def __init__(self, message="Failed to extract data", entity_type=None, url=None):
        """
        Initialize ExtractionError.
        
        Args:
            message: Error message
            entity_type: Type of entity being extracted (e.g., "track", "album")
            url: The URL being processed
        """
        self.entity_type = entity_type
        self.url = url
        msg = f"{message}"
        if entity_type:
            msg += f" for {entity_type}"
        if url:
            msg += f" from {url}"
        super().__init__(msg)


class NetworkError(SpotifyScraperError):
    """Exception raised for network-related errors."""
    
    def __init__(self, message="Network error", url=None, status_code=None):
        """
        Initialize NetworkError.
        
        Args:
            message: Error message
            url: The URL that was being accessed
            status_code: HTTP status code received
        """
        self.url = url
        self.status_code = status_code
        msg = f"{message}"
        if url:
            msg += f" for {url}"
        if status_code:
            msg += f" (status code: {status_code})"
        super().__init__(msg)


class AuthenticationError(SpotifyScraperError):
    """Exception raised for authentication-related errors."""
    
    def __init__(self, message="Authentication error", auth_type=None):
        """
        Initialize AuthenticationError.
        
        Args:
            message: Error message
            auth_type: Type of authentication that failed (e.g., "cookie", "token")
        """
        self.auth_type = auth_type
        msg = f"{message}"
        if auth_type:
            msg += f" ({auth_type})"
        super().__init__(msg)


class TokenError(AuthenticationError):
    """Exception raised for errors related to authentication tokens."""
    
    def __init__(self, message="Token error", token_type=None, details=None):
        """
        Initialize TokenError.
        
        Args:
            message: Error message
            token_type: Type of token (e.g., "access", "refresh")
            details: Additional details about the error
        """
        self.token_type = token_type
        self.details = details
        msg = f"{message}"
        if token_type:
            msg += f" ({token_type} token)"
        if details:
            msg += f": {details}"
        super().__init__(msg)


class BrowserError(SpotifyScraperError):
    """Exception raised for errors related to browser operation."""
    
    def __init__(self, message="Browser error", browser_type=None):
        """
        Initialize BrowserError.
        
        Args:
            message: Error message
            browser_type: Type of browser that encountered the error
        """
        self.browser_type = browser_type
        msg = f"{message}"
        if browser_type:
            msg += f" ({browser_type})"
        super().__init__(msg)


class MediaError(SpotifyScraperError):
    """Exception raised for errors related to media handling."""
    
    def __init__(self, message="Media error", media_type=None, path=None):
        """
        Initialize MediaError.
        
        Args:
            message: Error message
            media_type: Type of media (e.g., "image", "audio")
            path: Path to the media file
        """
        self.media_type = media_type
        self.path = path
        msg = f"{message}"
        if media_type:
            msg += f" for {media_type}"
        if path:
            msg += f" at {path}"
        super().__init__(msg)


class DownloadError(MediaError):
    """Exception raised for errors during file downloads."""
    
    def __init__(self, message="Download failed", url=None, path=None, status_code=None):
        """
        Initialize DownloadError.
        
        Args:
            message: Error message
            url: URL that failed to download
            path: Local path where file was supposed to be saved
            status_code: HTTP status code received
        """
        self.url = url
        self.status_code = status_code
        msg = f"{message}"
        if url:
            msg += f" from {url}"
        if status_code:
            msg += f" (status code: {status_code})"
        if path:
            msg += f" to {path}"
        super().__init__(msg, path=path)
