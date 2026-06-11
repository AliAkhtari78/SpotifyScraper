"""Track lyrics models."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.base import ModelBase


@dataclass(frozen=True, slots=True)
class LyricsLine(ModelBase):
    """A single lyrics line with its start offset."""

    start_ms: int
    text: str


@dataclass(frozen=True, slots=True)
class Lyrics(ModelBase):
    """Lyrics for a track.

    ``sync_type`` is ``"LINE_SYNCED"`` when ``start_ms`` offsets are
    meaningful, otherwise ``"UNSYNCED"``.
    """

    lines: tuple[LyricsLine, ...]
    sync_type: str = "UNSYNCED"
    provider: str | None = None
    language: str | None = None
