"""
Constants used throughout the SpotifyScraper library.

This module defines constants that are used by various components of the library.
Using centralized constants improves maintainability and consistency.
"""

# Base URLs
SPOTIFY_BASE_URL = "https://open.spotify.com"
SPOTIFY_EMBED_URL = "https://open.spotify.com/embed"
SPOTIFY_API_URL = "https://api.spotify.com/v1"
TOKEN_URL = "https://accounts.spotify.com/api/token"

# Default configuration values
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_RETRIES = 3
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
DEFAULT_LOG_LEVEL = "INFO"

# HTML Selectors
NEXT_DATA_SELECTOR = "script#__NEXT_DATA__"
RESOURCE_SELECTOR = "script#resource"
TRACK_CONTAINER_SELECTOR = "div[data-testid='track-list']"
LYRICS_CONTAINER_SELECTOR = "div[data-testid='lyrics-container']"

# JSON Paths
TRACK_JSON_PATH = "props.pageProps.state.data.entity"
ALBUM_JSON_PATH = "props.pageProps.state.data.entity"
ARTIST_JSON_PATH = "props.pageProps.state.data.entity"
PLAYLIST_JSON_PATH = "props.pageProps.state.data.entity"
AUTH_TOKEN_JSON_PATH = "props.pageProps.state.settings.session.accessToken"

# Error messages
ERROR_INVALID_URL = "The provided URL is not a valid Spotify URL."
ERROR_UNSUPPORTED_URL_TYPE = "The provided URL type is not supported."
ERROR_NETWORK = "A network error occurred while accessing the URL."
ERROR_PARSING = "Failed to parse the Spotify page data."
ERROR_EXTRACTION = "Failed to extract data from the Spotify page."
ERROR_AUTHENTICATION = "Failed to authenticate with Spotify."
ERROR_NO_DATA = "No data was found at the specified URL."

# URL patterns
TRACK_URL_PATTERN = r"^https://open\.spotify\.com/track/([a-zA-Z0-9]+)(\?.*)?$"
ALBUM_URL_PATTERN = r"^https://open\.spotify\.com/album/([a-zA-Z0-9]+)(\?.*)?$"
ARTIST_URL_PATTERN = r"^https://open\.spotify\.com/artist/([a-zA-Z0-9]+)(\?.*)?$"
PLAYLIST_URL_PATTERN = r"^https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)(\?.*)?$"
EMBED_TRACK_URL_PATTERN = r"^https://open\.spotify\.com/embed/track/([a-zA-Z0-9]+)(\?.*)?$"
EMBED_ALBUM_URL_PATTERN = r"^https://open\.spotify\.com/embed/album/([a-zA-Z0-9]+)(\?.*)?$"
EMBED_ARTIST_URL_PATTERN = r"^https://open\.spotify\.com/embed/artist/([a-zA-Z0-9]+)(\?.*)?$"
EMBED_PLAYLIST_URL_PATTERN = r"^https://open\.spotify\.com/embed/playlist/([a-zA-Z0-9]+)(\?.*)?$"

# Media download paths
DEFAULT_DOWNLOAD_PATH = "./downloads"
DEFAULT_IMAGE_DIRECTORY = "images"
DEFAULT_AUDIO_DIRECTORY = "audio"

# Default HTTP headers
DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": SPOTIFY_BASE_URL,
    "DNT": "1",  # Do Not Track
}

# Authentication and session constants
CREDENTIALS_FILE_NAME = ".spotify_credentials"
SESSION_CACHE_FILE = ".spotify_session_cache"
DEFAULT_SESSION_TIMEOUT = 3600  # 1 hour in seconds
MAX_SESSION_RETRIES = 3

# Browser configuration
DEFAULT_BROWSER_TYPE = "requests"
SELENIUM_TIMEOUT = 30
SELENIUM_IMPLICIT_WAIT = 10
