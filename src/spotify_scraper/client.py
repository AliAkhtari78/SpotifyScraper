"""Client module for the SpotifyScraper package.

This module provides the main entry point for users of the SpotifyScraper library.
The SpotifyClient class offers a high-level, user-friendly interface for extracting
data from Spotify's web player, including tracks, albums, artists, and playlists.

The client handles all the complexity of web scraping, including:
    - Browser management (requests vs Selenium)
    - Authentication and session handling
    - URL validation and conversion
    - Data extraction and parsing
    - Media downloading (audio previews and cover images)
    - Error handling and logging

Example:
    >>> from spotify_scraper import SpotifyClient
    >>> client = SpotifyClient()
    >>> track_info = client.get_track_info("https://open.spotify.com/track/...")
    >>> print(track_info['name'])
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
from spotify_scraper.exceptions import AuthenticationRequiredError, MediaError

logger = logging.getLogger(__name__)


class SpotifyClient:
    """High-level client for interacting with Spotify web player.
    
    This class provides a simplified, user-friendly interface for extracting
    information from Spotify's web player and downloading related media files.
    It abstracts away the complexity of web scraping and provides clean methods
    for common operations.
    
    The client supports extracting data from:
        - Tracks (including lyrics with authentication)
        - Albums (with full track listings)
        - Artists (including top tracks and discography)
        - Playlists (with all track details)
    
    It also supports downloading:
        - Audio preview clips (30-second MP3s)
        - Cover images in various sizes
    
    Attributes:
        session: Authentication session for accessing protected content.
        scraper: Core scraper instance that handles web interactions.
        browser: Browser backend (requests or Selenium) for fetching pages.
        track_extractor: Specialized extractor for track data.
        album_extractor: Specialized extractor for album data.
        artist_extractor: Specialized extractor for artist data.
        playlist_extractor: Specialized extractor for playlist data.
    
    Example:
        Basic usage without authentication::
        
            client = SpotifyClient()
            track = client.get_track_info("https://open.spotify.com/track/...")
            print(f"{track['name']} by {track['artists'][0]['name']}")
            
        With authentication for lyrics::
        
            client = SpotifyClient(cookie_file="spotify_cookies.txt")
            track = client.get_track_info_with_lyrics(track_url)
            print(track['lyrics'])
            
        Download media files::
        
            # Download 30-second preview
            client.download_preview_mp3(track_url, path="previews/")
            
            # Download album cover
            client.download_cover(album_url, path="covers/", size="large")
    
    Note:
        Authentication via cookies is required for some features like lyrics.
        The library will work without authentication for most metadata extraction.
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
        """Initialize the SpotifyClient.
        
        Creates a new SpotifyClient instance with the specified configuration.
        The client can be customized with authentication cookies, custom headers,
        proxy settings, and browser backend selection.
        
        Args:
            cookie_file: Path to a Netscape-format cookies.txt file containing
                Spotify authentication cookies. Used for accessing protected
                content like lyrics. Example: "spotify_cookies.txt"
            cookies: Dictionary of cookies to use instead of cookie_file.
                Keys should be cookie names, values should be cookie values.
                Example: {"sp_t": "auth_token_value"}
            headers: Custom HTTP headers to include in all requests.
                Useful for setting User-Agent or other headers.
                Example: {"User-Agent": "Custom Bot 1.0"}
            proxy: Proxy server configuration for all requests.
                Example: {"http": "http://proxy.example.com:8080",
                         "https": "https://proxy.example.com:8080"}
            browser_type: Backend browser implementation to use.
                - "requests": Lightweight, fast, no JavaScript support (default)
                - "selenium": Full browser, slower, full JavaScript support
                - "auto": Automatically choose based on requirements
            log_level: Logging verbosity level.
                Options: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
                Default: "INFO"
            log_file: Path to write log messages to. If None, logs to console only.
                Example: "spotify_scraper.log"
        
        Raises:
            ValueError: If browser_type is not one of the supported values.
            FileNotFoundError: If cookie_file is specified but doesn't exist.
        
        Example:
            >>> # Simple client with default settings
            >>> client = SpotifyClient()
            
            >>> # Client with authentication
            >>> client = SpotifyClient(cookie_file="cookies.txt")
            
            >>> # Client with custom configuration
            >>> client = SpotifyClient(
            ...     browser_type="selenium",
            ...     proxy={"https": "https://proxy.example.com:8080"},
            ...     log_level="DEBUG",
            ...     log_file="scraper.log"
            ... )
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
        """Get track information from a Spotify track URL.

        Extracts comprehensive metadata for a single track, including name,
        artists, album, duration, preview URL, and more. This method uses
        Spotify's embed endpoint which doesn't require authentication.

        Args:
            url: Spotify track URL in any supported format.
                Examples:
                - https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6
                - https://open.spotify.com/embed/track/6rqhFgbbKwnb9MLmUQDhG6
                - spotify:track:6rqhFgbbKwnb9MLmUQDhG6

        Returns:
            Dict[str, Any]: Track information with the following structure:
                {
                    "id": str,              # Spotify track ID
                    "name": str,            # Track title
                    "uri": str,             # Spotify URI (spotify:track:...)
                    "type": "track",        # Entity type
                    "duration_ms": int,     # Duration in milliseconds
                    "explicit": bool,       # Explicit content flag
                    "artists": List[Dict],  # List of artist objects
                    "album": Dict,          # Album object with images
                    "preview_url": str,     # 30-second preview MP3 URL
                    "popularity": int,      # Popularity score (0-100)
                    "track_number": int,    # Position in album
                    "disc_number": int,     # Disc number in album
                    "external_urls": Dict,  # External URLs
                    "is_playable": bool,    # Playability status
                    "linked_from": Dict,    # Original track if relinked
                    "restrictions": Dict    # Playback restrictions
                }

        Raises:
            URLError: If the URL is not a valid Spotify track URL.
            ScrapingError: If the track data cannot be extracted.
            NetworkError: If there are connection issues.

        Example:
            >>> client = SpotifyClient()
            >>> track = client.get_track_info(
            ...     "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
            ... )
            >>> print(f"{track['name']} - {track['duration_ms'] / 1000:.1f}s")
            Bohemian Rhapsody - 354.9s
            
        Note:
            This method automatically converts regular URLs to embed format
            for better reliability and to avoid authentication requirements.
        """
        logger.info(f"Getting track info for {url}")
        return self.track_extractor.get_track_info(url)

    def get_track_lyrics(self, url: str, require_auth: bool = True) -> Optional[str]:
        """Get lyrics for a Spotify track.

        Fetches the official lyrics for a track from Spotify. Note that lyrics
        are only available for some tracks and typically require authentication
        via cookies to access.

        Args:
            url: Spotify track URL in any supported format.
            require_auth: Whether to require authentication for lyrics access.
                If True (default), raises an error if not authenticated.
                If False, attempts to fetch lyrics anyway (may return None).

        Returns:
            Optional[str]: The complete lyrics text with line breaks preserved,
                or None if lyrics are not available for this track or if
                authentication is required but not provided.

        Raises:
            AuthenticationRequiredError: If require_auth is True and the client
                is not authenticated (no cookies provided).
            URLError: If the URL is not a valid Spotify track URL.
            ScrapingError: If there's an error extracting the lyrics.

        Example:
            >>> # With authentication
            >>> client = SpotifyClient(cookie_file="spotify_cookies.txt")
            >>> lyrics = client.get_track_lyrics(
            ...     "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
            ... )
            >>> if lyrics:
            ...     print(lyrics.split('\n')[0])  # Print first line
            Is this the real life?
            
            >>> # Without authentication (will likely fail)
            >>> client = SpotifyClient()
            >>> lyrics = client.get_track_lyrics(track_url, require_auth=False)
            >>> print(lyrics)  # Usually None without auth
            None

        Note:
            Spotify's lyrics are provided by Musixmatch and are not available
            for all tracks. Even with authentication, some tracks may not have
            lyrics available.
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
        """Get track information and lyrics in a single call.

        Convenience method that fetches both track metadata and lyrics (if available)
        in one operation. The lyrics are added to the track info dictionary under
        the 'lyrics' key.

        Args:
            url: Spotify track URL in any supported format.
            require_lyrics_auth: Whether to require authentication for lyrics.
                If True (default) and not authenticated, logs a warning and
                sets lyrics to None. If False, attempts lyrics fetch anyway.

        Returns:
            Dict[str, Any]: Track information dictionary (same as get_track_info)
                with an additional 'lyrics' key containing the lyrics string
                or None if lyrics are unavailable.

        Example:
            >>> client = SpotifyClient(cookie_file="spotify_cookies.txt")
            >>> track = client.get_track_info_with_lyrics(
            ...     "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
            ... )
            >>> print(f"Track: {track['name']}")
            Track: Bohemian Rhapsody
            >>> if track['lyrics']:
            ...     print(f"Lyrics available: {len(track['lyrics'])} characters")
            Lyrics available: 2845 characters

        Note:
            This method will not raise an exception if lyrics are unavailable.
            Instead, it sets the 'lyrics' field to None and logs a warning.
            This allows you to get track info even when lyrics aren't accessible.
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
        """Automatically detect URL type and extract appropriate information.

        This convenience method examines the provided Spotify URL, determines
        its type (track, album, artist, or playlist), and automatically routes
        it to the appropriate extraction method. Useful when processing mixed
        URL types or when the URL type is unknown.

        Args:
            url: Any valid Spotify URL. Supports all entity types:
                - Track: https://open.spotify.com/track/...
                - Album: https://open.spotify.com/album/...
                - Artist: https://open.spotify.com/artist/...
                - Playlist: https://open.spotify.com/playlist/...
                - Embed URLs: https://open.spotify.com/embed/.../...
                - Spotify URIs: spotify:track:..., spotify:album:..., etc.

        Returns:
            Dict[str, Any]: Extracted information. The structure varies by type:
                - For tracks: See get_track_info() return value
                - For albums: See get_album_info() return value
                - For artists: See get_artist_info() return value
                - For playlists: See get_playlist_info() return value

        Raises:
            URLError: If the URL is not a valid Spotify URL or if the type
                cannot be determined (e.g., search URLs are not supported).
            ScrapingError: If the data cannot be extracted from the page.
            NetworkError: If there are connection issues.

        Example:
            >>> client = SpotifyClient()
            >>> # Works with any Spotify URL type
            >>> data1 = client.get_all_info("https://open.spotify.com/track/...")
            >>> print(f"Track: {data1['name']}")
            
            >>> data2 = client.get_all_info("https://open.spotify.com/album/...")
            >>> print(f"Album: {data2['name']} ({data2['total_tracks']} tracks)")
            
            >>> # Useful for processing mixed URL lists
            >>> urls = [track_url, album_url, artist_url, playlist_url]
            >>> for url in urls:
            ...     info = client.get_all_info(url)
            ...     print(f"{info['type']}: {info['name']}")

        Note:
            This method adds a small overhead for URL type detection. If you
            know the URL type in advance, using the specific method (e.g.,
            get_track_info) will be slightly faster.
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
        """Download cover image from any Spotify entity.

        Downloads the cover art/image for a track, album, playlist, or artist.
        Automatically detects the entity type from the URL and downloads the
        appropriate image. Images are saved as JPEG files.

        Args:
            url: Spotify URL of any supported type (track, album, artist, playlist).
            path: Directory path where the image should be saved.
                Can be string or Path object. Defaults to current directory.
                Directory will be created if it doesn't exist.
            filename: Custom filename for the image (without extension).
                If None, generates filename as: "{name}_{type}_cover.jpg"
                Example: "Bohemian_Rhapsody_track_cover.jpg"
            quality_preference: List of size preferences in order. Options vary
                by entity type but typically include ["large", "medium", "small"].
                If None, defaults to ["large"].

        Returns:
            Optional[str]: Full path to the downloaded image file, or None if
                download failed. Example: "/path/to/album_cover.jpg"

        Raises:
            URLError: If the URL is not a valid Spotify URL.
            MediaError: If the cover image cannot be downloaded.
            DownloadError: If there are network or file system errors.

        Example:
            >>> client = SpotifyClient()
            >>> # Download track album cover
            >>> cover_path = client.download_cover(
            ...     "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
            ...     path="covers/",
            ...     filename="bohemian_rhapsody"
            ... )
            >>> print(f"Cover saved to: {cover_path}")
            Cover saved to: covers/bohemian_rhapsody.jpg
            
            >>> # Download with automatic filename
            >>> cover_path = client.download_cover(album_url)
            >>> print(cover_path)
            A_Night_at_the_Opera_album_cover.jpg

        Note:
            - Track URLs download the album cover (tracks don't have separate covers)
            - Image quality/size depends on what Spotify provides
            - Files are overwritten if they already exist
        """
        logger.info(f"Downloading cover for {url}")
        
        # First, extract the entity data based on URL type
        try:
            entity_data = self.get_all_info(url)
            
            # Download cover using the entity data
            return self._image_downloader.download_cover(
                entity_data=entity_data,
                filename=filename,
                path=str(path) if path else "",
                size="large" if not quality_preference else quality_preference[0]
            )
        except Exception as e:
            logger.error(f"Failed to download cover: {e}")
            raise MediaError(f"Failed to download cover: {e}") from e

    def download_preview_mp3(self, url: str, path: str = "", with_cover: bool = False) -> str:
        """Download 30-second preview MP3 from a Spotify track.

        Downloads the preview audio clip that Spotify provides for most tracks.
        These are typically 30-second MP3 files showcasing a portion of the song.
        Optionally embeds cover art and metadata into the MP3 file.

        Args:
            url: Spotify track URL in any supported format.
            path: Directory path where the MP3 should be saved.
                Defaults to current directory. Directory will be created
                if it doesn't exist.
            with_cover: Whether to embed the album cover art in the MP3
                metadata. Requires eyeD3 library. If eyeD3 is not installed,
                this option is ignored with a warning.

        Returns:
            str: Full path to the downloaded MP3 file.
                Example: "/path/to/Bohemian_Rhapsody_by_Queen.mp3"

        Raises:
            URLError: If the URL is not a valid Spotify track URL.
            MediaError: If the track has no preview available.
            DownloadError: If the preview cannot be downloaded.

        Example:
            >>> client = SpotifyClient()
            >>> # Basic download
            >>> mp3_path = client.download_preview_mp3(
            ...     "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6"
            ... )
            >>> print(f"Preview saved to: {mp3_path}")
            Preview saved to: Bohemian_Rhapsody_by_Queen.mp3
            
            >>> # Download with cover art embedded
            >>> mp3_path = client.download_preview_mp3(
            ...     track_url,
            ...     path="previews/",
            ...     with_cover=True
            ... )
            >>> print(f"Preview with artwork: {mp3_path}")
            Preview with artwork: previews/Bohemian_Rhapsody_by_Queen.mp3

        Note:
            - Not all tracks have preview URLs available
            - Preview clips are typically 30 seconds long
            - Audio quality is usually 96-128 kbps MP3
            - Cover embedding requires the eyeD3 library:
              pip install eyeD3
        """
        logger.info(f"Downloading preview MP3 for {url}")
        
        # First, extract the track data
        try:
            track_data = self.get_track_info(url)
            
            # Download preview using the track data
            return self._audio_downloader.download_preview(
                track_data=track_data,
                path=path,
                with_cover=with_cover
            )
        except Exception as e:
            logger.error(f"Failed to download preview MP3: {e}")
            raise MediaError(f"Failed to download preview MP3: {e}") from e

    def close(self) -> None:
        """Close the client and release all resources.
        
        Properly shuts down the SpotifyClient by closing browser connections,
        clearing caches, and releasing any held resources. This is especially
        important when using the Selenium browser backend to ensure the browser
        process is terminated.
        
        While Python's garbage collector will eventually clean up resources,
        explicitly calling close() ensures immediate cleanup and is considered
        best practice, especially in long-running applications.
        
        Example:
            >>> client = SpotifyClient(browser_type="selenium")
            >>> try:
            ...     # Use the client
            ...     track = client.get_track_info(track_url)
            ... finally:
            ...     # Always close when done
            ...     client.close()
            
            Or using context manager (if implemented)::
            
            >>> with SpotifyClient() as client:
            ...     track = client.get_track_info(track_url)
            ... # Automatically closed
        
        Note:
            After calling close(), the client instance should not be used again.
            Create a new client if you need to make more requests.
        """
        logger.debug("Closing SpotifyClient")
        self.browser.close()
