"""
Album command for SpotifyScraper CLI.

This module provides commands for extracting album information
from Spotify album URLs.
"""

import click
import sys
from typing import Optional
from pathlib import Path

from spotify_scraper.exceptions import SpotifyScraperError
from spotify_scraper.cli.utils import (
    format_output,
    print_error,
    print_success,
    print_info,
    create_client,
    save_to_file,
)


@click.command(name="album")
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
@click.pass_context
def album(
    ctx: click.Context,
    url: str,
    output: Optional[Path],
    pretty: bool,
    format: str,
    tracks_only: bool,
) -> None:
    """
    Extract album information from a Spotify album URL.
    
    This command extracts comprehensive album information including:
    - Album metadata (name, artists, release date, label)
    - Complete track listing with durations
    - Cover art URLs in various sizes
    - Album statistics (total duration, track count)
    
    Examples:
        # Basic album info
        spotify-scraper album https://open.spotify.com/album/4LH4d3cOWNNsVw41Gqt2kv
        
        # Save to file with pretty formatting
        spotify-scraper album -o album_info.json --pretty https://open.spotify.com/album/...
        
        # Display as table
        spotify-scraper album --format table https://open.spotify.com/album/...
        
        # Show only track listing
        spotify-scraper album --tracks-only https://open.spotify.com/album/...
    """
    try:
        # Create client from context
        client = create_client(ctx.obj)
        
        # Extract album information
        click.echo("Extracting album information...")
        album_info = client.get_album_info(url)
        
        # Check for errors in the response
        if "ERROR" in album_info:
            print_error(f"Failed to extract album: {album_info['ERROR']}")
            sys.exit(1)
        
        # Filter to tracks only if requested
        if tracks_only:
            output_data = {
                "album_name": album_info.get("name", "Unknown"),
                "album_id": album_info.get("id", ""),
                "tracks": album_info.get("tracks", {}).get("items", [])
            }
        else:
            output_data = album_info
        
        # Format and display output
        formatted_output = format_output(output_data, format, pretty)
        
        if output:
            # Save to file
            save_to_file(formatted_output, output, format)
            print_success(f"Album information saved to {output}")
        else:
            # Display to console
            click.echo(formatted_output)
        
        # Show summary
        if album_info.get("name") and not tracks_only:
            artist_names = ", ".join([
                artist.get("name", "Unknown") 
                for artist in album_info.get("artists", [])
            ])
            total_tracks = album_info.get("total_tracks", 0)
            duration_ms = album_info.get("duration_ms", 0)
            duration_min = duration_ms // 60000
            duration_sec = (duration_ms % 60000) // 1000
            
            click.echo("\n" + "─" * 50)
            click.echo(f"✓ Album: {album_info['name']}")
            click.echo(f"✓ Artist(s): {artist_names}")
            click.echo(f"✓ Release Date: {album_info.get('release_date', 'Unknown')}")
            click.echo(f"✓ Label: {album_info.get('label', 'Unknown')}")
            click.echo(f"✓ Total Tracks: {total_tracks}")
            click.echo(f"✓ Total Duration: {duration_min}:{duration_sec:02d}")
            
            # Show track count breakdown if available
            tracks = album_info.get("tracks", {}).get("items", [])
            if tracks:
                explicit_count = sum(1 for track in tracks if track.get("explicit", False))
                if explicit_count > 0:
                    click.echo(f"✓ Explicit Tracks: {explicit_count}/{len(tracks)}")
        
        elif tracks_only and output_data.get("tracks"):
            # Show track listing summary
            track_count = len(output_data["tracks"])
            print_info(f"Found {track_count} tracks in album '{output_data.get('album_name', 'Unknown')}'")
        
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