#!/bin/bash

# SpotifyScraper v2.0 CLI Examples
# This script demonstrates various CLI commands and options

echo "SpotifyScraper v2.0 - CLI Examples"
echo "=================================="

# Show version
echo -e "\n1. Show version:"
echo "$ spotify-scraper --version"

# Show help
echo -e "\n2. Show help:"
echo "$ spotify-scraper --help"

# Extract track information
echo -e "\n3. Extract track information:"
echo "$ spotify-scraper track https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"

# Extract track with pretty JSON output
echo -e "\n4. Extract track with pretty JSON:"
echo "$ spotify-scraper track --pretty https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"

# Save track info to file
echo -e "\n5. Save track info to file:"
echo "$ spotify-scraper track -o track_info.json https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"

# Extract track with lyrics (requires authentication)
echo -e "\n6. Extract track with lyrics (requires authentication):"
echo "$ spotify-scraper -c cookies.txt track --with-lyrics https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"

# Display track info as table
echo -e "\n7. Display track info as table:"
echo "$ spotify-scraper track --format table https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"

# Extract album information
echo -e "\n8. Extract album information:"
echo "$ spotify-scraper album https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"

# Extract album tracks only
echo -e "\n9. Extract album tracks only:"
echo "$ spotify-scraper album --tracks-only https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"

# Extract artist information
echo -e "\n10. Extract artist information:"
echo "$ spotify-scraper artist https://open.spotify.com/artist/0YC192cP3KPCRWx8zr8MfZ"

# Extract artist top tracks only
echo -e "\n11. Extract artist top tracks only:"
echo "$ spotify-scraper artist --top-tracks-only https://open.spotify.com/artist/0YC192cP3KPCRWx8zr8MfZ"

# Extract playlist information
echo -e "\n12. Extract playlist information:"
echo "$ spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

# Extract playlist with track limit
echo -e "\n13. Extract playlist with track limit:"
echo "$ spotify-scraper playlist --limit 10 https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

# Download cover image
echo -e "\n14. Download cover image:"
echo "$ spotify-scraper download cover https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"

# Download cover with custom filename
echo -e "\n15. Download cover with custom filename:"
echo "$ spotify-scraper download cover -f my_cover https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"

# Download track preview MP3
echo -e "\n16. Download track preview MP3:"
echo "$ spotify-scraper download track https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"

# Download track preview with embedded cover
echo -e "\n17. Download track preview with embedded cover:"
echo "$ spotify-scraper download track --with-cover https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"

# Batch download from file
echo -e "\n18. Batch download from file:"
echo "$ cat urls.txt"
echo "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp"
echo "https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI3"
echo "https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv"
echo ""
echo "$ spotify-scraper download batch urls.txt"

# Using different output formats
echo -e "\n19. Different output formats:"
echo "$ spotify-scraper track --format json https://open.spotify.com/track/..."
echo "$ spotify-scraper track --format yaml https://open.spotify.com/track/..."
echo "$ spotify-scraper track --format table https://open.spotify.com/track/..."

# Using debug logging
echo -e "\n20. Using debug logging:"
echo "$ spotify-scraper --log-level debug track https://open.spotify.com/track/..."

# Using proxy
echo -e "\n21. Using proxy:"
echo "$ spotify-scraper --proxy http://proxy.example.com:8080 track https://open.spotify.com/track/..."

# Using Selenium browser
echo -e "\n22. Using Selenium browser (for complex pages):"
echo "$ spotify-scraper --browser selenium track https://open.spotify.com/track/..."

echo -e "\n✓ These are the main CLI commands and options available in SpotifyScraper v2.0"