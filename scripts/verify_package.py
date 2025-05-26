#!/usr/bin/env python3
"""
Comprehensive package verification script for SpotifyScraper.
Tests all major functionality to ensure the package is working correctly.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add src to path for development testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import spotify_scraper
    from spotify_scraper import SpotifyClient
    from spotify_scraper.browsers import create_browser
    from spotify_scraper.extractors import TrackExtractor, AlbumExtractor, ArtistExtractor, PlaylistExtractor
    print(f"✅ Successfully imported spotify_scraper version {spotify_scraper.__version__}")
except ImportError as e:
    print(f"❌ Failed to import spotify_scraper: {e}")
    sys.exit(1)


def test_imports():
    """Test all imports work correctly."""
    print("\n📦 Testing imports...")
    
    modules = [
        "spotify_scraper.core.config",
        "spotify_scraper.core.exceptions",
        "spotify_scraper.utils.logger",
        "spotify_scraper.utils.url",
        "spotify_scraper.parsers.json_parser",
        "spotify_scraper.cli.utils",
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            return False
    
    return True


def test_browser_creation():
    """Test browser creation."""
    print("\n🌐 Testing browser creation...")
    
    try:
        browser = create_browser("requests")
        print("  ✅ RequestsBrowser created successfully")
        return True
    except Exception as e:
        print(f"  ❌ Failed to create browser: {e}")
        return False


def test_extractors():
    """Test extractor initialization."""
    print("\n🔍 Testing extractors...")
    
    try:
        browser = create_browser("requests")
        
        extractors = [
            ("TrackExtractor", TrackExtractor),
            ("AlbumExtractor", AlbumExtractor),
            ("ArtistExtractor", ArtistExtractor),
            ("PlaylistExtractor", PlaylistExtractor),
        ]
        
        for name, extractor_class in extractors:
            extractor = extractor_class(browser)
            print(f"  ✅ {name} initialized")
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to initialize extractors: {e}")
        return False


def test_client():
    """Test SpotifyClient initialization."""
    print("\n💼 Testing SpotifyClient...")
    
    try:
        client = SpotifyClient()
        print("  ✅ SpotifyClient created with default config")
        
        # Test with different browser type
        client_selenium = SpotifyClient(browser_type="requests")
        print("  ✅ SpotifyClient created with custom browser type")
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to create SpotifyClient: {e}")
        return False


def test_cli_commands():
    """Test CLI command availability."""
    print("\n🖥️  Testing CLI commands...")
    
    try:
        from spotify_scraper.cli import cli
        
        commands = ["track", "album", "artist", "playlist", "download"]
        available_commands = list(cli.commands.keys())
        
        for cmd in commands:
            if cmd in available_commands:
                print(f"  ✅ {cmd} command available")
            else:
                print(f"  ❌ {cmd} command missing")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Failed to test CLI: {e}")
        return False


def test_utilities():
    """Test utility functions."""
    print("\n🔧 Testing utilities...")
    
    try:
        from spotify_scraper.utils.url import validate_url, extract_id, get_url_type
        
        # Test URL validation
        test_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
        validate_url(test_url)
        print("  ✅ URL validation working")
        
        # Test ID extraction
        track_id = extract_id(test_url)
        assert track_id == "6rqhFgbbKwnb9MLmUQDhG6"
        print("  ✅ ID extraction working")
        
        # Test URL type detection
        url_type = get_url_type(test_url)
        assert url_type == "track"
        print("  ✅ URL type detection working")
        
        return True
    except Exception as e:
        print(f"  ❌ Utility test failed: {e}")
        return False


def test_configuration():
    """Test configuration system."""
    print("\n⚙️  Testing configuration...")
    
    try:
        from spotify_scraper.core.config import Config
        
        config = Config()
        print(f"  ✅ Default config loaded")
        
        # Test config values through dictionary access
        config_dict = config.as_dict()
        assert 'cache_enabled' in config_dict
        assert 'timeout' in config_dict
        print("  ✅ Config attributes accessible")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print(f"🧪 SpotifyScraper Package Verification")
    print(f"📌 Version: {spotify_scraper.__version__}")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Browser Creation", test_browser_creation),
        ("Extractors", test_extractors),
        ("Client", test_client),
        ("CLI Commands", test_cli_commands),
        ("Utilities", test_utilities),
        ("Configuration", test_configuration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n{'✅ All tests passed!' if passed == total else f'❌ {total - passed} tests failed'}")
    print(f"Score: {passed}/{total}")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())