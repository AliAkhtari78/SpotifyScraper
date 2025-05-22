"""
Browser abstract base class for the SpotifyScraper library.

This module defines the abstract interface for browser implementations,
which are responsible for fetching and interacting with Spotify web pages.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Browser(ABC):
    """
    Abstract base class defining the interface for browser implementations.
    
    Browser classes are responsible for making HTTP requests to Spotify,
    handling authentication, and returning the content of web pages.
    """
    
    @abstractmethod
    def get_page_content(self, url: str) -> str:
        """
        Get the HTML content of a web page.
        
        Args:
            url: URL of the page to get
            
        Returns:
            HTML content of the page as a string
            
        Raises:
            NetworkError: If the page cannot be accessed
            AuthenticationError: If authentication is required but fails
        """
        pass
    
    @abstractmethod
    def get_json(self, url: str) -> Dict[str, Any]:
        """
        Get JSON data from a URL.
        
        Args:
            url: URL to get JSON data from
            
        Returns:
            Parsed JSON data as a dictionary
            
        Raises:
            NetworkError: If the URL cannot be accessed
            ParsingError: If the response is not valid JSON
            AuthenticationError: If authentication is required but fails
        """
        pass
    
    @abstractmethod
    def download_file(self, url: str, path: str) -> str:
        """
        Download a file from a URL and save it to disk.
        
        Args:
            url: URL of the file to download
            path: Path where the file should be saved
            
        Returns:
            Path to the downloaded file
            
        Raises:
            NetworkError: If the file cannot be downloaded
            MediaError: If the file cannot be saved
        """
        pass
    
    @abstractmethod
    def get_auth_token(self) -> Optional[str]:
        """
        Get an authentication token for Spotify API access.
        
        Returns:
            Authentication token if available, None otherwise
            
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        Close the browser and release any resources.
        
        This method should be called when the browser is no longer needed.
        """
        pass
