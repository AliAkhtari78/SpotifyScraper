#!/usr/bin/env python
"""
Direct test script for track_extractor.py

This script directly imports the required modules and runs a test
without relying on the complex test infrastructure.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, TypedDict, Union, cast

# Import only the minimum necessary functionality
# These are simplified versions of the core types
class ImageData(TypedDict):
    url: str
    width: int
    height: int

class ArtistData(TypedDict, total=False):
    id: str
    name: str
    uri: str

class AlbumData(TypedDict, total=False):
    id: str
    name: str
    uri: str
    images: List[ImageData]
    release_date: str

class LyricsLineData(TypedDict):
    start_time_ms: int
    words: str
    end_time_ms: int

class LyricsData(TypedDict, total=False):
    sync_type: str
    lines: List[LyricsLineData]
    provider: str
    language: str

class TrackData(TypedDict, total=False):
    id: str
    name: str
    uri: str
    type: str
    title: str
    duration_ms: int
    artists: List[ArtistData]
    preview_url: str
    is_playable: bool
    is_explicit: bool
    album: AlbumData
    lyrics: LyricsData

# Mock Browser interface for testing
class Browser:
    def get(self, url: str) -> str:
        """Get page content from URL."""
        pass

class MockBrowser(Browser):
    def __init__(self, html_content: str):
        self.html_content = html_content
    
    def get(self, url: str) -> str:
        return self.html_content

# Import the simplified TrackExtractor implementation
from track_extractor import extract_track_data_from_html, TrackExtractor

def main():
    # Load test fixtures
    fixture_path = Path("/home/runner/work/SpotifyScraper/SpotifyScraper/tests/fixtures")
    
    with open(fixture_path / "html" / "track_modern.html", "r", encoding="utf-8") as f:
        track_html = f.read()
    
    with open(fixture_path / "json" / "track_expected.json", "r", encoding="utf-8") as f:
        expected_track_data = json.load(f)
    
    # Create a mock browser with the test HTML
    mock_browser = MockBrowser(track_html)
    
    # Print information about embed URL vs regular URLs
    print("\nSpotify URL handling:")
    print("===================")
    print("✅ Using /embed/ URLs: No authentication required, full access to track data & lyrics")
    print("❌ Using regular URLs: Requires authentication, may fail with 401 Unauthorized")
    print("🔄 Regular URL https://open.spotify.com/track/ID → https://open.spotify.com/embed/track/ID")
    
    # Create the track extractor
    extractor = TrackExtractor(browser=mock_browser)
    
    # Extract track data using the extractor with a regular URL
    # Note: The extractor will convert this to an embed URL internally
    track_data = extractor.extract(url="https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv")
    
    # Print results for comparison
    print("\nExpected Output JSON:")
    print(json.dumps(expected_track_data, indent=2))
    
    print("\nActual Output JSON:")
    print(json.dumps(track_data, indent=2))
    
    # Verification
    print("\nVerification Results:")
    success = True
    
    # Check track basics
    if track_data.get("id") != expected_track_data["id"]:
        print(f"❌ Track ID mismatch: {track_data.get('id')} != {expected_track_data['id']}")
        success = False
    else:
        print("✅ Track ID matches")
        
    if track_data.get("name") != expected_track_data["name"]:
        print(f"❌ Track name mismatch: {track_data.get('name')} != {expected_track_data['name']}")
        success = False
    else:
        print("✅ Track name matches")
    
    # Check album
    if "album" not in track_data:
        print("❌ Album data missing")
        success = False
    else:
        print("✅ Album data present")
        
    # Check lyrics
    if "lyrics" not in track_data:
        print("❌ Lyrics data missing")
        success = False
    else:
        print("✅ Lyrics data present")
        lyrics = track_data.get("lyrics", {})
        lines = lyrics.get("lines", [])
        print(f"   - Lyrics lines count: {len(lines)}")
        if lines and len(lines) > 0:
            if lines[1].get("words") != expected_track_data["lyrics"]["lines"][1].get("words"):
                print(f"❌ Lyrics line mismatch: {lines[1].get('words')} != {expected_track_data['lyrics']['lines'][1].get('words')}")
                success = False
            else:
                print("✅ Lyrics line matches")
    
    if success:
        print("\n🎉 All checks passed!")
    else:
        print("\n❌ Some checks failed!")


if __name__ == "__main__":
    main()