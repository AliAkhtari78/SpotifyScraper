"""
Simple script to test the TrackExtractor implementation.
This bypasses the complex test infrastructure and dependencies.
"""

import json
import os
from pathlib import Path

# Define a simple mock browser for testing
class MockBrowser:
    """Mock browser for testing extractors without network requests."""
    
    def __init__(self, html_content):
        self.html_content = html_content
    
    def get(self, url):
        """Return the mock HTML content regardless of URL."""
        return self.html_content


# Import the modules we need
from src.spotify_scraper.extractors.track import TrackExtractor
from src.spotify_scraper.parsers.json_parser import extract_track_data_from_page


def main():
    # Load test fixtures
    fixture_path = Path(__file__).parent / "tests" / "fixtures"
    
    with open(fixture_path / "html" / "track_modern.html", "r", encoding="utf-8") as f:
        track_html = f.read()
    
    with open(fixture_path / "json" / "track_expected.json", "r", encoding="utf-8") as f:
        expected_track_data = json.load(f)
    
    # Create a mock browser with the test HTML
    mock_browser = MockBrowser(track_html)
    
    # Create the track extractor
    extractor = TrackExtractor(browser=mock_browser)
    
    # Extract track data using the extractor
    track_data = extractor.extract(url="https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv")
    
    # Print results for comparison
    print("\nExpected Output JSON:")
    print(json.dumps(expected_track_data, indent=2))
    
    print("\nActual Output JSON:")
    print(json.dumps(track_data, indent=2))
    
    # Check for lyrics
    if "lyrics" in track_data:
        print("\nLyrics extraction successful!")
        print(f"Number of lyrics lines: {len(track_data['lyrics']['lines'])}")
    else:
        print("\nLyrics extraction failed!")


if __name__ == "__main__":
    main()