# Real-World Projects

This guide showcases complete applications and real-world projects built with SpotifyScraper, providing inspiration and practical examples for your own projects.

## Table of Contents
- [Music Analytics Dashboard](#music-analytics-dashboard)
- [Playlist Management Tool](#playlist-management-tool)
- [Music Discovery Bot](#music-discovery-bot)
- [Personal Music Archive](#personal-music-archive)
- [Concert Finder App](#concert-finder-app)
- [Music Recommendation Engine](#music-recommendation-engine)
- [Spotify Data Backup Tool](#spotify-data-backup-tool)
- [Integration Examples](#integration-examples)

---

## Music Analytics Dashboard

A comprehensive dashboard for analyzing your music listening patterns and discovering trends.

### Features

- **Real-time Analytics**: Track your listening habits over time
- **Genre Analysis**: Visualize your music taste distribution
- **Artist Discovery**: Find new artists similar to your favorites
- **Mood Tracking**: Correlate music with daily activities
- **Social Sharing**: Share your music insights with friends

### Technology Stack

- **Backend**: Python (FastAPI), SpotifyScraper
- **Frontend**: React.js with Chart.js
- **Database**: PostgreSQL with Redis caching
- **Deployment**: Docker on AWS ECS

### Code Example

```python
# analytics_dashboard/backend/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from spotify_scraper import SpotifyClient
import asyncio
from datetime import datetime, timedelta
import pandas as pd

app = FastAPI(title="Music Analytics Dashboard")

class MusicAnalyzer:
    def __init__(self):
        self.client = SpotifyClient()
        self.cache = {}
    
    async def analyze_listening_history(self, user_playlists: list) -> dict:
        """Analyze user's listening patterns."""
        
        # Extract all tracks from user playlists
        all_tracks = []
        for playlist_url in user_playlists:
            playlist = self.client.get_playlist_info(playlist_url)
            for item in playlist['tracks']['items']:
                if item['track']:
                    all_tracks.append(item['track'])
        
        # Analyze patterns
        analysis = {
            'total_tracks': len(all_tracks),
            'genre_distribution': self._analyze_genres(all_tracks),
            'artist_frequency': self._analyze_artists(all_tracks),
            'decade_distribution': self._analyze_decades(all_tracks),
            'energy_analysis': self._analyze_energy(all_tracks),
            'recommendations': await self._get_recommendations(all_tracks[:50])
        }
        
        return analysis
    
    def _analyze_genres(self, tracks: list) -> dict:
        """Analyze genre distribution."""
        genre_count = {}
        
        for track in tracks:
            # Get artist info to find genres
            artist_url = track['artists'][0]['external_urls']['spotify']
            try:
                artist = self.client.get_artist_info(artist_url)
                for genre in artist.get('genres', []):
                    genre_count[genre] = genre_count.get(genre, 0) + 1
            except Exception:
                continue
        
        # Return top 10 genres
        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_genres[:10])
    
    def _analyze_artists(self, tracks: list) -> dict:
        """Analyze most listened artists."""
        artist_count = {}
        
        for track in tracks:
            artist_name = (track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')
            artist_count[artist_name] = artist_count.get(artist_name, 0) + 1
        
        sorted_artists = sorted(artist_count.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_artists[:20])
    
    def _analyze_decades(self, tracks: list) -> dict:
        """Analyze music by decade."""
        decade_count = {}
        
        for track in tracks:
            try:
                album = self.client.get_album_info(track['album']['external_urls']['spotify'])
                release_date = album.get('release_date', '')
                if release_date and len(release_date) >= 4:
                    year = int(release_date[:4])
                    decade = f"{(year // 10) * 10}s"
                    decade_count[decade] = decade_count.get(decade, 0) + 1
            except Exception:
                continue
        
        return decade_count
    
    async def _get_recommendations(self, sample_tracks: list) -> list:
        """Get music recommendations based on listening history."""
        recommendations = []
        
        # Analyze sample tracks to find patterns
        for track in sample_tracks[:10]:  # Limit for performance
            try:
                # Get similar artists
                artist_url = track['artists'][0]['external_urls']['spotify']
                artist = self.client.get_artist_info(artist_url)
                
                # Get top tracks from related artists (simplified)
                # In a real implementation, you'd use Spotify's recommendation API
                recommendations.append({
                    'type': 'similar_artist',
                    'artist': artist.get('name', 'Unknown'),
                    'reason': f"Because you listen to {track.get('name', 'Unknown')}"
                })
                
            except Exception:
                continue
        
        return recommendations[:5]

# API endpoints
analyzer = MusicAnalyzer()

@app.post("/analyze/playlists")
async def analyze_playlists(playlist_urls: list):
    """Analyze user playlists."""
    try:
        analysis = await analyzer.analyze_listening_history(playlist_urls)
        return {"status": "success", "data": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/track/{track_id}/details")
async def get_track_details(track_id: str):
    """Get detailed track information."""
    try:
        track_url = f"https://open.spotify.com/track/{track_id}"
        track = analyzer.client.get_track_info(track_url)
        
        # Enhance with additional data
        enhanced_info = {
            **track_info,
            'analysis_timestamp': datetime.now().isoformat(),
            'preview_available': bool(track.get('preview_url')),
            'energy_score': calculate_energy_score(track_info)
        }
        
        return enhanced_info
    except Exception as e:
        raise HTTPException(status_code=404, detail="Track not found")

def calculate_energy_score(track_info: dict) -> float:
    """Calculate energy score based on track features."""
    # Simplified energy calculation
    # In practice, you'd use Spotify's audio features API
    duration = track.get('duration_ms', 0)
    popularity = track.get('popularity', 0)
    
    # Simple heuristic (replace with actual audio feature analysis)
    energy = min(100, (popularity * 0.7) + (min(300000, duration) / 3000))
    return round(energy, 2)
```

### Frontend Dashboard

```javascript
// analytics_dashboard/frontend/src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const Dashboard = () => {
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(false);
    const [playlists, setPlaylists] = useState(['']);

    const analyzeMusic = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/analyze/playlists', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(playlists.filter(p => p.trim()))
            });
            
            const data = await response.json();
            setAnalytics(data.data);
        } catch (error) {
            console.error('Analysis failed:', error);
        } finally {
            setLoading(false);
        }
    };

    const genreChartData = analytics?.genre_distribution ? {
        labels: Object.keys(analytics.genre_distribution),
        datasets: [{
            data: Object.values(analytics.genre_distribution),
            backgroundColor: [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
            ]
        }]
    } : null;

    const artistChartData = analytics?.artist_frequency ? {
        labels: Object.keys(analytics.artist_frequency).slice(0, 10),
        datasets: [{
            label: 'Tracks',
            data: Object.values(analytics.artist_frequency).slice(0, 10),
            backgroundColor: '#36A2EB'
        }]
    } : null;

    return (
        <div className="dashboard">
            <h1>🎵 Music Analytics Dashboard</h1>
            
            <div className="input-section">
                <h3>Add Your Spotify Playlists</h3>
                {playlists.map((playlist, index) => (
                    <input
                        key={index}
                        type="text"
                        placeholder="https://open.spotify.com/playlist/..."
                        value={playlist}
                        onChange={(e) => {
                            const newPlaylists = [...playlists];
                            newPlaylists[index] = e.target.value;
                            setPlaylists(newPlaylists);
                        }}
                    />
                ))}
                <button onClick={() => setPlaylists([...playlists, ''])}>
                    + Add Another Playlist
                </button>
                <button onClick={analyzeMusic} disabled={loading}>
                    {loading ? 'Analyzing...' : 'Analyze My Music'}
                </button>
            </div>

            {analytics && (
                <div className="analytics-results">
                    <div className="stats-grid">
                        <div className="stat-card">
                            <h3>{analytics.total_tracks}</h3>
                            <p>Total Tracks</p>
                        </div>
                        <div className="stat-card">
                            <h3>{Object.keys(analytics.genre_distribution).length}</h3>
                            <p>Unique Genres</p>
                        </div>
                        <div className="stat-card">
                            <h3>{Object.keys(analytics.artist_frequency).length}</h3>
                            <p>Unique Artists</p>
                        </div>
                    </div>

                    <div className="charts-grid">
                        <div className="chart-container">
                            <h3>Genre Distribution</h3>
                            {genreChartData && <Pie data={genreChartData} />}
                        </div>
                        
                        <div className="chart-container">
                            <h3>Top Artists</h3>
                            {artistChartData && <Bar data={artistChartData} />}
                        </div>
                    </div>

                    <div className="recommendations">
                        <h3>🎯 Recommendations for You</h3>
                        {analytics.recommendations.map((rec, index) => (
                            <div key={index} className="recommendation-card">
                                <strong>{rec.artist}</strong>
                                <p>{rec.reason}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
```

---

## Playlist Management Tool

A powerful tool for managing, organizing, and optimizing your Spotify playlists.

### Features

- **Duplicate Detection**: Find and remove duplicate tracks
- **Smart Organization**: Auto-organize by genre, mood, or decade
- **Playlist Merging**: Combine multiple playlists intelligently
- **Backup & Restore**: Create backups of your playlists
- **Collaborative Editing**: Share editing access with friends

### Core Implementation

```python
# playlist_manager/core.py
from spotify_scraper import SpotifyClient
from typing import List, Dict, Set, Tuple
import hashlib
from collections import defaultdict
import json
from datetime import datetime

class PlaylistManager:
    def __init__(self, cookies=None):
        self.client = SpotifyClient(cookies=cookies)
        self.processed_tracks = {}
    
    def find_duplicates(self, playlist_url: str) -> Dict[str, List[dict]]:
        """Find duplicate tracks in a playlist."""
        
        playlist = self.client.get_playlist_info(playlist_url)
        tracks = [item['track'] for item in playlist['tracks']['items'] if item['track']]
        
        # Group tracks by similarity
        duplicates = defaultdict(list)
        
        for track in tracks:
            # Create fingerprint for duplicate detection
            fingerprint = self._create_track_fingerprint(track)
            duplicates[fingerprint].append(track)
        
        # Return only groups with duplicates
        return {fp: tracks for fp, tracks in duplicates.items() if len(tracks) > 1}
    
    def _create_track_fingerprint(self, track: dict) -> str:
        """Create fingerprint for duplicate detection."""
        
        # Normalize track name and artist
        track_name = track.get('name', 'Unknown').lower().strip()
        artist_name = (track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown').lower().strip()
        
        # Remove common variations
        track_name = self._normalize_title(track_name)
        
        # Create hash
        fingerprint_str = f"{artist_name}:{track_name}"
        return hashlib.md5(fingerprint_str.encode()).hexdigest()
    
    def _normalize_title(self, title: str) -> str:
        """Normalize track title for comparison."""
        
        # Remove common suffixes and prefixes
        removals = [
            '(remastered)', '(remaster)', '(deluxe)', '(bonus track)',
            '(radio edit)', '(single version)', '(album version)',
            '- remastered', '- radio edit', '- single version'
        ]
        
        normalized = title.lower()
        for removal in removals:
            normalized = normalized.replace(removal, '')
        
        return normalized.strip()
    
    def organize_by_genre(self, playlist_url: str) -> Dict[str, List[dict]]:
        """Organize playlist tracks by genre."""
        
        playlist = self.client.get_playlist_info(playlist_url)
        tracks = [item['track'] for item in playlist['tracks']['items'] if item['track']]
        
        genre_groups = defaultdict(list)
        
        for track in tracks:
            try:
                # Get artist info for genre data
                artist_url = track['artists'][0]['external_urls']['spotify']
                artist = self.client.get_artist_info(artist_url)
                
                genres = artist.get('genres', ['Unknown'])
                primary_genre = self._get_primary_genre(genres)
                
                genre_groups[primary_genre].append(track)
                
            except Exception as e:
                print(f"Failed to get genre for {track.get('name', 'Unknown')}: {e}")
                genre_groups['Unknown'].append(track)
        
        return dict(genre_groups)
    
    def _get_primary_genre(self, genres: List[str]) -> str:
        """Determine primary genre from genre list."""
        
        # Genre priority mapping (more specific to general)
        genre_mapping = {
            'pop': ['pop', 'electropop', 'dance pop', 'indie pop'],
            'rock': ['rock', 'indie rock', 'alternative rock', 'classic rock'],
            'electronic': ['electronic', 'edm', 'house', 'techno', 'dubstep'],
            'hip-hop': ['hip hop', 'rap', 'trap', 'conscious hip hop'],
            'jazz': ['jazz', 'smooth jazz', 'bebop', 'swing'],
            'classical': ['classical', 'baroque', 'romantic', 'contemporary classical'],
            'country': ['country', 'contemporary country', 'country rock'],
            'r&b': ['r&b', 'soul', 'contemporary r&b', 'neo soul']
        }
        
        # Find best match
        for main_genre, sub_genres in genre_mapping.items():
            for genre in genres:
                if any(sub in genre.lower() for sub in sub_genres):
                    return main_genre.title()
        
        # Return first genre if no mapping found
        return genres[0].title() if genres else 'Unknown'
    
    def merge_playlists(self, playlist_urls: List[str], merge_strategy: str = 'union') -> List[dict]:
        """Merge multiple playlists using specified strategy."""
        
        all_tracks = []
        track_sets = []
        
        # Collect tracks from all playlists
        for url in playlist_urls:
            playlist = self.client.get_playlist_info(url)
            tracks = [item['track'] for item in playlist['tracks']['items'] if item['track']]
            
            all_tracks.extend(tracks)
            
            # Create set of track fingerprints for set operations
            track_fingerprints = {self._create_track_fingerprint(track) for track in tracks}
            track_sets.append(track_fingerprints)
        
        if merge_strategy == 'union':
            # Include all unique tracks
            seen_fingerprints = set()
            unique_tracks = []
            
            for track in all_tracks:
                fingerprint = self._create_track_fingerprint(track)
                if fingerprint not in seen_fingerprints:
                    unique_tracks.append(track)
                    seen_fingerprints.add(fingerprint)
            
            return unique_tracks
        
        elif merge_strategy == 'intersection':
            # Include only tracks present in all playlists
            if not track_sets:
                return []
            
            common_fingerprints = track_sets[0]
            for track_set in track_sets[1:]:
                common_fingerprints &= track_set
            
            # Return tracks with common fingerprints
            return [track for track in all_tracks 
                   if self._create_track_fingerprint(track) in common_fingerprints]
        
        else:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")
    
    def create_playlist_backup(self, playlist_url: str, backup_path: str = None) -> str:
        """Create a backup of playlist data."""
        
        playlist = self.client.get_playlist_info(playlist_url)
        
        backup_data = {
            'backup_date': datetime.now().isoformat(),
            'playlist_id': playlist['id'],
            'playlist_name': playlist.get('name', 'Unknown'),
            'description': playlist.get('description', ''),
            'total_tracks': playlist['tracks']['total'],
            'tracks': []
        }
        
        # Store detailed track information
        for item in playlist['tracks']['items']:
            if item['track']:
                track = item['track']
                track_data = {
                    'id': track['id'],
                    'name': track.get('name', 'Unknown'),
                    'artists': [{'name': artist.get('name', 'Unknown'), 'id': artist['id']} 
                              for artist in track['artists']],
                    'album': {
                        'name': track.get('album', {}).get('name', 'Unknown'),
                        'id': track['album']['id']
                    },
                    'duration_ms': track.get('duration_ms', 0),
                    'explicit': track.get('explicit', False),
                    'external_urls': track['external_urls'],
                    'added_at': item.get('added_at')
                }
                backup_data['tracks'].append(track_data)
        
        # Save backup
        if not backup_path:
            backup_path = f"playlist_backup_{playlist['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return backup_path
    
    def analyze_playlist_health(self, playlist_url: str) -> Dict[str, any]:
        """Analyze playlist for various issues and suggestions."""
        
        playlist = self.client.get_playlist_info(playlist_url)
        tracks = [item['track'] for item in playlist['tracks']['items'] if item['track']]
        
        analysis = {
            'total_tracks': len(tracks),
            'duplicates': len(self.find_duplicates(playlist_url)),
            'unavailable_tracks': 0,
            'genre_diversity': 0,
            'duration_analysis': {},
            'recommendations': []
        }
        
        # Check for unavailable tracks
        for track in tracks:
            if not track.get('preview_url') and track.get('is_local', False):
                analysis['unavailable_tracks'] += 1
        
        # Analyze duration distribution
        durations = [track.get('duration_ms', 0) for track in tracks]
        if durations:
            analysis['duration_analysis'] = {
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'total_duration': sum(durations)
            }
        
        # Genre diversity
        genre_groups = self.organize_by_genre(playlist_url)
        analysis['genre_diversity'] = len(genre_groups)
        
        # Generate recommendations
        recommendations = []
        
        if analysis['duplicates'] > 0:
            recommendations.append(f"Remove {analysis['duplicates']} duplicate tracks")
        
        if analysis['unavailable_tracks'] > 0:
            recommendations.append(f"Replace {analysis['unavailable_tracks']} unavailable tracks")
        
        if analysis['genre_diversity'] < 3:
            recommendations.append("Consider adding tracks from different genres for variety")
        
        if analysis['total_tracks'] > 100:
            recommendations.append("Consider splitting into smaller, themed playlists")
        
        analysis['recommendations'] = recommendations
        
        return analysis

# Example usage
def main():
    # Initialize with authentication cookies
    manager = PlaylistManager(cookies={'sp_dc': 'your_cookie_here'})
    
    playlist_url = "https://open.spotify.com/playlist/your_playlist_id"
    
    # Find duplicates
    duplicates = manager.find_duplicates(playlist_url)
    print(f"Found {len(duplicates)} groups of duplicates")
    
    # Organize by genre
    genres = manager.organize_by_genre(playlist_url)
    for genre, tracks in genres.items():
        print(f"{genre}: {len(tracks)} tracks")
    
    # Create backup
    backup_path = manager.create_playlist_backup(playlist_url)
    print(f"Backup saved to: {backup_path}")
    
    # Analyze health
    health = manager.analyze_playlist_health(playlist_url)
    print(f"Playlist health score: {health}")

if __name__ == "__main__":
    main()
```

---

## Music Discovery Bot

An intelligent bot that discovers new music based on your preferences and shares recommendations.

### Features

- **Smart Recommendations**: AI-powered music discovery
- **Social Integration**: Share finds on Discord/Slack
- **Trend Analysis**: Track emerging artists and songs
- **Personalized Alerts**: Get notified about new releases
- **Weekly Reports**: Curated music discovery reports

### Implementation

```python
# music_bot/discovery_bot.py
import asyncio
import discord
from discord.ext import commands, tasks
from spotify_scraper import SpotifyClient
import openai
from datetime import datetime, timedelta
import random

class MusicDiscoveryBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!music ', intents=intents)
        
        self.spotify = SpotifyClient()
        self.user_preferences = {}  # Store user music preferences
        
    async def on_ready(self):
        """Bot startup initialization."""
        print(f'{self.user} has connected to Discord!')
        self.weekly_discovery.start()  # Start scheduled tasks
    
    @commands.command(name='discover')
    async def discover_music(self, ctx, *, genre_or_artist=None):
        """Discover new music based on preferences or input."""
        
        user_id = ctx.author.id
        
        if genre_or_artist:
            # Discover based on user input
            recommendations = await self._discover_by_input(genre_or_artist)
        else:
            # Discover based on user's saved preferences
            if user_id in self.user_preferences:
                recommendations = await self._discover_by_preferences(user_id)
            else:
                recommendations = await self._discover_trending()
        
        if recommendations:
            embed = self._create_recommendation_embed(recommendations)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Sorry, I couldn't find any recommendations right now. Try again later!")
    
    async def _discover_by_input(self, input_text: str) -> List[dict]:
        """Discover music based on user input."""
        
        recommendations = []
        
        try:
            # Check if input is an artist name
            search_results = await self._search_spotify(input_text, 'artist')
            
            if search_results:
                artist_url = search_results[0]['external_urls']['spotify']
                artist = self.spotify.get_artist_info(artist_url)
                
                # Get related artists
                related = artist.get('related_artists', [])[:5]
                
                for related_artist in related:
                    # Get top tracks from related artist
                    top_tracks = await self._get_artist_top_tracks(related_artist['external_urls']['spotify'])
                    
                    if top_tracks:
                        recommendations.append({
                            'track': top_tracks[0],
                            'reason': f"Because you like {artist.get('name', 'Unknown')}",
                            'discovery_type': 'similar_artist'
                        })
            else:
                # Try as genre search
                recommendations = await self._discover_by_genre(input_text)
        
        except Exception as e:
            print(f"Discovery error: {e}")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    async def _discover_by_genre(self, genre: str) -> List[dict]:
        """Discover music by genre."""
        
        # In a real implementation, you'd use Spotify's recommendation API
        # For now, we'll simulate genre-based discovery
        
        genre_playlists = {
            'electronic': 'https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd',
            'pop': 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M',
            'rock': 'https://open.spotify.com/playlist/37i9dQZF1DXcF6B6QPhFDv',
            'hip-hop': 'https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd',
            'jazz': 'https://open.spotify.com/playlist/37i9dQZF1DXbITWG1ZJKYt'
        }
        
        playlist_url = None
        for key, url in genre_playlists.items():
            if key.lower() in genre.lower():
                playlist_url = url
                break
        
        if playlist_url:
            return await self._get_playlist_recommendations(playlist_url)
        
        return []
    
    async def _get_playlist_recommendations(self, playlist_url: str) -> List[dict]:
        """Get random tracks from a playlist."""
        
        try:
            playlist = self.spotify.get_playlist_info(playlist_url)
            tracks = [item['track'] for item in playlist['tracks']['items'] 
                     if item['track'] and item['track']['preview_url']]
            
            # Select random tracks
            selected = random.sample(tracks, min(5, len(tracks)))
            
            return [{
                'track': track,
                'reason': f"From {playlist.get('name', 'Unknown')} playlist",
                'discovery_type': 'playlist_random'
            } for track in selected]
        
        except Exception as e:
            print(f"Playlist recommendation error: {e}")
            return []
    
    @commands.command(name='save_preference')
    async def save_preference(self, ctx, *, artist_or_genre):
        """Save user's music preference."""
        
        user_id = ctx.author.id
        
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'favorite_artists': [],
                'favorite_genres': [],
                'discovered_tracks': []
            }
        
        # Try to determine if it's an artist or genre
        search_results = await self._search_spotify(artist_or_genre, 'artist')
        
        if search_results:
            # It's an artist
            artist_name = search_results[0]['name']
            if artist_name not in self.user_preferences[user_id]['favorite_artists']:
                self.user_preferences[user_id]['favorite_artists'].append(artist_name)
                await ctx.send(f"✅ Added {artist_name} to your favorite artists!")
            else:
                await ctx.send(f"You already have {artist_name} in your favorites.")
        else:
            # Treat as genre
            if artist_or_genre not in self.user_preferences[user_id]['favorite_genres']:
                self.user_preferences[user_id]['favorite_genres'].append(artist_or_genre)
                await ctx.send(f"✅ Added {artist_or_genre} to your favorite genres!")
            else:
                await ctx.send(f"You already have {artist_or_genre} in your favorite genres.")
    
    @commands.command(name='weekly_report')
    async def generate_weekly_report(self, ctx):
        """Generate a weekly music discovery report."""
        
        embed = discord.Embed(
            title="🎵 Weekly Music Discovery Report",
            description="Here's what's trending and what you might like!",
            color=0x1DB954  # Spotify green
        )
        
        # Trending tracks
        trending = await self._get_trending_tracks()
        if trending:
            trending_text = "\n".join([
                f"• {track.get('name', 'Unknown')} by {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}"
                for track in trending[:5]
            ])
            embed.add_field(
                name="🔥 Trending This Week",
                value=trending_text,
                inline=False
            )
        
        # Personalized recommendations
        user_id = ctx.author.id
        if user_id in self.user_preferences:
            recommendations = await self._discover_by_preferences(user_id)
            if recommendations:
                rec_text = "\n".join([
                    f"• {rec['track']['name']} by {rec['track']['artists'][0]['name']}"
                    for rec in recommendations[:3]
                ])
                embed.add_field(
                    name="🎯 For You",
                    value=rec_text,
                    inline=False
                )
        
        # New releases
        new_releases = await self._get_new_releases()
        if new_releases:
            releases_text = "\n".join([
                f"• {album.get('name', 'Unknown')} by {(album.get('artists', [{}])[0].get('name', 'Unknown') if album.get('artists') else 'Unknown')}"
                for album in new_releases[:3]
            ])
            embed.add_field(
                name="🆕 New Releases",
                value=releases_text,
                inline=False
            )
        
        embed.set_footer(text=f"Report generated on {datetime.now().strftime('%Y-%m-%d')}")
        await ctx.send(embed=embed)
    
    def _create_recommendation_embed(self, recommendations: List[dict]) -> discord.Embed:
        """Create Discord embed for recommendations."""
        
        embed = discord.Embed(
            title="🎵 Music Recommendations",
            description="Here are some tracks you might enjoy!",
            color=0x1DB954
        )
        
        for i, rec in enumerate(recommendations, 1):
            track = rec['track']
            reason = rec['reason']
            
            track_info = f"**{track.get('name', 'Unknown')}**\n"
            track_info += f"by {(track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown')}\n"
            track_info += f"*{reason}*"
            
            if track.get('preview_url'):
                track_info += f"\n[🎵 Preview]({track.get('preview_url', 'Not available')})"
            
            track_info += f"\n[🎧 Listen on Spotify]({track['external_urls']['spotify']})"
            
            embed.add_field(
                name=f"#{i}",
                value=track_info,
                inline=True
            )
        
        embed.set_footer(text="Use !music save_preference <artist/genre> to improve recommendations")
        return embed
    
    @tasks.loop(hours=168)  # Weekly (7 days * 24 hours)
    async def weekly_discovery(self):
        """Send weekly discovery reports to subscribed channels."""
        
        # In a real implementation, you'd have a database of subscribed channels
        # For now, this is a placeholder for the scheduled task
        print("Weekly discovery task executed")
    
    async def _search_spotify(self, query: str, search_type: str) -> List[dict]:
        """Search Spotify (simplified - in practice use Spotify Web API)."""
        # This is a simplified implementation
        # In practice, you'd use Spotify's search API
        return []
    
    async def _get_trending_tracks(self) -> List[dict]:
        """Get trending tracks."""
        # Get tracks from popular playlists
        try:
            # Global Top 50 playlist
            trending_playlist = "https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF"
            playlist = self.spotify.get_playlist_info(trending_playlist)
            
            tracks = [item['track'] for item in playlist['tracks']['items'][:10] 
                     if item['track']]
            return tracks
        except Exception:
            return []
    
    async def _get_new_releases(self) -> List[dict]:
        """Get new album releases."""
        # In practice, you'd use Spotify's new releases API
        # For now, return empty list
        return []

# Bot setup and run
def run_bot():
    bot = MusicDiscoveryBot()
    
    # Add more commands here
    @bot.command(name='help_music')
    async def help_music(ctx):
        """Show music bot help."""
        embed = discord.Embed(
            title="🎵 Music Discovery Bot Commands",
            color=0x1DB954
        )
        
        commands_help = [
            ("!music discover [artist/genre]", "Get music recommendations"),
            ("!music save_preference <artist/genre>", "Save your music preferences"),
            ("!music weekly_report", "Get weekly music discovery report"),
            ("!music help_music", "Show this help message")
        ]
        
        for command, description in commands_help:
            embed.add_field(
                name=command,
                value=description,
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    # Run the bot
    bot.run('YOUR_DISCORD_BOT_TOKEN')

if __name__ == "__main__":
    run_bot()
```

---

## Personal Music Archive

A comprehensive system for archiving and organizing your personal music collection with metadata from Spotify.

### Features

- **Automatic Metadata**: Enrich local files with Spotify metadata
- **Smart Organization**: Organize files by artist, album, genre
- **Duplicate Detection**: Find and manage duplicate files
- **Playlist Export**: Export Spotify playlists as M3U/PLS files
- **Missing Track Detection**: Find tracks missing from your archive

### Implementation

```python
# music_archive/archiver.py
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import eyed3
import hashlib
from spotify_scraper import SpotifyClient
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC

class MusicArchiver:
    def __init__(self, archive_path: str, cookies=None):
        self.archive_path = Path(archive_path)
        self.archive_path.mkdir(exist_ok=True)
        
        self.spotify = SpotifyClient(cookies=cookies)
        self.metadata_cache = {}
        self.load_cache()
    
    def load_cache(self):
        """Load metadata cache from file."""
        cache_file = self.archive_path / "metadata_cache.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                self.metadata_cache = json.load(f)
    
    def save_cache(self):
        """Save metadata cache to file."""
        cache_file = self.archive_path / "metadata_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(self.metadata_cache, f, indent=2)
    
    def archive_playlist(self, playlist_url: str, download_previews: bool = False) -> Dict[str, any]:
        """Archive a complete Spotify playlist."""
        
        playlist = self.spotify.get_playlist_info(playlist_url)
        playlist_name = self._sanitize_filename(playlist.get('name', 'Unknown'))
        playlist_path = self.archive_path / "Playlists" / playlist_name
        playlist_path.mkdir(parents=True, exist_ok=True)
        
        # Create playlist metadata file
        playlist_metadata = {
            'name': playlist.get('name', 'Unknown'),
            'description': playlist.get('description', ''),
            'owner': playlist.get('owner', {}).get('display_name', 'Unknown'),
            'total_tracks': playlist['tracks']['total'],
            'spotify_url': playlist_url,
            'archived_date': datetime.now().isoformat(),
            'tracks': []
        }
        
        # Process each track
        downloaded_count = 0
        for item in playlist['tracks']['items']:
            if not item['track']:
                continue
            
            track = item['track']
            track_result = self._archive_track(track, playlist_path, download_previews)
            
            if track_result:
                playlist_metadata['tracks'].append(track_result)
                if track_result.get('downloaded'):
                    downloaded_count += 1
        
        # Save playlist metadata
        metadata_file = playlist_path / "playlist_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(playlist_metadata, f, indent=2)
        
        # Create M3U playlist file
        self._create_m3u_playlist(playlist_metadata, playlist_path)
        
        return {
            'playlist_name': playlist.get('name', 'Unknown'),
            'total_tracks': len(playlist_metadata['tracks']),
            'downloaded_count': downloaded_count,
            'playlist_path': str(playlist_path)
        }
    
    def _archive_track(self, track: dict, base_path: Path, download_preview: bool = False) -> Optional[Dict[str, any]]:
        """Archive a single track with metadata."""
        
        track_id = track['id']
        track_metadata = {
            'id': track_id,
            'name': track.get('name', 'Unknown'),
            'artists': [artist.get('name', 'Unknown') for artist in track['artists']],
            'album': track.get('album', {}).get('name', 'Unknown'),
            'duration_ms': track.get('duration_ms', 0),
            'explicit': track.get('explicit', False),
            'spotify_url': track['external_urls']['spotify'],
            'preview_url': track.get('preview_url'),
            'downloaded': False,
            'file_path': None
        }
        
        # Try to download preview if requested and available
        if download_preview and track.get('preview_url'):
            try:
                # Create organized directory structure
                artist_name = self._sanitize_filename((track.get('artists', [{}])[0].get('name', 'Unknown') if track.get('artists') else 'Unknown'))
                album_name = self._sanitize_filename(track.get('album', {}).get('name', 'Unknown'))
                track_name = self._sanitize_filename(track.get('name', 'Unknown'))
                
                track_dir = base_path / artist_name / album_name
                track_dir.mkdir(parents=True, exist_ok=True)
                
                # Download preview
                preview_path = self.spotify.download_preview_mp3(
                    track['external_urls']['spotify'],
                    path=str(track_dir),
                    filename=f"{track_name}.mp3"
                )
                
                if preview_path:
                    # Enhance metadata
                    self._enhance_mp3_metadata(preview_path, track)
                    track_metadata['downloaded'] = True
                    track_metadata['file_path'] = str(Path(preview_path).relative_to(base_path))
                
            except Exception as e:
                print(f"Failed to download {track.get('name', 'Unknown')}: {e}")
        
        # Cache metadata
        self.metadata_cache[track_id] = track_metadata
        
        return track_metadata
    
    def _enhance_mp3_metadata(self, file_path: str, track_data: dict):
        """Enhance MP3 file with comprehensive metadata."""
        
        try:
            # Load the MP3 file
            audio_file = MP3(file_path, ID3=ID3)
            
            # Add ID3 tag if it doesn't exist
            if audio_file.tags is None:
                audio_file.add_tags()
            
            # Basic metadata
            audio_file.tags.add(TIT2(encoding=3, text=track_data.get('name', 'Unknown')))
            audio_file.tags.add(TPE1(encoding=3, text=track_data['artists'][0]['name']))
            audio_file.tags.add(TALB(encoding=3, text=track_data['album']['name']))
            
            # Release date
            if 'release_date' in track_data.get('album', {}):
                release_date = track_data['album'].get('release_date', '')[:4] if track_data['album'].get('release_date') else 'Unknown'  # Year only
                audio_file.tags.add(TDRC(encoding=3, text=release_date))
            
            # Genre (from artist info)
            try:
                artist_url = f"https://open.spotify.com/artist/{track_data['artists'][0]['id']}"
                artist = self.spotify.get_artist_info(artist_url)
                if artist.get('genres'):
                    audio_file.tags.add(TCON(encoding=3, text=artist['genres'][0]))
            except Exception:
                pass
            
            # Download and add album cover
            try:
                cover_url = track_data['album']['images'][0]['url']
                cover_data = self._download_cover_data(cover_url)
                if cover_data:
                    audio_file.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,  # Cover (front)
                            desc='Cover',
                            data=cover_data
                        )
                    )
            except Exception:
                pass
            
            # Save the tags
            audio_file.save()
            
        except Exception as e:
            print(f"Failed to enhance metadata for {file_path}: {e}")
    
    def _download_cover_data(self, cover_url: str) -> Optional[bytes]:
        """Download album cover as binary data."""
        try:
            import requests
            response = requests.get(cover_url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception:
            return None
    
    def _create_m3u_playlist(self, playlist_metadata: dict, playlist_path: Path):
        """Create M3U playlist file."""
        
        m3u_path = playlist_path / f"{playlist_metadata.get('name', 'Unknown')}.m3u"
        
        with open(m3u_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            f.write(f"# Playlist: {playlist_metadata.get('name', 'Unknown')}\n")
            f.write(f"# Created: {playlist_metadata['archived_date']}\n\n")
            
            for track in playlist_metadata['tracks']:
                if track.get('file_path'):
                    duration = track.get('duration_ms', 0) // 1000
                    artist = track['artists'][0] if track['artists'] else 'Unknown'
                    title = track.get('name', 'Unknown')
                    
                    f.write(f"#EXTINF:{duration},{artist} - {title}\n")
                    f.write(f"{track['file_path']}\n")
    
    def find_local_matches(self, music_directory: str) -> Dict[str, List[Tuple[str, dict]]]:
        """Find local music files that match Spotify tracks in cache."""
        
        music_path = Path(music_directory)
        local_files = list(music_path.rglob("*.mp3"))
        
        matches = {
            'exact_matches': [],
            'fuzzy_matches': [],
            'no_matches': []
        }
        
        for file_path in local_files:
            try:
                # Extract metadata from local file
                audio_file = eyed3.load(str(file_path))
                if not audio_file or not audio_file.tag:
                    matches['no_matches'].append((str(file_path), None))
                    continue
                
                local_metadata = {
                    'title': audio_file.tag.title,
                    'artist': audio_file.tag.artist,
                    'album': audio_file.tag.album
                }
                
                # Find matching Spotify tracks
                spotify_match = self._find_spotify_match(local_metadata)
                
                if spotify_match:
                    match_confidence = self._calculate_match_confidence(local_metadata, spotify_match)
                    
                    if match_confidence > 0.9:
                        matches['exact_matches'].append((str(file_path), spotify_match))
                    elif match_confidence > 0.7:
                        matches['fuzzy_matches'].append((str(file_path), spotify_match))
                    else:
                        matches['no_matches'].append((str(file_path), None))
                else:
                    matches['no_matches'].append((str(file_path), None))
            
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                matches['no_matches'].append((str(file_path), None))
        
        return matches
    
    def _find_spotify_match(self, local_metadata: dict) -> Optional[dict]:
        """Find matching Spotify track in cache."""
        
        if not all([local_metadata.get('title'), local_metadata.get('artist')]):
            return None
        
        title_lower = local_metadata['title'].lower()
        artist_lower = local_metadata['artist'].lower()
        
        best_match = None
        best_score = 0
        
        for track_id, spotify_track in self.metadata_cache.items():
            spotify_title = spotify_track.get('name', 'Unknown').lower()
            spotify_artist = spotify_track['artists'][0].lower()
            
            # Simple fuzzy matching
            title_score = self._fuzzy_match(title_lower, spotify_title)
            artist_score = self._fuzzy_match(artist_lower, spotify_artist)
            
            combined_score = (title_score + artist_score) / 2
            
            if combined_score > best_score:
                best_score = combined_score
                best_match = spotify_track
        
        return best_match if best_score > 0.6 else None
    
    def _fuzzy_match(self, str1: str, str2: str) -> float:
        """Calculate fuzzy match score between two strings."""
        # Simple implementation - could use libraries like fuzzywuzzy
        if str1 == str2:
            return 1.0
        
        # Check if one string contains the other
        if str1 in str2 or str2 in str1:
            return 0.8
        
        # Check common words
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _calculate_match_confidence(self, local: dict, spotify: dict) -> float:
        """Calculate confidence score for a match."""
        
        title_score = self._fuzzy_match(
            local.get('title', '').lower(),
            spotify['name'].lower()
        )
        
        artist_score = self._fuzzy_match(
            local.get('artist', '').lower(),
            spotify['artists'][0].lower()
        )
        
        album_score = 0.0
        if local.get('album') and spotify.get('album'):
            album_score = self._fuzzy_match(
                local['album'].lower(),
                spotify['album'].lower()
            )
        
        # Weighted average
        return (title_score * 0.5) + (artist_score * 0.4) + (album_score * 0.1)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()
    
    def generate_archive_report(self) -> dict:
        """Generate comprehensive archive report."""
        
        report = {
            'total_cached_tracks': len(self.metadata_cache),
            'total_playlists': 0,
            'total_downloaded_files': 0,
            'storage_stats': {},
            'top_artists': {},
            'top_genres': {},
            'recent_additions': []
        }
        
        # Count playlists
        playlists_dir = self.archive_path / "Playlists"
        if playlists_dir.exists():
            report['total_playlists'] = len(list(playlists_dir.iterdir()))
        
        # Analyze cached tracks
        artist_count = {}
        recent_tracks = []
        
        for track_id, track_data in self.metadata_cache.items():
            # Count artists
            for artist in track_data.get('artists', []):
                artist_count[artist] = artist_count.get(artist, 0) + 1
            
            # Track downloads
            if track_data.get('downloaded'):
                report['total_downloaded_files'] += 1
        
        # Top artists
        sorted_artists = sorted(artist_count.items(), key=lambda x: x[1], reverse=True)
        report['top_artists'] = dict(sorted_artists[:10])
        
        # Storage statistics
        total_size = 0
        for file_path in self.archive_path.rglob("*.mp3"):
            total_size += file_path.stat().st_size
        
        report['storage_stats'] = {
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'avg_file_size_mb': round(total_size / max(1, report['total_downloaded_files']) / (1024 * 1024), 2)
        }
        
        return report

# Example usage
def main():
    # Initialize archiver
    archiver = MusicArchiver("/path/to/music/archive", cookies={'sp_dc': 'your_cookie'})
    
    # Archive a playlist
    playlist_url = "https://open.spotify.com/playlist/your_playlist_id"
    result = archiver.archive_playlist(playlist_url, download_previews=True)
    print(f"Archived playlist: {result}")
    
    # Find local matches
    local_matches = archiver.find_local_matches("/path/to/local/music")
    print(f"Found {len(local_matches['exact_matches'])} exact matches")
    
    # Generate report
    report = archiver.generate_archive_report()
    print(f"Archive report: {report}")
    
    # Save cache
    archiver.save_cache()

if __name__ == "__main__":
    main()
```

---

## Integration Examples

### Flask Web Application

```python
# web_app/app.py
from flask import Flask, render_template, request, jsonify
from spotify_scraper import SpotifyClient
import json

app = Flask(__name__)
spotify = SpotifyClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/track/<track_id>')
def get_track(track_id):
    try:
        track_url = f"https://open.spotify.com/track/{track_id}"
        track = spotify.get_track_info(track_url)
        return jsonify(track_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/analyze', methods=['POST'])
def analyze_playlist():
    data = request.json
    playlist_url = data.get('playlist_url')
    
    if not playlist_url:
        return jsonify({'error': 'Playlist URL required'}), 400
    
    try:
        playlist = spotify.get_playlist_info(playlist_url)
        analysis = analyze_playlist_data(playlist)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def analyze_playlist_data(playlist):
    # Implementation of playlist analysis
    pass

if __name__ == '__main__':
    app.run(debug=True)
```

### Django REST API

```python
# django_api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from spotify_scraper import SpotifyClient
from .serializers import PlaylistAnalysisSerializer

class PlaylistAnalysisView(APIView):
    def __init__(self):
        super().__init__()
        self.spotify = SpotifyClient()
    
    def post(self, request):
        serializer = PlaylistAnalysisSerializer(data=request.data)
        
        if serializer.is_valid():
            playlist_url = serializer.validated_data['playlist_url']
            
            try:
                playlist = self.spotify.get_playlist_info(playlist_url)
                analysis = self.analyze_playlist(playlist)
                
                return Response(analysis, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def analyze_playlist(self, playlist):
        # Playlist analysis implementation
        pass
```

---

## Next Steps

These real-world projects demonstrate the versatility of SpotifyScraper:

1. 🎯 Choose a project that matches your interests
2. 🔧 Adapt the code to your specific needs
3. 🚀 Deploy using your preferred platform
4. 📊 Add monitoring and analytics
5. 🔄 Iterate based on user feedback

---

## Getting Help

For project-specific questions:

1. 📖 Review the [API documentation](../api/index.md)
2. 🔧 Check [configuration guide](../getting-started/configuration.md)
3. 💬 Ask on [GitHub Discussions](https://github.com/AliAkhtari78/SpotifyScraper/discussions)
4. 🐛 Report issues on [GitHub Issues](https://github.com/AliAkhtari78/SpotifyScraper/issues)