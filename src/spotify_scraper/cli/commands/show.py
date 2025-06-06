"""CLI commands for show-related operations."""

import json
import logging
from pathlib import Path
from typing import Optional

import click

from spotify_scraper.cli.utils import format_duration, handle_errors, setup_client
from spotify_scraper.core.exceptions import URLError

logger = logging.getLogger(__name__)


@click.group(name="show")
def show_group():
    """Commands for working with podcast shows."""


@show_group.command()
@click.argument("url")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path for show data (JSON format)",
)
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
@click.option(
    "--episodes/--no-episodes",
    default=True,
    help="Include episode list in output",
)
@handle_errors
def info(url: str, output: Optional[str], pretty: bool, episodes: bool):
    """Get information about a podcast show.

    Example:
        spotify-scraper show info https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk
    """
    client = setup_client()

    try:
        click.echo(f"Fetching show information for: {url}")
        show_data = client.get_show_info(url)

        if show_data.get("ERROR"):
            raise URLError(f"Failed to fetch show: {show_data['ERROR']}")

        # Display basic info
        click.echo(f"\nShow: {show_data.get('name', 'Unknown')}")
        click.echo(f"Publisher: {show_data.get('publisher', 'Unknown')}")
        click.echo(f"Total Episodes: {show_data.get('total_episodes', 'Unknown')}")

        # Categories
        categories = show_data.get("categories", [])
        if categories:
            click.echo(f"Categories: {', '.join(categories)}")

        # Rating if available
        rating = show_data.get("rating", {})
        if rating and rating.get("average"):
            click.echo(f"Rating: {rating['average']:.1f}/5.0 ({rating.get('count', 0)} ratings)")

        click.echo(f"Explicit: {'Yes' if show_data.get('explicit') else 'No'}")

        # Episodes list
        if episodes and show_data.get("episodes"):
            episode_list = show_data["episodes"]
            click.echo(f"\nRecent Episodes ({len(episode_list)}):")
            for i, ep in enumerate(episode_list[:5], 1):
                duration = format_duration(ep.get("duration_ms", 0))
                click.echo(f"  {i}. {ep.get('name', 'Unknown')} ({duration})")
            if len(episode_list) > 5:
                click.echo(f"  ... and {len(episode_list) - 5} more")

        # Save to file if requested
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Optionally remove episodes from output
            save_data = show_data.copy()
            if not episodes:
                save_data.pop("episodes", None)

            with open(output_path, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(save_data, f, ensure_ascii=False)

            click.echo(f"\nShow data saved to: {output_path}")

    finally:
        client.close()


@show_group.command()
@click.argument("url")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="episodes.json",
    help="Output file for episodes list",
)
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
@click.option(
    "--limit",
    "-l",
    type=int,
    help="Limit number of episodes (default: all available)",
)
@handle_errors
def episodes(url: str, output: str, pretty: bool, limit: Optional[int]):
    """Get list of episodes from a show.

    Example:
        spotify-scraper show episodes \\
            https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk -o jre_episodes.json
    """
    client = setup_client()

    try:
        click.echo(f"Fetching episodes from show: {url}")
        show_data = client.get_show_info(url)

        if show_data.get("ERROR"):
            raise URLError(f"Failed to fetch show: {show_data['ERROR']}")

        episode_list = show_data.get("episodes", [])

        if limit:
            episode_list = episode_list[:limit]

        click.echo(f"\nFound {len(episode_list)} episodes")

        # Save episodes
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        episodes_data = {
            "show": {
                "name": show_data.get("name"),
                "id": show_data.get("id"),
                "publisher": show_data.get("publisher"),
            },
            "episode_count": len(episode_list),
            "episodes": episode_list,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(episodes_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(episodes_data, f, ensure_ascii=False)

        click.echo(f"Episodes list saved to: {output_path}")

    finally:
        client.close()


@show_group.command()
@click.argument("urls", nargs=-1, required=True)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="shows.json",
    help="Output file for batch results",
)
@click.option("--pretty", is_flag=True, help="Pretty print JSON output")
@click.option(
    "--no-episodes",
    is_flag=True,
    help="Exclude episode lists from output",
)
@handle_errors
def batch(urls: tuple, output: str, pretty: bool, no_episodes: bool):
    """Get information for multiple shows.

    Example:
        spotify-scraper show batch URL1 URL2 URL3 -o batch_shows.json
    """
    client = setup_client()

    try:
        results = []
        errors = []

        with click.progressbar(urls, label="Processing shows") as progress:
            for url in progress:
                try:
                    show_data = client.get_show_info(url)
                    if show_data.get("ERROR"):
                        errors.append({"url": url, "error": show_data["ERROR"]})
                    else:
                        if no_episodes:
                            show_data.pop("episodes", None)
                        results.append(show_data)
                except Exception as e:
                    errors.append({"url": url, "error": str(e)})

        # Save results
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            data = {"shows": results, "errors": errors}
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)

        click.echo(f"\n✓ Processed {len(results)} shows successfully")
        if errors:
            click.echo(f"✗ {len(errors)} shows failed")
        click.echo(f"Results saved to: {output_path}")

    finally:
        client.close()
