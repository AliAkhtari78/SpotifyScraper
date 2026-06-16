"""Curated registry of Spotify editorial chart playlists.

Spotify exposes no dedicated anonymous "charts" endpoint; the editorial chart
playlists ("Top 50", "Today's Top Hits", …) are ordinary playlists. This module
maps a stable, human-friendly chart ``key`` to its playlist id so
:meth:`SpotifyClient.get_chart` / :meth:`list_charts` can reuse the existing
:meth:`SpotifyClient.get_playlist` ladder with no new persisted query.

Every id here is verified live against the pathfinder ``fetchPlaylist`` op.
Spotify's "Viral 50" charts were discontinued in 2026 and are deliberately
absent. Spotify rotates editorial inventory; treat a chart that has gone
:class:`~spotify_scraper.errors.NotFoundError` as retired, not as a bug.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChartDef:
    """A named Spotify chart and the playlist that backs it."""

    key: str
    name: str
    playlist_id: str


# Stable chart key -> definition. Keys are lowercase, hyphenated, and permanent.
CHARTS: dict[str, ChartDef] = {
    "top-50-global": ChartDef("top-50-global", "Top 50 - Global", "37i9dQZEVXbMDoHDwVN2tF"),
    "top-50-usa": ChartDef("top-50-usa", "Top 50 - USA", "37i9dQZEVXbLRQDuF5jeBp"),
    "top-songs-global": ChartDef(
        "top-songs-global", "Top Songs - Global", "37i9dQZEVXbNG2KDcFcKOF"
    ),
    "todays-top-hits": ChartDef("todays-top-hits", "Today's Top Hits", "37i9dQZF1DXcBWIGoYBM5M"),
}


def list_chart_defs() -> tuple[ChartDef, ...]:
    """Return every registered chart definition in registry order."""
    return tuple(CHARTS.values())


def chart_def(key: str) -> ChartDef:
    """Return the :class:`ChartDef` for ``key``.

    Raises:
        KeyError: If ``key`` is not a registered chart.
    """
    return CHARTS[key]
