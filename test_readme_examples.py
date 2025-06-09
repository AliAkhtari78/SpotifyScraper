#!/usr/bin/env python3
"""
Test script to verify README code examples work correctly with enhanced metadata fields.
Tests track extraction, album extraction, and artist extraction features.
"""

import sys
import json
from pathlib import Path

# Add the src directory to the path for development testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from spotify_scraper import SpotifyClient

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print('=' * 60)

def test_track_extraction():
    """Test track extraction with enhanced metadata fields."""
    print_section("Testing Track Extraction")
    
    client = SpotifyClient()
    
    try:
        # Test track from README - "One More Time" by Daft Punk
        track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        print(f"\nTesting track URL: {track_url}")
        
        track = client.get_track_info(track_url)
        
        # Basic info as shown in README
        print(f"\nBasic Info:")
        print(f"  Name: {track['name']}")
        print(f"  Artist: {track['artists'][0]['name']}")
        
        # Enhanced metadata fields
        print(f"\nEnhanced Metadata:")
        print(f"  Track #: {track.get('track_number', 'N/A')} on disc {track.get('disc_number', 'N/A')}")
        print(f"  Popularity: {track.get('popularity', 'Not available')}")
        print(f"  Duration: {track.get('duration_ms', 0) / 1000:.1f} seconds")
        print(f"  Explicit: {track.get('is_explicit', False)}")
        print(f"  Playable: {track.get('is_playable', True)}")
        
        # Artist verification status
        print(f"\nArtist Details:")
        for artist in track.get('artists', []):
            print(f"  - {artist['name']}")
            if 'verified' in artist:
                print(f"    Verified: {artist['verified']}")
            if 'url' in artist:
                print(f"    URL: {artist['url']}")
        
        # Album info
        if 'album' in track:
            album = track['album']
            print(f"\nAlbum Info:")
            print(f"  Name: {album['name']}")
            print(f"  Total Tracks: {album.get('total_tracks', 'N/A')}")
            print(f"  Release Date: {album.get('release_date', 'N/A')}")
            print(f"  Album Type: {album.get('album_type', 'N/A')}")
        
        # Preview URL
        if track.get('preview_url'):
            print(f"\nPreview Available: Yes")
            print(f"  URL: {track['preview_url'][:50]}...")
        
        # Test downloading cover
        print(f"\nTesting cover download...")
        cover_path = client.download_cover(track_url)
        if cover_path and Path(cover_path).exists():
            print(f"  ✓ Cover saved to: {cover_path}")
            Path(cover_path).unlink()  # Clean up
        else:
            print(f"  ✗ Cover download failed")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
    finally:
        client.close()

