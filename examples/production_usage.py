#!/usr/bin/env python3
"""
Production-ready SpotifyScraper usage example with comprehensive error handling.

This module demonstrates best practices for using the SpotifyScraper library,
including proper error handling, logging configuration, resource management,
and all available features with optional parameters.

Author: SpotifyScraper Development Team
Date: 2025-01-22
Version: 2.0.0
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from contextlib import contextmanager
from datetime import datetime

from spotify_scraper import SpotifyClient
from spotify_scraper.exceptions import (
    SpotifyScraperError,
    URLError,
    NetworkError,
    ScrapingError,
    AuthenticationRequiredError
)


class SpotifyScraperWrapper:
    """
    Production-ready wrapper for SpotifyScraper with enhanced functionality.
    
    This class provides a robust interface to the SpotifyScraper library with:
    - Comprehensive error handling and recovery
    - Automatic retry logic for network failures
    - Result caching to minimize API calls
    - Detailed logging and monitoring
    - Resource management and cleanup
    
    Attributes:
        client: The underlying SpotifyClient instance
        cache_dir: Directory for caching results
        max_retries: Maximum number of retry attempts for failed operations
        retry_delay: Delay in seconds between retry attempts
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
        cache_dir: Optional[Union[str, Path]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the SpotifyScraperWrapper with enhanced configuration.
        
        Args:
            cookie_file: Path to cookies.txt file for authentication
            cookies: Dictionary of cookies for authentication
            headers: Custom HTTP headers for requests
            proxy: Proxy configuration dictionary
            browser_type: Browser backend ('requests', 'selenium', or 'auto')
            log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
            log_file: Path to log file for persistent logging
            cache_dir: Directory for caching results (creates if not exists)
            max_retries: Maximum retry attempts for failed operations
            retry_delay: Delay between retry attempts in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Setup cache directory
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".spotify_scraper_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure enhanced logging
        self._setup_logging(log_level, log_file)
        
        # Initialize the client with all parameters
        try:
            self.client = SpotifyClient(
                cookie_file=cookie_file,
                cookies=cookies,
                headers=headers,
                proxy=proxy,
                browser_type=browser_type,
                log_level=log_level,
                log_file=log_file
            )
            self.logger.info("SpotifyScraperWrapper initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize SpotifyClient: {e}")
            raise
    
    def _setup_logging(self, log_level: str, log_file: Optional[str]) -> None:
        """
        Configure enhanced logging with both console and file handlers.
        
        Args:
            log_level: Logging level string
            log_file: Optional path to log file
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file, mode='a')
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            )
            self.logger.addHandler(file_handler)
    
    def _get_cache_key(self, url: str, operation: str) -> Path:
        """
        Generate cache file path for a given URL and operation.
        
        Args:
            url: Spotify URL
            operation: Operation type (e.g., 'track_info', 'lyrics')
            
        Returns:
            Path to cache file
        """
        # Extract ID from URL for cache key
        import re
        id_match = re.search(r'/(track|album|artist|playlist)/([a-zA-Z0-9]+)', url)
        if id_match:
            entity_type, entity_id = id_match.groups()
            return self.cache_dir / f"{entity_type}_{entity_id}_{operation}.json"
        return self.cache_dir / f"unknown_{hash(url)}_{operation}.json"
    
    def _load_from_cache(self, cache_key: Path) -> Optional[Dict[str, Any]]:
        """
        Load data from cache if available and not expired.
        
        Args:
            cache_key: Path to cache file
            
        Returns:
            Cached data or None if not available/expired
        """
        if cache_key.exists():
            try:
                with open(cache_key, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # Check if cache is still valid (24 hours)
                cache_time = datetime.fromisoformat(cached_data['timestamp'])
                if (datetime.now() - cache_time).total_seconds() < 86400:
                    self.logger.debug(f"Cache hit for {cache_key.name}")
                    return cached_data['data']
                else:
                    self.logger.debug(f"Cache expired for {cache_key.name}")
            except Exception as e:
                self.logger.warning(f"Failed to load cache {cache_key}: {e}")
        return None
    
    def _save_to_cache(self, cache_key: Path, data: Dict[str, Any]) -> None:
        """
        Save data to cache with timestamp.
        
        Args:
            cache_key: Path to cache file
            data: Data to cache
        """
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(cache_key, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            self.logger.debug(f"Cached data to {cache_key.name}")
        except Exception as e:
            self.logger.warning(f"Failed to save cache {cache_key}: {e}")
    
    def _retry_operation(self, operation, *args, **kwargs) -> Any:
        """
        Execute an operation with retry logic.
        
        Args:
            operation: Callable to execute
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Result of the operation
            
        Raises:
            Last exception if all retries fail
        """
        import time
        
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except (NetworkError, ScrapingError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    self.logger.warning(
                        f"Operation failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                    )
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    self.logger.error(f"Operation failed after {self.max_retries} attempts")
            except Exception as e:
                # Don't retry for non-network errors
                self.logger.error(f"Non-retryable error: {e}")
                raise
        
        raise last_exception
    
    def get_track_info(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get track information with caching and retry logic.
        
        Args:
            url: Spotify track URL
            use_cache: Whether to use cached results if available
            
        Returns:
            Dictionary containing comprehensive track information:
            {
                "id": str,                    # Spotify track ID
                "name": str,                  # Track title
                "artists": List[Dict],        # Artist information
                "album": Dict,                # Album information
                "duration_ms": int,           # Track duration in milliseconds
                "preview_url": Optional[str], # 30-second preview URL
                "images": List[Dict],         # Cover art in various sizes
                "release_date": str,          # Release date
                "popularity": int,            # Popularity score (0-100)
                "external_urls": Dict,        # External URLs
                "uri": str                    # Spotify URI
            }
            
        Raises:
            URLError: If the URL is invalid
            SpotifyScraperError: If extraction fails
        """
        self.logger.info(f"Getting track info for: {url}")
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(url, 'track_info')
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        # Fetch with retry logic
        try:
            track_info = self._retry_operation(self.client.get_track_info, url)
            
            # Save to cache
            if use_cache:
                self._save_to_cache(cache_key, track_info)
            
            self.logger.info(f"Successfully retrieved track: {track_info.get('name', 'Unknown')}")
            return track_info
            
        except URLError as e:
            self.logger.error(f"Invalid URL: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get track info: {e}")
            raise SpotifyScraperError(f"Failed to get track info: {e}")
    
    def get_track_lyrics(
        self,
        url: str,
        require_auth: bool = True,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Get track lyrics with authentication handling.
        
        Args:
            url: Spotify track URL
            require_auth: Whether to require authentication
            use_cache: Whether to use cached results
            
        Returns:
            Lyrics string or None if not available
            
        Raises:
            AuthenticationRequiredError: If authentication is required but not provided
        """
        self.logger.info(f"Getting lyrics for: {url}")
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(url, 'lyrics')
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data.get('lyrics')
        
        try:
            lyrics = self._retry_operation(
                self.client.get_track_lyrics,
                url,
                require_auth=require_auth
            )
            
            # Save to cache
            if use_cache and lyrics:
                self._save_to_cache(cache_key, {'lyrics': lyrics})
            
            return lyrics
            
        except AuthenticationRequiredError:
            self.logger.warning("Authentication required for lyrics")
            raise
        except Exception as e:
            self.logger.error(f"Failed to get lyrics: {e}")
            return None
    
    def get_album_info(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get album information with enhanced error handling.
        
        Args:
            url: Spotify album URL
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary containing album information with tracks
        """
        self.logger.info(f"Getting album info for: {url}")
        
        if use_cache:
            cache_key = self._get_cache_key(url, 'album_info')
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        try:
            album_info = self._retry_operation(self.client.get_album_info, url)
            
            if use_cache:
                self._save_to_cache(cache_key, album_info)
            
            self.logger.info(
                f"Successfully retrieved album: {album_info.get('name', 'Unknown')} "
                f"with {album_info.get('total_tracks', 0)} tracks"
            )
            return album_info
            
        except Exception as e:
            self.logger.error(f"Failed to get album info: {e}")
            raise SpotifyScraperError(f"Failed to get album info: {e}")
    
    def get_artist_info(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get artist information including top tracks and albums.
        
        Args:
            url: Spotify artist URL
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary containing artist information
        """
        self.logger.info(f"Getting artist info for: {url}")
        
        if use_cache:
            cache_key = self._get_cache_key(url, 'artist_info')
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        try:
            artist_info = self._retry_operation(self.client.get_artist_info, url)
            
            if use_cache:
                self._save_to_cache(cache_key, artist_info)
            
            self.logger.info(
                f"Successfully retrieved artist: {artist_info.get('name', 'Unknown')} "
                f"with {artist_info.get('followers', {}).get('total', 0)} followers"
            )
            return artist_info
            
        except Exception as e:
            self.logger.error(f"Failed to get artist info: {e}")
            raise SpotifyScraperError(f"Failed to get artist info: {e}")
    
    def get_playlist_info(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get playlist information with all tracks.
        
        Args:
            url: Spotify playlist URL
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary containing playlist information
        """
        self.logger.info(f"Getting playlist info for: {url}")
        
        if use_cache:
            cache_key = self._get_cache_key(url, 'playlist_info')
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        try:
            playlist_info = self._retry_operation(self.client.get_playlist_info, url)
            
            if use_cache:
                self._save_to_cache(cache_key, playlist_info)
            
            self.logger.info(
                f"Successfully retrieved playlist: {playlist_info.get('name', 'Unknown')} "
                f"with {playlist_info.get('tracks', {}).get('total', 0)} tracks"
            )
            return playlist_info
            
        except Exception as e:
            self.logger.error(f"Failed to get playlist info: {e}")
            raise SpotifyScraperError(f"Failed to get playlist info: {e}")
    
    def download_media(
        self,
        url: str,
        download_audio: bool = True,
        download_cover: bool = True,
        output_dir: Optional[Union[str, Path]] = None,
        audio_with_cover: bool = True,
        cover_quality_preference: Optional[List[str]] = None
    ) -> Dict[str, Optional[str]]:
        """
        Download media (audio preview and/or cover art) for a track.
        
        Args:
            url: Spotify track URL
            download_audio: Whether to download the audio preview
            download_cover: Whether to download the cover art
            output_dir: Directory to save files (defaults to current directory)
            audio_with_cover: Whether to embed cover art in the audio file
            cover_quality_preference: Preferred image quality order
            
        Returns:
            Dictionary with paths to downloaded files:
            {
                "audio_path": Optional[str],
                "cover_path": Optional[str]
            }
        """
        self.logger.info(f"Downloading media for: {url}")
        
        output_dir = Path(output_dir) if output_dir else Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {"audio_path": None, "cover_path": None}
        
        # Download audio preview
        if download_audio:
            try:
                audio_path = self._retry_operation(
                    self.client.download_preview_mp3,
                    url,
                    str(output_dir),
                    with_cover=audio_with_cover
                )
                results["audio_path"] = audio_path
                self.logger.info(f"Downloaded audio to: {audio_path}")
            except Exception as e:
                self.logger.error(f"Failed to download audio: {e}")
        
        # Download cover art
        if download_cover:
            try:
                cover_path = self._retry_operation(
                    self.client.download_cover,
                    url,
                    str(output_dir),
                    quality_preference=cover_quality_preference
                )
                results["cover_path"] = cover_path
                self.logger.info(f"Downloaded cover to: {cover_path}")
            except Exception as e:
                self.logger.error(f"Failed to download cover: {e}")
        
        return results
    
    def batch_process(
        self,
        urls: List[str],
        operation: str = "track_info",
        use_cache: bool = True,
        continue_on_error: bool = True
    ) -> Dict[str, Union[Dict[str, Any], Exception]]:
        """
        Process multiple URLs in batch with error handling.
        
        Args:
            urls: List of Spotify URLs to process
            operation: Operation to perform ('track_info', 'album_info', etc.)
            use_cache: Whether to use cached results
            continue_on_error: Whether to continue processing on errors
            
        Returns:
            Dictionary mapping URLs to results or exceptions
        """
        self.logger.info(f"Batch processing {len(urls)} URLs for operation: {operation}")
        
        results = {}
        operation_map = {
            'track_info': self.get_track_info,
            'album_info': self.get_album_info,
            'artist_info': self.get_artist_info,
            'playlist_info': self.get_playlist_info,
            'all_info': self.client.get_all_info
        }
        
        if operation not in operation_map:
            raise ValueError(f"Invalid operation: {operation}")
        
        operation_func = operation_map[operation]
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Processing {i}/{len(urls)}: {url}")
            
            try:
                results[url] = operation_func(url) if operation != 'all_info' else operation_func(url)
            except Exception as e:
                self.logger.error(f"Failed to process {url}: {e}")
                results[url] = e
                if not continue_on_error:
                    break
        
        # Summary
        successful = sum(1 for r in results.values() if not isinstance(r, Exception))
        self.logger.info(
            f"Batch processing complete: {successful}/{len(urls)} successful"
        )
        
        return results
    
    def export_results(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        output_file: Union[str, Path],
        format: str = "json"
    ) -> None:
        """
        Export results to file in various formats.
        
        Args:
            data: Data to export
            output_file: Output file path
            format: Export format ('json', 'csv', 'txt')
        """
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if format == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif format == "csv":
                import csv
                
                # Flatten nested data for CSV
                if isinstance(data, dict):
                    data = [data]
                
                if data and isinstance(data[0], dict):
                    keys = data[0].keys()
                    with open(output_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=keys)
                        writer.writeheader()
                        writer.writerows(data)
            
            elif format == "txt":
                with open(output_file, 'w', encoding='utf-8') as f:
                    if isinstance(data, dict):
                        for key, value in data.items():
                            f.write(f"{key}: {value}\n")
                    else:
                        f.write(str(data))
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            self.logger.info(f"Exported results to: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to export results: {e}")
            raise
    
    def clear_cache(self, older_than_days: Optional[int] = None) -> int:
        """
        Clear cache files.
        
        Args:
            older_than_days: Only clear files older than this many days
            
        Returns:
            Number of files cleared
        """
        cleared = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                if older_than_days:
                    # Check file age
                    file_age = (datetime.now() - datetime.fromtimestamp(
                        cache_file.stat().st_mtime
                    )).days
                    
                    if file_age < older_than_days:
                        continue
                
                cache_file.unlink()
                cleared += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to clear cache file {cache_file}: {e}")
        
        self.logger.info(f"Cleared {cleared} cache files")
        return cleared
    
    def close(self) -> None:
        """
        Close the client and clean up resources.
        """
        try:
            self.client.close()
            self.logger.info("SpotifyScraperWrapper closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing client: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()
        return False


# Utility functions for common operations
def create_authenticated_client(
    cookie_file: str,
    **kwargs
) -> SpotifyScraperWrapper:
    """
    Create an authenticated client from a cookie file.
    
    Args:
        cookie_file: Path to cookies.txt file
        **kwargs: Additional arguments for SpotifyScraperWrapper
        
    Returns:
        Configured SpotifyScraperWrapper instance
    """
    return SpotifyScraperWrapper(cookie_file=cookie_file, **kwargs)


def analyze_spotify_url(url: str) -> Dict[str, Any]:
    """
    Analyze a Spotify URL and extract metadata.
    
    Args:
        url: Spotify URL to analyze
        
    Returns:
        Dictionary with URL analysis results
    """
    from spotify_scraper.utils.url import get_url_type, get_spotify_id
    
    return {
        "url": url,
        "type": get_url_type(url),
        "id": get_spotify_id(url),
        "is_valid": get_url_type(url) is not None
    }


@contextmanager
def spotify_scraper_session(**kwargs):
    """
    Context manager for SpotifyScraper sessions with automatic cleanup.
    
    Args:
        **kwargs: Arguments for SpotifyScraperWrapper
        
    Yields:
        SpotifyScraperWrapper instance
    """
    scraper = SpotifyScraperWrapper(**kwargs)
    try:
        yield scraper
    finally:
        scraper.close()


def main():
    """
    Demonstration of SpotifyScraper usage with all features.
    """
    # Example URLs for demonstration
    example_urls = {
        "track": "https://open.spotify.com/track/6rqhFgbbKwnb9MLmUQDhG6",
        "album": "https://open.spotify.com/album/6tEZCJKMSqHjgk7lGOyVzT",
        "artist": "https://open.spotify.com/artist/4V8LLVI7PbaPR0K2TGSxFF",
        "playlist": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
    }
    
    # Create output directory for results
    output_dir = Path("spotify_scraper_output")
    output_dir.mkdir(exist_ok=True)
    
    # Use context manager for automatic cleanup
    with spotify_scraper_session(
        log_level="INFO",
        log_file=str(output_dir / "scraper.log"),
        cache_dir=str(output_dir / "cache"),
        browser_type="requests"
    ) as scraper:
        
        # 1. Get track information with lyrics (if authenticated)
        print("\n=== Track Information ===")
        try:
            track_info = scraper.get_track_info(example_urls["track"])
            print(f"Track: {track_info['name']} by {', '.join(a['name'] for a in track_info['artists'])}")
            print(f"Album: {track_info['album']['name']}")
            print(f"Duration: {track_info['duration_ms'] / 1000:.2f} seconds")
            
            # Try to get lyrics (will fail without authentication)
            try:
                lyrics = scraper.get_track_lyrics(example_urls["track"], require_auth=False)
                if lyrics:
                    print(f"Lyrics preview: {lyrics[:100]}...")
            except AuthenticationRequiredError:
                print("Lyrics require authentication")
                
        except Exception as e:
            print(f"Error getting track info: {e}")
        
        # 2. Get album information
        print("\n=== Album Information ===")
        try:
            album_info = scraper.get_album_info(example_urls["album"])
            print(f"Album: {album_info['name']} by {', '.join(a['name'] for a in album_info['artists'])}")
            print(f"Release Date: {album_info['release_date']}")
            print(f"Total Tracks: {album_info['total_tracks']}")
            
            # Export album info to JSON
            scraper.export_results(
                album_info,
                output_dir / "album_info.json",
                format="json"
            )
            
        except Exception as e:
            print(f"Error getting album info: {e}")
        
        # 3. Get artist information
        print("\n=== Artist Information ===")
        try:
            artist_info = scraper.get_artist_info(example_urls["artist"])
            print(f"Artist: {artist_info['name']}")
            print(f"Genres: {', '.join(artist_info.get('genres', []))}")
            print(f"Followers: {artist_info['followers']['total']:,}")
            
        except Exception as e:
            print(f"Error getting artist info: {e}")
        
        # 4. Get playlist information
        print("\n=== Playlist Information ===")
        try:
            playlist_info = scraper.get_playlist_info(example_urls["playlist"])
            print(f"Playlist: {playlist_info['name']}")
            print(f"Owner: {playlist_info['owner']['display_name']}")
            print(f"Total Tracks: {playlist_info['tracks']['total']}")
            
        except Exception as e:
            print(f"Error getting playlist info: {e}")
        
        # 5. Download media for a track
        print("\n=== Media Download ===")
        try:
            media_paths = scraper.download_media(
                example_urls["track"],
                output_dir=output_dir / "media",
                download_audio=True,
                download_cover=True,
                audio_with_cover=True
            )
            
            if media_paths["audio_path"]:
                print(f"Audio downloaded: {media_paths['audio_path']}")
            if media_paths["cover_path"]:
                print(f"Cover downloaded: {media_paths['cover_path']}")
                
        except Exception as e:
            print(f"Error downloading media: {e}")
        
        # 6. Batch processing example
        print("\n=== Batch Processing ===")
        batch_urls = list(example_urls.values())[:2]  # Process first 2 URLs
        batch_results = scraper.batch_process(
            batch_urls,
            operation="all_info",
            continue_on_error=True
        )
        
        # Export batch results
        successful_results = {
            url: data for url, data in batch_results.items()
            if not isinstance(data, Exception)
        }
        
        scraper.export_results(
            successful_results,
            output_dir / "batch_results.json",
            format="json"
        )
        
        print(f"Batch processing complete: {len(successful_results)}/{len(batch_urls)} successful")
        
        # 7. Cache management
        print("\n=== Cache Management ===")
        print(f"Cache directory: {scraper.cache_dir}")
        print(f"Cache size: {len(list(scraper.cache_dir.glob('*.json')))} files")
        
        # Clear old cache files
        cleared = scraper.clear_cache(older_than_days=7)
        print(f"Cleared {cleared} old cache files")
    
    print("\n=== Session Complete ===")
    print(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    main()