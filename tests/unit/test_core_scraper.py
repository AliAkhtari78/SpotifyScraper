"""Tests for core.scraper module."""

from unittest import mock

import pytest

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import BrowserError, ExtractionError, NetworkError
from spotify_scraper.core.scraper import Scraper


class MockBrowser(Browser):
    """Mock browser for testing."""
    
    def __init__(self, responses=None):
        super().__init__()
        self.responses = responses or {}
        self.closed = False
    
    def get(self, url, **kwargs):
        if url in self.responses:
            return self.responses[url]
        raise NetworkError(f"No mock response for {url}")
    
    def close(self):
        self.closed = True


class TestScraper:
    """Test Scraper class."""

    def test_init_with_browser(self):
        """Test initializing scraper with custom browser."""
        browser = MockBrowser()
        scraper = Scraper(browser=browser)
        
        assert scraper.browser is browser

    @mock.patch('spotify_scraper.core.scraper.RequestsBrowser')
    def test_init_default_browser(self, mock_browser_class):
        """Test initializing scraper with default browser."""
        mock_browser = mock.Mock()
        mock_browser_class.return_value = mock_browser
        
        scraper = Scraper()
        
        assert scraper.browser is mock_browser
        mock_browser_class.assert_called_once()

    def test_fetch_success(self):
        """Test successful page fetch."""
        browser = MockBrowser({
            "https://example.com": {"html": "<html><body>Test</body></html>"}
        })
        scraper = Scraper(browser=browser)
        
        result = scraper.fetch("https://example.com")
        
        assert result == {"html": "<html><body>Test</body></html>"}

    def test_fetch_network_error(self):
        """Test fetch with network error."""
        browser = MockBrowser()  # No responses configured
        scraper = Scraper(browser=browser)
        
        with pytest.raises(NetworkError):
            scraper.fetch("https://example.com")

    def test_extract_json_from_html_success(self):
        """Test extracting JSON from HTML."""
        html = '''
        <html>
        <body>
        <script id="session" data-testid="session">
            {"user": {"name": "Test User"}}
        </script>
        </body>
        </html>
        '''
        
        scraper = Scraper()
        data = scraper.extract_json_from_html(html, "session")
        
        assert data == {"user": {"name": "Test User"}}

    def test_extract_json_from_html_not_found(self):
        """Test extracting JSON when script not found."""
        html = '<html><body>No script here</body></html>'
        
        scraper = Scraper()
        
        with pytest.raises(ExtractionError) as exc_info:
            scraper.extract_json_from_html(html, "session")
        
        assert "Script with data-testid='session' not found" in str(exc_info.value)

    def test_extract_json_from_html_invalid_json(self):
        """Test extracting invalid JSON from HTML."""
        html = '''
        <html>
        <body>
        <script id="session" data-testid="session">
            {invalid json content}
        </script>
        </body>
        </html>
        '''
        
        scraper = Scraper()
        
        with pytest.raises(ExtractionError) as exc_info:
            scraper.extract_json_from_html(html, "session")
        
        assert "Failed to parse JSON" in str(exc_info.value)

    def test_extract_json_from_html_empty_script(self):
        """Test extracting from empty script tag."""
        html = '''
        <html>
        <body>
        <script id="session" data-testid="session"></script>
        </body>
        </html>
        '''
        
        scraper = Scraper()
        
        with pytest.raises(ExtractionError) as exc_info:
            scraper.extract_json_from_html(html, "session")
        
        assert "Failed to parse JSON" in str(exc_info.value)

    def test_extract_metadata_success(self):
        """Test extracting metadata from page."""
        html = '''
        <html>
        <head>
            <meta property="og:title" content="Test Title">
            <meta property="og:description" content="Test Description">
            <meta property="og:image" content="https://example.com/image.jpg">
            <meta property="og:type" content="music.song">
        </head>
        </html>
        '''
        
        scraper = Scraper()
        metadata = scraper.extract_metadata(html)
        
        assert metadata["title"] == "Test Title"
        assert metadata["description"] == "Test Description"
        assert metadata["image"] == "https://example.com/image.jpg"
        assert metadata["type"] == "music.song"

    def test_extract_metadata_missing_tags(self):
        """Test extracting metadata when tags are missing."""
        html = '''
        <html>
        <head>
            <meta property="og:title" content="Only Title">
        </head>
        </html>
        '''
        
        scraper = Scraper()
        metadata = scraper.extract_metadata(html)
        
        assert metadata["title"] == "Only Title"
        assert metadata["description"] is None
        assert metadata["image"] is None
        assert metadata["type"] is None

    def test_extract_metadata_no_content(self):
        """Test extracting metadata with no content attribute."""
        html = '''
        <html>
        <head>
            <meta property="og:title">
            <meta property="og:description" content="">
        </head>
        </html>
        '''
        
        scraper = Scraper()
        metadata = scraper.extract_metadata(html)
        
        assert metadata["title"] is None
        assert metadata["description"] == ""

    def test_parse_html(self):
        """Test parsing HTML content."""
        html = '<html><body><div class="test">Content</div></body></html>'
        
        scraper = Scraper()
        soup = scraper.parse_html(html)
        
        assert soup is not None
        assert soup.find("div", class_="test").text == "Content"

    def test_parse_html_invalid(self):
        """Test parsing invalid HTML."""
        html = "Not HTML content"
        
        scraper = Scraper()
        soup = scraper.parse_html(html)
        
        # BeautifulSoup handles invalid content gracefully
        assert soup is not None

    def test_close(self):
        """Test closing the scraper."""
        browser = MockBrowser()
        scraper = Scraper(browser=browser)
        
        assert not browser.closed
        
        scraper.close()
        
        assert browser.closed

    def test_context_manager(self):
        """Test using scraper as context manager."""
        browser = MockBrowser()
        
        with Scraper(browser=browser) as scraper:
            assert scraper.browser is browser
            assert not browser.closed
        
        assert browser.closed

    def test_fetch_and_extract_success(self):
        """Test combined fetch and extract operation."""
        html = '''
        <html>
        <body>
        <script id="session" data-testid="session">
            {"status": "success", "data": {"id": "123"}}
        </script>
        </body>
        </html>
        '''
        
        browser = MockBrowser({
            "https://example.com": {"html": html}
        })
        scraper = Scraper(browser=browser)
        
        page_data = scraper.fetch("https://example.com")
        json_data = scraper.extract_json_from_html(page_data["html"], "session")
        
        assert json_data["status"] == "success"
        assert json_data["data"]["id"] == "123"

    def test_browser_error_propagation(self):
        """Test that browser errors are properly propagated."""
        def raise_browser_error(url, **kwargs):
            raise BrowserError("Browser failed")
        
        browser = MockBrowser()
        browser.get = raise_browser_error
        
        scraper = Scraper(browser=browser)
        
        with pytest.raises(BrowserError) as exc_info:
            scraper.fetch("https://example.com")
        
        assert "Browser failed" in str(exc_info.value)