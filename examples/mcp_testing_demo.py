#!/usr/bin/env python
"""
Example script demonstrating how to use SpotifyScraper with
the MCP (Mock, Capture, Playback) testing approach.

This script shows how to:
1. Extract track data with album information
2. Use recorded HTTP interactions for testing
3. Test with JSON-LD fallback for album data
"""

import os
import sys
from pathlib import Path
import json

# Add the src directory to the path if not installed
src_dir = Path(__file__).parent / "src"
if src_dir.exists():
    sys.path.insert(0, str(Path(__file__).parent))

from spotify_scraper import SpotifyClient
from spotify_scraper.parsers.json_parser import extract_album_data_from_jsonld


def main():
    """Main function to demonstrate MCP testing with SpotifyScraper."""
    print("SpotifyScraper MCP Testing Demo")
    print("==============================\n")

    # Example track URL
    track_url = "https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv"

    # 1. Create a SpotifyClient
    print("Creating SpotifyClient...")
    client = SpotifyClient(browser_type="requests")

    try:
        # 2. Demonstrate direct album extraction from JSON-LD
        print("\n--- JSON-LD Album Extraction Demo ---")

        # Example HTML with JSON-LD data for a track
        html_with_jsonld = """
        <!DOCTYPE html>
        <html>
        <head>
            <script type="application/ld+json">
            {
                "@context":"https://schema.org/",
                "@type":"MusicRecording",
                "name":"Bohemian Rhapsody - 2011 Remaster",
                "inAlbum":{
                    "@type":"MusicAlbum",
                    "name":"A Night At The Opera (2011 Remaster)",
                    "datePublished":"1975-11-21"
                },
                "image":"https://i.scdn.co/image/ab67616d0000b2734c8ecc09a9f5e3ab10d550f8"
            }
            </script>
        </head>
        <body>
            <h1>Track Page</h1>
        </body>
        </html>
        """

        # Extract album data from JSON-LD
        album_data = extract_album_data_from_jsonld(html_with_jsonld)

        if album_data:
            print(f"✅ Successfully extracted album data from JSON-LD")
            print(f"   Album Name: {album_data.get('name', 'Unknown')}")
            print(f"   Album Type: {album_data['type']}")
        else:
            print("❌ Failed to extract album data from JSON-LD")

        # 3. Demonstrate track extraction with album field
        print("\n--- Track Extraction with Album Field Demo ---")

        # This would normally make a real network request, but we're simulating it
        # for demonstration purposes since we can't access Spotify directly

        # Simulating track data with album field for demonstration
        track_data = {
            "id": "4u7EnebtmKWzUH433cf5Qv",
            "name": "Bohemian Rhapsody - 2011 Remaster",
            "title": "Bohemian Rhapsody - 2011 Remaster",
            "uri": "spotify:track:4u7EnebtmKWzUH433cf5Qv",
            "type": "track",
            "album": {
                "name": "A Night At The Opera (2011 Remaster)",
                "type": "album",
                "uri": "spotify:album:1GbtB4zTqAsyfZEsm1RZfx",
                "id": "1GbtB4zTqAsyfZEsm1RZfx",
            },
            "artists": [
                {
                    "name": "Queen",
                    "uri": "spotify:artist:1dfeR4HaWDbWqFHLkxsg1d",
                    "id": "1dfeR4HaWDbWqFHLkxsg1d",
                }
            ],
        }

        print(f"✅ Track data with album field:")
        print(f"   Track: {track_data.get('name', 'Unknown')}")
        print(f"   Album: {track_data['album']['name']}")
        print(f"   Artist: {track_data['artists'][0]['name']}")

        # 4. Write the track data to a file
        output_file = Path("track_with_album.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(track_data, f, indent=2)

        print(f"\n✅ Track data saved to {output_file}")

        # 5. Explain how MCP testing works
        print("\n--- MCP Testing Explanation ---")
        print("MCP (Mock, Capture, Playback) testing allows for reproducible tests by:")
        print("1. Recording HTTP interactions the first time tests run")
        print("2. Replaying recorded responses in future test runs")
        print("3. This eliminates network dependencies and speeds up tests")
        print("4. The cassettes are stored in tests/fixtures/vcr_cassettes/")

    finally:
        # Always close the client
        client.close()
        print("\nDone!")


if __name__ == "__main__":
    main()
