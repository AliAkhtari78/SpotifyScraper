from spotify_scraper.browsers.base import Browser
import requests

class RequestsBrowser(Browser):
    """Implementation of Browser using the requests library."""
    
    def __init__(self, headers=None, cookies=None, timeout=30):
        """
        Initialize the browser with custom headers and cookies.
        
        Args:
            headers: Custom headers to send with each request
            cookies: Cookies to include with requests
            timeout: Request timeout in seconds
        """
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.cookies = cookies
        self.timeout = timeout
        
    def get_page_content(self, url: str) -> str:
        """
        Fetch page content from the given URL.
        
        Args:
            url: The URL to fetch content from
            
        Returns:
            The page content as string
            
        Raises:
            Exception: If the request fails
        """
        response = requests.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.text