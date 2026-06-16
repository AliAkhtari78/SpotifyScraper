"""Canvas (looping cover video) model."""

from __future__ import annotations

from dataclasses import dataclass

from spotify_scraper.models.base import ModelBase


@dataclass(frozen=True, slots=True)
class Canvas(ModelBase):
    """A track's Canvas: a short, silent, looping cover video.

    ``url`` is a direct, **non-DRM** MP4 hosted on ``canvaz.scdn.co`` that you can
    download or embed. ``canvas_type`` is Spotify's loop style (e.g.
    ``"VIDEO_LOOPING"`` / ``"VIDEO_LOOPING_RANDOM"``). ``id`` is the canvas id,
    derived from ``uri`` (``spotify:canvas:<id>``). Only some tracks have a
    Canvas; :meth:`SpotifyClient.get_canvas` returns ``None`` when one is absent.
    """

    id: str
    uri: str
    url: str
    canvas_type: str | None = None
    file_id: str | None = None
