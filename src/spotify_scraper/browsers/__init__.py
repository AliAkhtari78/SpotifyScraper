"""
Browser factory module for SpotifyScraper.

This module provides factory functions for creating browser instances.
"""

from typing import Optional, Union, Dict, Any
import logging

from spotify_scraper.exceptions import BrowserError
from spotify_scraper.browsers.base import Browser

logger = logging.getLogger(__name__)

def create_browser(browser_type: str = "auto", **kwargs) -> Browser:
    """
    Create appropriate browser instance.
    
    Args:
        browser_type: Type of browser ('requests', 'selenium', or 'auto')
        **kwargs: Additional arguments to pass to browser constructor
        
    Returns:
        Configured browser instance
        
    Raises:
        BrowserError: If browser creation fails
        ValueError: If browser_type is invalid
    """
    # Import implementation classes here to avoid circular imports
    from spotify_scraper.browsers.requests_browser import RequestsBrowser
    
    try:
        from spotify_scraper.browsers.selenium_browser import SeleniumBrowser
        selenium_available = True
    except ImportError:
        selenium_available = False
        logger.warning("Selenium is not available, falling back to requests")
    
    # Create browser based on type
    if browser_type == "requests":
        logger.debug("Creating RequestsBrowser")
        return RequestsBrowser(**kwargs)
    
    elif browser_type == "selenium":
        if selenium_available:
            logger.debug("Creating SeleniumBrowser")
            return SeleniumBrowser(**kwargs)
        else:
            logger.warning("Selenium requested but not available, falling back to requests")
            return RequestsBrowser(**kwargs)
    
    elif browser_type == "auto":
        # Try requests first, fallback to selenium if needed
        try:
            logger.debug("Trying RequestsBrowser")
            browser = RequestsBrowser(**kwargs)
            # Test browser with a simple request
            browser.get("https://open.spotify.com")
            return browser
        except Exception as e:
            logger.warning(f"RequestsBrowser failed: {e}")
            
            if selenium_available:
                logger.debug("Falling back to SeleniumBrowser")
                return SeleniumBrowser(**kwargs)
            else:
                logger.error("Neither RequestsBrowser nor SeleniumBrowser are working")
                raise BrowserError("Failed to create any browser instance") from e
    
    else:
        raise ValueError(f"Unknown browser type: {browser_type}")
