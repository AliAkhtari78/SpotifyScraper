"""
Selenium-based browser implementation for SpotifyScraper.

This module provides a browser implementation using Selenium for handling
dynamic web content.
"""

try:
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService

    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

import json
import logging
from typing import Any, Dict, Optional

from spotify_scraper.browsers.base import Browser
from spotify_scraper.core.exceptions import BrowserError, ParsingError

logger = logging.getLogger(__name__)


class SeleniumBrowser(Browser):
    """
    Browser implementation using Selenium.

    This class provides an implementation of the Browser interface
    using Selenium for handling dynamic web content.
    """

    def __init__(self, driver: Optional[Any] = None, browser_name: str = "chrome", use_webdriver_manager: bool = True):
        """
        Initialize the SeleniumBrowser.

        Args:
            driver: Selenium WebDriver instance (optional)
            browser_name: Browser to use ("chrome" or "firefox")
            use_webdriver_manager: Whether to use webdriver-manager for automatic driver downloads (default: True)
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError(
                "Selenium is not available. Please install it with 'pip install selenium'"
            )

        if driver is None:
            browser_name = browser_name.lower()

            if browser_name == "firefox":
                # Create a new Firefox driver
                options = webdriver.FirefoxOptions()
                options.add_argument("--headless")
                options.add_argument("--window-size=1920,1080")
                # Firefox-specific preferences
                options.set_preference("dom.webnotifications.enabled", False)
                options.set_preference("dom.push.enabled", False)

                try:
                    if use_webdriver_manager and WEBDRIVER_MANAGER_AVAILABLE:
                        # Use webdriver-manager to automatically download and manage driver
                        service = FirefoxService(GeckoDriverManager().install())
                        self.driver = webdriver.Firefox(service=service, options=options)
                        logger.info("Initialized Firefox WebDriver using webdriver-manager")
                    else:
                        # Fall back to system-installed driver
                        if use_webdriver_manager and not WEBDRIVER_MANAGER_AVAILABLE:
                            logger.warning(
                                "webdriver-manager requested but not available. "
                                "Install with: pip install webdriver-manager"
                            )
                        self.driver = webdriver.Firefox(options=options)
                        logger.info("Initialized Firefox WebDriver using system driver")
                except WebDriverException as e:
                    logger.error("Failed to create Firefox driver: %s", e)
                    raise BrowserError(f"Failed to create Firefox driver: {e}") from e
            elif browser_name == "chrome":
                # Create a new Chrome driver
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")

                try:
                    if use_webdriver_manager and WEBDRIVER_MANAGER_AVAILABLE:
                        # Use webdriver-manager to automatically download and manage driver
                        service = ChromeService(ChromeDriverManager().install())
                        self.driver = webdriver.Chrome(service=service, options=options)
                        logger.info("Initialized Chrome WebDriver using webdriver-manager")
                    else:
                        # Fall back to system-installed driver
                        if use_webdriver_manager and not WEBDRIVER_MANAGER_AVAILABLE:
                            logger.warning(
                                "webdriver-manager requested but not available. "
                                "Install with: pip install webdriver-manager"
                            )
                        self.driver = webdriver.Chrome(options=options)
                        logger.info("Initialized Chrome WebDriver using system driver")
                except WebDriverException as e:
                    logger.error("Failed to create Chrome driver: %s", e)
                    raise BrowserError(f"Failed to create Chrome driver: {e}") from e
            else:
                raise ValueError(f"Unsupported browser: {browser_name}. Use 'chrome' or 'firefox'")
        else:
            self.driver = driver

        logger.debug(
            "Initialized SeleniumBrowser with %s",
            browser_name if driver is None else "custom driver",
        )

    def get_page_content(self, url: str) -> str:
        """
        Get page content from URL.

        Args:
            url: URL to retrieve

        Returns:
            Page content as string
        """
        try:
            logger.debug("Navigating to %s", url)
            self.driver.get(url)
            return self.driver.page_source
        except WebDriverException as e:
            logger.error("Failed to navigate to %s: %s", url, e)
            raise BrowserError(f"Failed to navigate to {url}: {e}") from e

    def get_json(self, url: str) -> Dict[str, Any]:
        """
        Get JSON data from a URL.

        Args:
            url: URL that returns JSON data

        Returns:
            Parsed JSON data as a dictionary
        """
        try:
            content = self.get_page_content(url)
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON data: %s", e)
            raise ParsingError(f"Failed to parse JSON data: {e}") from e

    def download_file(self, url: str, path: str) -> str:
        """
        Download a file from a URL.

        Args:
            url: URL to download
            path: Local path to save file

        Returns:
            Path where file was saved
        """
        import os

        import requests

        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return path
        except Exception as e:
            logger.error("Failed to download file: %s", e)
            raise BrowserError(f"Failed to download file: {e}") from e

    def get_auth_token(self) -> Optional[str]:
        """
        Get authentication token.

        Returns:
            Authentication token if available
        """
        # Selenium browser doesn't have built-in auth
        return None

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
                logger.error("JSON data not found with selector: %s", selector)
                raise ParsingError(f"JSON data not found with selector: {selector}")

            # Parse the JSON data
            json_data = json.loads(json_str)

            return json_data
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON data: %s", e)
            raise ParsingError(f"Failed to parse JSON data: {e}") from e
        except Exception as e:
            logger.error("Failed to extract JSON data: %s", e)
            raise BrowserError(f"Failed to extract JSON data: {e}") from e

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
            logger.warning("Timeout waiting for element: %s", selector)
            return False

    def close(self) -> None:
        """
        Close browser session.
        """
        logger.debug("Closing SeleniumBrowser")
        self.driver.quit()
