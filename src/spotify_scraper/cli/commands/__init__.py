"""
CLI commands for SpotifyScraper.

This package contains all the command modules for the SpotifyScraper CLI.
Each module corresponds to a specific entity type or operation.
"""

from spotify_scraper.cli.commands import album, artist, download, playlist, track

__all__ = ["track", "album", "artist", "playlist", "download"]
