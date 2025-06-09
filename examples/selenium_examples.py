#!/usr/bin/env python3
"""
Selenium examples for SpotifyScraper.

This script demonstrates how to use Selenium browser backend
for dynamic content extraction and headless scraping.
"""

import sys
sys.path.insert(0, '../src')

from spotify_scraper import SpotifyClient
from spotify_scraper.browsers.selenium_browser import SeleniumBrowser
from spotify_scraper.extractors.track import TrackExtractor
from spotify_scraper.extractors.album import AlbumExtractor


def example_selenium_with_chrome():
    """Example: Using Selenium with Chrome browser."""
    print("=== Selenium Chrome Example ===")
    
    # Create Selenium browser with Chrome (headless by default)
    browser = SeleniumBrowser(browser_name="chrome")
    
    # Create client with Selenium browser
    client = SpotifyClient(browser=browser)
    
    # Extract track information
    track_url = "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
    track = client.get_track_info(track_url)
    
    print(f"Track: {track['name']}")
    print(f"Artist: {track['artists'][0]['name']}")
    print(f"Album: {track['album']['name'] if 'album' in track else 'N/A'}")
    
    # Clean up
    client.close()
    print()


def example_selenium_with_firefox():
    """Example: Using Selenium with Firefox browser."""
    print("=== Selenium Firefox Example ===")
    
    try:
        # Create Selenium browser with Firefox
        browser = SeleniumBrowser(browser_name="firefox")
        
        # Create album extractor
        album_extractor = AlbumExtractor(browser)
        
        # Extract album information
        album_url = "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy"
        album = album_extractor.extract(album_url)
        
        print(f"Album: {album['name']}")
        print(f"Artist: {album['artists'][0]['name']}")
        print(f"Total Tracks: {album.get('total_tracks', 'N/A')}")
        print(f"Release Date: {album.get('release_date', 'N/A')}")
        
        # Clean up
        browser.close()
        
    except Exception as e:
        print(f"Firefox example failed: {e}")
        print("Make sure Firefox and GeckoDriver are installed")
    
    print()


def example_selenium_with_webdriver_manager():
    """Example: Using Selenium with automatic driver management."""
    print("=== Selenium with WebDriver Manager Example ===")
    
    try:
        # This will use webdriver-manager to automatically download drivers
        # Install with: pip install webdriver-manager
        browser = SeleniumBrowser(browser_name="chrome")
        
        # Create track extractor
        track_extractor = TrackExtractor(browser)
        
        # Extract track with enhanced metadata
        track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        track = track_extractor.extract(track_url)
        
        print(f"Track: {track['name']}")
        print(f"Duration: {track['duration_ms'] / 1000:.2f} seconds")
        
        # Check for new fields
        if 'track_number' in track:
            print(f"Track Number: {track['track_number']}")
        if 'disc_number' in track:
            print(f"Disc Number: {track['disc_number']}")
        if 'popularity' in track:
            print(f"Popularity: {track['popularity']}")
        
        # Clean up
        browser.close()
        
    except ImportError:
        print("webdriver-manager not installed")
        print("Install with: pip install webdriver-manager")
    except Exception as e:
        print(f"WebDriver Manager example failed: {e}")
    
    print()


def example_selenium_advanced_features():
    """Example: Advanced Selenium features."""
    print("=== Advanced Selenium Features ===")
    
    # Create browser with custom options
    browser = SeleniumBrowser(browser_name="chrome")
    
    # Test waiting for elements
    test_url = "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
    browser.get_page_content(test_url)
    
    # Wait for specific element
    if browser.wait_for_element('script#__NEXT_DATA__', timeout=10):
        print("✓ Found __NEXT_DATA__ script")
        
        # Extract JSON data from the page
        json_data = browser.extract_json('script#__NEXT_DATA__')
        print(f"✓ Extracted JSON with {len(json_data)} keys")
    else:
        print("✗ __NEXT_DATA__ script not found")
    
    # Clean up
    browser.close()
    print()


def example_selenium_performance_comparison():
    """Example: Compare performance between browsers."""
    import time
    
    print("=== Performance Comparison ===")
    
    test_url = "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy"
    
    # Test with requests (baseline)
    print("Testing with Requests browser...")
    start_time = time.time()
    client = SpotifyClient(browser_type="requests")
    album = client.get_album_info(test_url)
    requests_time = time.time() - start_time
    print(f"  Time: {requests_time:.2f}s")
    print(f"  Album: {album['name']}")
    client.close()
    
    # Test with Selenium Chrome
    print("\nTesting with Selenium Chrome...")
    start_time = time.time()
    client = SpotifyClient(browser_type="selenium")
    album = client.get_album_info(test_url)
    selenium_time = time.time() - start_time
    print(f"  Time: {selenium_time:.2f}s")
    print(f"  Album: {album['name']}")
    client.close()
    
    # Compare results
    print(f"\nPerformance difference: {selenium_time / requests_time:.1f}x slower")
    print("Note: Selenium is slower but can handle JavaScript-rendered content")
    print()


def main():
    """Run all Selenium examples."""
    print("SpotifyScraper Selenium Examples")
    print("=" * 40)
    print()
    
    # Run examples
    example_selenium_with_chrome()
    example_selenium_with_firefox()
    example_selenium_with_webdriver_manager()
    example_selenium_advanced_features()
    example_selenium_performance_comparison()
    
    print("All examples completed!")


if __name__ == "__main__":
    main()