"""
Download command for SpotifyScraper CLI.

This module provides commands for downloading media content
(cover images and preview MP3s) from Spotify URLs.
"""

import click
import sys
from typing import Optional
from pathlib import Path

from spotify_scraper.exceptions import SpotifyScraperError, MediaError
from spotify_scraper.cli.utils import (
    print_error,
    print_success,
    print_info,
    print_warning,
    create_client,
    confirm_action,
)


@click.group(name="download")
def download():
    """Download media content from Spotify URLs."""
    pass


@download.command(name="cover")
@click.argument("url", type=str)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    help="Output directory (default: current directory)",
)
@click.option(
    "--filename", "-f",
    type=str,
    help="Custom filename (without extension)",
)
@click.option(
    "--quality", "-q",
    type=click.Choice(["high", "medium", "low"], case_sensitive=False),
    default="high",
    help="Image quality preference",
)
@click.option(
    "--force", "-F",
    is_flag=True,
    help="Overwrite existing files without asking",
)
@click.pass_context
def cover(
    ctx: click.Context,
    url: str,
    output: Optional[Path],
    filename: Optional[str],
    quality: str,
    force: bool,
) -> None:
    """
    Download cover image from a Spotify URL.
    
    Supports track, album, playlist, and artist URLs. The image will be
    downloaded in the highest available quality by default.
    
    Examples:
        # Download track cover to current directory
        spotify-scraper download cover https://open.spotify.com/track/...
        
        # Download album cover with custom filename
        spotify-scraper download cover -f "my_album_cover" https://open.spotify.com/album/...
        
        # Download to specific directory
        spotify-scraper download cover -o ~/Music/Covers https://open.spotify.com/album/...
        
        # Download in medium quality
        spotify-scraper download cover --quality medium https://open.spotify.com/playlist/...
    """
    try:
        # Create client from context
        client = create_client(ctx.obj)
        
        # Set output directory
        output_dir = output or Path.cwd()
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Map quality to preference list
        quality_map = {
            "high": ["extralarge", "large", "medium", "small"],
            "medium": ["large", "medium", "small", "extralarge"],
            "low": ["small", "medium", "large", "extralarge"]
        }
        quality_preference = quality_map.get(quality, quality_map["high"])
        
        click.echo(f"Downloading cover image from: {url}")
        click.echo(f"Quality preference: {quality}")
        
        # Download cover
        downloaded_path = client.download_cover(
            url=url,
            path=str(output_dir),
            filename=filename,
            quality_preference=quality_preference
        )
        
        if downloaded_path:
            # Check if file already exists and handle accordingly
            downloaded_file = Path(downloaded_path)
            if downloaded_file.exists() and not force:
                if not confirm_action(f"File {downloaded_file.name} already exists. Overwrite?"):
                    print_warning("Download cancelled")
                    return
            
            print_success(f"Cover image saved to: {downloaded_path}")
            
            # Show file info
            file_size = downloaded_file.stat().st_size
            size_mb = file_size / (1024 * 1024)
            print_info(f"File size: {size_mb:.2f} MB")
        else:
            print_error("Failed to download cover image")
            sys.exit(1)
            
    except MediaError as e:
        print_error(f"Media error: {e}")
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


@download.command(name="track")
@click.argument("url", type=str)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    help="Output directory (default: current directory)",
)
@click.option(
    "--with-cover", "-c",
    is_flag=True,
    help="Embed cover art in the MP3 file",
)
@click.option(
    "--force", "-F",
    is_flag=True,
    help="Overwrite existing files without asking",
)
@click.pass_context
def track(
    ctx: click.Context,
    url: str,
    output: Optional[Path],
    with_cover: bool,
    force: bool,
) -> None:
    """
    Download track preview MP3 from a Spotify track URL.
    
    Downloads the 30-second preview MP3 if available. Optionally embeds
    cover art and metadata into the MP3 file.
    
    Examples:
        # Download track preview to current directory
        spotify-scraper download track https://open.spotify.com/track/...
        
        # Download with embedded cover art
        spotify-scraper download track --with-cover https://open.spotify.com/track/...
        
        # Download to specific directory
        spotify-scraper download track -o ~/Music/Previews https://open.spotify.com/track/...
        
        # Force overwrite existing files
        spotify-scraper download track --force https://open.spotify.com/track/...
    """
    try:
        # Create client from context
        client = create_client(ctx.obj)
        
        # Set output directory
        output_dir = output or Path.cwd()
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        
        click.echo(f"Downloading track preview from: {url}")
        if with_cover:
            click.echo("Will embed cover art in MP3")
        
        # First check if preview is available
        print_info("Checking track information...")
        track_info = client.get_track_info(url)
        
        if "ERROR" in track_info:
            print_error(f"Failed to get track info: {track_info['ERROR']}")
            sys.exit(1)
        
        if not track_info.get("preview_url"):
            print_error("No preview available for this track")
            print_info("Not all tracks have preview MP3s available")
            sys.exit(1)
        
        # Download preview MP3
        downloaded_path = client.download_preview_mp3(
            url=url,
            path=str(output_dir),
            with_cover=with_cover
        )
        
        if downloaded_path:
            # Check if file already exists and handle accordingly
            downloaded_file = Path(downloaded_path)
            if downloaded_file.exists() and not force:
                if not confirm_action(f"File {downloaded_file.name} already exists. Overwrite?"):
                    print_warning("Download cancelled")
                    return
            
            print_success(f"Track preview saved to: {downloaded_path}")
            
            # Show file info
            file_size = downloaded_file.stat().st_size
            size_mb = file_size / (1024 * 1024)
            print_info(f"File size: {size_mb:.2f} MB")
            
            # Show track info
            artist_names = ", ".join([
                artist.get("name", "Unknown") 
                for artist in track_info.get("artists", [])
            ])
            print_info(f"Track: {track_info.get('name', 'Unknown')} by {artist_names}")
            print_info("Duration: 30 seconds (preview)")
            
            if with_cover:
                print_info("Cover art: Embedded")
        else:
            print_error("Failed to download track preview")
            sys.exit(1)
            
    except MediaError as e:
        print_error(f"Media error: {e}")
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


