"""
Backward compatibility layer for SpotifyScraper.

This module provides the old interface for users who are upgrading from
SpotifyScraper 1.x to 2.x. Think of this as a translation layer that makes
old code work with the new architecture underneath.
"""

from typing import Optional, Dict, Any, Union
import logging

from spotify_scraper.auth.session import Session, Request
from spotify_scraper.core.client import SpotifyClient
from spotify_scraper.core.types import TrackData, PlaylistData
from spotify_scraper.browsers.requests_browser import RequestsBrowser

logger = logging.getLogger(__name__)


class Scraper:
    """
    Backward compatibility class for the original Scraper interface.
    
    This class maintains the exact same method signatures and behavior as
    the original SpotifyScraper, but uses the new architecture underneath.
    This means existing user code doesn't need to change, but gets the
    benefits of the improved implementation.
    
    Think of this as a facade pattern - it presents the old familiar interface
    while delegating the actual work to the new, more powerful components.
    """
    
    def __init__(self, session: Session, log: bool = False):
        """
        Initialize with the same interface as the original Scraper.
        
        Args:
            session: Session object (from Request().request())
            log: Whether to enable logging (legacy parameter)
        """
        self.session = session
        self.log = log
        
        # Create a browser and client using the new architecture
        # but keep them internal so the user doesn't need to know about them
        try:
            self.browser = RequestsBrowser(session=session)
            self.client = SpotifyClient(browser=self.browser)
        except Exception as e:
            # If we can't create the browser, we'll fall back to basic functionality
            logger.warning(f"Could not initialize full browser support: {e}")
            self.browser = None
            self.client = None
        
        logger.debug("Initialized Scraper (compatibility mode)")
    
    def get_track_url_info(self, url: str) -> Dict[str, Any]:
        """
        Extract track information from a URL.
        
        This method maintains the exact same interface as the original
        get_track_url_info method, including the same return format and
        error handling behavior.
        
        Args:
            url: Spotify track URL
            
        Returns:
            Dictionary with track information in the original format
        """
        try:
            if self.client:
                # Use the new extraction system
                track_data = self.client.get_track(url)
                
                # Convert to the old format expected by legacy code
                return self._convert_track_data_to_legacy_format(track_data)
            else:
                # Fallback error response in the original format
                return {"ERROR": "Browser initialization failed"}
                
        except Exception as e:
            if self.log:
                logger.error(f"Track extraction failed: {e}")
            return {"ERROR": str(e)}
    
    def get_playlist_url_info(self, url: str) -> Dict[str, Any]:
        """
        Extract playlist information from a URL.
        
        Args:
            url: Spotify playlist URL
            
        Returns:
            Dictionary with playlist information in the original format
        """
        try:
            if self.client:
                # This will use the new playlist extractor when it's implemented
                playlist_data = self.client.get_playlist(url)
                return self._convert_playlist_data_to_legacy_format(playlist_data)
            else:
                return {"ERROR": "Browser initialization failed"}
                
        except NotImplementedError:
            return {"ERROR": "Playlist extraction not yet implemented in v2.0"}
        except Exception as e:
            if self.log:
                logger.error(f"Playlist extraction failed: {e}")
            return {"ERROR": str(e)}
    
    def download_cover(self, url: str, path: str = '') -> str:
        """
        Download cover art for a track or playlist.
        
        Args:
            url: Spotify URL
            path: Download path (default: current directory)
            
        Returns:
            Path to downloaded file or error message
        """
        try:
            # This functionality will be implemented when media downloaders are ready
            return "Cover download not yet implemented in v2.0"
        except Exception as e:
            if self.log:
                logger.error(f"Cover download failed: {e}")
            return f"Couldn't download the cover: {e}"
    
    def download_preview_mp3(self, url: str, path: str = '', with_cover: bool = False) -> str:
        """
        Download preview MP3 for a track.
        
        Args:
            url: Spotify track URL
            path: Download path (default: current directory)
            with_cover: Whether to embed cover art in the MP3
            
        Returns:
            Path to downloaded file or error message
        """
        try:
            # This functionality will be implemented when media downloaders are ready
            return "MP3 download not yet implemented in v2.0"
        except Exception as e:
            if self.log:
                logger.error(f"MP3 download failed: {e}")
            return f"Couldn't download the preview: {e}"
    
    def _convert_track_data_to_legacy_format(self, track_data: TrackData) -> Dict[str, Any]:
        """
        Convert new track data format to the legacy format expected by old code.
        
        This method handles the translation between the new structured data format
        and the flat dictionary format that the original library used.
        
        Args:
            track_data: Track data in new format
            
        Returns:
            Track data in legacy format
        """
        # Handle error cases first
        if "ERROR" in track_data:
            return {"ERROR": track_data["ERROR"]}
        
        # Convert the structured data to the flat format
        legacy_data = {
            "title": track_data.get("name", ""),
            "preview_mp3": track_data.get("preview_url", ""),
            "duration": self._ms_to_readable(track_data.get("duration_ms", 0)),
            "artist_name": "",
            "artist_url": "",
            "album_title": "",
            "album_cover_url": "",
            "album_cover_height": 0,
            "album_cover_width": 0,
            "release_date": "",
            "total_tracks": 0,
            "type_": "track",
            "ERROR": None,
        }
        
        # Extract artist information
        artists = track_data.get("artists", [])
        if artists and len(artists) > 0:
            legacy_data["artist_name"] = artists[0].get("name", "")
            legacy_data["artist_url"] = artists[0].get("uri", "").replace("spotify:artist:", "https://open.spotify.com/artist/")
        
        # Extract album information
        album = track_data.get("album", {})
        if album:
            legacy_data["album_title"] = album.get("name", "")
            legacy_data["release_date"] = album.get("release_date", "")
            
            # Extract album cover information
            images = album.get("images", [])
            if images and len(images) > 0:
                # Use the largest image (first in the list)
                largest_image = images[0]
                legacy_data["album_cover_url"] = largest_image.get("url", "")
                legacy_data["album_cover_height"] = largest_image.get("height", 0)
                legacy_data["album_cover_width"] = largest_image.get("width", 0)
        
        return legacy_data
    
    def _convert_playlist_data_to_legacy_format(self, playlist_data: PlaylistData) -> Dict[str, Any]:
        """
        Convert new playlist data format to the legacy format.
        
        Args:
            playlist_data: Playlist data in new format
            
        Returns:
            Playlist data in legacy format
        """
        # This is a placeholder for when playlist extraction is implemented
        return {"ERROR": "Playlist conversion not yet implemented"}
    
    @staticmethod
    def _ms_to_readable(millis: int) -> str:
        """
        Convert milliseconds to readable time format (MM:SS).
        
        This maintains the exact same behavior as the original implementation.
        
        Args:
            millis: Time in milliseconds
            
        Returns:
            Formatted time string
        """
        if millis <= 0:
            return "0:00"
        
        seconds = int(millis / 1000) % 60
        minutes = int(millis / (1000 * 60)) % 60
        hours = int(millis / (1000 * 60 * 60)) % 24
        
        if hours == 0:
            return f"{minutes}:{seconds:02d}"
        else:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
