"""
Session management module for SpotifyScraper.

This module provides functionality for creating and managing authenticated sessions
with the Spotify web player, supporting both cookie-based and token-based authentication.
"""

import os
import json
import re
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Any, Union, Tuple
import requests

from spotify_scraper.core.exceptions import (
    AuthenticationError,
    TokenError,
    NetworkError,
)
from spotify_scraper.core.constants import (
    DEFAULT_HEADERS,
    TOKEN_URL,
    CREDENTIALS_FILE_NAME,
    SPOTIFY_BASE_URL,
    DEFAULT_CLIENT_ID,
)

logger = logging.getLogger(__name__)


class Session:
    """
    Session management class for authentication with Spotify web player.
    
    This class provides functionality to create authenticated sessions using
    cookies, headers, OAuth tokens, and proxies. It supports token refresh and
    credential persistence.
    
    Attributes:
        cookie_file: Path to the cookies file (if used)
        auth_token: OAuth token (if used)
        refresh_token: OAuth refresh token (if used)
        session: Requests session for HTTP communication
    """
    
    def __init__(
        self,
        cookie_file: Optional[str] = None,
        auth_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        credentials_path: Optional[Union[str, Path]] = None,
        proxy: Optional[Dict[str, str]] = None,
        user_agent: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the Session.
        
        Args:
            cookie_file: Path to a cookies.txt file (optional)
            auth_token: OAuth token for authentication (optional)
            refresh_token: OAuth refresh token (optional)
            client_id: Spotify API client ID (optional)
            client_secret: Spotify API client secret (optional)
            credentials_path: Path to store credentials (default: ~/.spotify-scraper)
            proxy: Proxy configuration (optional)
            user_agent: Custom user agent (optional)
            headers: Custom headers for requests (optional)
        """
        # Store provided parameters
        self.cookie_file = cookie_file
        self.auth_token = auth_token
        self.refresh_token = refresh_token
        self.client_id = client_id or DEFAULT_CLIENT_ID
        self.client_secret = client_secret
        self.proxy = proxy
        
        # Set credentials path
        if credentials_path:
            self.credentials_path = Path(credentials_path)
        else:
            self.credentials_path = Path.home() / ".spotify-scraper"
        
        # Create credentials directory if it doesn't exist
        self.credentials_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize cookie dictionary
        self.cookie = None
        if cookie_file:
            try:
                self.cookie = self._parse_cookie_file()
                logger.debug(f"Loaded cookies from {cookie_file}")
            except Exception as e:
                logger.error(f"Failed to load cookies from {cookie_file}: {e}")
                raise AuthenticationError(f"Failed to load cookies: {e}")
        
        # Initialize headers
        self.headers = DEFAULT_HEADERS.copy()
        if user_agent:
            self.headers["User-Agent"] = user_agent
        if headers:
            self.headers.update(headers)
        
        # Load saved credentials if available
        if not auth_token and not refresh_token:
            self._load_credentials()
        
        # Create a session
        self._session = requests.Session()
        self._session.headers.update(self.headers)
        
        # Set cookies if provided
        if self.cookie:
            self._session.cookies.update(self.cookie)
        
        # Set proxy if provided
        if self.proxy:
            self._session.proxies.update(self.proxy)
        
        # Set token expiry time if we have a token
        self.token_expires_at = 0
        if self.auth_token:
            # Set a default expiry time (1 hour from now)
            self.token_expires_at = int(time.time()) + 3600
        
        logger.debug("Session initialized")
    
    def _parse_cookie_file(self) -> Dict[str, str]:
        """
        Parse a cookies.txt file and return a dictionary of key-value pairs.
        
        Returns:
            Dictionary of cookies
            
        Raises:
            AuthenticationError: If the cookie file cannot be parsed
        """
        if not self.cookie_file:
            raise AuthenticationError("No cookie file specified")
        
        cookies = {}
        try:
            with open(self.cookie_file, "r") as fp:
                for line in fp:
                    if not re.match(r"^\#", line):
                        line_fields = line.strip().split("\t")
                        if len(line_fields) >= 7:
                            cookies[line_fields[5]] = line_fields[6]
            
            logger.debug(f"Parsed {len(cookies)} cookies from file")
            return cookies
        except Exception as e:
            logger.error(f"Failed to parse cookie file: {e}")
            raise AuthenticationError(f"Failed to parse cookie file: {e}")
    
    def _load_credentials(self) -> None:
        """
        Load saved credentials from file.
        """
        credentials_file = self.credentials_path / CREDENTIALS_FILE_NAME
        
        if not credentials_file.exists():
            logger.debug("No saved credentials found")
            return
        
        try:
            with open(credentials_file, "r") as f:
                credentials = json.load(f)
                
            # Load token data
            self.auth_token = credentials.get("auth_token")
            self.refresh_token = credentials.get("refresh_token")
            self.client_id = credentials.get("client_id", self.client_id)
            self.client_secret = credentials.get("client_secret")
            self.token_expires_at = credentials.get("token_expires_at", 0)
            
            logger.debug("Loaded credentials from file")
        except Exception as e:
            logger.warning(f"Failed to load credentials: {e}")
    
    def _save_credentials(self) -> None:
        """
        Save credentials to file.
        """
        credentials_file = self.credentials_path / CREDENTIALS_FILE_NAME
        
        try:
            credentials = {
                "auth_token": self.auth_token,
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "token_expires_at": self.token_expires_at,
            }
            
            with open(credentials_file, "w") as f:
                json.dump(credentials, f, indent=2)
                
            # Set file permissions to readable/writable only by the owner
            os.chmod(credentials_file, 0o600)
            
            logger.debug("Saved credentials to file")
        except Exception as e:
            logger.warning(f"Failed to save credentials: {e}")
    
    def refresh_auth_token(self) -> bool:
        """
        Refresh the OAuth token using the refresh token.
        
        Returns:
            True if token was refreshed successfully, False otherwise
        """
        if not self.refresh_token:
            logger.warning("No refresh token available")
            return False
        
        if not self.client_id:
            logger.warning("No client ID available")
            return False
        
        try:
            logger.debug("Refreshing OAuth token")
            
            # Prepare request data
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
            }
            
            # Add client secret if available
            if self.client_secret:
                data["client_secret"] = self.client_secret
            
            # Make request to token endpoint
            response = requests.post(TOKEN_URL, data=data)
            response.raise_for_status()
            
            # Parse response
            token_data = response.json()
            
            # Update token data
            self.auth_token = token_data.get("access_token")
            
            # Update refresh token if provided
            if "refresh_token" in token_data:
                self.refresh_token = token_data.get("refresh_token")
            
            # Calculate expiry time
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = int(time.time()) + expires_in
            
            # Save credentials
            self._save_credentials()
            
            logger.debug("OAuth token refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to refresh OAuth token: {e}")
            return False
    
    def is_token_valid(self) -> bool:
        """
        Check if the OAuth token is valid and not expired.
        
        Returns:
            True if token is valid, False otherwise
        """
        if not self.auth_token:
            return False
        
        # Add a safety margin of 60 seconds
        return time.time() < (self.token_expires_at - 60)
    
    def ensure_token_valid(self) -> bool:
        """
        Ensure that the OAuth token is valid, refreshing it if necessary.
        
        Returns:
            True if token is valid, False otherwise
        """
        if self.is_token_valid():
            return True
        
        return self.refresh_auth_token()
    
    def request(self) -> requests.Session:
        """
        Get a requests session with authentication.
        
        Returns:
            Configured requests.Session object
        """
        # Ensure token is valid if we're using OAuth
        if self.auth_token and not self.is_token_valid():
            self.refresh_auth_token()
        
        # If we have an OAuth token, add it to the session
        if self.auth_token:
            self._session.headers.update({
                "Authorization": f"Bearer {self.auth_token}"
            })
        
        return self._session
    
    def get_auth_header(self) -> Dict[str, str]:
        """
        Get authorization header.
        
        Returns:
            Authorization header dictionary
        """
        # Ensure token is valid if we're using OAuth
        if self.auth_token and not self.is_token_valid():
            self.refresh_auth_token()
        
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        
        return {}
    
    def is_authenticated(self) -> bool:
        """
        Check if the session is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        return bool(self.cookie or (self.auth_token and self.is_token_valid()))
    
    def logout(self) -> None:
        """
        Log out by clearing authentication data.
        """
        self.auth_token = None
        self.refresh_token = None
        self.token_expires_at = 0
        self.cookie = None
        
        # Clear session cookies
        self._session.cookies.clear()
        
        # Remove saved credentials
        credentials_file = self.credentials_path / CREDENTIALS_FILE_NAME
        if credentials_file.exists():
            try:
                credentials_file.unlink()
                logger.debug("Removed saved credentials")
            except Exception as e:
                logger.warning(f"Failed to remove saved credentials: {e}")
