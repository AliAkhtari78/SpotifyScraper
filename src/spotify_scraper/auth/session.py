"""
Session management for SpotifyScraper authentication.

This module handles authentication and session management for Spotify access.
Think of this as the key management system - it handles getting and maintaining
the credentials needed to access Spotify's data.
"""

from typing import Optional, Dict, Any, Union
import logging
import json
import os
from datetime import datetime, timedelta

from spotify_scraper.core.exceptions import AuthenticationError
from spotify_scraper.core.constants import (
    CREDENTIALS_FILE_NAME,
    SESSION_CACHE_FILE,
    DEFAULT_SESSION_TIMEOUT,
    MAX_SESSION_RETRIES,
)

logger = logging.getLogger(__name__)


class Session:
    """
    Manages authentication sessions for Spotify access.
    
    This class handles the complex task of maintaining valid authentication
    with Spotify. It can work with different authentication methods like
    cookies from a browser session or API tokens.
    
    The session acts like a smart credential manager - it knows when credentials
    are expired and can attempt to refresh them automatically.
    """
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize a session for Spotify authentication.
        
        Args:
            access_token: Spotify access token if available
            cookies: HTTP cookies for authentication
            headers: Additional HTTP headers to include in requests
        """
        self.access_token = access_token
        self.cookies = cookies or {}
        self.headers = headers or {}
        self.expires_at: Optional[datetime] = None
        self.is_anonymous = access_token is None
        
        logger.debug(f"Initialized Session (anonymous: {self.is_anonymous})")
    
    def is_valid(self) -> bool:
        """
        Check if the session is currently valid.
        
        A session is considered valid if it has authentication credentials
        and those credentials haven't expired.
        
        Returns:
            True if session is valid and can be used for requests
        """
        # If we have no authentication method, session is not valid
        if not self.access_token and not self.cookies:
            return False
        
        # If we have an expiration time, check if we're still within it
        if self.expires_at and datetime.now() >= self.expires_at:
            logger.debug("Session has expired")
            return False
        
        return True
    
    def refresh(self) -> bool:
        """
        Attempt to refresh the session credentials.
        
        This method tries to get new credentials when the current ones
        have expired. The actual refresh mechanism depends on the type
        of authentication being used.
        
        Returns:
            True if refresh was successful, False otherwise
        """
        # For now, this is a placeholder. A real implementation would:
        # 1. Use refresh tokens to get new access tokens
        # 2. Re-authenticate with stored credentials
        # 3. Prompt user for new authentication if needed
        
        logger.warning("Session refresh not yet implemented")
        return False
    
    def set_access_token(self, token: str, expires_in: Optional[int] = None) -> None:
        """
        Set a new access token for the session.
        
        Args:
            token: The access token to use
            expires_in: Token lifetime in seconds (optional)
        """
        self.access_token = token
        self.is_anonymous = False
        
        if expires_in:
            self.expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        logger.debug("Updated session with new access token")
    
    def add_cookies(self, cookies: Dict[str, str]) -> None:
        """
        Add cookies to the session.
        
        Args:
            cookies: Dictionary of cookie name-value pairs
        """
        self.cookies.update(cookies)
        logger.debug(f"Added {len(cookies)} cookies to session")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers needed for authenticated requests.
        
        Returns:
            Dictionary of headers to include in HTTP requests
        """
        auth_headers = self.headers.copy()
        
        if self.access_token:
            auth_headers["Authorization"] = f"Bearer {self.access_token}"
        
        return auth_headers
    
    def save_to_file(self, filepath: Optional[str] = None) -> bool:
        """
        Save session data to a file for persistence.
        
        This allows sessions to be restored after the program restarts,
        which is convenient for users so they don't have to re-authenticate
        every time.
        
        Args:
            filepath: Path to save session data. If None, uses default location.
            
        Returns:
            True if save was successful, False otherwise
        """
        if filepath is None:
            filepath = SESSION_CACHE_FILE
        
        try:
            session_data = {
                "access_token": self.access_token,
                "cookies": self.cookies,
                "headers": self.headers,
                "expires_at": self.expires_at.isoformat() if self.expires_at else None,
                "is_anonymous": self.is_anonymous,
            }
            
            with open(filepath, "w") as f:
                json.dump(session_data, f, indent=2)
            
            logger.debug(f"Saved session to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filepath: Optional[str] = None) -> Optional["Session"]:
        """
        Load session data from a file.
        
        Args:
            filepath: Path to load session data from. If None, uses default location.
            
        Returns:
            Session instance if loading was successful, None otherwise
        """
        if filepath is None:
            filepath = SESSION_CACHE_FILE
        
        if not os.path.exists(filepath):
            logger.debug(f"Session file {filepath} does not exist")
            return None
        
        try:
            with open(filepath, "r") as f:
                session_data = json.load(f)
            
            session = cls(
                access_token=session_data.get("access_token"),
                cookies=session_data.get("cookies", {}),
                headers=session_data.get("headers", {}),
            )
            
            # Restore expiration time if available
            expires_at_str = session_data.get("expires_at")
            if expires_at_str:
                session.expires_at = datetime.fromisoformat(expires_at_str)
            
            session.is_anonymous = session_data.get("is_anonymous", True)
            
            logger.debug(f"Loaded session from {filepath}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return None
    
    def clear(self) -> None:
        """
        Clear all authentication data from the session.
        
        This essentially logs the user out by removing all stored credentials.
        """
        self.access_token = None
        self.cookies.clear()
        self.headers.clear()
        self.expires_at = None
        self.is_anonymous = True
        
        logger.debug("Cleared session authentication data")


# Backward compatibility class for the old Request interface
class Request:
    """
    Backward compatibility wrapper for the old Request class.
    
    This class provides the same interface as the original SpotifyScraper
    Request class, but internally uses the new Session system. This allows
    existing code to work without changes while benefiting from the improved
    architecture underneath.
    """
    
    def __init__(self, cookie_file: Optional[str] = None, headers: Optional[Dict[str, str]] = None, proxy: Optional[str] = None):
        """
        Initialize with the same interface as the original Request class.
        
        Args:
            cookie_file: Path to cookie file (legacy parameter)
            headers: HTTP headers to use
            proxy: Proxy URL to use (legacy parameter)
        """
        self.session = Session(headers=headers)
        logger.debug("Initialized Request (compatibility mode)")
    
    def request(self) -> Session:
        """
        Return a session object that can be used with the old Scraper interface.
        
        Returns:
            Session object compatible with old code
        """
        return self.session
