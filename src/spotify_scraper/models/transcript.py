"""Podcast episode transcript models."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.base import ModelBase


@dataclass(frozen=True, slots=True)
class TranscriptLine(ModelBase):
    """A single transcript line (cue) with its start offset."""

    start_ms: int
    text: str


@dataclass(frozen=True, slots=True)
class Transcript(ModelBase):
    """A podcast episode's read-along transcript.

    Episode-level ``language`` / ``provider`` / ``is_auto_generated`` are
    ``| None`` because their presence in the live envelope is unverified (see
    ``api/transcripts.py``).
    """

    lines: tuple[TranscriptLine, ...]
    language: str | None = None
    provider: str | None = None
    is_auto_generated: bool | None = None
