#!/usr/bin/env python3
"""
Test script to explore Spotify podcast data extraction.
This script demonstrates how to extract podcast episode and show information.
"""

import json
import re
from typing import Dict, Any, Optional

def extract_podcast_data_from_embed(html_content: str) -> Dict[str, Any]:
    """Extract podcast episode data from embed page HTML."""
    
    # Try to find audioPreview URL
    audio_preview_match = re.search(r'"audioPreview":\{"url":"([^"]+)"', html_content)
    audio_preview_url = audio_preview_match.group(1) if audio_preview_match else None
    
    # Try to find episode title
    title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content)
    title = title_match.group(1) if title_match else None
    
    # Try to find show name
    show_match = re.search(r'<h2[^>]*>[^<]*<a[^>]*>([^<]+)</a>', html_content)
    show_name = show_match.group(1) if show_match else None
    
    # Extract episode ID from URL patterns
    episode_id_match = re.search(r'/episode/([a-zA-Z0-9]+)', html_content)
    episode_id = episode_id_match.group(1) if episode_id_match else None
    
    # Extract show ID from URL patterns  
    show_id_match = re.search(r'/show/([a-zA-Z0-9]+)', html_content)
    show_id = show_id_match.group(1) if show_id_match else None
    
    return {
        "episode_id": episode_id,
        "title": title,
        "show_name": show_name,
        "show_id": show_id,
        "audio_preview_url": audio_preview_url,
        "type": "episode"
    }

def test_embed_extraction():
    """Test extraction from embed page."""
    print("Testing podcast data extraction from embed page...")
    
    # Read the embed HTML file
    with open('debug_html/episode_embed.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract data
    podcast_data = extract_podcast_data_from_embed(html_content)
    
    print("\nExtracted podcast data:")
    print(json.dumps(podcast_data, indent=2))
    
    # Try to find more data patterns
    print("\nSearching for additional patterns...")
    
    # Look for duration
    duration_match = re.search(r'"duration":\s*(\d+)', html_content)
    if duration_match:
        print(f"Duration (ms): {duration_match.group(1)}")
    
    # Look for release date
    date_match = re.search(r'"releaseDate":\s*"([^"]+)"', html_content)
    if date_match:
        print(f"Release date: {date_match.group(1)}")
    
    # Look for description
    desc_match = re.search(r'"description":\s*"([^"]+)"', html_content)
    if desc_match:
        desc = desc_match.group(1)[:100] + "..." if len(desc_match.group(1)) > 100 else desc_match.group(1)
        print(f"Description: {desc}")

if __name__ == "__main__":
    test_embed_extraction()