"""Extracted-color model for cover-art theming."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.base import ModelBase


@dataclass(frozen=True, slots=True)
class Colors(ModelBase):
    """Dominant colors Spotify extracts from an image, for UI theming.

    Each value is a ``#RRGGBB`` hex string. ``raw`` is the dominant color as
    extracted; ``dark`` and ``light`` are contrast-adjusted variants suitable as
    accents over dark and light backgrounds (Spotify uses them for the
    now-playing gradient). ``is_fallback`` is ``True`` when Spotify could not
    extract a color and returned its default instead.
    """

    raw: str
    dark: str
    light: str
    is_fallback: bool = False
