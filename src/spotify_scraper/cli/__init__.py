"""Command-line interface for SpotifyScraper.

Exposes the Typer ``app`` used by the ``spotifyscraper`` entry point. Importing
this module without the ``cli`` extra installed raises a helpful
:class:`ImportError` instead of an opaque ``ModuleNotFoundError`` on ``typer``.
"""

from __future__ import annotations

try:
    from spotify_scraper.cli.main import app
except ImportError as exc:  # pragma: no cover - exercised only without the extra
    raise ImportError('The CLI requires the cli extra: pip install "spotifyscraper[cli]"') from exc

__all__ = ["app"]
