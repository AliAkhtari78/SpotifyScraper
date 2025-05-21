"""
Requests-based browser implementation for SpotifyScraper.

This module provides a browser implementation using the requests library,
specialized for interacting with Spotify's web interface.
"""

import requests
import json
import logging
import time
from typing import Dict, Optional, Any, Union
from bs4 import BeautifulSoup

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import (
    NetworkError,
    ParsingError,
    RequestsError,
    RateLimitError,
    TimeoutError,
)
from spotify_scraper.core.constants import (
    DEFAULT_HEADERS,
    NEXT_DATA_SELECTOR,
    DEFAULT_TIMEOUT,
    DEFAULT_RETRIES,
    DEFAULT_RETRY_DELAY,
)

logger = logging.getLogger(__name__)


class RequestsBrowser(Browser):
    """
    Browser implementation using the requests library.
    
    This class provides a browser implementation for SpotifyScraper using
    the requests library, with support for retries, rate limiting, and
    customizable headers and proxies.
    
    Attributes:
        session: Requests session for HTTP communication
        timeout: Timeout for requests in seconds
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries in seconds
        headers: Custom headers for requests
    """
    
    def __init__(
        self,
        session: Optional[requests.Session] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_RETRIES,
        retry_delay: int = DEFAULT_RETRY_DELAY,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the RequestsBrowser.
        
        Args:
            session: Requests session (optional)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Initial delay between retries in seconds (default: 1)
            headers: Custom headers for requests (optional)
        """
        self.session = session or requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialize headers
        if headers:
            self.session.headers.update(headers)
        elif not session or not session.headers:
            # Use default headers if no custom headers are provided
            self.session.headers.update(DEFAULT_HEADERS)
        
        logger.debug(f"Initialized RequestsBrowser with timeout={timeout}, max_retries={max_retries}")
    
    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Get page content from URL with retry logic.
        
        Args:
            url: URL to retrieve
            params: Query parameters (optional)
            
        Returns:
            Page content as string
            
        Raises:
            NetworkError: If the request fails after retries
            RateLimitError: If rate limited by Spotify
            TimeoutError: If the request times out
        """
        retry_count = 0
        current_delay = self.retry_delay
        
        while retry_count <= self.max_retries:
            try:
                logger.debug(f"GET request to {url} (attempt {retry_count + 1}/{self.max_retries + 1})")
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                    stream=True,
                )
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited by Spotify. Retry after {retry_after} seconds.")
                    
                    # If this is our last retry, raise an error
                    if retry_count == self.max_retries:
                        raise RateLimitError(
                            f"Rate limited by Spotify after {self.max_retries + 1} attempts",
                            retry_after=retry_after,
                        )
                    
                    # Otherwise, wait and retry
                    time.sleep(retry_after)
                    retry_count += 1
                    continue
                
                # Check for other errors
                response.raise_for_status()
                
                return response.text
            except requests.exceptions.Timeout as e:
                logger.warning(f"Request timed out: {e}")
                
                # If this is our last retry, raise an error
                if retry_count == self.max_retries:
                    raise TimeoutError(
                        f"Request timed out after {self.max_retries + 1} attempts",
                        timeout=self.timeout,
                    )
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed: {e}")
                
                # If this is our last retry, raise an error
                if retry_count == self.max_retries:
                    if isinstance(e, requests.exceptions.HTTPError):
                        status_code = e.response.status_code if hasattr(e, "response") else None
                        raise NetworkError(
                            f"HTTP error after {self.max_retries + 1} attempts: {e}",
                            status_code=status_code,
                        )
                    else:
                        raise NetworkError(f"Request failed after {self.max_retries + 1} attempts: {e}")
            
            # Exponential backoff for retries
            time.sleep(current_delay)
            current_delay *= 2  # Double the delay for next retry
            retry_count += 1
    
    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Post data to URL with retry logic.
        
        Args:
            url: URL to post to
            data: Form data (optional)
            json_data: JSON data (optional)
            params: Query parameters (optional)
            
        Returns:
            Response content as string
            
        Raises:
            NetworkError: If the request fails after retries
            RateLimitError: If rate limited by Spotify
            TimeoutError: If the request times out
        """
        retry_count = 0
        current_delay = self.retry_delay
        
        while retry_count <= self.max_retries:
            try:
                logger.debug(f"POST request to {url} (attempt {retry_count + 1}/{self.max_retries + 1})")
                response = self.session.post(
                    url,
                    data=data,
                    json=json_data,
                    params=params,
                    timeout=self.timeout,
                )
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited by Spotify. Retry after {retry_after} seconds.")
                    
                    # If this is our last retry, raise an error
                    if retry_count == self.max_retries:
                        raise RateLimitError(
                            f"Rate limited by Spotify after {self.max_retries + 1} attempts",
                            retry_after=retry_after,
                        )
                    
                    # Otherwise, wait and retry
                    time.sleep(retry_after)
                    retry_count += 1
                    continue
                
                # Check for other errors
                response.raise_for_status()
                
                return response.text
            except requests.exceptions.Timeout as e:
                logger.warning(f"Request timed out: {e}")
                
                # If this is our last retry, raise an error
                if retry_count == self.max_retries:
                    raise TimeoutError(
                        f"Request timed out after {self.max_retries + 1} attempts",
                        timeout=self.timeout,
                    )
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed: {e}")
                
                # If this is our last retry, raise an error
                if retry_count == self.max_retries:
                    if isinstance(e, requests.exceptions.HTTPError):
                        status_code = e.response.status_code if hasattr(e, "response") else None
                        raise NetworkError(
                            f"HTTP error after {self.max_retries + 1} attempts: {e}",
                            status_code=status_code,
                        )
                    else:
                        raise NetworkError(f"Request failed after {self.max_retries + 1} attempts: {e}")
            
            # Exponential backoff for retries
            time.sleep(current_delay)
            current_delay *= 2  # Double the delay for next retry
            retry_count += 1
    
    def extract_json(self, selector: str) -> Dict[str, Any]:
        """
        Extract JSON data from current page using a CSS selector.
        
        Args:
            selector: CSS selector for the script tag containing JSON
            
        Returns:
            Parsed JSON data
            
        Raises:
            ParsingError: If JSON extraction or parsing fails
        """
        try:
            # We need the current page content from the last request
            # This is not stored in the session, so we need to get it again
            if not hasattr(self, "_last_response"):
                raise ParsingError("No page content available")
            
            page_content = self._last_response
            
            # Parse HTML content
            soup = BeautifulSoup(page_content, "html.parser")
            
            # Find script tag with the given selector
            script_tag = soup.select_one(selector)
            if not script_tag or not script_tag.string:
                raise ParsingError(f"No JSON data found with selector: {selector}")
            
            # Extract and parse JSON data
            json_data = json.loads(script_tag.string)
            
            return json_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON data: {e}")
            raise ParsingError(f"Failed to parse JSON data: {e}", data_type="JSON")
        except Exception as e:
            logger.error(f"Failed to extract JSON data: {e}")
            raise ParsingError(f"Failed to extract JSON data: {e}")
    
    def extract_element(self, selector: str) -> Optional[str]:
        """
        Extract an HTML element from current page using a CSS selector.
        
        Args:
            selector: CSS selector for the element
            
        Returns:
            Element HTML as string, or None if not found
            
        Raises:
            ParsingError: If HTML parsing fails
        """
        try:
            # We need the current page content from the last request
            if not hasattr(self, "_last_response"):
                raise ParsingError("No page content available")
            
            page_content = self._last_response
            
            # Parse HTML content
            soup = BeautifulSoup(page_content, "html.parser")
            
            # Find element with the given selector
            element = soup.select_one(selector)
            if not element:
                return None
            
            return str(element)
        except Exception as e:
            logger.error(f"Failed to extract element: {e}")
            raise ParsingError(f"Failed to extract element: {e}")
    
    def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """
        Wait for element to be available (always returns True for requests).
        
        Requests browser doesn't support waiting, so this is a no-op.
        
        Args:
            selector: CSS selector for the element (unused)
            timeout: Maximum time to wait in seconds (unused)
            
        Returns:
            Always True for RequestsBrowser
        """
        # Requests browser doesn't support waiting
        # This is here for compatibility with the Browser interface
        return True
    
    def close(self) -> None:
        """
        Close browser session and release resources.
        """
        logger.debug("Closing RequestsBrowser session")
        self.session.close()
