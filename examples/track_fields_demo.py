#!/usr/bin/env python3
"""
Demonstration of available track fields in SpotifyScraper v2.0.20

This example shows all the fields that are actually available when
extracting track data via web scraping, and explains which fields
are NOT available compared to the official Spotify API.
"""

from spotify_scraper import SpotifyClient
import json


def main():
    """Demonstrate available track fields."""
    print("SpotifyScraper v2.0.20 - Track Fields Demo")
    print("=" * 50)

    # Create client
    client = SpotifyClient()

    # Example track
    track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"

    print(f"\nExtracting track: {track_url}")
    track = client.get_track_info(track_url)

    print("\n=== AVAILABLE FIELDS ===")
    print(f"Keys in track data: {list(track.keys())}")

    print("\n=== TRACK DATA (formatted) ===")
    print(json.dumps(track, indent=2))

    print("\n=== SAFE FIELD ACCESS EXAMPLES ===")
    # Always use .get() method with defaults for safe access
    print(f"Track ID: {track.get('id', 'Unknown')}")
    print(f"Track Name: {track.get('name', 'Unknown')}")
    print(f"Track URI: {track.get('uri', 'Unknown')}")
    print(f"Duration: {track.get('duration_ms', 0) / 60000:.2f} minutes")
    print(f"Is Explicit: {track.get('is_explicit', False)}")
    print(f"Is Playable: {track.get('is_playable', True)}")
    print(f"Preview URL: {track.get('preview_url', 'Not available')}")

    # Artist information
    artists = track.get("artists", [])
    if artists:
        print(f"\nArtists:")
        for artist in artists:
            print(f"  - {artist.get('name', 'Unknown')} (ID: {artist.get('id', 'Unknown')})")

    # Album information
    album = track.get("album", {})
    if album:
        print(f"\nAlbum:")
        print(f"  Name: {album.get('name', 'Unknown')}")
        print(f"  ID: {album.get('id', 'Unknown')}")
        print(f"  URI: {album.get('uri', 'Unknown')}")
        print(f"  Images: {len(album.get('images', []))} available")

    print("\n=== FIELDS NOT AVAILABLE VIA WEB SCRAPING ===")
    print("The following fields are available in Spotify's official API but NOT via web scraping:")
    print("- popularity (0-100 score)")
    print("- track_number (position on album)")
    print("- disc_number")
    print("- available_markets (region availability)")
    print("- external_ids (ISRC, EAN, UPC)")
    print("- external_urls")
    print("- analysis_url")
    print("- time_signature")
    print("- key")
    print("- mode")
    print("- loudness")
    print("- tempo")

    print("\n=== CORRECT ERROR HANDLING ===")
    # Example of handling missing fields properly

    # WRONG - This will raise KeyError
    # popularity = track.get('popularity', 0)  # KeyError!

    # CORRECT - Use .get() with default
    popularity = track.get("popularity", "Not available")
    print(f"Popularity: {popularity}")

    # Clean up
    client.close()
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
