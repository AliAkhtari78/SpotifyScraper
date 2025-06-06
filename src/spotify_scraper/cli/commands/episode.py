"""CLI commands for episode-related operations."""

import json
import logging
from pathlib import Path
from typing import Optional

import click

from spotify_scraper.cli.utils import format_duration, handle_errors, setup_client
from spotify_scraper.core.exceptions import URLError

logger = logging.getLogger(__name__)


@click.group(name="episode")
def episode_group():
    """Commands for working with podcast episodes."""


@episode_group.command()
@click.argument("url")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path for episode data (JSON format)",
)
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
@handle_errors
def info(url: str, output: Optional[str], pretty: bool):
    """Get information about a podcast episode.

    Example:
        spotify-scraper episode info https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G
    """
    client = setup_client()

    try:
        click.echo(f"Fetching episode information for: {url}")
        episode_data = client.get_episode_info(url)

        if episode_data.get("ERROR"):
            raise URLError(f"Failed to fetch episode: {episode_data['ERROR']}")

        # Display basic info
        click.echo(f"\nEpisode: {episode_data.get('name', 'Unknown')}")
        click.echo(f"Show: {episode_data.get('show', {}).get('name', 'Unknown')}")
        click.echo(f"Duration: {format_duration(episode_data.get('duration_ms', 0))}")
        click.echo(f"Release Date: {episode_data.get('release_date', 'Unknown')}")
        click.echo(f"Explicit: {'Yes' if episode_data.get('explicit') else 'No'}")

        if episode_data.get("has_video"):
            click.echo("Type: Video Podcast")
        else:
            click.echo("Type: Audio Podcast")

        if episode_data.get("audio_preview_url"):
            click.echo("\nPreview Available: Yes")
        else:
            click.echo("\nPreview Available: No")

        # Save to file if requested
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(episode_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(episode_data, f, ensure_ascii=False)

            click.echo(f"\nEpisode data saved to: {output_path}")

    finally:
        client.close()


@episode_group.command()
@click.argument("url")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=".",
    help="Output directory for preview file",
)
@click.option(
    "--filename",
    "-f",
    help="Custom filename for the preview (without extension)",
)
@handle_errors
def download(url: str, output: str, filename: Optional[str]):
    """Download episode preview audio.

    Downloads the preview clip (typically 1-2 minutes) of a podcast episode.
    Full episodes require Premium authentication.

    Example:
        spotify-scraper episode download \\
            https://open.spotify.com/episode/5Q2dkZHfnGb2Y4BzzoBu2G -o ~/podcasts/
    """
    client = setup_client()

    try:
        click.echo(f"Downloading episode preview from: {url}")

        # Create output directory
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        # Download preview
        file_path = client.download_episode_preview(url, path=str(output_path), filename=filename)

        if file_path:
            click.echo(f"\nPreview downloaded successfully to: {file_path}")
        else:
            click.echo("\nFailed to download episode preview")

    finally:
        client.close()


@episode_group.command()
@click.argument("urls", nargs=-1, required=True)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="episodes.json",
    help="Output file for batch results",
)
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
@handle_errors
def batch(urls: tuple, output: str, pretty: bool):
    """Get information for multiple episodes.

    Example:
        spotify-scraper episode batch URL1 URL2 URL3 -o batch_episodes.json
    """
    client = setup_client()

    try:
        results = []
        errors = []

        with click.progressbar(urls, label="Processing episodes") as progress:
            for url in progress:
                try:
                    episode_data = client.get_episode_info(url)
                    if episode_data.get("ERROR"):
                        errors.append({"url": url, "error": episode_data["ERROR"]})
                    else:
                        results.append(episode_data)
                except Exception as e:
                    errors.append({"url": url, "error": str(e)})

        # Save results
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            data = {"episodes": results, "errors": errors}
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)

        click.echo(f"\n✓ Processed {len(results)} episodes successfully")
        if errors:
            click.echo(f"✗ {len(errors)} episodes failed")
        click.echo(f"Results saved to: {output_path}")

    finally:
        client.close()
