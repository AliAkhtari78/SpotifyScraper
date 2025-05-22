#!/usr/bin/env python3
"""
Common utility functions for SpotifyScraper operations.

This module provides high-level utility functions that simplify common
SpotifyScraper operations, including bulk operations, data validation,
formatting, and analysis.

Author: SpotifyScraper Development Team
Date: 2025-01-22
Version: 2.0.0
"""

import re
import json
import csv
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple, Iterator
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging

from spotify_scraper import SpotifyClient
from spotify_scraper.utils.url import get_url_type, get_spotify_id
from spotify_scraper.exceptions import URLError, SpotifyScraperError


logger = logging.getLogger(__name__)


class SpotifyDataAnalyzer:
    """
    Analyzer for Spotify data with statistical and aggregation capabilities.
    
    This class provides methods to analyze and aggregate data from Spotify,
    including playlist analysis, artist statistics, and track metrics.
    """
    
    @staticmethod
    def analyze_playlist(playlist_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a playlist and generate comprehensive statistics.
        
        Args:
            playlist_data: Dictionary containing playlist information
            
        Returns:
            Dictionary with playlist analysis:
            {
                "basic_stats": {
                    "total_tracks": int,
                    "total_duration_ms": int,
                    "total_duration_formatted": str,
                    "average_track_duration_ms": float,
                    "average_popularity": float
                },
                "artist_stats": {
                    "unique_artists": int,
                    "top_artists": List[Tuple[str, int]],
                    "artist_distribution": Dict[str, int]
                },
                "album_stats": {
                    "unique_albums": int,
                    "albums_per_artist": Dict[str, List[str]]
                },
                "temporal_stats": {
                    "oldest_track": Dict[str, Any],
                    "newest_track": Dict[str, Any],
                    "release_year_distribution": Dict[int, int]
                },
                "popularity_stats": {
                    "most_popular_tracks": List[Dict[str, Any]],
                    "least_popular_tracks": List[Dict[str, Any]],
                    "popularity_distribution": Dict[str, int]
                }
            }
        """
        tracks = playlist_data.get('tracks', {}).get('items', [])
        
        if not tracks:
            return {"error": "No tracks found in playlist"}
        
        # Extract track details
        track_details = []
        for item in tracks:
            track = item.get('track', {})
            if track:
                track_details.append({
                    'id': track.get('id'),
                    'name': track.get('name'),
                    'artists': track.get('artists', []),
                    'album': track.get('album', {}),
                    'duration_ms': track.get('duration_ms', 0),
                    'popularity': track.get('popularity', 0),
                    'release_date': track.get('album', {}).get('release_date', '')
                })
        
        # Basic statistics
        total_duration = sum(t['duration_ms'] for t in track_details)
        avg_duration = total_duration / len(track_details) if track_details else 0
        avg_popularity = sum(t['popularity'] for t in track_details) / len(track_details) if track_details else 0
        
        # Artist statistics
        artist_counter = Counter()
        for track in track_details:
            for artist in track['artists']:
                artist_counter[artist.get('name', 'Unknown')] += 1
        
        # Album statistics
        albums_per_artist = defaultdict(set)
        unique_albums = set()
        for track in track_details:
            album_name = track['album'].get('name', 'Unknown')
            unique_albums.add(album_name)
            for artist in track['artists']:
                albums_per_artist[artist.get('name', 'Unknown')].add(album_name)
        
        # Temporal statistics
        valid_dates = [t for t in track_details if t['release_date']]
        oldest_track = min(valid_dates, key=lambda x: x['release_date']) if valid_dates else None
        newest_track = max(valid_dates, key=lambda x: x['release_date']) if valid_dates else None
        
        # Release year distribution
        year_counter = Counter()
        for track in track_details:
            release_date = track['release_date']
            if release_date and len(release_date) >= 4:
                year = int(release_date[:4])
                year_counter[year] += 1
        
        # Popularity statistics
        sorted_by_popularity = sorted(track_details, key=lambda x: x['popularity'], reverse=True)
        
        # Popularity distribution (grouped by ranges)
        popularity_ranges = {
            '0-20': 0,
            '21-40': 0,
            '41-60': 0,
            '61-80': 0,
            '81-100': 0
        }
        
        for track in track_details:
            pop = track['popularity']
            if pop <= 20:
                popularity_ranges['0-20'] += 1
            elif pop <= 40:
                popularity_ranges['21-40'] += 1
            elif pop <= 60:
                popularity_ranges['41-60'] += 1
            elif pop <= 80:
                popularity_ranges['61-80'] += 1
            else:
                popularity_ranges['81-100'] += 1
        
        return {
            "basic_stats": {
                "total_tracks": len(track_details),
                "total_duration_ms": total_duration,
                "total_duration_formatted": format_duration(total_duration),
                "average_track_duration_ms": avg_duration,
                "average_track_duration_formatted": format_duration(int(avg_duration)),
                "average_popularity": round(avg_popularity, 2)
            },
            "artist_stats": {
                "unique_artists": len(artist_counter),
                "top_artists": artist_counter.most_common(10),
                "artist_distribution": dict(artist_counter)
            },
            "album_stats": {
                "unique_albums": len(unique_albums),
                "albums_per_artist": {
                    artist: list(albums) 
                    for artist, albums in albums_per_artist.items()
                }
            },
            "temporal_stats": {
                "oldest_track": oldest_track,
                "newest_track": newest_track,
                "release_year_distribution": dict(year_counter)
            },
            "popularity_stats": {
                "most_popular_tracks": sorted_by_popularity[:5],
                "least_popular_tracks": sorted_by_popularity[-5:],
                "popularity_distribution": popularity_ranges
            }
        }
    
    @staticmethod
    def compare_playlists(
        playlist1: Dict[str, Any],
        playlist2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two playlists and find similarities and differences.
        
        Args:
            playlist1: First playlist data
            playlist2: Second playlist data
            
        Returns:
            Dictionary with comparison results
        """
        tracks1 = {
            item['track']['id']: item['track']
            for item in playlist1.get('tracks', {}).get('items', [])
            if item.get('track')
        }
        
        tracks2 = {
            item['track']['id']: item['track']
            for item in playlist2.get('tracks', {}).get('items', [])
            if item.get('track')
        }
        
        # Find common and unique tracks
        common_ids = set(tracks1.keys()) & set(tracks2.keys())
        unique_to_1 = set(tracks1.keys()) - set(tracks2.keys())
        unique_to_2 = set(tracks2.keys()) - set(tracks1.keys())
        
        # Extract artist information
        artists1 = set()
        artists2 = set()
        
        for track in tracks1.values():
            for artist in track.get('artists', []):
                artists1.add(artist.get('name', 'Unknown'))
        
        for track in tracks2.values():
            for artist in track.get('artists', []):
                artists2.add(artist.get('name', 'Unknown'))
        
        common_artists = artists1 & artists2
        
        return {
            "playlist1_name": playlist1.get('name', 'Playlist 1'),
            "playlist2_name": playlist2.get('name', 'Playlist 2'),
            "track_comparison": {
                "playlist1_total": len(tracks1),
                "playlist2_total": len(tracks2),
                "common_tracks": len(common_ids),
                "unique_to_playlist1": len(unique_to_1),
                "unique_to_playlist2": len(unique_to_2),
                "similarity_percentage": (len(common_ids) / max(len(tracks1), len(tracks2)) * 100) if tracks1 or tracks2 else 0
            },
            "artist_comparison": {
                "playlist1_artists": len(artists1),
                "playlist2_artists": len(artists2),
                "common_artists": len(common_artists),
                "common_artist_names": sorted(list(common_artists))[:20]  # Top 20
            },
            "common_tracks": [
                {
                    "name": tracks1[track_id]['name'],
                    "artists": ', '.join(a['name'] for a in tracks1[track_id].get('artists', []))
                }
                for track_id in list(common_ids)[:10]  # First 10
            ]
        }


class SpotifyDataFormatter:
    """
    Formatter for Spotify data with various output formats.
    
    Provides methods to format Spotify data for different use cases
    including human-readable text, markdown, and structured formats.
    """
    
    @staticmethod
    def format_track_summary(track_data: Dict[str, Any]) -> str:
        """
        Format track data as a human-readable summary.
        
        Args:
            track_data: Track information dictionary
            
        Returns:
            Formatted string summary
        """
        artists = ', '.join(artist['name'] for artist in track_data.get('artists', []))
        album = track_data.get('album', {}).get('name', 'Unknown Album')
        duration = format_duration(track_data.get('duration_ms', 0))
        popularity = track_data.get('popularity', 0)
        release_date = track_data.get('album', {}).get('release_date', 'Unknown')
        
        summary = f"""
Track: {track_data.get('name', 'Unknown Track')}
Artists: {artists}
Album: {album}
Duration: {duration}
Popularity: {popularity}/100
Release Date: {release_date}
Spotify URI: {track_data.get('uri', 'N/A')}
Preview: {'Available' if track_data.get('preview_url') else 'Not Available'}
"""
        
        if track_data.get('lyrics'):
            lyrics_preview = track_data['lyrics'][:200] + '...' if len(track_data['lyrics']) > 200 else track_data['lyrics']
            summary += f"\nLyrics Preview:\n{lyrics_preview}"
        
        return summary.strip()
    
    @staticmethod
    def format_playlist_markdown(playlist_data: Dict[str, Any]) -> str:
        """
        Format playlist data as Markdown.
        
        Args:
            playlist_data: Playlist information dictionary
            
        Returns:
            Markdown formatted string
        """
        tracks = playlist_data.get('tracks', {}).get('items', [])
        
        markdown = f"""# {playlist_data.get('name', 'Unnamed Playlist')}

**Owner:** {playlist_data.get('owner', {}).get('display_name', 'Unknown')}  
**Tracks:** {playlist_data.get('tracks', {}).get('total', 0)}  
**Public:** {'Yes' if playlist_data.get('public') else 'No'}  
**Collaborative:** {'Yes' if playlist_data.get('collaborative') else 'No'}  

## Description
{playlist_data.get('description', 'No description available')}

## Track List

| # | Title | Artist(s) | Album | Duration |
|---|-------|-----------|-------|----------|
"""
        
        for i, item in enumerate(tracks, 1):
            track = item.get('track', {})
            if track:
                title = track.get('name', 'Unknown')
                artists = ', '.join(a['name'] for a in track.get('artists', []))
                album = track.get('album', {}).get('name', 'Unknown')
                duration = format_duration(track.get('duration_ms', 0))
                
                markdown += f"| {i} | {title} | {artists} | {album} | {duration} |\n"
        
        return markdown
    
    @staticmethod
    def format_artist_card(artist_data: Dict[str, Any]) -> str:
        """
        Format artist data as a card-style summary.
        
        Args:
            artist_data: Artist information dictionary
            
        Returns:
            Formatted artist card string
        """
        genres = ', '.join(artist_data.get('genres', [])) or 'Not specified'
        followers = f"{artist_data.get('followers', {}).get('total', 0):,}"
        popularity = artist_data.get('popularity', 0)
        
        card = f"""
╔══════════════════════════════════════════════════════════════╗
║ ARTIST PROFILE                                               ║
╠══════════════════════════════════════════════════════════════╣
║ Name: {artist_data.get('name', 'Unknown'):<54} ║
║ Genres: {genres:<52} ║
║ Followers: {followers:<49} ║
║ Popularity: {popularity:<48} ║
║ Verified: {'Yes' if artist_data.get('verified') else 'No':<50} ║
╚══════════════════════════════════════════════════════════════╝
"""
        
        if artist_data.get('top_tracks'):
            card += "\nTop Tracks:\n"
            for i, track in enumerate(artist_data['top_tracks'][:5], 1):
                card += f"{i}. {track.get('name', 'Unknown')}\n"
        
        return card
    
    @staticmethod
    def export_to_m3u(
        tracks: List[Dict[str, Any]],
        output_file: Union[str, Path],
        include_metadata: bool = True
    ) -> None:
        """
        Export tracks to M3U playlist format.
        
        Args:
            tracks: List of track dictionaries
            output_file: Output file path
            include_metadata: Whether to include extended info
        """
        output_file = Path(output_file)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            if include_metadata:
                f.write("#EXTM3U\n")
            
            for track in tracks:
                if include_metadata:
                    artists = ', '.join(a['name'] for a in track.get('artists', []))
                    duration_seconds = track.get('duration_ms', 0) // 1000
                    f.write(f"#EXTINF:{duration_seconds},{artists} - {track.get('name', 'Unknown')}\n")
                
                # Write Spotify URI or URL
                uri = track.get('uri', '')
                if uri:
                    f.write(f"{uri}\n")
                else:
                    track_id = track.get('id', '')
                    if track_id:
                        f.write(f"https://open.spotify.com/track/{track_id}\n")


class SpotifyBulkOperations:
    """
    Utilities for bulk operations on Spotify data.
    
    Provides methods for processing multiple items efficiently,
    including batch downloads, parallel processing, and bulk exports.
    """
    
    def __init__(self, client: Optional[SpotifyClient] = None):
        """
        Initialize bulk operations handler.
        
        Args:
            client: SpotifyClient instance (creates new if None)
        """
        self.client = client or SpotifyClient()
        self.logger = logging.getLogger(__name__)
    
    def extract_urls_from_text(self, text: str) -> List[str]:
        """
        Extract all Spotify URLs from a text string.
        
        Args:
            text: Text containing Spotify URLs
            
        Returns:
            List of valid Spotify URLs
        """
        # Pattern to match Spotify URLs
        pattern = r'https?://(?:open\.)?spotify\.com/(?:track|album|artist|playlist)/[a-zA-Z0-9]+'
        
        urls = re.findall(pattern, text)
        
        # Also match Spotify URIs
        uri_pattern = r'spotify:(?:track|album|artist|playlist):[a-zA-Z0-9]+'
        uris = re.findall(uri_pattern, text)
        
        # Convert URIs to URLs
        for uri in uris:
            parts = uri.split(':')
            if len(parts) == 3:
                entity_type, entity_id = parts[1], parts[2]
                urls.append(f"https://open.spotify.com/{entity_type}/{entity_id}")
        
        return list(set(urls))  # Remove duplicates
    
    def process_url_file(
        self,
        file_path: Union[str, Path],
        operation: str = "info",
        output_dir: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """
        Process a file containing Spotify URLs.
        
        Args:
            file_path: Path to file containing URLs (one per line)
            operation: Operation to perform ('info', 'download', 'both')
            output_dir: Directory for outputs
            
        Returns:
            Dictionary with processing results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read URLs from file
        urls = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    found_urls = self.extract_urls_from_text(line)
                    urls.extend(found_urls)
        
        self.logger.info(f"Found {len(urls)} URLs in {file_path}")
        
        results = {
            "total_urls": len(urls),
            "processed": 0,
            "failed": 0,
            "results": {}
        }
        
        output_dir = Path(output_dir) if output_dir else Path.cwd()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for url in urls:
            try:
                url_type = get_url_type(url)
                
                if operation in ["info", "both"]:
                    # Get information based on URL type
                    if url_type == "track":
                        info = self.client.get_track_info(url)
                    elif url_type == "album":
                        info = self.client.get_album_info(url)
                    elif url_type == "artist":
                        info = self.client.get_artist_info(url)
                    elif url_type == "playlist":
                        info = self.client.get_playlist_info(url)
                    else:
                        info = {"error": "Unknown URL type"}
                    
                    results["results"][url] = {"info": info}
                
                if operation in ["download", "both"] and url_type == "track":
                    # Download media for tracks
                    try:
                        audio_path = self.client.download_preview_mp3(
                            url,
                            str(output_dir / "audio")
                        )
                        cover_path = self.client.download_cover(
                            url,
                            str(output_dir / "covers")
                        )
                        
                        if url not in results["results"]:
                            results["results"][url] = {}
                        
                        results["results"][url]["downloads"] = {
                            "audio": audio_path,
                            "cover": cover_path
                        }
                    except Exception as e:
                        self.logger.error(f"Download failed for {url}: {e}")
                
                results["processed"] += 1
                
            except Exception as e:
                self.logger.error(f"Failed to process {url}: {e}")
                results["failed"] += 1
                results["results"][url] = {"error": str(e)}
        
        return results
    
    def create_dataset(
        self,
        urls: List[str],
        output_file: Union[str, Path],
        format: str = "json",
        include_audio_features: bool = False
    ) -> None:
        """
        Create a dataset from multiple Spotify URLs.
        
        Args:
            urls: List of Spotify URLs
            output_file: Output file path
            format: Output format ('json', 'csv')
            include_audio_features: Whether to include audio features (requires auth)
        """
        output_file = Path(output_file)
        dataset = []
        
        for url in urls:
            try:
                url_type = get_url_type(url)
                
                if url_type == "track":
                    data = self.client.get_track_info(url)
                    
                    # Flatten for CSV if needed
                    if format == "csv":
                        flattened = {
                            "id": data.get("id"),
                            "name": data.get("name"),
                            "artists": ', '.join(a['name'] for a in data.get('artists', [])),
                            "album": data.get("album", {}).get("name"),
                            "duration_ms": data.get("duration_ms"),
                            "popularity": data.get("popularity"),
                            "release_date": data.get("album", {}).get("release_date"),
                            "preview_url": data.get("preview_url")
                        }
                        dataset.append(flattened)
                    else:
                        dataset.append(data)
                
                elif url_type == "playlist":
                    # Extract all tracks from playlist
                    playlist_data = self.client.get_playlist_info(url)
                    tracks = playlist_data.get('tracks', {}).get('items', [])
                    
                    for item in tracks:
                        track = item.get('track', {})
                        if track:
                            if format == "csv":
                                flattened = {
                                    "playlist_name": playlist_data.get("name"),
                                    "id": track.get("id"),
                                    "name": track.get("name"),
                                    "artists": ', '.join(a['name'] for a in track.get('artists', [])),
                                    "album": track.get("album", {}).get("name"),
                                    "duration_ms": track.get("duration_ms"),
                                    "popularity": track.get("popularity")
                                }
                                dataset.append(flattened)
                            else:
                                track["playlist_name"] = playlist_data.get("name")
                                dataset.append(track)
                
            except Exception as e:
                self.logger.error(f"Failed to process {url}: {e}")
        
        # Save dataset
        if format == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            if dataset:
                keys = dataset[0].keys()
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(dataset)
        
        self.logger.info(f"Created dataset with {len(dataset)} items: {output_file}")
    
    def download_playlist_covers(
        self,
        playlist_url: str,
        output_dir: Union[str, Path],
        size_preference: str = "large"
    ) -> List[str]:
        """
        Download all album covers from a playlist.
        
        Args:
            playlist_url: Spotify playlist URL
            output_dir: Directory to save covers
            size_preference: Preferred image size ('small', 'medium', 'large')
            
        Returns:
            List of downloaded file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        playlist_data = self.client.get_playlist_info(playlist_url)
        tracks = playlist_data.get('tracks', {}).get('items', [])
        
        downloaded = []
        seen_albums = set()  # Avoid downloading duplicate album covers
        
        for item in tracks:
            track = item.get('track', {})
            if track:
                album = track.get('album', {})
                album_id = album.get('id')
                
                if album_id and album_id not in seen_albums:
                    seen_albums.add(album_id)
                    
                    try:
                        # Create album URL
                        album_url = f"https://open.spotify.com/album/{album_id}"
                        
                        # Download cover
                        cover_path = self.client.download_cover(
                            album_url,
                            str(output_dir),
                            filename=f"{album_id}_{album.get('name', 'unknown').replace('/', '_')}"
                        )
                        
                        if cover_path:
                            downloaded.append(cover_path)
                            self.logger.info(f"Downloaded cover for: {album.get('name')}")
                    
                    except Exception as e:
                        self.logger.error(f"Failed to download cover for album {album_id}: {e}")
        
        self.logger.info(f"Downloaded {len(downloaded)} unique album covers")
        return downloaded


# Utility functions

def format_duration(milliseconds: int) -> str:
    """
    Format duration from milliseconds to human-readable format.
    
    Args:
        milliseconds: Duration in milliseconds
        
    Returns:
        Formatted string (e.g., "3:45", "1:02:30")
    """
    total_seconds = milliseconds // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"


def validate_spotify_urls(urls: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate a list of Spotify URLs.
    
    Args:
        urls: List of URLs to validate
        
    Returns:
        Tuple of (valid_urls, invalid_urls)
    """
    valid = []
    invalid = []
    
    for url in urls:
        if get_url_type(url):
            valid.append(url)
        else:
            invalid.append(url)
    
    return valid, invalid


def group_urls_by_type(urls: List[str]) -> Dict[str, List[str]]:
    """
    Group Spotify URLs by their type.
    
    Args:
        urls: List of Spotify URLs
        
    Returns:
        Dictionary with URL types as keys and lists of URLs as values
    """
    grouped = defaultdict(list)
    
    for url in urls:
        url_type = get_url_type(url)
        if url_type:
            grouped[url_type].append(url)
    
    return dict(grouped)


def create_shareable_playlist_text(
    playlist_data: Dict[str, Any],
    include_links: bool = True,
    max_tracks: Optional[int] = None
) -> str:
    """
    Create a shareable text representation of a playlist.
    
    Args:
        playlist_data: Playlist information
        include_links: Whether to include Spotify links
        max_tracks: Maximum number of tracks to include
        
    Returns:
        Formatted text suitable for sharing
    """
    tracks = playlist_data.get('tracks', {}).get('items', [])
    
    if max_tracks:
        tracks = tracks[:max_tracks]
    
    text = f"🎵 {playlist_data.get('name', 'Playlist')} 🎵\n"
    text += f"By: {playlist_data.get('owner', {}).get('display_name', 'Unknown')}\n"
    
    if playlist_data.get('description'):
        text += f"\n{playlist_data['description']}\n"
    
    text += f"\n{len(tracks)} tracks:\n\n"
    
    for i, item in enumerate(tracks, 1):
        track = item.get('track', {})
        if track:
            artists = ', '.join(a['name'] for a in track.get('artists', []))
            text += f"{i}. {track.get('name')} - {artists}\n"
            
            if include_links and track.get('id'):
                text += f"   🔗 https://open.spotify.com/track/{track['id']}\n"
    
    if max_tracks and len(playlist_data.get('tracks', {}).get('items', [])) > max_tracks:
        text += f"\n... and {len(playlist_data['tracks']['items']) - max_tracks} more tracks"
    
    return text


def merge_playlists(playlists: List[Dict[str, Any]], name: str = "Merged Playlist") -> Dict[str, Any]:
    """
    Merge multiple playlists into one.
    
    Args:
        playlists: List of playlist data dictionaries
        name: Name for the merged playlist
        
    Returns:
        Merged playlist data
    """
    merged_tracks = []
    seen_ids = set()
    
    for playlist in playlists:
        tracks = playlist.get('tracks', {}).get('items', [])
        
        for item in tracks:
            track = item.get('track', {})
            if track and track.get('id') not in seen_ids:
                seen_ids.add(track.get('id'))
                merged_tracks.append(item)
    
    return {
        "name": name,
        "description": f"Merged from {len(playlists)} playlists",
        "tracks": {
            "total": len(merged_tracks),
            "items": merged_tracks
        },
        "type": "playlist",
        "public": False,
        "collaborative": False
    }


# Example usage
if __name__ == "__main__":
    # Example: Analyze a playlist
    client = SpotifyClient()
    
    playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
    playlist_data = client.get_playlist_info(playlist_url)
    
    # Analyze the playlist
    analyzer = SpotifyDataAnalyzer()
    analysis = analyzer.analyze_playlist(playlist_data)
    
    print(json.dumps(analysis, indent=2))
    
    # Format as markdown
    formatter = SpotifyDataFormatter()
    markdown = formatter.format_playlist_markdown(playlist_data)
    
    with open("playlist_analysis.md", "w", encoding="utf-8") as f:
        f.write(markdown)
    
    client.close()