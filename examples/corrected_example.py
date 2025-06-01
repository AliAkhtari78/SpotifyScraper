#!/usr/bin/env python3
"""Corrected example showing proper field access for SpotifyScraper."""

from spotify_scraper import SpotifyClient

# Create client
client = SpotifyClient()

# Extract track info
track_url = "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
track = client.get_track_info(track_url)

# Display available information
print(f"Track: {track.get('name', 'Unknown')}")
print(f"Artist: {', '.join([a.get('name', 'Unknown') for a in track.get('artists', [])])}")
print(f"Album: {track.get('album', {}).get('name', 'Unknown')}")
print(f"Duration: {track.get('duration_ms', 0) / 60000:.2f} minutes")
print(f"Is Explicit: {track.get('is_explicit', False)}")
print(f"Preview URL: {track.get('preview_url', 'Not available')}")

# Note: The 'popularity' field is NOT available in the extracted data
# This is a limitation of web scraping vs using the official Spotify API

# If you need popularity data, you would need to use the official Spotify Web API
# which requires authentication and provides more detailed metadata including:
# - popularity (0-100 score)
# - track_number
# - disc_number
# - available_markets
# - external_ids
# - and more...

# Clean up
client.close()
