"""Live smoke tests for media downloads (network-dependent)."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper import AsyncSpotifyClient, SpotifyClient

TRACK_ID = "4uLU6hMCjMI75M1A2tKUQC"
JPEG_MAGIC = b"\xff\xd8\xff"


def read_id3(path: Path) -> Any:
    """Load ID3 tags as an untyped object (mutagen ships no type stubs)."""
    id3 = importlib.import_module("mutagen.id3")
    return id3.ID3(path)


@pytest.mark.live
def test_download_cover_and_preview_live(tmp_path: Path) -> None:
    with SpotifyClient() as client:
        track = client.get_track(TRACK_ID)
        cover = client.download_cover(track, tmp_path)
        preview = client.download_preview(track, tmp_path, embed_cover=True)

    cover_bytes = cover.read_bytes()
    assert cover.exists()
    assert cover_bytes.startswith(JPEG_MAGIC)

    audio = preview.read_bytes()
    assert preview.suffix == ".mp3"
    assert audio.startswith(b"ID3") or audio[:2] == b"\xff\xfb"

    apic = read_id3(preview).getall("APIC")
    assert apic
    assert apic[0].data.startswith(JPEG_MAGIC)


@pytest.mark.live
async def test_download_cover_and_preview_live_async(tmp_path: Path) -> None:
    async with AsyncSpotifyClient() as client:
        track = await client.get_track(TRACK_ID)
        cover = await client.download_cover(track, tmp_path)
        preview = await client.download_preview(track, tmp_path)

    assert cover.exists()
    assert cover.read_bytes().startswith(JPEG_MAGIC)

    audio = preview.read_bytes()
    assert preview.suffix == ".mp3"
    assert audio.startswith(b"ID3") or audio[:2] == b"\xff\xfb"
