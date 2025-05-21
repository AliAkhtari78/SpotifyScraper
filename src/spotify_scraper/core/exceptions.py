class SpotifyScraperError(Exception):
    """Base exception for the spotify_scraper package."""
    pass

class URLValidationError(SpotifyScraperError):
    """Raised when a URL is not valid."""
    pass

class ContentExtractionError(SpotifyScraperError):
    """Raised when data cannot be extracted from the HTML content."""
    pass

class TrackNotFoundError(SpotifyScraperError):
    """Raised when a track is not found."""
    pass