def test_album_extraction():
    """Test album extraction with all tracks."""
    print_section("Testing Album Extraction")
    
    client = SpotifyClient()
    
    try:
        # Discovery album by Daft Punk
        album_url = "https://open.spotify.com/album/2noRn2Aes5aoNVsU6iWThc"
        print(f"\nTesting album URL: {album_url}")
        
        album = client.get_album_info(album_url)
        
        # Album info as shown in README
        print(f"\nAlbum Info:")
        print(f"  Name: {album.get('name', 'Unknown')}")
        print(f"  Artist: {(album.get('artists', [{}])[0].get('name', 'Unknown') if album.get('artists') else 'Unknown')}")
        print(f"  Released: {album.get('release_date', 'N/A')}")
        print(f"  Total Tracks: {album.get('total_tracks', 0)}")
        print(f"  Album Type: {album.get('album_type', 'N/A')}")
        
        # List first 5 tracks
        print(f"\nTracks (first 5):")
        for track in album.get('tracks', [])[:5]:
            track_num = track.get('track_number', '?')
            disc_num = track.get('disc_number', 1)
            name = track.get('name', 'Unknown')
            duration = track.get('duration_ms', 0) / 1000 / 60
            print(f"  {disc_num}.{track_num}. {name} ({duration:.1f} min)")
        
        if len(album.get('tracks', [])) > 5:
            print(f"  ... and {len(album['tracks']) - 5} more tracks")
        
        # Check for additional metadata
        print(f"\nAdditional Metadata:")
        print(f"  Label: {album.get('label', 'N/A')}")
        print(f"  Copyrights: {len(album.get('copyrights', []))} entries")
        print(f"  External IDs: {list(album.get('external_ids', {}).keys())}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
    finally:
        client.close()

def test_artist_extraction():
    """Test artist extraction with enhanced fields."""
    print_section("Testing Artist Extraction")
    
    client = SpotifyClient()
    
    try:
        # Daft Punk artist page
        artist_url = "https://open.spotify.com/artist/4tZwfgrHOc3mvqYlEYSvVi"
        print(f"\nTesting artist URL: {artist_url}")
        
        artist = client.get_artist_info(artist_url)
        
        # Artist info as shown in README
        print(f"\nArtist Info:")
        print(f"  Name: {artist.get('name', 'Unknown')}")
        print(f"  Followers: {artist.get('followers', {}).get('total', 'N/A'):,}" if isinstance(artist.get('followers', {}).get('total'), int) else f"  Followers: {artist.get('followers', {}).get('total', 'N/A')}")
        print(f"  Genres: {', '.join(artist.get('genres', []))}")
        print(f"  Popularity: {artist.get('popularity', 'N/A')}/100")
        
        # Additional metadata
        print(f"\nAdditional Details:")
        print(f"  Verified: {artist.get('verified', False)}")
        print(f"  Images: {len(artist.get('images', []))} available")
        
        # Top tracks
        print(f"\nTop Tracks (first 5):")
        for i, track in enumerate(artist.get('top_tracks', [])[:5], 1):
            print(f"  {i}. {track.get('name', 'Unknown')}")
            if 'popularity' in track:
                print(f"     Popularity: {track['popularity']}")
        
        # Recent albums
        if 'albums' in artist and 'items' in artist['albums']:
            print(f"\nRecent Albums (first 3):")
            for album in artist['albums']['items'][:3]:
                print(f"  - {album.get('name', 'Unknown')} ({album.get('release_date', 'N/A')[:4]})")
                print(f"    Type: {album.get('album_type', 'N/A')}")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
    finally:
        client.close()

def test_playlist_extraction():
    """Test playlist extraction with track details."""
    print_section("Testing Playlist Extraction")
    
    client = SpotifyClient()
    
    try:
        # Today's Top Hits playlist
        playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
        print(f"\nTesting playlist URL: {playlist_url}")
        
        playlist = client.get_playlist_info(playlist_url)
        
        # Playlist info as shown in README
        print(f"\nPlaylist Info:")
        print(f"  Name: {playlist.get('name', 'Unknown')}")
        print(f"  Owner: {playlist.get('owner', {}).get('display_name', playlist.get('owner', {}).get('id', 'Unknown'))}")
        print(f"  Tracks: {playlist.get('track_count', 0)}")
        print(f"  Followers: {playlist.get('followers', {}).get('total', 'N/A'):,}" if isinstance(playlist.get('followers', {}).get('total'), int) else f"  Followers: {playlist.get('followers', {}).get('total', 'N/A')}")
        
        # Additional metadata
        print(f"\nAdditional Details:")
        print(f"  Description: {playlist.get('description', 'N/A')[:100]}...")
        print(f"  Public: {playlist.get('public', True)}")
        print(f"  Collaborative: {playlist.get('collaborative', False)}")
        
        # First 5 tracks
        print(f"\nTracks (first 5):")
        for i, track in enumerate(playlist.get('tracks', [])[:5], 1):
            track_name = track.get('name', 'Unknown')
            artist_name = (track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')
            print(f"  {i}. {track_name} by {artist_name}")
            if 'added_at' in track:
                print(f"     Added: {track['added_at'][:10]}")
        
        if len(playlist.get('tracks', [])) > 5:
            print(f"  ... and {len(playlist['tracks']) - 5} more tracks")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
    finally:
        client.close()

def test_error_handling():
    """Test error handling with invalid URLs."""
    print_section("Testing Error Handling")
    
    from spotify_scraper.core.exceptions import (
        SpotifyScraperError,
        URLError,
        ExtractionError,
        DownloadError
    )
    
    client = SpotifyClient()
    
    try:
        # Test invalid URL
        print("\nTesting invalid URL handling...")
        invalid_url = "https://open.spotify.com/track/invalid123"
        
        try:
            track = client.get_track_info(invalid_url)
            print("  ✗ Error: Expected URLError or ExtractionError")
        except URLError:
            print("  ✓ URLError caught correctly")
        except ExtractionError as e:
            print(f"  ✓ ExtractionError caught: {e}")
        except SpotifyScraperError as e:
            print(f"  ✓ General SpotifyScraperError caught: {e}")
        
        # Test non-Spotify URL
        print("\nTesting non-Spotify URL...")
        non_spotify_url = "https://example.com/track/123"
        
        try:
            track = client.get_track_info(non_spotify_url)
            print("  ✗ Error: Expected URLError")
        except URLError:
            print("  ✓ URLError caught for non-Spotify URL")
        
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
    finally:
        client.close()

def main():
    """Run all tests."""
    print("=" * 60)
    print("SpotifyScraper README Examples Test")
    print("Testing enhanced metadata fields")
    print("=" * 60)
    
    # Run all tests
    test_track_extraction()
    test_album_extraction()
    test_artist_extraction()
    test_playlist_extraction()
    test_error_handling()
    
    print_section("Test Summary")
    print("\nAll tests completed!")
    print("\nNote: Some fields like 'popularity', 'followers', and 'genres' may not")
    print("be available through web scraping and will show as 'N/A' or 'Not available'.")
    print("This is expected behavior as noted in the README.")

if __name__ == "__main__":
    main()