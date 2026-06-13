"""Cover-art helpers and transport-driven cover downloads.

Pure helpers (``pick_image``, ``safe_filename``, ``extension_from_content_type``)
carry no I/O. The download functions take a transport so the client can reuse
its configured HTTP stack.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable

from spotify_scraper.errors import MediaError
from spotify_scraper.models.common import Image

if TYPE_CHECKING:
    from collections.abc import Sequence

    from spotify_scraper.http.transport import AsyncTransport, Transport

ImageSize = Literal["largest", "smallest"]

_CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}

_ILLEGAL_CHARS = re.compile(r'[\x00-\x1f<>:"/\\|?*]')
_WHITESPACE = re.compile(r"\s+")


@runtime_checkable
class HasImagesAndName(Protocol):
    """Structural type for any entity carrying a name and cover images."""

    @property
    def name(self) -> str:
        """Display name of the entity."""
        ...

    @property
    def images(self) -> tuple[Image, ...]:
        """Cover images, ordered however the source provided them."""
        ...


def _image_area(image: Image) -> int:
    """Pixel area used to rank images; unknown dimensions sort smallest."""
    if image.width is None or image.height is None:
        return 0
    return image.width * image.height


def pick_image(images: Sequence[Image], size: ImageSize) -> Image:
    """Return the largest or smallest image by pixel area.

    Args:
        images: Candidate images; must be non-empty.
        size: ``"largest"`` or ``"smallest"``.

    Returns:
        The selected :class:`Image`.

    Raises:
        MediaError: If ``images`` is empty.
    """
    if not images:
        raise MediaError("Entity has no images to download.")
    if size == "smallest":
        return min(images, key=_image_area)
    return max(images, key=_image_area)


def _entity_images(entity: HasImagesAndName) -> tuple[Image, ...]:
    """Return the entity's images, falling back to its album's when empty."""
    if entity.images:
        return entity.images
    album = getattr(entity, "album", None)
    album_images = getattr(album, "images", None)
    if album_images:
        return tuple(album_images)
    return ()


def safe_filename(name: str, max_length: int = 150) -> str:
    """Sanitize ``name`` into a single safe path component.

    Strips control characters and path separators, collapses whitespace,
    preserves Unicode word characters, and caps the result length.

    Args:
        name: Raw entity name.
        max_length: Maximum length of the returned stem.

    Returns:
        A non-empty, separator-free filename stem.
    """
    normalized = unicodedata.normalize("NFC", name)
    cleaned = _ILLEGAL_CHARS.sub(" ", normalized)
    cleaned = _WHITESPACE.sub(" ", cleaned).strip()
    cleaned = cleaned.strip(". ")
    if not cleaned:
        cleaned = "untitled"
    return cleaned[:max_length].strip()


def extension_from_content_type(content_type: str | None) -> str:
    """Map a response content type to a bare file extension (default ``jpg``)."""
    if not content_type:
        return "jpg"
    media_type = content_type.split(";", 1)[0].strip().lower()
    return _CONTENT_TYPE_EXTENSIONS.get(media_type, "jpg")


def _pick_cover(entity: HasImagesAndName, size: ImageSize) -> Image:
    """Pick the cover image for ``entity``, raising if it has none."""
    images = _entity_images(entity)
    if not images:
        raise MediaError(f"Entity {entity.name!r} has no images to download.")
    return pick_image(images, size)


def _write_cover(
    dest: Path, name: str, filename: str | None, content_type: str | None, body: bytes
) -> Path:
    """Write downloaded cover bytes and return the path."""
    if filename is None:
        ext = extension_from_content_type(content_type)
        out_name = f"{safe_filename(name)}.{ext}"
    else:
        out_name = filename
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / out_name
    path.write_bytes(body)
    return path


def download_cover_sync(
    transport: Transport,
    entity: HasImagesAndName,
    dest: Path,
    *,
    size: ImageSize = "largest",
    filename: str | None = None,
) -> Path:
    """Download an entity's cover art and return the written path.

    Args:
        transport: HTTP transport to fetch the image with.
        entity: Any entity carrying ``name`` and ``images``.
        dest: Destination directory (created if missing).
        size: ``"largest"`` or ``"smallest"``.
        filename: Explicit filename; defaults to ``<name>.<ext>``.

    Returns:
        The path of the written image.

    Raises:
        MediaError: If the entity has no images.
    """
    image = _pick_cover(entity, size)
    response = transport.get(image.url)
    return _write_cover(
        dest, entity.name, filename, response.headers.get("Content-Type"), response.content
    )


async def download_cover_async(
    transport: AsyncTransport,
    entity: HasImagesAndName,
    dest: Path,
    *,
    size: ImageSize = "largest",
    filename: str | None = None,
) -> Path:
    """Async mirror of :func:`download_cover_sync`."""
    image = _pick_cover(entity, size)
    response = await transport.get(image.url)
    return _write_cover(
        dest, entity.name, filename, response.headers.get("Content-Type"), response.content
    )
