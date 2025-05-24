#!/usr/bin/env python3
"""
Real functionality test for SpotifyScraper.

This script tests the library with real Spotify URLs to ensure
basic functionality is working correctly. Run this after each build
to validate the package works with real-world data.
"""

import sys
import json
import time
from pathlib import Path

# Test if package can be imported
try:
    from spotify_scraper import SpotifyClient
    from spotify_scraper.core.exceptions import SpotifyScraperError, URLError
    from spotify_scraper.utils.url import is_spotify_url, get_url_type
    print("✓ Package imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)


def quick_functionality_test():
    """Run a quick test of core functionality."""
    print("\n🎵 SpotifyScraper Quick Functionality Test 🎵")
    print("=" * 50)
    
    # Test URLs
    test_track = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"  # Pink Floyd
    test_album = "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"   # Dark Side of the Moon
    test_artist = "https://open.spotify.com/artist/0L8ExT028jH3ddEcZwqJJ5"  # RHCP
    
    results = {"passed": 0, "failed": 0}
    
    # Initialize client
    print("\n1. Client Initialization")
    try:
        client = SpotifyClient()
        print("   ✓ Client created successfully")
        results["passed"] += 1
    except Exception as e:
        print(f"   ✗ Client creation failed: {e}")
        results["failed"] += 1
        return results
    
    # Test URL utilities
    print("\n2. URL Utilities")
    try:
        assert is_spotify_url(test_track) == True
        assert get_url_type(test_track) == "track"
        print("   ✓ URL utilities working")
        results["passed"] += 1
    except Exception as e:
        print(f"   ✗ URL utilities failed: {e}")
        results["failed"] += 1
    
    # Test track extraction
    print("\n3. Track Extraction")
    try:
        track_data = client.get_track_info(test_track)
        if track_data and track_data.get("name"):
            print(f"   ✓ Track: {track_data['name']}")
            if track_data.get("artists"):
                print(f"   ✓ Artists: {', '.join(a['name'] for a in track_data['artists'])}")
            results["passed"] += 1
        else:
            print("   ✗ Track extraction returned no data")
            results["failed"] += 1
    except Exception as e:
        print(f"   ✗ Track extraction failed: {e}")
        results["failed"] += 1
    
    # Test album extraction
    print("\n4. Album Extraction")
    try:
        album_data = client.get_album_info(test_album)
        if album_data and album_data.get("name"):
            print(f"   ✓ Album: {album_data['name']}")
            results["passed"] += 1
        else:
            print("   ✗ Album extraction returned no data")
            results["failed"] += 1
    except Exception as e:
        print(f"   ✗ Album extraction failed: {e}")
        results["failed"] += 1
    
    # Test artist extraction
    print("\n5. Artist Extraction")
    try:
        artist_data = client.get_artist_info(test_artist)
        if artist_data and artist_data.get("name"):
            print(f"   ✓ Artist: {artist_data['name']}")
            results["passed"] += 1
        else:
            print("   ✗ Artist extraction returned no data")
            results["failed"] += 1
    except Exception as e:
        print(f"   ✗ Artist extraction failed: {e}")
        results["failed"] += 1
    
    # Clean up
    try:
        client.close()
        print("\n6. Cleanup")
        print("   ✓ Client closed successfully")
        results["passed"] += 1
    except Exception as e:
        print(f"   ✗ Cleanup failed: {e}")
        results["failed"] += 1
    
    return results


def main():
    """Run the functionality test."""
    results = quick_functionality_test()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Total:  {results['passed'] + results['failed']}")
    
    if results["failed"] == 0:
        print("\n🎉 ALL TESTS PASSED! Library is working correctly.")
        return True
    else:
        print(f"\n❌ {results['failed']} test(s) failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)