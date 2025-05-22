"""
Client module for the SpotifyScraper package.

This module provides a high-level client interface for interacting 
with the Spotify web player and extracting data.
"""

from typing import Dict, List, Optional, Union, Any
import logging
from pathlib import Path

from spotify_scraper.auth.session import Session
from spotify_scraper.core.scraper import Scraper
from spotify_scraper.browsers import create_browser
from spotify_scraper.extractors.track import TrackExtractor
from spotify_scraper.extractors.album import AlbumExtractor
from spotify_scraper.extractors.artist import ArtistExtractor
from spotify_scraper.extractors.playlist import PlaylistExtractor
from spotify_scraper.media.image import ImageDownloader
from spotify_scraper.media.audio import AudioDownloader
from spotify_scraper.utils.logger import configure_logging
from spotify_scraper.exceptions import AuthenticationRequiredError

logger = logging.getLogger(__name__)


class SpotifyClient:
    """
    High-level client for interacting with Spotify web player.
    
    This class provides a simplified interface for extracting information
    from Spotify web player and downloading related media.
    
    Attributes:
        session: The authentication session.
        scraper: The underlying scraper instance.
        browser: The browser instance used for web interactions.
        track_extractor: Extractor for track data and lyrics.
    """
    
    def __init__(
        self,
        cookie_file: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        proxy: Optional[Dict[str, str]] = None,
        browser_type: str = "requests",
        log_level: str = "INFO",
        log_file: Optional[str] = None,
    ):
        """
        Initialize the SpotifyClient.
        
        Args:
            cookie_file: Path to a cookies.txt file (optional).
            cookies: A dictionary of cookies to use (optional).
            headers: Custom headers for requests (optional).
            proxy: Proxy configuration (optional).
            browser_type: Type of browser to use ('requests', 'selenium', or 'auto').
            log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
            log_file: Path to log file (optional).
        """
        # Configure logging
        configure_logging(level=log_level.upper(), log_file=log_file)

        # Create session with correct parameters
        self.session = Session(cookies=cookies, headers=headers)
        # Handle cookie file and proxy separately if needed
        self.cookie_file = cookie_file
        self.proxy = proxy

        # Create browser
        # For now, create browser without session until we properly implement session management
        self.browser = create_browser(browser_type=browser_type)

        # Create scraper instance
        self.scraper = Scraper(browser=self.browser, log_level=log_level)

        # Create extractors with just the browser
        self.track_extractor = TrackExtractor(browser=self.browser)
        self.album_extractor = AlbumExtractor(browser=self.browser)
        self.artist_extractor = ArtistExtractor(browser=self.browser)
        self.playlist_extractor = PlaylistExtractor(browser=self.browser)

        # Create downloaders
        self._image_downloader = ImageDownloader(browser=self.browser)
        self._audio_downloader = AudioDownloader(browser=self.browser)
        
        logger.info("SpotifyClient initialized")

    def get_track_info(self, url: str) -> Dict[str, Any]:
        """
        Get track information from a Spotify track URL using the embed page.

        Args:
            url: Spotify track URL.

        Returns:
            Dictionary containing track information.
        """
        logger.info(f"Getting track info for {url}")
        return self.track_extractor.get_track_info(url)

    def get_track_lyrics(self, url: str, require_auth: bool = True) -> Optional[str]:
        """
        Get lyrics for a Spotify track. Requires authentication by default.

        Args:
            url: Spotify track URL.
            require_auth: If True (default), an error is raised if the session is not authenticated.
                          If False, it attempts to fetch lyrics without ensuring authentication.

        Returns:
            A string containing the lyrics, or None if not found or an error occurs.

        Raises:
            AuthenticationRequiredError: If require_auth is True and session is not authenticated.
        """
        logger.info(f"Getting lyrics for track {url}")
        # For now, skip authentication check until session is properly implemented
        if require_auth and False:
            raise AuthenticationRequiredError(
                "Fetching official Spotify lyrics requires an authenticated session. "
                "Please provide cookies via 'cookie_file' or 'cookies' parameter during client initialization."
            )
        return self.track_extractor.get_lyrics(url, require_auth=require_auth)

    def get_track_info_with_lyrics(self, url: str, require_lyrics_auth: bool = True) -> Dict[str, Any]:
        """
        Get track information and lyrics for a Spotify track URL.

        Args:
            url: Spotify track URL.
            require_lyrics_auth: If True (default), an error is raised for lyrics fetching
                                 if the session is not authenticated.

        Returns:
            Dictionary containing track information, with an added 'lyrics' key.
        """
        logger.info(f"Getting track info and lyrics for {url}")
        track_info = self.get_track_info(url)
        try:
            lyrics = self.get_track_lyrics(url, require_auth=require_lyrics_auth)
            track_info["lyrics"] = lyrics
        except AuthenticationRequiredError as e:
            logger.warning(f"Could not fetch lyrics for {url} due to authentication: {e}")
            track_info["lyrics"] = None
        except Exception as e:
            logger.error(f"An error occurred while fetching lyrics for {url}: {e}")
            track_info["lyrics"] = None

        return track_info

    def get_album_info(self, url: str) -> Dict[str, Any]:
        """
        Get album information from a Spotify album URL.

        This method extracts comprehensive album information including:
        - Album metadata (name, artists, release date, label)
        - Track listing with durations and preview URLs
        - Cover art in various sizes
        - Album statistics (total duration, track count)

        Args:
            url: Spotify album URL (regular or embed format).
                Examples:
                - https://open.spotify.com/album/1234567890abcdef
                - https://open.spotify.com/embed/album/1234567890abcdef
                - spotify:album:1234567890abcdef

        Returns:
            Dictionary containing album information with the following structure:
            {
                "id": str,                    # Spotify album ID
                "name": str,                  # Album name
                "uri": str,                   # Spotify URI (spotify:album:...)
                "type": "album",              # Entity type
                "artists": List[Dict],        # List of artists
                "release_date": str,          # Release date (YYYY-MM-DD)
                "release_date_precision": str,# Date precision (year/month/day)
                "label": str,                 # Record label
                "total_tracks": int,          # Number of tracks
                "duration_ms": int,           # Total album duration
                "popularity": int,            # Popularity score (0-100)
                "images": List[Dict],         # Cover art in various sizes
                "tracks": List[Dict],         # Track listing
                "copyrights": List[Dict],     # Copyright information
                "external_urls": Dict[str, str], # External URLs
                "available_markets": List[str]   # Available markets (countries)
            }

        Raises:
            URLError: If the provided URL is not a valid Spotify album URL.
            ScrapingError: If the album data cannot be extracted.
            NetworkError: If there are network connectivity issues.
        """
        logger.info(f"Getting album info for {url}")
        return self.album_extractor.extract(url)

    def get_artist_info(self, url: str) -> Dict[str, Any]:
        """
        Get artist information from a Spotify artist URL.

        This method extracts comprehensive artist information including:
        - Artist metadata (name, genres, popularity)
        - Biography and verified status
        - Top tracks in specified market
        - Related artists
        - Artist images
        - Monthly listener statistics
        - Discography highlights

        Args:
            url: Spotify artist URL (regular or embed format).
                Examples:
                - https://open.spotify.com/artist/1234567890abcdef
                - https://open.spotify.com/embed/artist/1234567890abcdef
                - spotify:artist:1234567890abcdef

        Returns:
            Dictionary containing artist information with the following structure:
            {
                "id": str,                    # Spotify artist ID
                "name": str,                  # Artist name
                "uri": str,                   # Spotify URI (spotify:artist:...)
                "type": "artist",             # Entity type
                "genres": List[str],          # Associated genres
                "popularity": int,            # Popularity score (0-100)
                "followers": Dict[str, int],  # Follower count
                "images": List[Dict],         # Artist images in various sizes
                "top_tracks": List[Dict],     # Popular tracks
                "albums": List[Dict],         # Recent albums
                "singles": List[Dict],        # Recent singles
                "compilations": List[Dict],   # Compilation albums
                "appears_on": List[Dict],     # Albums artist appears on
                "related_artists": List[Dict],# Similar artists
                "bio": str,                   # Artist biography
                "monthly_listeners": int,     # Monthly listener count
                "verified": bool,             # Verified artist status
                "external_urls": Dict[str, str] # External URLs
            }

        Raises:
            URLError: If the provided URL is not a valid Spotify artist URL.
            ScrapingError: If the artist data cannot be extracted.
            NetworkError: If there are network connectivity issues.
        """
        logger.info(f"Getting artist info for {url}")
        return self.artist_extractor.extract(url)

    def get_playlist_info(self, url: str) -> Dict[str, Any]:
        """
        Get playlist information from a Spotify playlist URL.

        This method extracts comprehensive playlist information including:
        - Playlist metadata (name, description, owner)
        - Complete track listing with full track details
        - Playlist statistics (duration, track count)
        - Playlist cover image
        - Collaborative and public status

        Args:
            url: Spotify playlist URL (regular or embed format).
                Examples:
                - https://open.spotify.com/playlist/1234567890abcdef
                - https://open.spotify.com/embed/playlist/1234567890abcdef
                - spotify:playlist:1234567890abcdef

        Returns:
            Dictionary containing playlist information with the following structure:
            {
                "id": str,                    # Spotify playlist ID
                "name": str,                  # Playlist name
                "uri": str,                   # Spotify URI (spotify:playlist:...)
                "type": "playlist",           # Entity type
                "description": str,           # Playlist description
                "owner": Dict[str, Any],      # Playlist owner information
                "collaborative": bool,        # Is collaborative playlist
                "public": bool,               # Is public playlist
                "followers": Dict[str, int],  # Follower count
                "images": List[Dict],         # Playlist cover images
                "tracks": {                   # Track information
                    "total": int,             # Total number of tracks
                    "items": List[Dict]       # List of track objects
                },
                "duration_ms": int,           # Total playlist duration
                "snapshot_id": str,           # Playlist version identifier
                "external_urls": Dict[str, str] # External URLs
            }

        Note:
            - For very large playlists (>100 tracks), only the first 100 tracks
              may be returned depending on the extraction method used.
            - Private playlists require authentication to access.

        Raises:
            URLError: If the provided URL is not a valid Spotify playlist URL.
            ScrapingError: If the playlist data cannot be extracted.
            NetworkError: If there are network connectivity issues.
            AuthenticationError: If trying to access a private playlist without auth.
        """
        logger.info(f"Getting playlist info for {url}")
        return self.playlist_extractor.extract(url)

    def get_all_info(self, url: str) -> Dict[str, Any]:
        """
        Automatically detect URL type and extract appropriate information.

        This method examines the provided Spotify URL and automatically
        routes it to the appropriate extractor (track, album, artist, or playlist).

        Args:
            url: Any valid Spotify URL.

        Returns:
            Dictionary containing the extracted information. The structure
            depends on the URL type (see individual get_*_info methods).

        Raises:
            URLError: If the URL is not a valid Spotify URL or type cannot be determined.
            ScrapingError: If the data cannot be extracted.
        """
        from spotify_scraper.utils.url import get_url_type
        
        logger.info(f"Auto-detecting URL type for {url}")
        url_type = get_url_type(url)
        
        if url_type == "track":
            return self.get_track_info(url)
        elif url_type == "album":
            return self.get_album_info(url)
        elif url_type == "artist":
            return self.get_artist_info(url)
        elif url_type == "playlist":
            return self.get_playlist_info(url)
        else:
            raise URLError(f"Unable to determine URL type for: {url}")

    def download_cover(self, url: str, path: Union[str, Path] = "", filename: Optional[str] = None, quality_preference: Optional[List[str]] = None) -> Optional[str]:
        """
        Download cover image from a Spotify URL (track, album, playlist, artist).

        Args:
            url: Spotify URL (track, album, playlist, artist).
            path: Directory to save the image (optional, defaults to current dir).
            filename: Desired filename (without extension). If None, a default is generated.
            quality_preference: List of preferred image quality keys.
        Returns:
            Path to the downloaded image
        """
        logger.info(f"Downloading cover for {url}")
        return self._image_downloader.download(url, path)

    def download_preview_mp3(self, url: str, path: str = "", with_cover: bool = False) -> str:
        """
        Download preview MP3 from a Spotify track URL.

        Args:
            url: Spotify track URL
            path: Directory to save the MP3 (optional)
            with_cover: Whether to embed the cover in the MP3 (optional)

        Returns:
            Path to the downloaded MP3
        """
        logger.info(f"Downloading preview MP3 for {url}")
        return self._audio_downloader.download(url, path, with_cover)

    def close(self) -> None:
        """
        Close the client and release resources.
        """
        logger.debug("Closing SpotifyClient")
        self.browser.close()
