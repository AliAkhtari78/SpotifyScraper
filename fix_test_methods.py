#!/usr/bin/env python3
"""Fix method names in test files to match the production_usage.py methods."""

import re

def fix_test_file():
    """Fix method names in test_production_usage.py."""
    filepath = "tests/integration/test_production_usage.py"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix method names in the test file
    # The SpotifyScraperWrapper uses get_track, not get_track_info
    content = re.sub(r'wrapper\.get_track_info\(', r'wrapper.get_track(', content)
    content = re.sub(r'wrapper\.get_album_info\(', r'wrapper.get_album(', content)
    content = re.sub(r'wrapper\.get_artist_info\(', r'wrapper.get_artist(', content)
    content = re.sub(r'wrapper\.get_playlist_info\(', r'wrapper.get_playlist(', content)
    
    # Also fix the mock client calls
    content = re.sub(r'mock_client\.get_track_info', r'mock_client.get_track_info', content)
    content = re.sub(r'mock_client\.get_album_info', r'mock_client.get_album_info', content)
    content = re.sub(r'mock_client\.get_artist_info', r'mock_client.get_artist_info', content)
    content = re.sub(r'mock_client\.get_playlist_info', r'mock_client.get_playlist_info', content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Fixed: {filepath}")
        return True
    else:
        print(f"  No changes needed: {filepath}")
        return False

def fix_test_full_system():
    """Fix method names in test_full_system.py."""
    filepath = "tests/integration/test_full_system.py"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix wrapper method calls
    content = re.sub(r'wrapper\.get_track_info\(', r'wrapper.get_track(', content)
    content = re.sub(r'wrapper\.get_album_info\(', r'wrapper.get_album(', content)
    content = re.sub(r'wrapper\.get_artist_info\(', r'wrapper.get_artist(', content)
    content = re.sub(r'wrapper\.get_playlist_info\(', r'wrapper.get_playlist(', content)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Fixed: {filepath}")
        return True
    else:
        print(f"  No changes needed: {filepath}")
        return False

print("=== Fixing Test Method Names ===\n")
fix_test_file()
fix_test_full_system()
print("\nDone!")