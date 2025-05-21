from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.types import TrackData
from spotify_scraper.parsers.json_parser import extract_track_data_from_page
from spotify_scraper.utils.url import convert_to_embed_url
from spotify_scraper.core.exceptions import URLValidationError, ContentExtractionError, TrackNotFoundError

class TrackExtractor:
    """Extracts track data from Spotify web pages."""
    
    def __init__(self, browser: Browser):
        """
        Initialize with browser interface.
        
        Args:
            browser: An instance of a Browser implementation.
        """
        self.browser = browser
    
    def extract(self, url: str) -> TrackData:
        """
        Main extraction method.
        
        Args:
            url: A Spotify track URL (regular or embed).
            
        Returns:
            TrackData object with all extracted information.
            
        Raises:
            URLValidationError: If the URL is not valid.
            ContentExtractionError: If data cannot be extracted from the HTML.
            TrackNotFoundError: If the track is not found.
        """
        validated_url = self._validate_url(url)
        html = self.browser.get_page_content(validated_url)
        return self._extract_from_html(html)
    
    def _validate_url(self, url: str) -> str:
        """
        Validate and convert to embed URL.
        
        Args:
            url: A Spotify track URL.
            
        Returns:
            Validated and converted embed URL.
            
        Raises:
            URLValidationError: If the URL is not valid.
        """
        try:
            return convert_to_embed_url(url)
        except URLValidationError as e:
            raise URLValidationError(f"Invalid Spotify track URL: {str(e)}")
    
    def _extract_from_html(self, html: str) -> TrackData:
        """
        Extract data from HTML content.
        
        Args:
            html: HTML content from a Spotify track page.
            
        Returns:
            TrackData object with all extracted information.
            
        Raises:
            ContentExtractionError: If data cannot be extracted from the HTML.
            TrackNotFoundError: If the track is not found.
        """
        try:
            return extract_track_data_from_page(html)
        except ContentExtractionError as e:
            # Check if it's a "not found" error
            if "Sorry, couldn't find that" in html:
                raise TrackNotFoundError("Track not found on Spotify")
            raise ContentExtractionError(f"Failed to extract track data: {str(e)}")