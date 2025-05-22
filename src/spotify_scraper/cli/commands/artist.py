"""
Artist command for SpotifyScraper CLI.

This module provides commands for extracting artist information
from Spotify artist URLs.
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


@click.command(name="artist")
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
    "--top-tracks-only",
    is_flag=True,
    help="Only show top tracks",
)
@click.option(
    "--discography-only",
    is_flag=True,
    help="Only show discography (albums, singles, compilations)",
)
@click.pass_context
def artist(
    ctx: click.Context,
    url: str,
    output: Optional[Path],
    pretty: bool,
    format: str,
    top_tracks_only: bool,
    discography_only: bool,
) -> None:
    """
    Extract artist information from a Spotify artist URL.
    
    This command extracts comprehensive artist information including:
    - Artist metadata (name, genres, popularity)
    - Biography and verified status
    - Top tracks in your market
    - Discography (albums, singles, compilations)
    - Related artists
    - Monthly listener statistics
    
    Examples:
        # Basic artist info
        spotify-scraper artist https://open.spotify.com/artist/0OdUWJ0sBjDrqHygGUXeCF
        
        # Save to file with pretty formatting
        spotify-scraper artist -o artist_info.json --pretty https://open.spotify.com/artist/...
        
        # Display as table
        spotify-scraper artist --format table https://open.spotify.com/artist/...
        
        # Show only top tracks
        spotify-scraper artist --top-tracks-only https://open.spotify.com/artist/...
        
        # Show only discography
        spotify-scraper artist --discography-only https://open.spotify.com/artist/...
    """
    try:
        # Create client from context
        client = create_client(ctx.obj)
        
        # Extract artist information
        click.echo("Extracting artist information...")
        artist_info = client.get_artist_info(url)
        
        # Check for errors in the response
        if "ERROR" in artist_info:
            print_error(f"Failed to extract artist: {artist_info['ERROR']}")
            sys.exit(1)
        
        # Filter based on options
        if top_tracks_only:
            output_data = {
                "artist_name": artist_info.get("name", "Unknown"),
                "artist_id": artist_info.get("id", ""),
                "top_tracks": artist_info.get("top_tracks", [])
            }
        elif discography_only:
            output_data = {
                "artist_name": artist_info.get("name", "Unknown"),
                "artist_id": artist_info.get("id", ""),
                "albums": artist_info.get("albums", []),
                "singles": artist_info.get("singles", []),
                "compilations": artist_info.get("compilations", []),
                "appears_on": artist_info.get("appears_on", [])
            }
        else:
            output_data = artist_info
        
        # Format and display output
        formatted_output = format_output(output_data, format, pretty)
        
        if output:
            # Save to file
            save_to_file(formatted_output, output, format)
            print_success(f"Artist information saved to {output}")
        else:
            # Display to console
            click.echo(formatted_output)
        
        # Show summary
        if artist_info.get("name") and not (top_tracks_only or discography_only):
            genres = ", ".join(artist_info.get("genres", [])) or "Not specified"
            followers = artist_info.get("followers", {}).get("total", 0)
            monthly_listeners = artist_info.get("monthly_listeners", 0)
            
            click.echo("\n" + "─" * 50)
            click.echo(f"✓ Artist: {artist_info['name']}")
            click.echo(f"✓ Genres: {genres}")
            click.echo(f"✓ Popularity: {artist_info.get('popularity', 0)}/100")
            click.echo(f"✓ Followers: {followers:,}")
            if monthly_listeners:
                click.echo(f"✓ Monthly Listeners: {monthly_listeners:,}")
            if artist_info.get("verified"):
                click.echo("✓ Verified Artist: Yes")
            
            # Show content counts
            top_tracks = artist_info.get("top_tracks", [])
            albums = artist_info.get("albums", [])
            singles = artist_info.get("singles", [])
            
            if top_tracks:
                click.echo(f"✓ Top Tracks Available: {len(top_tracks)}")
            if albums:
                click.echo(f"✓ Albums: {len(albums)}")
            if singles:
                click.echo(f"✓ Singles & EPs: {len(singles)}")
                
        elif top_tracks_only and output_data.get("top_tracks"):
            # Show top tracks summary
            track_count = len(output_data["top_tracks"])
            print_info(f"Found {track_count} top tracks for '{output_data.get('artist_name', 'Unknown')}'")
            
        elif discography_only:
            # Show discography summary
            total_releases = (
                len(output_data.get("albums", [])) +
                len(output_data.get("singles", [])) +
                len(output_data.get("compilations", []))
            )
            print_info(f"Found {total_releases} releases for '{output_data.get('artist_name', 'Unknown')}'")
        
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