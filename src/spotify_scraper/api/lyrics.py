"""URL and header construction for Spotify's color-lyrics endpoint.

The lyrics host (``spclient.wg.spotify.com``) is distinct from the pathfinder
host and is reached with the cookie-derived web-player token. These helpers are
I/O-free; the sync and async facades reuse them.
"""

from __future__ import annotations

_LYRICS_BASE = "https://spclient.wg.spotify.com/color-lyrics/v2/track"
_LYRICS_QUERY = "format=json&vocalRemoval=false&market=from_token"


def lyrics_url(track_id: str) -> str:
    """Return the color-lyrics URL for a track ID.

    Args:
        track_id: The 22-character Spotify track ID.

    Returns:
        The fully-qualified color-lyrics request URL.
    """
    return f"{_LYRICS_BASE}/{track_id}?{_LYRICS_QUERY}"


def auth_headers(token: str) -> dict[str, str]:
    """Return the authorization headers for a color-lyrics request.

    Args:
        token: A cookie-derived web-player bearer token.

    Returns:
        Headers carrying the bearer token and the web-player platform marker.
    """
    return {"Authorization": f"Bearer {token}", "app-platform": "WebPlayer"}
