"""
Track command for SpotifyScraper CLI.

This module provides commands for extracting track information
and lyrics from Spotify track URLs.
"""

import click
import json
import sys
from typing import Optional, Dict, Any
from pathlib import Path

from spotify_scraper.client import SpotifyClient
from spotify_scraper.exceptions import SpotifyScraperError, AuthenticationRequiredError
from spotify_scraper.cli.utils import (
    format_output,
    print_error,
    print_success,
    create_client,
    save_to_file,
)


@click.command(name="track")
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
    "--with-lyrics", "-l",
    is_flag=True,
    help="Include lyrics (requires authentication)",
)
@click.option(
    "--format", "-f",
    type=click.Choice(["json", "yaml", "table"], case_sensitive=False),
    default="json",
    help="Output format",
)
@click.pass_context
def track(
    ctx: click.Context,
    url: str,
    output: Optional[Path],
    pretty: bool,
    with_lyrics: bool,
    format: str,
) -> None:
    """
    Extract track information from a Spotify track URL.
    
    This command extracts comprehensive track information including:
    - Track metadata (name, artists, album, duration)
    - Audio features (preview URL if available)
    - Cover art URLs in various sizes
    - Lyrics (if --with-lyrics flag is used and authenticated)
    
    Examples:
        # Basic track info
        spotify-scraper track https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp
        
        # Track info with lyrics (requires authentication)
        spotify-scraper -c cookies.txt track --with-lyrics https://open.spotify.com/track/...
        
        # Save to file with pretty formatting
        spotify-scraper track -o track_info.json --pretty https://open.spotify.com/track/...
        
        # Display as table
        spotify-scraper track --format table https://open.spotify.com/track/...
    """
    try:
        # Create client from context
        client = create_client(ctx.obj)
        
        # Extract track information
        if with_lyrics:
            click.echo("Extracting track information with lyrics...")
            try:
                track_info = client.get_track_info_with_lyrics(url)
            except AuthenticationRequiredError as e:
                print_error(f"Authentication required for lyrics: {e}")
                click.echo("Falling back to track info without lyrics...")
                track_info = client.get_track_info(url)
        else:
            click.echo("Extracting track information...")
            track_info = client.get_track_info(url)
        
        # Check for errors in the response
        if "ERROR" in track_info:
            print_error(f"Failed to extract track: {track_info['ERROR']}")
            sys.exit(1)
        
        # Format and display output
        formatted_output = format_output(track_info, format, pretty)
        
        if output:
            # Save to file
            save_to_file(formatted_output, output, format)
            print_success(f"Track information saved to {output}")
        else:
            # Display to console
            click.echo(formatted_output)
        
        # Show summary
        if track_info.get("name"):
            artist_names = ", ".join([
                artist.get("name", "Unknown") 
                for artist in track_info.get("artists", [])
            ])
            duration_ms = track_info.get("duration_ms", 0)
            duration_min = duration_ms // 60000
            duration_sec = (duration_ms % 60000) // 1000
            
            click.echo("\n" + "─" * 50)
            click.echo(f"✓ Track: {track_info['name']}")
            click.echo(f"✓ Artist(s): {artist_names}")
            click.echo(f"✓ Album: {track_info.get('album', {}).get('name', 'Unknown')}")
            click.echo(f"✓ Duration: {duration_min}:{duration_sec:02d}")
            if track_info.get("preview_url"):
                click.echo("✓ Preview available: Yes")
            if track_info.get("lyrics"):
                click.echo(f"✓ Lyrics: {len(track_info['lyrics'])} characters")
        
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