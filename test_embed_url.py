#!/usr/bin/env python
"""
Simple test script to validate the behavior of the embed URL conversion and extraction.
"""

import sys
import os
import requests

# Add the repository root to the Python path
sys.path.append('/home/runner/work/SpotifyScraper/SpotifyScraper')

from track_extractor import convert_to_embed_url

def test_url_conversion():
    """Test the conversion of regular URLs to embed URLs."""
    urls = [
        "https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv",
        "https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv?si=abcdef",
        "https://open.spotify.com/embed/track/4u7EnebtmKWzUH433cf5Qv",
        "https://open.spotify.com/embed/track/4u7EnebtmKWzUH433cf5Qv?si=abcdef",
    ]
    
    for url in urls:
        embed_url = convert_to_embed_url(url)
        print(f"Original URL: {url}")
        print(f"Embed URL:    {embed_url}")
        print()

def test_request_headers():
    """Test different request headers to see what's needed for authenticated vs unauthenticated requests."""
    track_url = "https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv"
    embed_url = convert_to_embed_url(track_url)
    
    # Default user agent header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }
    
    print(f"Testing regular URL: {track_url}")
    try:
        response = requests.get(track_url, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Contains __NEXT_DATA__: {'<script id=\"__NEXT_DATA__\"' in response.text}")
        print(f"Response size: {len(response.text)} bytes")
    except Exception as e:
        print(f"Error requesting regular URL: {e}")
    
    print(f"\nTesting embed URL: {embed_url}")
    try:
        response = requests.get(embed_url, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Contains __NEXT_DATA__: {'<script id=\"__NEXT_DATA__\"' in response.text}")
        print(f"Response size: {len(response.text)} bytes")
    except Exception as e:
        print(f"Error requesting embed URL: {e}")

if __name__ == "__main__":
    print("Testing URL conversion:")
    print("---------------------")
    test_url_conversion()
    
    print("\nTesting request responses:")
    print("-----------------------")
    test_request_headers()