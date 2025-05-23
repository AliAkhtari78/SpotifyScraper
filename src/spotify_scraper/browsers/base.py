"""Browser abstract base class for the SpotifyScraper library.

This module defines the abstract interface that all browser implementations
must follow. Browsers are responsible for fetching web pages, handling
authentication, and managing network requests to Spotify's web interface.

The library provides two concrete implementations:
    - RequestsBrowser: Lightweight, fast, suitable for most use cases
    - SeleniumBrowser: Full browser engine, handles JavaScript, slower

Example:
    >>> from spotify_scraper.browsers import create_browser
    >>> # Create appropriate browser based on requirements
    >>> browser = create_browser("requests")  # or "selenium" or "auto"
    >>> 
    >>> # Use the browser to fetch content
    >>> html_content = browser.get_page_content("https://open.spotify.com/...")
    >>> browser.close()  # Clean up resources
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Browser(ABC):
    """Abstract base class defining the interface for browser implementations.
    
    This abstract class defines the contract that all browser implementations
    must follow. Browsers handle all network interactions with Spotify's web
    interface, including page fetching, authentication, and file downloads.
    
    Concrete implementations provide different trade-offs:
        - RequestsBrowser: Fast, lightweight, no JavaScript support
        - SeleniumBrowser: Full browser, JavaScript support, slower
    
    All methods are abstract and must be implemented by subclasses.
    
    Example implementation:
        >>> class MyBrowser(Browser):
        ...     def get_page_content(self, url: str) -> str:
        ...         # Implementation here
        ...         return html_content
        ...     # ... implement other abstract methods
    
    Note:
        Browser instances should be properly closed after use to release
        resources, especially important for SeleniumBrowser.
    """
    
    @abstractmethod
    def get_page_content(self, url: str) -> str:
        """Get the HTML content of a web page.
        
        Fetches the complete HTML content of the specified URL. This is the
        primary method for retrieving Spotify web pages for parsing.
        
        Args:
            url: Full URL of the Spotify page to fetch.
                Example: "https://open.spotify.com/track/..."
            
        Returns:
            str: Complete HTML content of the page as a string, including
                all script tags and embedded JSON data needed for parsing.
            
        Raises:
            NetworkError: If the page cannot be accessed due to network issues,
                timeouts, or invalid URLs.
            AuthenticationError: If the page requires authentication (login)
                but valid credentials/cookies were not provided.
            BrowserError: If there are browser-specific issues (e.g., Selenium
                WebDriver crashes).
        
        Example:
            >>> browser = create_browser("requests")
            >>> html = browser.get_page_content("https://open.spotify.com/track/...")
            >>> # Parse the HTML to extract data
            >>> data = extract_track_data_from_page(html)
        """
        pass
    
    @abstractmethod
    def get_json(self, url: str) -> Dict[str, Any]:
        """Get JSON data from a URL.
        
        Fetches and parses JSON data from the specified URL. Useful for
        accessing Spotify's API endpoints or other JSON resources.
        
        Args:
            url: URL that returns JSON data.
                Example: "https://api.spotify.com/v1/..."
            
        Returns:
            Dict[str, Any]: Parsed JSON data as a Python dictionary.
                The structure depends on the specific endpoint.
            
        Raises:
            NetworkError: If the URL cannot be accessed or returns non-200 status.
            ParsingError: If the response body is not valid JSON or cannot
                be parsed.
            AuthenticationError: If the endpoint requires authentication but
                valid credentials were not provided.
        
        Example:
            >>> browser = create_browser("requests")
            >>> data = browser.get_json("https://api.spotify.com/v1/tracks/...")
            >>> print(data['name'])  # Track name from API response
        
        Note:
            This method expects the response Content-Type to be application/json.
            For HTML pages with embedded JSON, use get_page_content() instead.
        """
        pass
    
    @abstractmethod
    def download_file(self, url: str, path: str) -> str:
        """Download a file from a URL and save it to disk.
        
        Downloads any file type (audio, image, etc.) from the specified URL
        and saves it to the local filesystem. Handles large files efficiently
        using streaming.
        
        Args:
            url: Direct URL to the file to download.
                Example: "https://p.scdn.co/mp3-preview/..."
            path: Full local filesystem path where the file should be saved.
                Parent directories will be created if needed.
                Example: "/downloads/preview.mp3"
            
        Returns:
            str: The same path that was provided, confirming successful save.
                This allows for easy chaining of operations.
            
        Raises:
            NetworkError: If the file cannot be downloaded due to network issues,
                404 errors, or other HTTP errors.
            MediaError: If the file cannot be saved due to permissions,
                disk space, or invalid path.
        
        Example:
            >>> browser = create_browser("requests")
            >>> # Download a track preview
            >>> saved_path = browser.download_file(
            ...     "https://p.scdn.co/mp3-preview/...",
            ...     "downloads/preview.mp3"
            ... )
            >>> print(f"File saved to: {saved_path}")
        
        Note:
            - This method should handle redirects automatically
            - Large files should be downloaded in chunks to avoid memory issues
            - The file is saved with binary mode to handle all file types
        """
        pass
    
    @abstractmethod
    def get_auth_token(self) -> Optional[str]:
        """Get an authentication token for Spotify API access.
        
        Attempts to retrieve or generate an authentication token for accessing
        protected Spotify resources. The token may come from cookies, OAuth,
        or other authentication mechanisms.
        
        Returns:
            Optional[str]: Authentication token string if available, None if
                no authentication is configured or available. The token format
                depends on the authentication method used.
            
        Raises:
            AuthenticationError: If authentication is configured but fails
                (e.g., invalid credentials, expired tokens).
        
        Example:
            >>> browser = create_browser("requests", cookies={"sp_t": "..."})  
            >>> token = browser.get_auth_token()
            >>> if token:
            ...     print("Authenticated")
            ... else:
            ...     print("No authentication available")
        
        Note:
            - This method may trigger authentication flows in some implementations
            - Tokens may have expiration times and need refresh
            - Not all browser implementations support authentication
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the browser and release all resources.
        
        Performs cleanup operations including closing network connections,
        terminating browser processes (for Selenium), and releasing any
        other held resources. This method should always be called when
        the browser is no longer needed.
        
        Example:
            >>> browser = create_browser("selenium")
            >>> try:
            ...     # Use the browser
            ...     content = browser.get_page_content(url)
            ... finally:
            ...     # Always close to prevent resource leaks
            ...     browser.close()
        
        Note:
            - For RequestsBrowser: Closes the requests session
            - For SeleniumBrowser: Quits the WebDriver and closes browser window
            - Calling close() multiple times should be safe (idempotent)
            - After close(), the browser instance should not be used again
        """
        pass
