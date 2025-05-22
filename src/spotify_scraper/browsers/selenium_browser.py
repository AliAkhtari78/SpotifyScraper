"""
Selenium-based browser implementation for SpotifyScraper.

This module provides a browser implementation using Selenium for handling
dynamic web content.
"""

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

import json
import logging
from typing import Dict, Optional, Any, Union

from spotify_scraper.browsers.base import Browser
from spotify_scraper.exceptions import BrowserError, SeleniumError, ParsingError

logger = logging.getLogger(__name__)


class SeleniumBrowser(Browser):
    """
    Browser implementation using Selenium.
    
    This class provides an implementation of the Browser interface
    using Selenium for handling dynamic web content.
    """
    
    def __init__(self, driver: Optional[Any] = None):
        """
        Initialize the SeleniumBrowser.
        
        Args:
            driver: Selenium WebDriver instance (optional)
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium is not available. Please install it with 'pip install selenium'"
            )
        
        if driver is None:
            # Create a new Chrome driver
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            try:
                self.driver = webdriver.Chrome(options=options)
            except WebDriverException as e:
                logger.error(f"Failed to create Chrome driver: {e}")
                raise SeleniumError(f"Failed to create Chrome driver: {e}") from e
        else:
            self.driver = driver
        
        logger.debug("Initialized SeleniumBrowser")
    
    def get(self, url: str) -> str:
        """
        Get page content from URL.
        
        Args:
            url: URL to retrieve
            
        Returns:
            Page content as string
        """
        try:
            logger.debug(f"Navigating to {url}")
            self.driver.get(url)
            return self.driver.page_source
        except WebDriverException as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise SeleniumError(f"Failed to navigate to {url}: {e}") from e
    
    def extract_json(self, selector: str) -> Dict[str, Any]:
        """
        Extract JSON data from page using JavaScript.
        
        Args:
            selector: CSS selector to locate the JSON data
            
        Returns:
            Parsed JSON data as a dictionary
        """
        try:
            # Wait for the selector to be available
            self.wait_for_element(selector)
            
            # Get the JSON string from the page
            script = f"""
            return document.querySelector('{selector}').textContent;
            """
            json_str = self.driver.execute_script(script)
            
            if not json_str:
                logger.error(f"JSON data not found with selector: {selector}")
                raise ParsingError(f"JSON data not found with selector: {selector}")
            
            # Parse the JSON data
            json_data = json.loads(json_str)
            
            return json_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON data: {e}")
            raise ParsingError(f"Failed to parse JSON data: {e}") from e
        except Exception as e:
            logger.error(f"Failed to extract JSON data: {e}")
            raise SeleniumError(f"Failed to extract JSON data: {e}") from e
    
    def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """
        Wait for element to be available.
        
        Args:
            selector: CSS selector for the element
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if element is found, False otherwise
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {selector}")
            return False
    
    def close(self) -> None:
        """
        Close browser session.
        """
        logger.debug("Closing SeleniumBrowser")
        self.driver.quit()
