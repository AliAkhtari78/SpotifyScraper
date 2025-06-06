#!/usr/bin/env python3
"""Test accessing regular show page."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spotify_scraper.browsers import create_browser
import re
import json

def test_regular_show_page():
    """Test if we can access the regular show page."""
    
    # Test with selenium browser for JavaScript support
    browser = create_browser("selenium")
    
    show_url = "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"
    
    print(f"Testing regular show page: {show_url}")
    print("-" * 80)
    
    try:
        # Get page content
        page_content = browser.get_page_content(show_url)
        
        # Save for inspection
        with open("regular_show_page.html", "w", encoding="utf-8") as f:
            f.write(page_content)
        print(f"Saved page content ({len(page_content)} bytes) to regular_show_page.html")
        
        # Look for __NEXT_DATA__ or other data structures
        if "__NEXT_DATA__" in page_content:
            print("Found __NEXT_DATA__ script tag")
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">([^<]+)</script>', page_content)
            if match:
                data = json.loads(match.group(1))
                print(f"Data structure keys: {list(data.keys())}")
                
                # Try to find show data
                if "props" in data:
                    props = data["props"]
                    if "pageProps" in props:
                        page_props = props["pageProps"]
                        print(f"PageProps keys: {list(page_props.keys())}")
        
        # Look for meta tags with show info
        title_match = re.search(r'<meta property="og:title" content="([^"]+)"', page_content)
        if title_match:
            print(f"Found title in meta tag: {title_match.group(1)}")
            
        desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', page_content)
        if desc_match:
            print(f"Found description in meta tag: {desc_match.group(1)}")
            
        # Look for JSON-LD data
        jsonld_match = re.search(r'<script type="application/ld\+json">([^<]+)</script>', page_content)
        if jsonld_match:
            print("\nFound JSON-LD data:")
            jsonld_data = json.loads(jsonld_match.group(1))
            print(json.dumps(jsonld_data, indent=2))
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Make sure to close the browser
        if hasattr(browser, 'driver'):
            browser.driver.quit()

if __name__ == "__main__":
    test_regular_show_page()