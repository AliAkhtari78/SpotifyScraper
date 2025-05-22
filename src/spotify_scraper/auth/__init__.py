"""
Authentication module for SpotifyScraper.

This module handles session management and authentication.
"""

from typing import Dict, Optional, Any
import re
import requests
import logging

from spotify_scraper.exceptions import AuthenticationError
from spotify_scraper.constants import DEFAULT_HEADERS

logger = logging.getLogger(__name__)


class Session:
    """
    Session management class for authentication with Spotify web player.
    
    This class provides functionality to create authenticated sessions
    using cookies, headers, and proxies. It is designed to be backward
    compatible with the original Request class from SpotifyScraper v1.
    """
    
    def __init__(
        self,
        cookie_file: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        proxy: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the Session.
        
        Args:
            cookie_file: Path to a cookies.txt file (optional)
            headers: Custom headers for requests (optional)
            proxy: Proxy configuration (optional)
        """
        # Store provided parameters
        self.cookie_file = cookie_file
        self.headers = headers
        self.proxy = proxy
        
        # Initialize cookie dictionary
        if cookie_file is None:
            self.cookie = None
        else:
            try:
                self.cookie = self._parse_cookie_file()
                logger.debug(f"Loaded cookies from {cookie_file}")
            except Exception as e:
                logger.error(f"Failed to load cookies from {cookie_file}: {e}")
                raise AuthenticationError(f"Failed to load cookies: {e}") from e
    
    def _parse_cookie_file(self) -> Dict[str, str]:
        """
        Parse a cookies.txt file and return a dictionary of key-value pairs.
        
        Returns:
            Dictionary of cookies
        """
        cookies = {}
        with open(self.cookie_file, "r") as fp:
            for line in fp:
                if not re.match(r"^\#", line):
                    line_fields = line.strip().split("\t")
                    if len(line_fields) >= 7:
                        cookies[line_fields[5]] = line_fields[6]
        
        return cookies
    
    def request(self) -> requests.Session:
        """
        Create session using requests library and set cookie and headers.
        
        Returns:
            Configured requests.Session object
        """
        # Create a new session
        request_session = requests.Session()
        
        # Set headers with defaults if not provided
        if self.headers is None:
            request_session.headers.update(DEFAULT_HEADERS)
        else:
            request_session.headers.update(self.headers)
        
        # Set cookies if provided
        if self.cookie is not None:
            request_session.cookies.update(self.cookie)
        
        # Set proxy if provided
        if self.proxy is not None:
            request_session.proxies.update(self.proxy)
        
        logger.debug("Created requests session")
        
        return request_session
