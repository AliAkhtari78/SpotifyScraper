"""
Pytest configuration file for test fixtures.

This file contains shared fixtures and configuration for all test modules.
"""

import os
import pytest
from pathlib import Path


@pytest.fixture
def fixtures_path():
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def html_fixtures_path(fixtures_path):
    """Return the path to the HTML fixtures directory."""
    return fixtures_path / "html"


@pytest.fixture
def json_fixtures_path(fixtures_path):
    """Return the path to the JSON fixtures directory."""
    return fixtures_path / "json"


# Browser mock for testing extractors without network requests
class MockBrowser:
    """
    Mock browser for testing extractors without network requests.
    
    This browser returns predefined HTML content instead of making actual HTTP requests.
    It can be used to simulate different response scenarios for testing how extractors
    handle different types of data.
    """
    
    def __init__(self, html_content):
        """
        Initialize the mock browser with predefined HTML content.
        
        Args:
            html_content: The HTML content to return for any URL request
        """
        self.html_content = html_content
    
    def get_page_content(self, url):
        """
        Return the mock HTML content regardless of URL.
        
        Args:
            url: The URL to get content from (ignored in mock)
            
        Returns:
            The predefined HTML content
        """
        return self.html_content


@pytest.fixture
def mock_browser_factory():
    """
    Return a factory function to create mock browsers with specific content.
    
    This fixture provides a convenient way to create mock browsers with different
    HTML content for testing.
    
    Returns:
        A factory function that takes HTML content and returns a MockBrowser
    """
    def factory(html_content):
        return MockBrowser(html_content)
    
    return factory
