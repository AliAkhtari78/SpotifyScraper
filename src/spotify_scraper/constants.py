"""
Constants used throughout the SpotifyScraper package.

This module contains constant values, URLs, and configuration defaults
used by other modules in the package.
"""

# Base URLs
SPOTIFY_BASE_URL = "https://open.spotify.com"
SPOTIFY_EMBED_URL = "https://open.spotify.com/embed"
SPOTIFY_API_URL = "https://api.spotify.com/v1"
SPOTIFY_CDN_URL = "https://i.scdn.co"

# Domains
SPOTIFY_DOMAINS = [
    "open.spotify.com",
    "spotify.com",
    "www.spotify.com"
]

# URL patterns
TRACK_URL_PATTERN = f"{SPOTIFY_BASE_URL}/track/"
PLAYLIST_URL_PATTERN = f"{SPOTIFY_BASE_URL}/playlist/"
ALBUM_URL_PATTERN = f"{SPOTIFY_BASE_URL}/album/"
ARTIST_URL_PATTERN = f"{SPOTIFY_BASE_URL}/artist/"

# Common headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": SPOTIFY_BASE_URL,
    "DNT": "1",  # Do Not Track
}

# HTML/CSS Selectors
# These will be updated based on the current Spotify web interface
TRACK_INFO_SELECTOR = "script#resource"
PLAYER_CONFIG_SELECTOR = "script#config"

# API Response fields
TRACK_FIELDS = [
    "title",
    "preview_mp3",
    "duration",
    "artist_name",
    "artist_url",
    "album_title",
    "album_cover_url",
    "album_cover_height",
    "album_cover_width",
    "release_date",
    "total_tracks",
    "type_",
]

PLAYLIST_FIELDS = [
    "album_title",
    "cover_url",
    "author",
    "author_url",
    "playlist_description",
    "tracks_list",
]

# Default configuration
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_RETRIES = 3
DEFAULT_RETRY_DELAY = 1  # seconds
MAX_CONNECTIONS = 10
DEFAULT_CACHE_TTL = 3600  # 1 hour

# File types
AUDIO_FORMATS = ["mp3", "ogg", "wav"]
IMAGE_FORMATS = ["jpg", "jpeg", "png", "webp"]

# Media quality
IMAGE_QUALITY_SMALL = "small"
IMAGE_QUALITY_MEDIUM = "medium"
IMAGE_QUALITY_LARGE = "large"

# Error messages
ERROR_URL_MALFORMED = "The provided URL is malformed."
ERROR_URL_NOT_FOUND = "The provided URL doesn't belong to any song on Spotify."
ERROR_DOWNLOAD_FAILED = "Couldn't download the file."
ERROR_EXTRACTION_FAILED = "Failed to extract data from the page."
