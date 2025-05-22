"""
Backward compatibility layer for SpotifyScraper.

This module provides the old interface for users who are upgrading from
SpotifyScraper 1.x to 2.x. Think of this as a translation layer that makes
old code work with the new architecture underneath.
"""

from typing import Optional, Dict, Any, Union
import logging

from spotify_scraper.auth.session import Session, Request
from spotify_scraper.client import SpotifyClient
from spotify_scraper.core.types import TrackData, PlaylistData, AlbumData, ArtistData

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
        
        # Create client using the new architecture
        # Extract cookies from session if available
        cookies = None
        if hasattr(session, 'cookies') and session.cookies:
            cookies = dict(session.cookies)
        
        # Set log level based on log parameter
        log_level = "DEBUG" if log else "WARNING"
        
        try:
            self.client = SpotifyClient(
                cookies=cookies,
                log_level=log_level,
                browser_type="requests"
            )
        except Exception as e:
            # If we can't create the client, we'll provide error responses
            logger.warning(f"Could not initialize SpotifyClient: {e}")
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
                track_data = self.client.get_track_info(url)
                
                # Convert to the old format expected by legacy code
                return self._convert_track_data_to_legacy_format(track_data)
            else:
                # Fallback error response in the original format
                return {"ERROR": "Client initialization failed"}
                
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
                # Use the new playlist extractor
                playlist_data = self.client.get_playlist_info(url)
                return self._convert_playlist_data_to_legacy_format(playlist_data)
            else:
                return {"ERROR": "Client initialization failed"}
                
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
            if self.client:
                result = self.client.download_cover(url, path)
                if result:
                    return result
                else:
                    return "Couldn't download the cover: No cover found"
            else:
                return "Couldn't download the cover: Client not initialized"
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
            if self.client:
                result = self.client.download_preview_mp3(url, path, with_cover)
                if result:
                    return result
                else:
                    return "Couldn't download the preview: No preview available"
            else:
                return "Couldn't download the preview: Client not initialized"
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
        # Handle error cases first
        if "ERROR" in playlist_data:
            return {"ERROR": playlist_data["ERROR"]}
        
        # Convert the structured data to the flat format used by v1.x
        legacy_data = {
            "name": playlist_data.get("name", ""),
            "owner_name": playlist_data.get("owner", {}).get("display_name", ""),
            "owner_url": playlist_data.get("owner", {}).get("uri", "").replace("spotify:user:", "https://open.spotify.com/user/"),
            "description": playlist_data.get("description", ""),
            "followers": playlist_data.get("followers", {}).get("total", 0),
            "is_public": playlist_data.get("public", True),
            "collaborative": playlist_data.get("collaborative", False),
            "image_url": "",
            "image_height": 0,
            "image_width": 0,
            "tracks_total": playlist_data.get("tracks", {}).get("total", 0),
            "tracks": [],
            "type_": "playlist",
            "ERROR": None,
        }
        
        # Extract cover image information
        images = playlist_data.get("images", [])
        if images and len(images) > 0:
            # Use the largest image (first in the list)
            largest_image = images[0]
            legacy_data["image_url"] = largest_image.get("url", "")
            legacy_data["image_height"] = largest_image.get("height", 0)
            legacy_data["image_width"] = largest_image.get("width", 0)
        
        # Convert tracks to legacy format
        tracks_items = playlist_data.get("tracks", {}).get("items", [])
        for item in tracks_items:
            track = item.get("track", {})
            if track:
                legacy_track = {
                    "name": track.get("name", ""),
                    "artist": ", ".join([a.get("name", "") for a in track.get("artists", [])]),
                    "album": track.get("album", {}).get("name", ""),
                    "duration_ms": track.get("duration_ms", 0),
                    "uri": track.get("uri", ""),
                    "url": track.get("external_urls", {}).get("spotify", ""),
                }
                legacy_data["tracks"].append(legacy_track)
        
        return legacy_data
    
    def get_album_url_info(self, url: str) -> Dict[str, Any]:
        """
        Extract album information from a URL.
        
        Args:
            url: Spotify album URL
            
        Returns:
            Dictionary with album information in the original format
        """
        try:
            if self.client:
                # Use the new album extractor
                album_data = self.client.get_album_info(url)
                return self._convert_album_data_to_legacy_format(album_data)
            else:
                return {"ERROR": "Client initialization failed"}
                
        except Exception as e:
            if self.log:
                logger.error(f"Album extraction failed: {e}")
            return {"ERROR": str(e)}
    
    def get_artist_url_info(self, url: str) -> Dict[str, Any]:
        """
        Extract artist information from a URL.
        
        Args:
            url: Spotify artist URL
            
        Returns:
            Dictionary with artist information in the original format
        """
        try:
            if self.client:
                # Use the new artist extractor
                artist_data = self.client.get_artist_info(url)
                return self._convert_artist_data_to_legacy_format(artist_data)
            else:
                return {"ERROR": "Client initialization failed"}
                
        except Exception as e:
            if self.log:
                logger.error(f"Artist extraction failed: {e}")
            return {"ERROR": str(e)}
    
    def _convert_album_data_to_legacy_format(self, album_data: AlbumData) -> Dict[str, Any]:
        """
        Convert new album data format to the legacy format.
        
        Args:
            album_data: Album data in new format
            
        Returns:
            Album data in legacy format
        """
        # Handle error cases first
        if "ERROR" in album_data:
            return {"ERROR": album_data["ERROR"]}
        
        # Convert the structured data to the flat format
        legacy_data = {
            "name": album_data.get("name", ""),
            "artist": ", ".join([a.get("name", "") for a in album_data.get("artists", [])]),
            "release_date": album_data.get("release_date", ""),
            "total_tracks": album_data.get("total_tracks", 0),
            "label": album_data.get("label", ""),
            "popularity": album_data.get("popularity", 0),
            "album_type": album_data.get("album_type", ""),
            "uri": album_data.get("uri", ""),
            "cover_url": "",
            "cover_height": 0,
            "cover_width": 0,
            "tracks": [],
            "type_": "album",
            "ERROR": None,
        }
        
        # Extract cover image information
        images = album_data.get("images", [])
        if images and len(images) > 0:
            largest_image = images[0]
            legacy_data["cover_url"] = largest_image.get("url", "")
            legacy_data["cover_height"] = largest_image.get("height", 0)
            legacy_data["cover_width"] = largest_image.get("width", 0)
        
        # Convert tracks
        tracks_items = album_data.get("tracks", {}).get("items", [])
        for track in tracks_items:
            legacy_track = {
                "name": track.get("name", ""),
                "artist": ", ".join([a.get("name", "") for a in track.get("artists", [])]),
                "duration_ms": track.get("duration_ms", 0),
                "track_number": track.get("track_number", 0),
                "uri": track.get("uri", ""),
            }
            legacy_data["tracks"].append(legacy_track)
        
        return legacy_data
    
    def _convert_artist_data_to_legacy_format(self, artist_data: ArtistData) -> Dict[str, Any]:
        """
        Convert new artist data format to the legacy format.
        
        Args:
            artist_data: Artist data in new format
            
        Returns:
            Artist data in legacy format
        """
        # Handle error cases first
        if "ERROR" in artist_data:
            return {"ERROR": artist_data["ERROR"]}
        
        # Convert the structured data to the flat format
        legacy_data = {
            "name": artist_data.get("name", ""),
            "genres": artist_data.get("genres", []),
            "popularity": artist_data.get("popularity", 0),
            "followers": artist_data.get("followers", {}).get("total", 0),
            "monthly_listeners": artist_data.get("monthly_listeners", 0),
            "bio": artist_data.get("bio", ""),
            "verified": artist_data.get("verified", False),
            "uri": artist_data.get("uri", ""),
            "image_url": "",
            "image_height": 0,
            "image_width": 0,
            "top_tracks": [],
            "albums": [],
            "type_": "artist",
            "ERROR": None,
        }
        
        # Extract image information
        images = artist_data.get("images", [])
        if images and len(images) > 0:
            largest_image = images[0]
            legacy_data["image_url"] = largest_image.get("url", "")
            legacy_data["image_height"] = largest_image.get("height", 0)
            legacy_data["image_width"] = largest_image.get("width", 0)
        
        # Convert top tracks
        for track in artist_data.get("top_tracks", [])[:10]:  # Legacy format typically had top 10
            legacy_track = {
                "name": track.get("name", ""),
                "album": track.get("album", {}).get("name", ""),
                "duration_ms": track.get("duration_ms", 0),
                "popularity": track.get("popularity", 0),
                "uri": track.get("uri", ""),
            }
            legacy_data["top_tracks"].append(legacy_track)
        
        # Convert albums
        for album in artist_data.get("albums", []):
            legacy_album = {
                "name": album.get("name", ""),
                "release_date": album.get("release_date", ""),
                "total_tracks": album.get("total_tracks", 0),
                "album_type": album.get("album_type", ""),
                "uri": album.get("uri", ""),
            }
            legacy_data["albums"].append(legacy_album)
        
        return legacy_data
    
    def close(self) -> None:
        """
        Clean up resources. Added for proper resource management.
        """
        if self.client:
            self.client.close()
    
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
