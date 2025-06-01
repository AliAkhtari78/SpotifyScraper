#!/usr/bin/env python3
"""
Basic usage examples for SpotifyScraper v2.0

This script demonstrates the basic functionality of the SpotifyScraper library,
including extracting information from tracks, albums, artists, and playlists.
"""

from spotify_scraper import SpotifyClient, extract_id, is_spotify_url


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
        track = client.get_track_info(track_url)

        if "ERROR" not in track:
            print(f"   Title: {track.get('name', 'Unknown')}")
            artists = ", ".join([a.get("name", "") for a in track.get("artists", [])])
            print(f"   Artists: {artists}")
            print(f"   Album: {track.get('album', {}).get('name', 'Unknown')}")
            duration_ms = track.get("duration_ms", 0)
            duration_min = duration_ms // 60000
            duration_sec = (duration_ms % 60000) // 1000
            print(f"   Duration: {duration_min}:{duration_sec:02d}")
            print(f"   Preview Available: {'Yes' if track.get('preview_url') else 'No'}")
        else:
            print(f"   Error: {track['ERROR']}")
    except Exception as e:
        print(f"   Error extracting track: {e}")

    # Example album URL
    album_url = "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"

    print(f"\n3. Extracting album information:")
    try:
        album = client.get_album_info(album_url)

        if "ERROR" not in album:
            print(f"   Title: {album.get('name', 'Unknown')}")
            artists = ", ".join([a.get("name", "") for a in album.get("artists", [])])
            print(f"   Artists: {artists}")
            print(f"   Release Date: {album.get('release_date', 'Unknown')}")
            print(f"   Total Tracks: {album.get('total_tracks', 0)}")
            print(f"   Label: {album.get('label', 'Unknown')}")
        else:
            print(f"   Error: {album['ERROR']}")
    except Exception as e:
        print(f"   Error extracting album: {e}")

    # Example artist URL
    artist_url = "https://open.spotify.com/artist/0YC192cP3KPCRWx8zr8MfZ"

    print(f"\n4. Extracting artist information:")
    try:
        artist = client.get_artist_info(artist_url)

        if "ERROR" not in artist:
            print(f"   Name: {artist.get('name', 'Unknown')}")
            genres = ", ".join(artist.get("genres", [])) or "Not specified"
            print(f"   Genres: {genres}")
            print(f"   Popularity: {artist.get('popularity', 0)}/100")
            followers = artist.get("followers", {}).get("total", 0)
            print(f"   Followers: {followers:,}")
        else:
            print(f"   Error: {artist['ERROR']}")
    except Exception as e:
        print(f"   Error extracting artist: {e}")

    # Example playlist URL
    playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

    print(f"\n5. Extracting playlist information:")
    try:
        playlist = client.get_playlist_info(playlist_url)

        if "ERROR" not in playlist:
            print(f"   Name: {playlist.get('name', 'Unknown')}")
            print(f"   Owner: {playlist.get('owner', {}).get('name', 'Unknown')}")
            print(f"   Description: {playlist.get('description', 'N/A')[:50]}...")
            print(f"   Total Tracks: {playlist.get('track_count', 0)}")
            print(f"   Public: {'Yes' if playlist.get('public') else 'No'}")
        else:
            print(f"   Error: {playlist['ERROR']}")
    except Exception as e:
        print(f"   Error extracting playlist: {e}")

    # Automatic URL type detection
    print(f"\n6. Automatic URL type detection:")
    test_urls = [track_url, album_url, artist_url, playlist_url]

    for url in test_urls:
        try:
            # Use get_all_info which automatically detects the URL type
            info = client.get_all_info(url)
            entity_type = info.get("type", "unknown")
            entity_name = info.get("name", "Unknown")
            print(f"   {entity_type.capitalize()}: {entity_name}")
        except Exception as e:
            print(f"   Error with {url}: {e}")

    # Clean up
    client.close()
    print("\n✓ Client closed successfully")


if __name__ == "__main__":
    main()
