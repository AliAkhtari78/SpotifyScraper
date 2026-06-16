"""Canvas (looping cover video) downloads.

A Canvas is a short, silent MP4 on ``canvaz.scdn.co`` (no DRM), so each is
fetched fully and written with :meth:`Path.write_bytes`, exactly like a preview
clip. The sync and async client facades share these helpers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from spotify_scraper.media.images import safe_filename, safe_output_name

if TYPE_CHECKING:
    from pathlib import Path

    from spotify_scraper.http.transport import AsyncTransport, Transport
    from spotify_scraper.models.canvas import Canvas


def _canvas_path(canvas: Canvas, dest: Path, filename: str | None) -> Path:
    """Resolve the destination MP4 path, creating ``dest`` if missing."""
    out_name = (
        safe_output_name(filename)
        if filename is not None
        else f"{safe_filename(canvas.id or 'canvas')}.mp4"
    )
    dest.mkdir(parents=True, exist_ok=True)
    return dest / out_name


def download_canvas_sync(
    transport: Transport,
    canvas: Canvas,
    dest: Path,
    *,
    filename: str | None = None,
) -> Path:
    """Download a :class:`Canvas` MP4 and return the written path.

    Args:
        transport: HTTP transport to fetch with.
        canvas: A :class:`Canvas` carrying a ``url``.
        dest: Destination directory (created if missing).
        filename: Explicit filename; defaults to ``<canvas-id>.mp4``.

    Returns:
        The path of the written MP4.
    """
    path = _canvas_path(canvas, dest, filename)
    path.write_bytes(transport.get(canvas.url).content)
    return path


async def download_canvas_async(
    transport: AsyncTransport,
    canvas: Canvas,
    dest: Path,
    *,
    filename: str | None = None,
) -> Path:
    """Async mirror of :func:`download_canvas_sync`."""
    path = _canvas_path(canvas, dest, filename)
    response = await transport.get(canvas.url)
    path.write_bytes(response.content)
    return path
