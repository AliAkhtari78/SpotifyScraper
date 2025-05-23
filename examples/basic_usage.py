#!/usr/bin/env python3
"""
Basic usage examples for SpotifyScraper v2.0

This script demonstrates the basic functionality of the SpotifyScraper library,
including extracting information from tracks, albums, artists, and playlists.
"""

from spotify_scraper import SpotifyClient, is_spotify_url, extract_id

def main():
    """Demonstrate basic SpotifyScraper usage."""
    print("SpotifyScraper v2.0 - Basic Usage Examples")
    print("=" * 50)
    
    # Create a client (no authentication required for basic info)
    client = SpotifyClient(log_level="INFO")
    
    # Example track URL
    track_url = "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
    
    print(f"\n1. Checking URL validity:")
    print(f"   URL: {track_url}")
    print(f"   Valid Spotify URL: {is_spotify_url(track_url)}")
    print(f"   Track ID: {extract_id(track_url)}")
    
    print(f"\n2. Extracting track information:")
    try:
        track_info = client.get_track_info(track_url)
        
        if "ERROR" not in track_info:
            print(f"   Title: {track_info.get('name', 'Unknown')}")
            artists = ", ".join([a.get('name', '') for a in track_info.get('artists', [])])
            print(f"   Artists: {artists}")
            print(f"   Album: {track_info.get('album', {}).get('name', 'Unknown')}")
            duration_ms = track_info.get('duration_ms', 0)
            duration_min = duration_ms // 60000
            duration_sec = (duration_ms % 60000) // 1000
            print(f"   Duration: {duration_min}:{duration_sec:02d}")
            print(f"   Preview Available: {'Yes' if track_info.get('preview_url') else 'No'}")
        else:
            print(f"   Error: {track_info['ERROR']}")
    except Exception as e:
        print(f"   Error extracting track: {e}")
    
    # Example album URL
    album_url = "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"
    
    print(f"\n3. Extracting album information:")
    try:
        album_info = client.get_album_info(album_url)
        
        if "ERROR" not in album_info:
            print(f"   Title: {album_info.get('name', 'Unknown')}")
            artists = ", ".join([a.get('name', '') for a in album_info.get('artists', [])])
            print(f"   Artists: {artists}")
            print(f"   Release Date: {album_info.get('release_date', 'Unknown')}")
            print(f"   Total Tracks: {album_info.get('total_tracks', 0)}")
            print(f"   Label: {album_info.get('label', 'Unknown')}")
        else:
            print(f"   Error: {album_info['ERROR']}")
    except Exception as e:
        print(f"   Error extracting album: {e}")
    
    # Example artist URL
    artist_url = "https://open.spotify.com/artist/0YC192cP3KPCRWx8zr8MfZ"
    
    print(f"\n4. Extracting artist information:")
    try:
        artist_info = client.get_artist_info(artist_url)
        
        if "ERROR" not in artist_info:
            print(f"   Name: {artist_info.get('name', 'Unknown')}")
            genres = ", ".join(artist_info.get('genres', [])) or "Not specified"
            print(f"   Genres: {genres}")
            print(f"   Popularity: {artist_info.get('popularity', 0)}/100")
            followers = artist_info.get('followers', {}).get('total', 0)
            print(f"   Followers: {followers:,}")
        else:
            print(f"   Error: {artist_info['ERROR']}")
    except Exception as e:
        print(f"   Error extracting artist: {e}")
    
    # Example playlist URL
    playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
    
    print(f"\n5. Extracting playlist information:")
    try:
        playlist_info = client.get_playlist_info(playlist_url)
        
        if "ERROR" not in playlist_info:
            print(f"   Name: {playlist_info.get('name', 'Unknown')}")
            print(f"   Owner: {playlist_info.get('owner', {}).get('display_name', 'Unknown')}")
            print(f"   Description: {playlist_info.get('description', 'N/A')[:50]}...")
            print(f"   Total Tracks: {playlist_info.get('tracks', {}).get('total', 0)}")
            print(f"   Public: {'Yes' if playlist_info.get('public') else 'No'}")
        else:
            print(f"   Error: {playlist_info['ERROR']}")
    except Exception as e:
        print(f"   Error extracting playlist: {e}")
    
    # Automatic URL type detection
    print(f"\n6. Automatic URL type detection:")
    test_urls = [
        track_url,
        album_url,
        artist_url,
        playlist_url
    ]
    
    for url in test_urls:
        try:
            # Use get_all_info which automatically detects the URL type
            info = client.get_all_info(url)
            entity_type = info.get('type', 'unknown')
            entity_name = info.get('name', 'Unknown')
            print(f"   {entity_type.capitalize()}: {entity_name}")
        except Exception as e:
            print(f"   Error with {url}: {e}")
    
    # Clean up
    client.close()
    print("\n✓ Client closed successfully")


if __name__ == "__main__":
    main()