import re
from urllib.parse import urlparse
from spotify_scraper.core.exceptions import URLValidationError

def convert_to_embed_url(url: str) -> str:
    """
    Convert a regular Spotify URL to an embed URL.
    
    Args:
        url: A Spotify track URL
        
    Returns:
        The embed version of the URL
        
    Raises:
        URLValidationError: If the URL is not a valid Spotify track URL
    """
    if 'embed' in url:
        return url
    
    parsed = urlparse(url)
    
    # Check if it's a Spotify domain
    if parsed.netloc not in ('open.spotify.com', 'spotify.com'):
        raise URLValidationError(f"Not a Spotify URL: {url}")
    
    # Extract the path parts
    path_parts = parsed.path.strip('/').split('/')
    
    # Check if it's a track URL
    if len(path_parts) < 2 or path_parts[0] != 'track':
        raise URLValidationError(f"Not a Spotify track URL: {url}")
    
    # Get the track ID
    track_id = path_parts[1].split('?')[0]
    
    # Validate track ID format (Spotify IDs are 22 characters)
    if not re.match(r'^[0-9A-Za-z]{22}$', track_id):
        raise URLValidationError(f"Invalid Spotify track ID: {track_id}")
    
    return f"https://open.spotify.com/embed/track/{track_id}"