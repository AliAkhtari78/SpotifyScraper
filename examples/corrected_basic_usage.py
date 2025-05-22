#!/usr/bin/env python3
"""
Corrected basic usage example for SpotifyScraper.

This example demonstrates the correct way to use the SpotifyClient API,
addressing the AttributeError the user encountered.

The main issue was using `get_track` instead of `get_track_info`.
"""

from spotify_scraper import SpotifyClient


def main():
    """Demonstrate correct SpotifyClient usage."""
    
    # Initialize the client
    client = SpotifyClient()
    
    # CORRECT: Use get_track_info instead of get_track
    track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
    
    try:
        # Get track information
        track_info = client.get_track_info(track_url)
        
        # Display track information
        print(f"Track: {track_info['name']}")
        print(f"Artists: {', '.join(artist['name'] for artist in track_info.get('artists', []))}")
        
        # Handle album information safely
        album = track_info.get('album', {})
        if isinstance(album, dict) and album.get('name'):
            print(f"Album: {album['name']}")
        else:
            print("Album: Information not available")
        
        # Handle duration safely
        duration_ms = track_info.get('duration_ms', 0)
        if duration_ms:
            print(f"Duration: {duration_ms / 1000:.2f} seconds")
        
        if track_info.get('preview_url'):
            print(f"Preview URL: {track_info['preview_url']}")
        else:
            print("Preview: Not available")
        
        # Additional methods available:
        print("\n--- Available Methods ---")
        print("client.get_track_info(url) - Get track information")
        print("client.get_track_lyrics(url) - Get lyrics (requires auth)")
        print("client.get_track_info_with_lyrics(url) - Get track info + lyrics")
        print("client.get_album_info(url) - Get album information")
        print("client.get_artist_info(url) - Get artist information")
        print("client.get_playlist_info(url) - Get playlist information")
        print("client.get_all_info(url) - Auto-detect URL type")
        print("client.download_cover(url) - Download cover art")
        print("client.download_preview_mp3(url) - Download 30-second preview")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Always close the client to clean up resources
        client.close()


if __name__ == "__main__":
    main()