"""Tests for cover-art helpers and transport-driven cover downloads."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
import respx

from spotify_scraper.errors import MediaError
from spotify_scraper.http.transport import HttpxTransport
from spotify_scraper.media.images import (
    download_cover_sync,
    extension_from_content_type,
    pick_image,
    safe_filename,
    safe_output_name,
)
from spotify_scraper.models.common import AlbumRef, Image
from spotify_scraper.models.track import Track

COVER_URL = "https://i.scdn.co/image/cover640"
COVER_BYTES = b"\xff\xd8\xff\xe0FAKEJPEGDATA"

IMAGES = (
    Image(url="https://i.scdn.co/image/small", width=64, height=64),
    Image(url="https://i.scdn.co/image/large", width=640, height=640),
    Image(url="https://i.scdn.co/image/mid", width=300, height=300),
)


def make_track(
    *,
    name: str = "Never Gonna Give You Up",
    images: tuple[Image, ...] = IMAGES,
    album: AlbumRef | None = None,
) -> Track:
    return Track(
        id="4uLU6hMCjMI75M1A2tKUQC",
        uri="spotify:track:4uLU6hMCjMI75M1A2tKUQC",
        name=name,
        duration_ms=213_000,
        explicit=False,
        playable=True,
        preview_url="https://p.scdn.co/mp3-preview/abc",
        artists=(),
        images=images,
        release_date=None,
        album=album,
    )


@pytest.mark.parametrize(
    ("size", "expected_url"),
    [
        ("largest", "https://i.scdn.co/image/large"),
        ("smallest", "https://i.scdn.co/image/small"),
    ],
)
def test_pick_image_selects_by_area(size: str, expected_url: str) -> None:
    assert pick_image(IMAGES, size).url == expected_url  # type: ignore[arg-type]


def test_pick_image_unknown_dimensions_sort_smallest() -> None:
    images = (
        Image(url="https://i.scdn.co/image/unknown"),
        Image(url="https://i.scdn.co/image/known", width=10, height=10),
    )
    assert pick_image(images, "smallest").url == "https://i.scdn.co/image/unknown"
    assert pick_image(images, "largest").url == "https://i.scdn.co/image/known"


def test_pick_image_empty_raises() -> None:
    with pytest.raises(MediaError):
        pick_image((), "largest")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('../../etc/passwd<>:"|?*', "etc passwd"),
        ("a/b\\c:d", "a b c d"),
        ("  spaced   out  name  ", "spaced out name"),
        ("with\nnewline\tand\ttabs", "with newline and tabs"),
        ("...", "untitled"),
        ("", "untitled"),
        ("Café Münchën ñ", "Café Münchën ñ"),
        ("song?.mp3", "song .mp3"),
    ],
)
def test_safe_filename_hostile_names(raw: str, expected: str) -> None:
    assert safe_filename(raw) == expected


def test_safe_filename_strips_path_separators() -> None:
    out = safe_filename("../../etc/passwd")
    assert "/" not in out
    assert "\\" not in out
    assert ".." not in out


def test_safe_filename_caps_length() -> None:
    out = safe_filename("x" * 500, max_length=150)
    assert len(out) == 150


@pytest.mark.parametrize(
    ("content_type", "expected"),
    [
        ("image/jpeg", "jpg"),
        ("image/jpg", "jpg"),
        ("image/png", "png"),
        ("image/webp", "webp"),
        ("image/gif", "gif"),
        ("image/jpeg; charset=binary", "jpg"),
        ("IMAGE/PNG", "png"),
        ("application/octet-stream", "jpg"),
        (None, "jpg"),
        ("", "jpg"),
    ],
)
def test_extension_from_content_type(content_type: str | None, expected: str) -> None:
    assert extension_from_content_type(content_type) == expected


@respx.mock
def test_download_cover_writes_file(tmp_path: Path) -> None:
    respx.get("https://i.scdn.co/image/large").mock(
        return_value=httpx.Response(
            200, content=COVER_BYTES, headers={"Content-Type": "image/jpeg"}
        )
    )
    transport = HttpxTransport()
    track = make_track()

    path = download_cover_sync(transport, track, tmp_path)
    transport.close()

    assert path == tmp_path / "Never Gonna Give You Up.jpg"
    assert path.read_bytes() == COVER_BYTES


@respx.mock
def test_download_cover_smallest_and_png_extension(tmp_path: Path) -> None:
    respx.get("https://i.scdn.co/image/small").mock(
        return_value=httpx.Response(200, content=COVER_BYTES, headers={"Content-Type": "image/png"})
    )
    transport = HttpxTransport()

    path = download_cover_sync(transport, make_track(), tmp_path, size="smallest")
    transport.close()

    assert path.suffix == ".png"
    assert path.read_bytes() == COVER_BYTES


@respx.mock
def test_download_cover_explicit_filename(tmp_path: Path) -> None:
    respx.get("https://i.scdn.co/image/large").mock(
        return_value=httpx.Response(
            200, content=COVER_BYTES, headers={"Content-Type": "image/jpeg"}
        )
    )
    transport = HttpxTransport()

    path = download_cover_sync(transport, make_track(), tmp_path, filename="custom.jpeg")
    transport.close()

    assert path == tmp_path / "custom.jpeg"


@respx.mock
def test_download_cover_hostile_name_stays_inside_dest(tmp_path: Path) -> None:
    respx.get("https://i.scdn.co/image/large").mock(
        return_value=httpx.Response(
            200, content=COVER_BYTES, headers={"Content-Type": "image/jpeg"}
        )
    )
    transport = HttpxTransport()
    track = make_track(name='../../etc/passwd<>:"|?*')

    path = download_cover_sync(transport, track, tmp_path)
    transport.close()

    assert path.parent == tmp_path
    assert path.exists()


@respx.mock
def test_download_cover_falls_back_to_album_images(tmp_path: Path) -> None:
    respx.get(COVER_URL).mock(
        return_value=httpx.Response(
            200, content=COVER_BYTES, headers={"Content-Type": "image/jpeg"}
        )
    )
    album = AlbumRef(
        id="alb",
        uri="spotify:album:alb",
        name="Album",
        images=(Image(url=COVER_URL, width=640, height=640),),
    )
    track = make_track(images=(), album=album)
    transport = HttpxTransport()

    path = download_cover_sync(transport, track, tmp_path)
    transport.close()

    assert path.read_bytes() == COVER_BYTES


def test_download_cover_no_images_raises_naming_entity() -> None:
    track = make_track(name="Lonely Track", images=())
    transport = HttpxTransport()
    with pytest.raises(MediaError, match="Lonely Track"):
        download_cover_sync(transport, track, Path("."))
    transport.close()


@respx.mock
async def test_download_cover_async_writes_file(tmp_path: Path) -> None:
    from spotify_scraper.http.transport import AsyncHttpxTransport
    from spotify_scraper.media.images import download_cover_async

    respx.get("https://i.scdn.co/image/large").mock(
        return_value=httpx.Response(
            200, content=COVER_BYTES, headers={"Content-Type": "image/jpeg"}
        )
    )
    transport = AsyncHttpxTransport()

    path = await download_cover_async(transport, make_track(), tmp_path)
    await transport.aclose()

    assert path == tmp_path / "Never Gonna Give You Up.jpg"
    assert path.read_bytes() == COVER_BYTES


def test_safe_output_name_strips_traversal() -> None:
    assert safe_output_name("../../etc/passwd") == "passwd"
    assert safe_output_name("/abs/cover.jpg") == "cover.jpg"
    assert safe_output_name("plain.png") == "plain.png"
    with pytest.raises(MediaError):
        safe_output_name("..")


@respx.mock
def test_download_cover_hostile_filename_stays_in_dest(tmp_path: Path) -> None:
    from spotify_scraper.models.common import Image
    from spotify_scraper.models.track import Track

    track = Track(
        id="x",
        uri="spotify:track:x",
        name="t",
        duration_ms=1,
        explicit=False,
        playable=True,
        preview_url=None,
        artists=(),
        images=(Image(url="https://img/c.jpg"),),
        release_date=None,
    )
    respx.get("https://img/c.jpg").mock(return_value=httpx.Response(200, content=b"\xff\xd8\xff"))
    transport = HttpxTransport()
    dest = tmp_path / "covers"
    path = download_cover_sync(transport, track, dest, filename="../../escape.jpg")
    transport.close()
    assert path.parent == dest  # did not escape the destination directory
    assert path.name == "escape.jpg"
