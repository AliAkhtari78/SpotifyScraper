#!/usr/bin/env python3
"""Test Selenium headless scraping with SpotifyScraper."""

import sys
import time
sys.path.insert(0, 'src')

from spotify_scraper.browsers.selenium_browser import SeleniumBrowser
from spotify_scraper.extractors.track import TrackExtractor
from spotify_scraper.extractors.album import AlbumExtractor
from spotify_scraper.extractors.playlist import PlaylistExtractor

def test_selenium_headless():
    """Test Selenium browser in headless mode with different browsers."""
    print("🧪 Testing Selenium Headless Scraping\n")
    
    # Test URLs
    track_url = "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
    album_url = "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy"
    playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
    
    # Test with Chrome (default)
    print("1️⃣ Testing Chrome Headless Browser")
    try:
        print("   Initializing Chrome browser...")
        chrome_browser = SeleniumBrowser(browser_name="chrome")
        print("   ✅ Chrome browser initialized successfully")
        
        # Test track extraction
        print("\n   Testing track extraction...")
        track_extractor = TrackExtractor(chrome_browser)
        track_data = track_extractor.extract(track_url)
        print(f"   ✅ Track extracted: {track_data.get('name')} by {track_data.get('artists', [{}])[0].get('name')}")
        
        # Test page load time
        start_time = time.time()
        page_content = chrome_browser.get_page_content(album_url)
        load_time = time.time() - start_time
        print(f"   ⏱️  Page load time: {load_time:.2f} seconds")
        print(f"   📄 Page size: {len(page_content)} characters")
        
        chrome_browser.close()
        print("   ✅ Chrome browser closed successfully")
        
    except Exception as e:
        print(f"   ❌ Chrome test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with Firefox
    print("\n2️⃣ Testing Firefox Headless Browser")
    try:
        print("   Initializing Firefox browser...")
        firefox_browser = SeleniumBrowser(browser_name="firefox")
        print("   ✅ Firefox browser initialized successfully")
        
        # Test album extraction
        print("\n   Testing album extraction...")
        album_extractor = AlbumExtractor(firefox_browser)
        album_data = album_extractor.extract(album_url)
        print(f"   ✅ Album extracted: {album_data.get('name')} ({album_data.get('total_tracks')} tracks)")
        
        firefox_browser.close()
        print("   ✅ Firefox browser closed successfully")
        
    except Exception as e:
        print(f"   ❌ Firefox test failed: {e}")
        print("   ℹ️  Make sure Firefox and GeckoDriver are installed")
    
    # Test with webdriver-manager
    print("\n3️⃣ Testing Automatic Driver Management")
    try:
        print("   Testing webdriver-manager support...")
        # This will use webdriver-manager if installed
        auto_browser = SeleniumBrowser(browser_name="chrome")
        print("   ✅ Automatic driver management working")
        
        # Quick functionality test
        content = auto_browser.get_page_content("https://open.spotify.com/")
        print(f"   ✅ Successfully loaded Spotify homepage ({len(content)} bytes)")
        
        auto_browser.close()
        
    except Exception as e:
        print(f"   ⚠️  Webdriver-manager not available: {e}")
        print("   ℹ️  Install with: pip install webdriver-manager")
    
    print("\n✅ Selenium headless testing completed!")

if __name__ == "__main__":
    test_selenium_headless()