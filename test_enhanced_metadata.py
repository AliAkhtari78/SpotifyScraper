#!/usr/bin/env python3
"""
Test script specifically for enhanced metadata fields.
Demonstrates the availability of track_number, disc_number, popularity, 
artist verification status, and other enhanced fields.
"""

import sys
import json
from pathlib import Path

# Add the src directory to the path for development testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from spotify_scraper import SpotifyClient

def test_track_metadata():
    """Test and display all enhanced track metadata fields."""
    print("\n" + "="*60)
    print("Enhanced Track Metadata Test")
    print("="*60)
    
    client = SpotifyClient()
    
    # Test URLs with known metadata
    test_tracks = [
        {
            "url": "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp",  # Mr. Brightside
            "name": "The Killers - Mr. Brightside"
        },
        {
            "url": "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b",  # Blinding Lights
            "name": "The Weeknd - Blinding Lights"
        }
    ]
    
    for test_track in test_tracks:
        print(f"\nTesting: {test_track['name']}")
        print(f"URL: {test_track['url']}")
        print("-" * 60)
        
        try:
            track = client.get_track_info(test_track['url'])
            
            # Basic info
            print(f"Track Name: {track.get('name', 'N/A')}")
            print(f"Track ID: {track.get('id', 'N/A')}")
            print(f"Track URI: {track.get('uri', 'N/A')}")
            
            # Enhanced metadata
            print(f"\nEnhanced Metadata:")
            print(f"  Track Number: {track.get('track_number', 'Not available')}")
            print(f"  Disc Number: {track.get('disc_number', 'Not available')}")
            print(f"  Popularity: {track.get('popularity', 'Not available')}")
            print(f"  Duration: {track.get('duration_ms', 0) / 1000:.1f} seconds")
            print(f"  Explicit: {track.get('is_explicit', False)}")
            print(f"  Playable: {track.get('is_playable', True)}")
            print(f"  Type: {track.get('type', 'N/A')}")
            
            # Artist details with verification
            print(f"\nArtist Information:")
            for i, artist in enumerate(track.get('artists', [])):
                print(f"  Artist {i+1}:")
                print(f"    Name: {artist.get('name', 'N/A')}")
                print(f"    ID: {artist.get('id', 'N/A')}")
                print(f"    URI: {artist.get('uri', 'N/A')}")
                print(f"    URL: {artist.get('url', 'N/A')}")
                print(f"    Verified: {artist.get('verified', 'Not available')}")
                print(f"    Type: {artist.get('type', 'N/A')}")
            
            # Album information
            if 'album' in track and track['album']:
                album = track['album']
                print(f"\nAlbum Information:")
                print(f"  Name: {album.get('name', 'N/A')}")
                print(f"  ID: {album.get('id', 'N/A')}")
                print(f"  URI: {album.get('uri', 'N/A')}")
                print(f"  Type: {album.get('album_type', 'N/A')}")
                print(f"  Total Tracks: {album.get('total_tracks', 'N/A')}")
                print(f"  Release Date: {album.get('release_date', 'N/A')}")
                print(f"  Release Date Precision: {album.get('release_date_precision', 'N/A')}")
                
                # Album artists
                if 'artists' in album:
                    print(f"  Album Artists:")
                    for artist in album['artists']:
                        print(f"    - {artist.get('name', 'N/A')} (ID: {artist.get('id', 'N/A')})")
                
                # Album images
                if 'images' in album and album['images']:
                    print(f"  Cover Images: {len(album['images'])} sizes available")
                    for img in album['images']:
                        print(f"    - {img.get('width', '?')}x{img.get('height', '?')} px")
            
            # External URLs
            if 'external_urls' in track:
                print(f"\nExternal URLs:")
                for platform, url in track['external_urls'].items():
                    print(f"  {platform}: {url}")
            
            # Preview URL
            if track.get('preview_url'):
                print(f"\nPreview URL: {track['preview_url'][:60]}...")
            
            # Additional metadata that might be available
            print(f"\nAdditional Fields:")
            print(f"  Available Markets: {'available_markets' in track}")
            print(f"  External IDs: {'external_ids' in track}")
            print(f"  Restrictions: {track.get('restrictions', 'None')}")
            
        except Exception as e:
            print(f"Error processing track: {e}")
    
    client.close()

