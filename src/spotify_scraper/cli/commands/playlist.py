"""
Playlist command for SpotifyScraper CLI.

This module provides commands for extracting playlist information
from Spotify playlist URLs.
"""

import click
import sys
from typing import Optional
from pathlib import Path

from spotify_scraper.exceptions import SpotifyScraperError, AuthenticationError
from spotify_scraper.cli.utils import (
    format_output,
    print_error,
    print_success,
    print_info,
    print_warning,
    create_client,
    save_to_file,
)


@click.command(name="playlist")
@click.argument("url", type=str)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    help="Save output to file (JSON format)",
)
@click.option(
    "--pretty", "-p",
    is_flag=True,
    help="Pretty print the output",
)
@click.option(
    "--format", "-f",
    type=click.Choice(["json", "yaml", "table"], case_sensitive=False),
    default="json",
    help="Output format",
)
@click.option(
    "--tracks-only",
    is_flag=True,
    help="Only show track listing",
)
@click.option(
    "--limit", "-l",
    type=int,
    help="Limit number of tracks to retrieve (default: all)",
)
@click.pass_context
def playlist(
    ctx: click.Context,
    url: str,
    output: Optional[Path],
    pretty: bool,
    format: str,
    tracks_only: bool,
    limit: Optional[int],
) -> None:
    """
    Extract playlist information from a Spotify playlist URL.
    
    This command extracts comprehensive playlist information including:
    - Playlist metadata (name, description, owner)
    - Complete track listing with full details
    - Playlist statistics (duration, track count)
    - Collaborative and public status
    
    Examples:
        # Basic playlist info
        spotify-scraper playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
        
        # Save to file with pretty formatting
        spotify-scraper playlist -o playlist.json --pretty https://open.spotify.com/playlist/...
        
        # Display as table
        spotify-scraper playlist --format table https://open.spotify.com/playlist/...
        
        # Show only first 50 tracks
        spotify-scraper playlist --tracks-only --limit 50 https://open.spotify.com/playlist/...
        
        # Export playlist for backup
        spotify-scraper playlist -o my_playlist_backup.yaml --format yaml https://open.spotify.com/playlist/...
    """
    try:
        # Create client from context
        client = create_client(ctx.obj)
        
        # Extract playlist information
        click.echo("Extracting playlist information...")
        playlist_info = client.get_playlist_info(url)
        
        # Check for errors in the response
        if "ERROR" in playlist_info:
            error_msg = playlist_info['ERROR']
            if "private" in error_msg.lower() or "not found" in error_msg.lower():
                print_error(f"Failed to extract playlist: {error_msg}")
                print_warning("Private playlists require authentication. Use -c/--cookie-file option.")
            else:
                print_error(f"Failed to extract playlist: {error_msg}")
            sys.exit(1)
        
        # Apply track limit if specified
        if limit and playlist_info.get("tracks", {}).get("items"):
            playlist_info["tracks"]["items"] = playlist_info["tracks"]["items"][:limit]
            playlist_info["tracks"]["limited_to"] = limit
        
        # Filter to tracks only if requested
        if tracks_only:
            output_data = {
                "playlist_name": playlist_info.get("name", "Unknown"),
                "playlist_id": playlist_info.get("id", ""),
                "owner": playlist_info.get("owner", {}).get("display_name", "Unknown"),
                "total_tracks": playlist_info.get("tracks", {}).get("total", 0),
                "tracks": playlist_info.get("tracks", {}).get("items", [])
            }
            if limit:
                output_data["limited_to"] = limit
        else:
            output_data = playlist_info
        
        # Format and display output
        formatted_output = format_output(output_data, format, pretty)
        
        if output:
            # Save to file
            save_to_file(formatted_output, output, format)
            print_success(f"Playlist information saved to {output}")
        else:
            # Display to console
            click.echo(formatted_output)
        
        # Show summary
        if playlist_info.get("name") and not tracks_only:
            owner_name = playlist_info.get("owner", {}).get("display_name", "Unknown")
            total_tracks = playlist_info.get("tracks", {}).get("total", 0)
            duration_ms = playlist_info.get("duration_ms", 0)
            
            # Calculate duration
            if duration_ms:
                hours = duration_ms // 3600000
                minutes = (duration_ms % 3600000) // 60000
                seconds = (duration_ms % 60000) // 1000
                
                if hours > 0:
                    duration_str = f"{hours}h {minutes}m {seconds}s"
                else:
                    duration_str = f"{minutes}m {seconds}s"
            else:
                duration_str = "Unknown"
            
            click.echo("\n" + "─" * 50)
            click.echo(f"✓ Playlist: {playlist_info['name']}")
            click.echo(f"✓ Owner: {owner_name}")
            click.echo(f"✓ Total Tracks: {total_tracks}")
            if duration_ms:
                click.echo(f"✓ Total Duration: {duration_str}")
            
            # Show description if available
            description = playlist_info.get("description", "").strip()
            if description:
                # Truncate long descriptions
                if len(description) > 100:
                    description = description[:97] + "..."
                click.echo(f"✓ Description: {description}")
            
            # Show playlist attributes
            followers = playlist_info.get("followers", {}).get("total", 0)
            if followers:
                click.echo(f"✓ Followers: {followers:,}")
            
            if playlist_info.get("public") is not None:
                click.echo(f"✓ Public: {'Yes' if playlist_info.get('public') else 'No'}")
            if playlist_info.get("collaborative") is not None:
                click.echo(f"✓ Collaborative: {'Yes' if playlist_info.get('collaborative') else 'No'}")
                
            # Show track retrieval info
            retrieved_tracks = len(playlist_info.get("tracks", {}).get("items", []))
            if limit and retrieved_tracks == limit:
                print_info(f"Retrieved {retrieved_tracks} tracks (limited by --limit option)")
            elif retrieved_tracks < total_tracks:
                print_warning(f"Retrieved {retrieved_tracks} of {total_tracks} tracks")
                
        elif tracks_only and output_data.get("tracks"):
            # Show track listing summary
            track_count = len(output_data["tracks"])
            total = output_data.get("total_tracks", track_count)
            
            if limit and track_count == limit:
                print_info(f"Retrieved {track_count} tracks from '{output_data.get('playlist_name', 'Unknown')}' (limited to {limit})")
            else:
                print_info(f"Retrieved {track_count} of {total} tracks from '{output_data.get('playlist_name', 'Unknown')}'")
        
    except AuthenticationError as e:
        print_error(f"Authentication error: {e}")
        print_warning("This playlist may be private. Use -c/--cookie-file option to authenticate.")
        sys.exit(1)
    except SpotifyScraperError as e:
        print_error(f"Scraping error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Clean up
        if 'client' in locals():
            client.close()