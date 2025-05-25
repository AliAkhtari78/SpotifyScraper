"""
Requests-based browser implementation for SpotifyScraper.

This module provides a browser implementation using the requests library.
Think of this as a simple web client that can fetch Spotify pages without
the complexity of a full browser like Selenium. It's lighter weight but
still handles the essential tasks of getting web page content.
"""

import logging
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter

try:
    from requests.packages.urllib3.util.retry import Retry
except ImportError:
    from urllib3.util.retry import Retry

from spotify_scraper.auth.session import Session
from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.constants import DEFAULT_HEADERS, DEFAULT_RETRIES, DEFAULT_TIMEOUT
from spotify_scraper.core.exceptions import AuthenticationError, BrowserError, NetworkError

logger = logging.getLogger(__name__)


class RequestsBrowser(Browser):
    """
    Browser implementation using the requests library.

    This browser handles HTTP requests to Spotify using the popular requests
    library. It's designed to be simple but robust, with automatic retries,
    proper error handling, and session management.

    Think of this as your primary tool for fetching Spotify web pages. It knows
    how to handle authentication, cookies, and the various quirks of making
    requests to Spotify's servers.
    """

    def __init__(
        self,
        session: Optional[Session] = None,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the requests-based browser.

        Args:
            session: Authentication session to use
            timeout: Request timeout in seconds
            retries: Number of retry attempts for failed requests
            headers: Additional headers to include in requests
        """
        self.session = session
        self.timeout = timeout
        self.retries = retries

        # Set up the requests session with retry strategy
        self.requests_session = requests.Session()

        # Configure automatic retries for network issues
        retry_strategy = Retry(
            total=retries,
            backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.requests_session.mount("http://", adapter)
        self.requests_session.mount("https://", adapter)

        # Set up headers
        self.default_headers = DEFAULT_HEADERS.copy()
        if headers:
            self.default_headers.update(headers)

        # Add authentication headers if we have a session
        if self.session:
            auth_headers = self.session.get_auth_headers()
            self.default_headers.update(auth_headers)

            # Add cookies if available
            if self.session.cookies:
                self.requests_session.cookies.update(self.session.cookies)

        self.requests_session.headers.update(self.default_headers)

        logger.debug("Initialized RequestsBrowser")

    def get_page_content(self, url: str) -> str:
        """
        Get the HTML content of a web page.

        This is the main method for fetching Spotify pages. It handles all the
        complexity of making HTTP requests, dealing with errors, and returning
        clean HTML content that can be parsed.

        Args:
            url: URL of the page to get

        Returns:
            HTML content of the page as a string

        Raises:
            NetworkError: If the page cannot be accessed
            AuthenticationError: If authentication is required but fails
        """
        try:
            logger.debug("Fetching page content from: %s", url)

            response = self.requests_session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
            )

            # Check for authentication issues
            if response.status_code == 401:
                raise AuthenticationError(f"Authentication required for {url}")
            elif response.status_code == 403:
                raise AuthenticationError(f"Access forbidden for {url}")

            # Check for other HTTP errors
            response.raise_for_status()

            # Log success
            logger.debug("Successfully fetched %d characters from %s", len(response.text), url)

            return response.text

        except requests.exceptions.Timeout as e:
            logger.error("Request timeout for %s: %s", url, e)
            raise NetworkError("Request timeout", url=url) from e

        except requests.exceptions.ConnectionError as e:
            logger.error("Connection error for %s: %s", url, e)
            raise NetworkError("Connection error", url=url) from e

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            logger.error("HTTP error for %s: %s", url, e)
            raise NetworkError(f"HTTP error: {e}", url=url, status_code=status_code) from e

        except Exception as e:
            logger.error("Unexpected error fetching %s: %s", url, e)
            raise BrowserError(f"Unexpected error: {e}", browser_type="requests") from e

    def get_json(self, url: str) -> Dict[str, Any]:
        """
        Get JSON data from a URL.

        This method is useful for API endpoints that return JSON directly,
        though most Spotify scraping will use get_page_content instead.

        Args:
            url: URL to get JSON data from

        Returns:
            Parsed JSON data as a dictionary

        Raises:
            NetworkError: If the URL cannot be accessed
            ParsingError: If the response is not valid JSON
        """
        try:
            logger.debug("Fetching JSON from: %s", url)

            response = self.requests_session.get(
                url,
                timeout=self.timeout,
                headers={"Accept": "application/json"},
            )

            response.raise_for_status()

            json_data = response.json()
            logger.debug("Successfully fetched JSON with %d keys from %s", len(json_data), url)

            return json_data

        except requests.exceptions.JSONDecodeError as e:
            logger.error("Invalid JSON response from %s: %s", url, e)
            raise NetworkError("Invalid JSON response", url=url) from e

        except Exception as e:
            logger.error("Error fetching JSON from %s: %s", url, e)
            raise NetworkError(f"Error fetching JSON: {e}", url=url) from e

    def download_file(self, url: str, path: str) -> str:
        """
        Download a file from a URL and save it to disk.

        This method handles downloading media files like images and audio previews.
        It streams the download to avoid loading large files entirely into memory.

        Args:
            url: URL of the file to download
            path: Path where the file should be saved

        Returns:
            Path to the downloaded file

        Raises:
            NetworkError: If the file cannot be downloaded
            MediaError: If the file cannot be saved
        """
        try:
            logger.debug("Downloading file from %s to %s", url, path)

            # Stream the download to handle large files efficiently
            response = self.requests_session.get(
                url,
                stream=True,
                timeout=self.timeout,
            )

            response.raise_for_status()

            # Save the file in chunks
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)

            logger.debug("Successfully downloaded file to %s", path)
            return path

        except Exception as e:
            logger.error("Error downloading file from %s: %s", url, e)
            raise NetworkError(f"Download error: {e}", url=url) from e

    def get_auth_token(self) -> Optional[str]:
        """
        Get an authentication token for Spotify API access.

        This method attempts to extract an authentication token from the current
        session or from Spotify pages. These tokens can be used for API calls
        that require authentication.

        Returns:
            Authentication token if available, None otherwise
        """
        if self.session and self.session.access_token:
            return self.session.access_token

        # For now, we don't have a way to extract tokens from pages
        # This could be implemented by parsing the __NEXT_DATA__ script tag
        # and extracting the session token from there
        logger.debug("No authentication token available")
        return None

    def close(self) -> None:
        """
        Close the browser and release any resources.

        This method cleans up the requests session and any other resources
        that the browser was using. It's good practice to call this when
        you're done using the browser.
        """
        if self.requests_session:
            self.requests_session.close()
        logger.debug("Closed RequestsBrowser")

    def update_session(self, session: Session) -> None:
        """
        Update the authentication session used by this browser.

        This method allows you to change the authentication credentials
        without creating a new browser instance.

        Args:
            session: New session to use for authentication
        """
        self.session = session

        # Update headers with new authentication info
        if session:
            auth_headers = session.get_auth_headers()
            self.requests_session.headers.update(auth_headers)

            # Update cookies
            if session.cookies:
                self.requests_session.cookies.update(session.cookies)

        logger.debug("Updated browser session")