def test_album_metadata():
    """Test and display all enhanced album metadata fields."""
    print("\n" + "="*60)
    print("Enhanced Album Metadata Test")
    print("="*60)
    
    client = SpotifyClient()
    
    # Test album with known metadata
    album_url = "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"  # The Dark Side of the Moon
    print(f"\nTesting album: Pink Floyd - The Dark Side of the Moon")
    print(f"URL: {album_url}")
    print("-" * 60)
    
    try:
        album = client.get_album_info(album_url)
        
        # Basic album info
        print(f"Album Name: {album.get('name', 'N/A')}")
        print(f"Album ID: {album.get('id', 'N/A')}")
        print(f"Album URI: {album.get('uri', 'N/A')}")
        print(f"Album Type: {album.get('album_type', 'N/A')}")
        print(f"Total Tracks: {album.get('total_tracks', 'N/A')}")
        
        # Release information
        print(f"\nRelease Information:")
        print(f"  Release Date: {album.get('release_date', 'N/A')}")
        print(f"  Release Date Precision: {album.get('release_date_precision', 'N/A')}")
        
        # Artists
        print(f"\nAlbum Artists:")
        for artist in album.get('artists', []):
            print(f"  - {artist.get('name', 'N/A')} (ID: {artist.get('id', 'N/A')})")
        
        # Copyrights and label
        print(f"\nLabel & Copyright:")
        print(f"  Label: {album.get('label', 'Not available')}")
        if 'copyrights' in album and album['copyrights']:
            print(f"  Copyrights:")
            for copyright in album['copyrights']:
                print(f"    - {copyright.get('text', 'N/A')} ({copyright.get('type', 'N/A')})")
        
        # Tracks with enhanced metadata
        print(f"\nTracks (showing first 3 with metadata):")
        for track in album.get('tracks', [])[:3]:
            print(f"  Track {track.get('track_number', '?')}: {track.get('name', 'N/A')}")
            print(f"    Disc: {track.get('disc_number', 'N/A')}")
            print(f"    Duration: {track.get('duration_ms', 0) / 1000:.1f}s")
            print(f"    Explicit: {track.get('is_explicit', False)}")
            print(f"    Preview: {'Yes' if track.get('preview_url') else 'No'}")
        
        # Additional metadata
        print(f"\nAdditional Album Metadata:")
        print(f"  Popularity: {album.get('popularity', 'Not available')}")
        print(f"  Available Markets: {'available_markets' in album}")
        print(f"  External IDs: {list(album.get('external_ids', {}).keys())}")
        print(f"  Genres: {album.get('genres', 'Not available')}")
        
    except Exception as e:
        print(f"Error processing album: {e}")
    
    client.close()

def test_field_availability_summary():
    """Summary of which fields are available through web scraping."""
    print("\n" + "="*60)
    print("Field Availability Summary")
    print("="*60)
    
    print("\nTrack Fields:")
    print("✅ Available:")
    print("  - name, id, uri, type")
    print("  - duration_ms, is_explicit, is_playable")
    print("  - artists (with name, id, uri, url)")
    print("  - album (with name, id, images, release_date, total_tracks)")
    print("  - preview_url, external_urls")
    print("  - track_number, disc_number (when part of album context)")
    
    print("\n❌ NOT Available (require API access):")
    print("  - popularity")
    print("  - available_markets")
    print("  - audio_features (tempo, key, etc.)")
    print("  - artist.verified status")
    
    print("\nAlbum Fields:")
    print("✅ Available:")
    print("  - name, id, uri, album_type")
    print("  - total_tracks, release_date")
    print("  - artists, images")
    print("  - tracks (with all track metadata)")
    print("  - external_urls")
    
    print("\n❌ NOT Available (require API access):")
    print("  - popularity")
    print("  - label")
    print("  - copyrights")
    print("  - available_markets")
    
    print("\nArtist Fields:")
    print("✅ Available:")
    print("  - name, id, uri, type")
    print("  - images")
    print("  - top_tracks (limited)")
    print("  - albums (limited)")
    
    print("\n❌ NOT Available (require API access):")
    print("  - followers")
    print("  - genres")
    print("  - popularity")
    print("  - verified status")

def main():
    """Run all enhanced metadata tests."""
    print("SpotifyScraper Enhanced Metadata Test")
    print("Testing availability of enhanced fields")
    
    test_track_metadata()
    test_album_metadata()
    test_field_availability_summary()
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)

if __name__ == "__main__":
    main()