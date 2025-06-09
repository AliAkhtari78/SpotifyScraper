#!/usr/bin/env python3
"""
Demonstration of webdriver-manager integration in SpotifyScraper.

This example shows how to use the new use_webdriver_manager parameter
to automatically download browser drivers when using Selenium.
"""

import logging
from spotify_scraper import SpotifyClient

# Configure logging to see driver download info
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def demo_webdriver_manager():
    """Demonstrate webdriver-manager functionality."""
    
    # Example track URL
    track_url = "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"
    
    print("SpotifyScraper webdriver-manager Demo")
    print("=" * 50)
    
    # Example 1: Using Selenium with automatic driver download (default)
    print("\n1. Using Selenium with automatic driver download:")
    print("-" * 50)
    try:
        client = SpotifyClient(
            browser_type="selenium",
            use_webdriver_manager=True  # This is the default
        )
        print("✓ Client created with webdriver-manager")
        print("  Drivers will be automatically downloaded if needed")
        
        # Test with a simple request
        track_info = client.get_track_info(track_url)
        print(f"✓ Successfully fetched track: {track_info['name']} by {track_info['artists'][0]['name']}")
        
        client.close()
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Example 2: Using Selenium with system-installed drivers
    print("\n2. Using Selenium with system-installed drivers:")
    print("-" * 50)
    try:
        client = SpotifyClient(
            browser_type="selenium",
            use_webdriver_manager=False  # Use system drivers
        )
        print("✓ Client created with system drivers")
        print("  Requires chromedriver/geckodriver in PATH")
        
        # Test with a simple request
        track_info = client.get_track_info(track_url)
        print(f"✓ Successfully fetched track: {track_info['name']}")
        
        client.close()
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Make sure you have chromedriver/geckodriver installed in your PATH")
    
    # Example 3: Using Firefox with webdriver-manager
    print("\n3. Using Firefox with webdriver-manager:")
    print("-" * 50)
    try:
        # Note: We need to create the browser directly for Firefox
        from spotify_scraper.browsers.selenium_browser import SeleniumBrowser
        
        browser = SeleniumBrowser(
            browser_name="firefox",
            use_webdriver_manager=True
        )
        print("✓ Firefox browser created with webdriver-manager")
        
        # Test page fetching
        content = browser.get_page_content("https://open.spotify.com")
        if content:
            print("✓ Successfully fetched page with Firefox")
        
        browser.close()
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Demo complete!")
    print("\nNotes:")
    print("- webdriver-manager automatically downloads and caches drivers")
    print("- Drivers are stored in ~/.wdm/ (or %USERPROFILE%\\.wdm on Windows)")
    print("- First run may take longer due to driver download")
    print("- Subsequent runs use cached drivers for faster startup")

if __name__ == "__main__":
    demo_webdriver_manager()