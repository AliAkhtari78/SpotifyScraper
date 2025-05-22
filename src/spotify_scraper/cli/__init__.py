"""
SpotifyScraper CLI module.

This module provides the command-line interface for SpotifyScraper,
allowing users to extract data from Spotify directly from the terminal.
"""

import click
import logging
import sys
from typing import Optional, Dict, Any
from pathlib import Path

from spotify_scraper import __version__
from spotify_scraper.cli.commands import track, album, artist, playlist, download

logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="SpotifyScraper")
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    default="INFO",
    help="Set the logging level",
)
@click.option(
    "--cookie-file",
    "-c",
    type=click.Path(exists=True, readable=True, path_type=Path),
    help="Path to cookies.txt file for authentication",
)
@click.option(
    "--browser",
    "-b",
    type=click.Choice(["requests", "selenium", "auto"], case_sensitive=False),
    default="requests",
    help="Browser backend to use",
)
@click.option(
    "--proxy",
    "-p",
    type=str,
    help="Proxy URL (e.g., http://user:pass@host:port)",
)
@click.pass_context
def cli(
    ctx: click.Context,
    log_level: str,
    cookie_file: Optional[Path],
    browser: str,
    proxy: Optional[str],
) -> None:
    """
    SpotifyScraper - Extract data from Spotify's web interface.
    
    A modern Python library and CLI for extracting track, album, artist,
    and playlist information from Spotify without using the official API.
    
    Examples:
        # Get track information
        spotify-scraper track https://open.spotify.com/track/...
        
        # Get album with pretty output
        spotify-scraper album --pretty https://open.spotify.com/album/...
        
        # Download track preview MP3
        spotify-scraper download track --with-cover https://open.spotify.com/track/...
        
        # Get playlist info and save to file
        spotify-scraper playlist -o playlist.json https://open.spotify.com/playlist/...
    """
    # Configure logging
    from spotify_scraper.utils.logger import configure_logging
    configure_logging(level=log_level.upper())
    
    # Store shared options in context
    ctx.ensure_object(dict)
    ctx.obj['cookie_file'] = str(cookie_file) if cookie_file else None
    ctx.obj['browser'] = browser
    ctx.obj['log_level'] = log_level
    
    # Parse proxy if provided
    if proxy:
        ctx.obj['proxy'] = {"http": proxy, "https": proxy}
    else:
        ctx.obj['proxy'] = None
    
    # Show help if no command is provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Add all command groups
cli.add_command(track.track)
cli.add_command(album.album)
cli.add_command(artist.artist)
cli.add_command(playlist.playlist)
cli.add_command(download.download)


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()