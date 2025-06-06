"""
Core type definitions for the SpotifyScraper library.

This module defines TypedDict classes for all data structures used in the library.
"""

from typing import Any, Dict, List, TypedDict


class ImageData(TypedDict):
    """
    Data for an image resource.

    Attributes:
        url: URL of the image
        width: Width of the image in pixels
        height: Height of the image in pixels
    """

    url: str
    width: int
    height: int


class ArtistData(TypedDict, total=False):
    """
    Data for an artist.

    Required Attributes:
        id: Spotify ID of the artist
        name: Name of the artist
        uri: Spotify URI of the artist
        type: Type of entity ("artist")

    Optional Attributes:
        is_verified: Whether the artist is verified on Spotify
        bio: Artist biography text
        images: List of artist images
        stats: Statistics about the artist
        popular_releases: Popular releases by the artist
        discography_stats: Statistics about the artist's discography
        top_tracks: List of the artist's top tracks
    """

    id: str
    name: str
    uri: str
    type: str
    is_verified: bool
    bio: str
    images: List[ImageData]
    stats: Dict[str, Any]
    popular_releases: List[Dict[str, Any]]
    discography_stats: Dict[str, int]
    top_tracks: List[Dict[str, Any]]


class AlbumData(TypedDict, total=False):
    """
    Data for an album.

    Required Attributes:
        id: Spotify ID of the album
        name: Name of the album
        uri: Spotify URI of the album
        type: Type of entity ("album")

    Optional Attributes:
        artists: List of album artists
        images: List of album cover art images
        release_date: Release date of the album
        total_tracks: Total number of tracks in the album
        tracks: List of tracks in the album
    """

    id: str
    name: str
    uri: str
    type: str
    artists: List[ArtistData]
    images: List[ImageData]
    release_date: str
    total_tracks: int
    tracks: List[Dict[str, Any]]


class LyricsLineData(TypedDict):
    """
    Data for a lyrics line with timing information.

    Attributes:
        start_time_ms: Start time of the line in milliseconds
        words: Text of the lyrics line
        end_time_ms: End time of the line in milliseconds
    """

    start_time_ms: int
    words: str
    end_time_ms: int


class LyricsData(TypedDict, total=False):
    """
    Data for lyrics.

    Required Attributes:
        sync_type: Type of lyrics synchronization (e.g., "LINE_SYNCED")
        lines: List of lyrics lines with timing information

    Optional Attributes:
        provider: Provider of the lyrics
        language: Language of the lyrics
    """

    sync_type: str
    lines: List[LyricsLineData]
    provider: str
    language: str


class TrackData(TypedDict, total=False):
    """
    Data for a track.

    Required Attributes:
        id: Spotify ID of the track
        name: Name of the track
        uri: Spotify URI of the track
        type: Type of entity ("track")

    Optional Attributes:
        title: Title of the track (alternative to name)
        duration_ms: Duration of the track in milliseconds
        artists: List of track artists
        preview_url: URL to a preview of the track
        is_playable: Whether the track is playable
        is_explicit: Whether the track has explicit content
        album: Album the track belongs to
        lyrics: Lyrics of the track with timing information
        track_number: Position of the track in its album
        disc_number: Disc number of the track in its album
    """

    id: str
    name: str
    uri: str
    type: str
    title: str
    duration_ms: int
    artists: List[ArtistData]
    preview_url: str
    is_playable: bool
    is_explicit: bool
    album: AlbumData
    lyrics: LyricsData
    track_number: int
    disc_number: int


class PlaylistData(TypedDict, total=False):
    """
    Data for a playlist.

    Required Attributes:
        id: Spotify ID of the playlist
        name: Name of the playlist
        uri: Spotify URI of the playlist
        type: Type of entity ("playlist")

    Optional Attributes:
        description: Description of the playlist
        owner: Owner of the playlist
        images: List of playlist cover art images
        track_count: Number of tracks in the playlist
        tracks: List of tracks in the playlist
    """

    id: str
    name: str
    uri: str
    type: str
    description: str
    owner: Dict[str, str]
    images: List[ImageData]
    track_count: int
    tracks: List[TrackData]


class VisualIdentityData(TypedDict, total=False):
    """
    Data for visual identity.

    Attributes:
        image: List of images
    """

    image: List[Dict[str, Any]]


class EpisodeData(TypedDict, total=False):
    """
    Data for a podcast episode.

    Required Attributes:
        id: Spotify ID of the episode
        name: Name of the episode
        uri: Spotify URI of the episode
        type: Type of entity ("episode")

    Optional Attributes:
        title: Title of the episode (alternative to name)
        subtitle: Subtitle (usually show name)
        duration_ms: Duration of the episode in milliseconds
        release_date: Release date ISO string
        description: Episode description
        explicit: Whether the episode has explicit content
        is_playable: Whether the episode is playable
        is_trailer: Whether it's a trailer
        is_audiobook: Whether it's an audiobook
        has_video: Whether episode has video
        audio_preview_url: URL to a preview clip
        video_preview_url: URL to video preview (if available)
        video_thumbnails: List of video thumbnail images
        show: Show information
        images: List of episode images
        visual_identity: Visual identity with colors and images
        full_audio_urls: Full episode URLs (requires Premium)
        audio_format: Audio format type
        file_id: Audio file ID
        requires_drm: Whether DRM is required
    """

    id: str
    name: str
    uri: str
    type: str
    title: str
    subtitle: str
    duration_ms: int
    release_date: str
    description: str
    explicit: bool
    is_playable: bool
    is_trailer: bool
    is_audiobook: bool
    has_video: bool
    audio_preview_url: str
    video_preview_url: str
    video_thumbnails: List[ImageData]
    show: Dict[str, Any]
    images: List[ImageData]
    visual_identity: Dict[str, Any]
    full_audio_urls: List[str]
    audio_format: str
    file_id: str
    requires_drm: bool


class ShowData(TypedDict, total=False):
    """
    Data for a podcast show.

    Required Attributes:
        id: Spotify ID of the show
        name: Name of the show
        uri: Spotify URI of the show
        type: Type of entity ("show")

    Optional Attributes:
        title: Title of the show (alternative to name)
        subtitle: Show subtitle
        description: Show description
        publisher: Publisher name
        categories: List of categories/genres
        total_episodes: Total number of episodes
        images: List of show cover art images
        episodes: List of recent episodes
        rating: Rating information (average and count)
        explicit: Whether show has explicit content
        media_type: Type of media (audio/video)
        is_externally_hosted: Whether hosted outside Spotify
        visual_identity: Visual identity with colors
    """

    id: str
    name: str
    uri: str
    type: str
    title: str
    subtitle: str
    description: str
    publisher: str
    categories: List[str]
    total_episodes: int
    images: List[ImageData]
    episodes: List[EpisodeData]
    rating: Dict[str, Any]
    explicit: bool
    media_type: str
    is_externally_hosted: bool
    visual_identity: Dict[str, Any]


class ConfigurationData(TypedDict, total=False):
    """
    Configuration data for the scraper.

    Attributes:
        log_level: Logging level
        timeout: Request timeout in seconds
        user_agent: User agent to use for requests
        retries: Number of retries for failed requests
        proxy: Proxy URL
        cookie_file: Path to cookie file
    """

    log_level: str
    timeout: int
    user_agent: str
    retries: int
    proxy: str
    cookie_file: str
