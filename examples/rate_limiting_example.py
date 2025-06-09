#!/usr/bin/env python3
"""
Rate limiting example for SpotifyScraper.

This script demonstrates how to use the built-in rate limiting
features to avoid hitting Spotify's rate limits.
"""

import sys
import time
sys.path.insert(0, '../src')

from spotify_scraper import SpotifyClient
from spotify_scraper.browsers.requests_browser import RequestsBrowser


def example_default_rate_limiting():
    """Example: Using default rate limiting."""
    print("=== Default Rate Limiting Example ===")
    
    # Client uses 0.5s delay by default
    client = SpotifyClient()
    
    # Process multiple URLs
    urls = [
        "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp",
        "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
        "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
    ]
    
    print("Processing tracks with default rate limiting (0.5s between requests)...")
    start_time = time.time()
    
    for i, url in enumerate(urls, 1):
        track = client.get_track_info(url)
        print(f"  {i}. {track['name']} by {track['artists'][0]['name']}")
    
    elapsed = time.time() - start_time
    print(f"Total time: {elapsed:.2f}s (includes rate limiting delays)")
    
    client.close()
    print()


def example_custom_rate_limiting():
    """Example: Using custom rate limiting settings."""
    print("=== Custom Rate Limiting Example ===")
    
    # Create browser with custom rate limiting
    browser = RequestsBrowser(
        rate_limit_delay=1.0,      # 1 second between requests
        rate_limit_backoff=3.0     # Triple the delay on rate limit errors
    )
    
    # Create client with custom browser
    client = SpotifyClient(browser=browser)
    
    print("Processing with custom rate limiting (1s delay, 3x backoff)...")
    
    # Test with album tracks
    album_url = "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy"
    album = client.get_album_info(album_url)
    
    print(f"Album: {album['name']} ({album.get('total_tracks', 'N/A')} tracks)")
    
    # Process first 3 tracks
    start_time = time.time()
    for i, track in enumerate(album['tracks'][:3], 1):
        track_url = f"https://open.spotify.com/track/{track['id']}"
        track_info = client.get_track_info(track_url)
        print(f"  {i}. {track_info['name']} ({track_info['duration_ms'] / 1000:.2f}s)")
    
    elapsed = time.time() - start_time
    print(f"Time for 3 tracks: {elapsed:.2f}s")
    
    client.close()
    print()


def example_rate_limit_recovery():
    """Example: Handling rate limit errors gracefully."""
    print("=== Rate Limit Recovery Example ===")
    
    # Create browser with aggressive settings to potentially trigger rate limits
    browser = RequestsBrowser(
        rate_limit_delay=0.1,      # Very short delay (not recommended!)
        rate_limit_backoff=2.0,    # Double delay on errors
        retries=3                  # Retry up to 3 times
    )
    
    client = SpotifyClient(browser=browser)
    
    print("Testing rate limit recovery with aggressive settings...")
    print("(This may trigger rate limits - for demonstration only)")
    
    # Process many URLs quickly
    urls = [
        f"https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9L{i}" 
        for i in range(5)
    ]
    
    success_count = 0
    error_count = 0
    
    for url in urls:
        try:
            # This might fail with invalid URLs but demonstrates rate limiting
            track = client.get_track_info(url)
            success_count += 1
            print(f"  ✓ Successfully processed track")
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error: {type(e).__name__}")
    
    print(f"\nResults: {success_count} success, {error_count} errors")
    print("The browser automatically handles rate limits with exponential backoff")
    
    client.close()
    print()


def example_bulk_operations_with_rate_limiting():
    """Example: Bulk operations with rate limiting."""
    print("=== Bulk Operations with Rate Limiting ===")
    
    from spotify_scraper.utils.common import SpotifyBulkOperations
    
    # Client with default rate limiting
    client = SpotifyClient()
    bulk = SpotifyBulkOperations(client)
    
    # Process playlist with rate limiting
    playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
    
    print("Downloading playlist covers with rate limiting...")
    start_time = time.time()
    
    # This will respect rate limits while downloading
    covers = bulk.download_playlist_covers(
        playlist_url,
        output_dir="playlist_covers/",
        max_tracks=5  # Limit to first 5 for demo
    )
    
    elapsed = time.time() - start_time
    print(f"Downloaded {len(covers)} covers in {elapsed:.2f}s")
    print("Rate limiting ensures we don't overwhelm Spotify's servers")
    
    client.close()
    print()


def example_monitoring_rate_limits():
    """Example: Monitor rate limiting in action."""
    print("=== Monitoring Rate Limits ===")
    
    import logging
    
    # Enable debug logging to see rate limiting in action
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create client (rate limiting messages will be logged)
    client = SpotifyClient()
    
    print("Processing tracks with debug logging enabled...")
    print("Watch for 'Rate limiting: sleeping for X seconds' messages\n")
    
    # Process a few tracks
    urls = [
        "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp",
        "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
    ]
    
    for url in urls:
        track = client.get_track_info(url)
        print(f"Processed: {track['name']}")
    
    client.close()
    
    # Reset logging
    logging.basicConfig(level=logging.WARNING)
    print()


def main():
    """Run all rate limiting examples."""
    print("SpotifyScraper Rate Limiting Examples")
    print("=" * 40)
    print()
    
    # Run examples
    example_default_rate_limiting()
    example_custom_rate_limiting()
    example_rate_limit_recovery()
    example_bulk_operations_with_rate_limiting()
    example_monitoring_rate_limits()
    
    print("All examples completed!")
    print("\nKey Takeaways:")
    print("- Default rate limiting (0.5s) prevents most rate limit errors")
    print("- Custom delays can be configured for different use cases")
    print("- The library automatically handles 429 errors with exponential backoff")
    print("- Rate limiting works transparently with bulk operations")


if __name__ == "__main__":
    main()