import json
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List

from spotify_scraper.core.types import TrackData, TrackArtist, TrackAlbum, SyncedLyric
from spotify_scraper.core.exceptions import ContentExtractionError

def extract_from_next_data(html: str) -> Dict[str, Any]:
    """
    Extract JSON data from __NEXT_DATA__ script tag in Spotify HTML.
    
    Args:
        html: HTML content from Spotify page
        
    Returns:
        Parsed JSON data
        
    Raises:
        ContentExtractionError: If data cannot be extracted
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        if not script or not script.string:
            raise ContentExtractionError("No __NEXT_DATA__ script found in HTML")
        
        return json.loads(script.string)
    except (json.JSONDecodeError, AttributeError) as e:
        raise ContentExtractionError(f"Failed to parse __NEXT_DATA__: {str(e)}")

def extract_track_data_from_page(html: str) -> TrackData:
    """
    Extract track data from Spotify HTML page.
    
    Args:
        html: HTML content from Spotify track page
        
    Returns:
        TrackData object with extracted information
        
    Raises:
        ContentExtractionError: If data cannot be extracted
    """
    try:
        data = extract_from_next_data(html)
        
        # Navigate to track data in the JSON structure
        # This path might need adjustment based on the actual structure
        track_data = data.get('props', {}).get('pageProps', {}).get('state', {}).get('data', {})
        
        if not track_data:
            # Try alternative path for embed pages
            track_data = data.get('props', {}).get('pageProps', {}).get('embedData', {}).get('data', {})
            
        if not track_data:
            raise ContentExtractionError("Track data not found in parsed JSON")
        
        # Extract basic track info
        name = track_data.get('name', '')
        track_id = track_data.get('id', '')
        uri = track_data.get('uri', '')
        duration_ms = track_data.get('duration_ms', 0)
        preview_url = track_data.get('preview_url')
        is_playable = track_data.get('is_playable', False)
        
        # Extract artists
        artists_data = track_data.get('artists', [])
        artists = [
            TrackArtist(
                name=artist.get('name', ''),
                id=artist.get('id', ''),
                uri=artist.get('uri', '')
            )
            for artist in artists_data
        ]
        
        # Extract album
        album_data = track_data.get('album', {})
        album = TrackAlbum(
            name=album_data.get('name', ''),
            id=album_data.get('id', ''),
            uri=album_data.get('uri', ''),
            images=album_data.get('images', []),
            release_date=album_data.get('release_date', ''),
            total_tracks=album_data.get('total_tracks', 0),
            album_type=album_data.get('album_type', '')
        )
        
        # Extract lyrics if available
        lyrics: Optional[List[SyncedLyric]] = None
        lyrics_data = data.get('props', {}).get('pageProps', {}).get('state', {}).get('lyrics', {}).get('lines', [])
        
        if lyrics_data:
            lyrics = [
                SyncedLyric(
                    text=line.get('words', ''),
                    start_time_ms=line.get('startTimeMs', 0),
                    end_time_ms=line.get('endTimeMs')
                )
                for line in lyrics_data
            ]
        
        return TrackData(
            name=name,
            id=track_id,
            uri=uri,
            duration_ms=duration_ms,
            preview_url=preview_url,
            is_playable=is_playable,
            artists=artists,
            album=album,
            lyrics=lyrics
        )
        
    except Exception as e:
        raise ContentExtractionError(f"Failed to extract track data: {str(e)}")