@download.command(name="batch")
@click.argument("file", type=click.Path(exists=True, readable=True, path_type=Path))
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    help="Output directory (default: current directory)",
)
@click.option(
    "--type", "-t",
    type=click.Choice(["cover", "track", "both"], case_sensitive=False),
    default="both",
    help="What to download",
)
@click.option(
    "--with-cover", "-c",
    is_flag=True,
    help="Embed cover art in MP3 files (for track downloads)",
)
@click.option(
    "--force", "-F",
    is_flag=True,
    help="Overwrite existing files without asking",
)
@click.option(
    "--continue-on-error", "-C",
    is_flag=True,
    help="Continue downloading even if some URLs fail",
)
@click.pass_context
def batch(
    ctx: click.Context,
    file: Path,
    output: Optional[Path],
    type: str,
    with_cover: bool,
    force: bool,
    continue_on_error: bool,
) -> None:
    """
    Download media from multiple URLs listed in a file.
    
    The file should contain one Spotify URL per line. Empty lines and
    lines starting with # are ignored.
    
    Examples:
        # Download covers and tracks from URLs in file
        spotify-scraper download batch urls.txt
        
        # Download only covers to specific directory
        spotify-scraper download batch --type cover -o ~/Music/Covers urls.txt
        
        # Download tracks with covers embedded, continue on errors
        spotify-scraper download batch --type track --with-cover -C urls.txt
    """
    try:
        # Create client from context
        client = create_client(ctx.obj)
        
        # Set output directory
        output_dir = output or Path.cwd()
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Read URLs from file
        urls = []
        for line in file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
        
        if not urls:
            print_error("No URLs found in file")
            sys.exit(1)
        
        print_info(f"Found {len(urls)} URLs to process")
        print_info(f"Download type: {type}")
        
        # Track results
        successful = 0
        failed = 0
        
        # Process each URL
        for i, url in enumerate(urls, 1):
            click.echo(f"\n[{i}/{len(urls)}] Processing: {url}")
            
            try:
                if type in ["cover", "both"]:
                    # Download cover
                    click.echo("  Downloading cover...")
                    cover_path = client.download_cover(
                        url=url,
                        path=str(output_dir)
                    )
                    if cover_path:
                        print_success(f"  Cover saved: {Path(cover_path).name}")
                    else:
                        print_warning("  No cover available")
                
                if type in ["track", "both"]:
                    # Check if it's a track URL
                    from spotify_scraper.utils.url import get_url_type
                    if get_url_type(url) == "track":
                        click.echo("  Downloading track preview...")
                        track_path = client.download_preview_mp3(
                            url=url,
                            path=str(output_dir),
                            with_cover=with_cover
                        )
                        if track_path:
                            print_success(f"  Track saved: {Path(track_path).name}")
                        else:
                            print_warning("  No preview available")
                    else:
                        print_info("  Skipping track download (not a track URL)")
                
                successful += 1
                
            except Exception as e:
                failed += 1
                print_error(f"  Failed: {e}")
                if not continue_on_error:
                    print_error("Stopping batch download due to error")
                    break
        
        # Show summary
        click.echo("\n" + "─" * 50)
        print_info(f"Batch download complete")
        print_success(f"Successful: {successful}")
        if failed > 0:
            print_error(f"Failed: {failed}")
        
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        # Clean up
        if 'client' in locals():
            client.close()