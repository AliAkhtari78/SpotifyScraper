#!/usr/bin/env python3
"""
Simple test to verify SpotifyScraper is working correctly.
This tests basic functionality without network calls.
"""

import sys

try:
    # Test 1: Import the package
    print("1. Testing package import...")
    import spotify_scraper
    print(f"   ✓ Package imported successfully")
    print(f"   ✓ Version: {spotify_scraper.__version__}")
    
    # Test 2: Import main components
    print("\n2. Testing component imports...")
    from spotify_scraper import SpotifyClient, is_spotify_url, extract_id
    print("   ✓ SpotifyClient imported")
    print("   ✓ Utility functions imported")
    
    # Test 3: Test utility functions
    print("\n3. Testing utility functions...")
    test_url = "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
    print(f"   Test URL: {test_url}")
    print(f"   ✓ is_spotify_url: {is_spotify_url(test_url)}")
    print(f"   ✓ extract_id: {extract_id(test_url)}")
    
    # Test 4: Create client
    print("\n4. Testing client creation...")
    client = SpotifyClient(log_level="WARNING")
    print("   ✓ Client created successfully")
    
    # Test 5: Test extractors
    print("\n5. Testing extractor imports...")
    from spotify_scraper.extractors import TrackExtractor, AlbumExtractor, ArtistExtractor, PlaylistExtractor
    print("   ✓ All extractors imported successfully")
    
    # Test 6: Test CLI availability
    print("\n6. Testing CLI availability...")
    from spotify_scraper.cli import main
    print("   ✓ CLI module imported successfully")
    
    print("\n✅ All basic tests passed!")
    print("\nSpotifyScraper v2.0 is installed and ready to use.")
    print("\nNext steps:")
    print("- Use 'spotify-scraper --help' to see CLI commands")
    print("- Try extracting data from a Spotify URL")
    print("- Check the examples/ directory for more usage examples")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print("\nMake sure you have installed the package:")
    print("pip install -e .")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    sys.exit(1)