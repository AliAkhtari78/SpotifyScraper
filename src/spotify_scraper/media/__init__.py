"""Media downloads: cover art and preview audio.

Pure helpers and transport-driven download functions live here so the sync
and async client facades can share one implementation. Cover embedding pulls
in ``mutagen`` (the ``media`` extra) lazily, only when requested.
"""

from __future__ import annotations

from spotify_scraper.media.audio import (
    download_preview_async,
    download_preview_sync,
)
from spotify_scraper.media.images import (
    HasImagesAndName,
    ImageSize,
    download_cover_async,
    download_cover_sync,
    extension_from_content_type,
    pick_image,
    safe_filename,
)
from spotify_scraper.media.video import (
    download_canvas_async,
    download_canvas_sync,
)

__all__ = [
    "HasImagesAndName",
    "ImageSize",
    "download_canvas_async",
    "download_canvas_sync",
    "download_cover_async",
    "download_cover_sync",
    "download_preview_async",
    "download_preview_sync",
    "extension_from_content_type",
    "pick_image",
    "safe_filename",
]
