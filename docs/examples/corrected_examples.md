# SpotifyScraper - Corrected Code Examples

## Track Example
```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Get track information
track_url = 'https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh'
track = client.get_track_info(track_url)

# Display available track information
print(f"Track: {track.get('name', 'Unknown')}")
if 'artists' in track and track['artists']:
    print(f"Artist: {track['artists'][0].get('name', 'Unknown')}")
if 'album' in track:
    print(f"Album: {track['album'].get('name', 'Unknown')}")
    # Note: release_date is available within track.album
    if 'release_date' in track['album']:
        print(f"Release Date: {track['album'].get('release_date', 'N/A')}")
print(f"Duration: {track.get('duration_ms', 0) / 1000:.2f} seconds")
print(f"Preview URL: {track.get('preview_url', 'Not available')}")

client.close()
```

## Album Example
```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Get album information
album_url = 'https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv'
album = client.get_album_info(album_url)

# Display available album information
print(f"Album: {album.get('name', 'Unknown')}")
if 'artists' in album and album['artists']:
    print(f"Artist: {album['artists'][0].get('name', 'Unknown')}")

# Note: release_date and label are NOT available in basic album extraction
# To get these fields, you would need to fetch a track from the album

# Display tracks
if 'tracks' in album:
    print(f"\nTracklist ({album.get('total_tracks', 'Unknown')} tracks):")
    if isinstance(album['tracks'], dict) and 'items' in album['tracks']:
        for i, track in enumerate(album['tracks']['items'][:5], 1):
            print(f"{i}. {track.get('name', 'Unknown')}")
    elif isinstance(album['tracks'], list):
        for i, track in enumerate(album['tracks'][:5], 1):
            print(f"{i}. {track.get('name', 'Unknown')}")

client.close()
```

## Artist Example
```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Get artist information
artist_url = 'https://open.spotify.com/artist/1dfeR4HaWDbWqFHLkxsg1d'
artist = client.get_artist_info(artist_url)

# Display available artist information
print(f"Artist: {artist.get('name', 'Unknown')}")
print(f"Spotify URI: {artist.get('uri', 'Unknown')}")

# Note: genres, followers, and popularity are NOT available in basic artist extraction
# The basic extraction only provides: id, name, uri, type, and images

if 'images' in artist and artist['images']:
    print(f"Image URL: {artist['images'][0].get('url', 'Not available')}")

client.close()
```

## Playlist Example
```python
from spotify_scraper import SpotifyClient

client = SpotifyClient()

# Get playlist information
playlist_url = 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M'
playlist = client.get_playlist_info(playlist_url)

# Display available playlist information
print(f"Playlist: {playlist.get('name', 'Unknown')}")

# Handle owner information (structure may vary)
if 'owner' in playlist:
    if isinstance(playlist['owner'], dict):
        print(f"Owner: {playlist['owner'].get('display_name', playlist['owner'].get('id', 'Unknown'))}")
    else:
        print(f"Owner: {playlist['owner']}")

# Note: description may not always be available
if 'description' in playlist:
    print(f"Description: {playlist.get('description', '')}")

# Display tracks
if 'tracks' in playlist:
    if isinstance(playlist['tracks'], dict) and 'items' in playlist['tracks']:
        print(f"\nFirst 5 tracks:")
        for i, item in enumerate(playlist['tracks']['items'][:5], 1):
            if item and 'track' in item and item['track']:
                track = item['track']
                track_name = track.get('name', 'Unknown')
                artist_name = 'Unknown'
                if 'artists' in track and track['artists']:
                    artist_name = track['artists'][0].get('name', 'Unknown')
                print(f"{i}. {track_name} by {artist_name}")

client.close()
```

## Error Handling Example
```python
from spotify_scraper import SpotifyClient, URLError, NetworkError, ExtractionError

client = SpotifyClient()

try:
    # Try to get track info
    track = client.get_track_info("https://open.spotify.com/track/invalid")
except URLError as e:
    print(f"Invalid URL: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
except ExtractionError as e:
    print(f"Extraction error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    client.close()
```
