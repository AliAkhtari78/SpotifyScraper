from typing import List, Dict, Optional, Any

class SyncedLyric:
    """Represents a timed lyric line."""
    def __init__(self, text: str, start_time_ms: int, end_time_ms: Optional[int] = None):
        self.text = text
        self.start_time_ms = start_time_ms
        self.end_time_ms = end_time_ms

class TrackArtist:
    """Represents an artist associated with a track."""
    def __init__(self, name: str, id: str, uri: str):
        self.name = name
        self.id = id
        self.uri = uri

class TrackAlbum:
    """Represents the album of a track."""
    def __init__(self, name: str, id: str, uri: str, images: List[Dict[str, Any]], 
                 release_date: str, total_tracks: int, album_type: str):
        self.name = name
        self.id = id
        self.uri = uri
        self.images = images
        self.release_date = release_date
        self.total_tracks = total_tracks
        self.album_type = album_type

class TrackData:
    """Container for all track data."""
    def __init__(
        self,
        name: str,
        id: str,
        uri: str,
        duration_ms: int,
        preview_url: Optional[str],
        is_playable: bool,
        artists: List[TrackArtist],
        album: TrackAlbum,
        lyrics: Optional[List[SyncedLyric]] = None
    ):
        self.name = name
        self.id = id
        self.uri = uri
        self.duration_ms = duration_ms
        self.preview_url = preview_url
        self.is_playable = is_playable
        self.artists = artists
        self.album = album
        self.lyrics = lyrics
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the track data to a dictionary."""
        artists_data = [
            {"name": artist.name, "id": artist.id, "uri": artist.uri}
            for artist in self.artists
        ]
        
        album_data = {
            "name": self.album.name,
            "id": self.album.id,
            "uri": self.album.uri,
            "images": self.album.images,
            "release_date": self.album.release_date,
            "total_tracks": self.album.total_tracks,
            "type": self.album.album_type
        }
        
        lyrics_data = None
        if self.lyrics:
            lyrics_data = [
                {
                    "text": lyric.text,
                    "start_time_ms": lyric.start_time_ms,
                    "end_time_ms": lyric.end_time_ms
                }
                for lyric in self.lyrics
            ]
        
        return {
            "name": self.name,
            "id": self.id,
            "uri": self.uri,
            "duration_ms": self.duration_ms,
            "preview_url": self.preview_url,
            "is_playable": self.is_playable,
            "artists": artists_data,
            "album": album_data,
            "lyrics": lyrics_data
        }