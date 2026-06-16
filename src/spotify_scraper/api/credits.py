"""Track-credits (``track-credits-view``) request building.

Track credits live on the authenticated ``spclient`` host and need the
cookie-derived user token, like lyrics/transcripts. All functions are I/O-free.
"""

from __future__ import annotations

from urllib.parse import quote

_SPCLIENT = "https://spclient.wg.spotify.com"


def credits_url(track_id: str) -> str:
    """Build the ``track-credits-view`` URL for a track id.

    Args:
        track_id: The 22-character track id.

    Returns:
        The fully-qualified credits URL.
    """
    return f"{_SPCLIENT}/track-credits-view/v0/experimental/{quote(track_id, safe='')}/credits"


def auth_headers(token: str) -> dict[str, str]:
    """Return the authorization headers for a credits request.

    Args:
        token: A cookie-derived user access token.

    Returns:
        Headers carrying the bearer token and the web-player platform marker.
    """
    return {"Authorization": f"Bearer {token}", "app-platform": "WebPlayer"}
