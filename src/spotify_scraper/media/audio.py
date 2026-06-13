"""Preview-audio downloads and optional ID3 cover embedding.

Previews are small MP3s (~350 KB), so each is fetched fully and written with
:meth:`Path.write_bytes`; no streaming is needed. Cover embedding is optional
and only pulls in ``mutagen`` (the ``media`` extra) when requested.
"""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from spotify_scraper.errors import MediaError
from spotify_scraper.media.images import _pick_cover, safe_filename
from spotify_scraper.models.episode import Episode
from spotify_scraper.models.track import Track

if TYPE_CHECKING:
    from pathlib import Path

    from spotify_scraper.http.transport import AsyncTransport, Transport

Previewable = Track | Episode

_MEDIA_HINT = (
    "Embedding cover art requires mutagen. Install it with 'pip install spotifyscraper[media]'."
)


def _preview_url(entity: Previewable) -> str:
    """Return the entity's preview URL or raise if it has none."""
    url = entity.preview_url
    if not url:
        raise MediaError(
            f"No preview audio is available for {entity.name!r}; "
            "Spotify does not expose a preview clip for this item."
        )
    return url


def _artist_for_tags(entity: Previewable) -> str | None:
    """Pick the artist tag value: first track artist or the show name."""
    if isinstance(entity, Track):
        return entity.artists[0].name if entity.artists else None
    show = entity.show
    return show.name if show is not None else None


def _preview_path(entity: Previewable, dest: Path, filename: str | None) -> Path:
    """Resolve the destination MP3 path, creating ``dest`` if missing."""
    out_name = filename if filename is not None else f"{safe_filename(entity.name)}.mp3"
    dest.mkdir(parents=True, exist_ok=True)
    return dest / out_name


def _embed_cover(mp3_path: Path, cover_bytes: bytes, *, title: str, artist: str | None) -> None:
    """Embed ``cover_bytes`` as an ID3 APIC frame plus basic tags.

    Args:
        mp3_path: Path to the MP3 to tag in place.
        cover_bytes: Raw JPEG cover bytes.
        title: Value for the TIT2 (title) frame.
        artist: Value for the TPE1 (artist) frame, when known.

    Raises:
        MediaError: If mutagen (the ``media`` extra) is not installed.
    """
    try:
        id3 = importlib.import_module("mutagen.id3")
    except ImportError as exc:
        raise MediaError(_MEDIA_HINT) from exc

    try:
        tags = id3.ID3(mp3_path)
    except id3.ID3NoHeaderError:
        tags = id3.ID3()
    tags.setall("TIT2", [id3.TIT2(encoding=3, text=[title])])
    if artist:
        tags.setall("TPE1", [id3.TPE1(encoding=3, text=[artist])])
    tags.setall(
        "APIC",
        [id3.APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover_bytes)],
    )
    tags.save(mp3_path)


def download_preview_sync(
    transport: Transport,
    entity: Previewable,
    dest: Path,
    *,
    filename: str | None = None,
    embed_cover: bool = False,
) -> Path:
    """Download a track or episode preview MP3 and return the written path.

    Args:
        transport: HTTP transport to fetch with.
        entity: A :class:`Track` or :class:`Episode` with a ``preview_url``.
        dest: Destination directory (created if missing).
        filename: Explicit filename; defaults to ``<name>.mp3``.
        embed_cover: When ``True``, embed the entity's cover art and basic
            tags via mutagen (the ``media`` extra).

    Returns:
        The path of the written MP3.

    Raises:
        MediaError: If no preview exists, or ``embed_cover`` is requested
            without mutagen installed.
    """
    url = _preview_url(entity)
    cover_bytes = _fetch_cover_sync(transport, entity) if embed_cover else None
    path = _preview_path(entity, dest, filename)
    path.write_bytes(transport.get(url).content)
    if cover_bytes is not None:
        _embed_cover(path, cover_bytes, title=entity.name, artist=_artist_for_tags(entity))
    return path


async def download_preview_async(
    transport: AsyncTransport,
    entity: Previewable,
    dest: Path,
    *,
    filename: str | None = None,
    embed_cover: bool = False,
) -> Path:
    """Async mirror of :func:`download_preview_sync`."""
    url = _preview_url(entity)
    cover_bytes = await _fetch_cover_async(transport, entity) if embed_cover else None
    path = _preview_path(entity, dest, filename)
    response = await transport.get(url)
    path.write_bytes(response.content)
    if cover_bytes is not None:
        _embed_cover(path, cover_bytes, title=entity.name, artist=_artist_for_tags(entity))
    return path


def _fetch_cover_sync(transport: Transport, entity: Previewable) -> bytes:
    """Fetch the largest cover image's bytes for embedding."""
    image = _pick_cover(entity, "largest")
    return transport.get(image.url).content


async def _fetch_cover_async(transport: AsyncTransport, entity: Previewable) -> bytes:
    """Async mirror of :func:`_fetch_cover_sync`."""
    image = _pick_cover(entity, "largest")
    response = await transport.get(image.url)
    return response.content
