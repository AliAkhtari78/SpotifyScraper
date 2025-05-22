"""
Utility functions for the SpotifyScraper CLI.

This module provides common utilities used across different CLI commands,
including output formatting, error handling, and client creation.
"""

import json
import yaml
import sys
from typing import Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint

from spotify_scraper.client import SpotifyClient

# Initialize Rich console for beautiful output
console = Console()


def create_client(ctx_obj: Dict[str, Any]) -> SpotifyClient:
    """
    Create a SpotifyClient instance from CLI context.
    
    Args:
        ctx_obj: Context object containing CLI options
        
    Returns:
        Configured SpotifyClient instance
    """
    return SpotifyClient(
        cookie_file=ctx_obj.get('cookie_file'),
        browser_type=ctx_obj.get('browser', 'requests'),
        log_level=ctx_obj.get('log_level', 'INFO'),
        proxy=ctx_obj.get('proxy'),
    )


def format_output(
    data: Dict[str, Any],
    format: str = "json",
    pretty: bool = False,
) -> str:
    """
    Format data for output based on the specified format.
    
    Args:
        data: Data to format
        format: Output format (json, yaml, table)
        pretty: Whether to use pretty formatting
        
    Returns:
        Formatted string
    """
    if format == "json":
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
        else:
            return json.dumps(data, ensure_ascii=False)
    
    elif format == "yaml":
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=True)
    
    elif format == "table":
        return format_as_table(data)
    
    else:
        raise ValueError(f"Unknown format: {format}")


def format_as_table(data: Dict[str, Any]) -> str:
    """
    Format data as a rich table.
    
    Args:
        data: Data to format as table
        
    Returns:
        Formatted table string
    """
    # Create a table based on the data type
    entity_type = data.get("type", "unknown")
    
    if entity_type == "track":
        return format_track_table(data)
    elif entity_type == "album":
        return format_album_table(data)
    elif entity_type == "artist":
        return format_artist_table(data)
    elif entity_type == "playlist":
        return format_playlist_table(data)
    else:
        # Generic table for unknown types
        return format_generic_table(data)


def format_track_table(track: Dict[str, Any]) -> str:
    """Format track data as a table."""
    table = Table(title=f"Track: {track.get('name', 'Unknown')}", show_header=False)
    table.add_column("Property", style="cyan", width=20)
    table.add_column("Value", style="white")
    
    # Add track information
    table.add_row("ID", track.get("id", ""))
    table.add_row("Name", track.get("name", ""))
    table.add_row("Artists", ", ".join([a.get("name", "") for a in track.get("artists", [])]))
    table.add_row("Album", track.get("album", {}).get("name", ""))
    
    # Format duration
    duration_ms = track.get("duration_ms", 0)
    duration_min = duration_ms // 60000
    duration_sec = (duration_ms % 60000) // 1000
    table.add_row("Duration", f"{duration_min}:{duration_sec:02d}")
    
    table.add_row("Popularity", str(track.get("popularity", "")))
    table.add_row("Explicit", "Yes" if track.get("explicit") else "No")
    table.add_row("Preview Available", "Yes" if track.get("preview_url") else "No")
    
    # Convert to string
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def format_album_table(album: Dict[str, Any]) -> str:
    """Format album data as a table."""
    table = Table(title=f"Album: {album.get('name', 'Unknown')}", show_header=False)
    table.add_column("Property", style="cyan", width=20)
    table.add_column("Value", style="white")
    
    # Add album information
    table.add_row("ID", album.get("id", ""))
    table.add_row("Name", album.get("name", ""))
    table.add_row("Artists", ", ".join([a.get("name", "") for a in album.get("artists", [])]))
    table.add_row("Release Date", album.get("release_date", ""))
    table.add_row("Total Tracks", str(album.get("total_tracks", "")))
    table.add_row("Label", album.get("label", ""))
    table.add_row("Popularity", str(album.get("popularity", "")))
    
    # Convert to string
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def format_artist_table(artist: Dict[str, Any]) -> str:
    """Format artist data as a table."""
    table = Table(title=f"Artist: {artist.get('name', 'Unknown')}", show_header=False)
    table.add_column("Property", style="cyan", width=20)
    table.add_column("Value", style="white")
    
    # Add artist information
    table.add_row("ID", artist.get("id", ""))
    table.add_row("Name", artist.get("name", ""))
    table.add_row("Genres", ", ".join(artist.get("genres", [])))
    table.add_row("Popularity", str(artist.get("popularity", "")))
    table.add_row("Followers", f"{artist.get('followers', {}).get('total', 0):,}")
    table.add_row("Monthly Listeners", f"{artist.get('monthly_listeners', 0):,}")
    table.add_row("Verified", "Yes" if artist.get("verified") else "No")
    
    # Convert to string
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def format_playlist_table(playlist: Dict[str, Any]) -> str:
    """Format playlist data as a table."""
    table = Table(title=f"Playlist: {playlist.get('name', 'Unknown')}", show_header=False)
    table.add_column("Property", style="cyan", width=20)
    table.add_column("Value", style="white")
    
    # Add playlist information
    table.add_row("ID", playlist.get("id", ""))
    table.add_row("Name", playlist.get("name", ""))
    table.add_row("Owner", playlist.get("owner", {}).get("display_name", ""))
    table.add_row("Description", playlist.get("description", "")[:50] + "..." if len(playlist.get("description", "")) > 50 else playlist.get("description", ""))
    table.add_row("Total Tracks", str(playlist.get("tracks", {}).get("total", 0)))
    table.add_row("Followers", f"{playlist.get('followers', {}).get('total', 0):,}")
    table.add_row("Public", "Yes" if playlist.get("public") else "No")
    table.add_row("Collaborative", "Yes" if playlist.get("collaborative") else "No")
    
    # Convert to string
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def format_generic_table(data: Dict[str, Any]) -> str:
    """Format generic data as a table."""
    table = Table(title="Data", show_header=True)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, ensure_ascii=False)[:100] + "..."
        else:
            value_str = str(value)
        table.add_row(key, value_str)
    
    # Convert to string
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def save_to_file(
    content: str,
    filepath: Path,
    format: str = "json",
) -> None:
    """
    Save content to a file.
    
    Args:
        content: Content to save
        filepath: Path to save file
        format: File format
    """
    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Add appropriate extension if not present
    if not filepath.suffix:
        if format == "json":
            filepath = filepath.with_suffix(".json")
        elif format == "yaml":
            filepath = filepath.with_suffix(".yaml")
        elif format == "table":
            filepath = filepath.with_suffix(".txt")
    
    # Write content
    filepath.write_text(content, encoding="utf-8")


def print_error(message: str) -> None:
    """Print an error message with formatting."""
    console.print(f"[red]✗ Error:[/red] {message}")


def print_success(message: str) -> None:
    """Print a success message with formatting."""
    console.print(f"[green]✓ Success:[/green] {message}")


def print_warning(message: str) -> None:
    """Print a warning message with formatting."""
    console.print(f"[yellow]⚠ Warning:[/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message with formatting."""
    console.print(f"[blue]ℹ Info:[/blue] {message}")


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        message: Confirmation message
        default: Default value if user just presses enter
        
    Returns:
        User's choice
    """
    return click.confirm(message, default=default)