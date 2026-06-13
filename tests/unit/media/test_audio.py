"""Tests for preview-audio downloads and ID3 cover embedding."""

from __future__ import annotations

import builtins
import importlib
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from spotify_scraper.errors import MediaError
from spotify_scraper.http.transport import HttpxTransport
from spotify_scraper.media.audio import (
    _embed_cover,
    download_preview_sync,
)
from spotify_scraper.models.common import ArtistRef, Image, ShowRef
from spotify_scraper.models.episode import Episode
from spotify_scraper.models.track import Track

PREVIEW_URL = "https://p.scdn.co/mp3-preview/abc"
COVER_URL = "https://i.scdn.co/image/large"
# A minimal ID3v2 header + frame-ish payload; mutagen reads/writes it fine.
MP3_BYTES = b"ID3\x03\x00\x00\x00\x00\x00\x00" + b"\xff\xfb\x90\x00" + b"\x00" * 64
COVER_BYTES = b"\xff\xd8\xff\xe0" + b"FAKEJPEGCOVER" * 8


def make_track(
    *, name: str = "Never Gonna Give You Up", preview: str | None = PREVIEW_URL
) -> Track:
    return Track(
        id="4uLU6hMCjMI75M1A2tKUQC",
        uri="spotify:track:4uLU6hMCjMI75M1A2tKUQC",
        name=name,
        duration_ms=213_000,
        explicit=False,
        playable=True,
        preview_url=preview,
        artists=(ArtistRef(name="Rick Astley"),),
        images=(Image(url=COVER_URL, width=640, height=640),),
        release_date=None,
    )


def make_episode(*, preview: str | None = PREVIEW_URL) -> Episode:
    return Episode(
        id="epid",
        uri="spotify:episode:epid",
        name="Episode One",
        duration_ms=1_800_000,
        preview_url=preview,
        images=(Image(url=COVER_URL, width=640, height=640),),
        show=ShowRef(id="sid", uri="spotify:show:sid", name="My Podcast"),
    )


def read_id3(path: Path) -> Any:
    """Load ID3 tags as an untyped object (mutagen ships no type stubs)."""
    id3 = importlib.import_module("mutagen.id3")
    return id3.ID3(path)


@respx.mock
def test_download_preview_writes_mp3(tmp_path: Path) -> None:
    respx.get(PREVIEW_URL).mock(return_value=httpx.Response(200, content=MP3_BYTES))
    transport = HttpxTransport()

    path = download_preview_sync(transport, make_track(), tmp_path)
    transport.close()

    assert path == tmp_path / "Never Gonna Give You Up.mp3"
    assert path.read_bytes() == MP3_BYTES
    assert path.read_bytes().startswith(b"ID3")


@respx.mock
def test_download_preview_episode(tmp_path: Path) -> None:
    respx.get(PREVIEW_URL).mock(return_value=httpx.Response(200, content=MP3_BYTES))
    transport = HttpxTransport()

    path = download_preview_sync(transport, make_episode(), tmp_path)
    transport.close()

    assert path == tmp_path / "Episode One.mp3"
    assert path.read_bytes() == MP3_BYTES


@respx.mock
def test_download_preview_explicit_filename(tmp_path: Path) -> None:
    respx.get(PREVIEW_URL).mock(return_value=httpx.Response(200, content=MP3_BYTES))
    transport = HttpxTransport()

    path = download_preview_sync(transport, make_track(), tmp_path, filename="clip.mp3")
    transport.close()

    assert path == tmp_path / "clip.mp3"


def test_download_preview_no_preview_raises_naming_entity() -> None:
    transport = HttpxTransport()
    track = make_track(name="Silent Track", preview=None)
    with pytest.raises(MediaError, match="Silent Track"):
        download_preview_sync(transport, track, Path("."))
    transport.close()


@respx.mock
def test_download_preview_embed_cover_round_trip(tmp_path: Path) -> None:
    respx.get(PREVIEW_URL).mock(return_value=httpx.Response(200, content=MP3_BYTES))
    respx.get(COVER_URL).mock(return_value=httpx.Response(200, content=COVER_BYTES))
    transport = HttpxTransport()

    path = download_preview_sync(transport, make_track(), tmp_path, embed_cover=True)
    transport.close()

    tags = read_id3(path)
    apic_frames = tags.getall("APIC")
    assert len(apic_frames) == 1
    assert apic_frames[0].data == COVER_BYTES
    assert tags.getall("TIT2")[0].text[0] == "Never Gonna Give You Up"
    assert tags.getall("TPE1")[0].text[0] == "Rick Astley"


def test_embed_cover_round_trip_direct(tmp_path: Path) -> None:
    mp3 = tmp_path / "song.mp3"
    mp3.write_bytes(MP3_BYTES)

    _embed_cover(mp3, COVER_BYTES, title="A Title", artist="An Artist")

    tags = read_id3(mp3)
    assert tags.getall("APIC")[0].data == COVER_BYTES
    assert tags.getall("TIT2")[0].text[0] == "A Title"
    assert tags.getall("TPE1")[0].text[0] == "An Artist"


def test_embed_cover_no_artist_omits_tpe1(tmp_path: Path) -> None:
    mp3 = tmp_path / "song.mp3"
    mp3.write_bytes(MP3_BYTES)

    _embed_cover(mp3, COVER_BYTES, title="Solo", artist=None)

    tags = read_id3(mp3)
    assert not tags.getall("TPE1")
    assert tags.getall("TIT2")[0].text[0] == "Solo"


def test_embed_episode_artist_is_show_name(tmp_path: Path) -> None:
    from spotify_scraper.media.audio import _artist_for_tags

    episode = make_episode()
    assert _artist_for_tags(episode) == "My Podcast"

    mp3 = tmp_path / "ep.mp3"
    mp3.write_bytes(MP3_BYTES)
    _embed_cover(mp3, COVER_BYTES, title=episode.name, artist=_artist_for_tags(episode))

    assert read_id3(mp3).getall("TPE1")[0].text[0] == "My Podcast"


def test_embed_cover_missing_extra_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Drop any cached mutagen modules so import_module re-runs the loader,
    # which routes through the patched builtins.__import__.
    for name in list(sys.modules):
        if name == "mutagen" or name.startswith("mutagen."):
            monkeypatch.delitem(sys.modules, name)

    real_import: Callable[..., Any] = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "mutagen" or name.startswith("mutagen."):
            raise ImportError("No module named 'mutagen'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    mp3 = tmp_path / "song.mp3"
    mp3.write_bytes(MP3_BYTES)

    with pytest.raises(MediaError, match=r"spotifyscraper\[media\]"):
        _embed_cover(mp3, COVER_BYTES, title="T", artist="A")


@respx.mock
async def test_download_preview_async_embed_round_trip(tmp_path: Path) -> None:
    from spotify_scraper.http.transport import AsyncHttpxTransport
    from spotify_scraper.media.audio import download_preview_async

    respx.get(PREVIEW_URL).mock(return_value=httpx.Response(200, content=MP3_BYTES))
    respx.get(COVER_URL).mock(return_value=httpx.Response(200, content=COVER_BYTES))
    transport = AsyncHttpxTransport()

    path = await download_preview_async(transport, make_track(), tmp_path, embed_cover=True)
    await transport.aclose()

    assert read_id3(path).getall("APIC")[0].data == COVER_BYTES
