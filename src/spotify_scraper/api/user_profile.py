"""Public user-profile (``user-profile-view``) request building.

The public-profile endpoint lives on the authenticated ``spclient`` host, like
lyrics/transcripts/product-state, and requires the cookie-derived user token
(the anonymous token gets ``403 RBAC: access denied``). All functions are
I/O-free.
"""

from __future__ import annotations

from urllib.parse import quote

_SPCLIENT = "https://spclient.wg.spotify.com"


def profile_url(user_id: str, *, playlist_limit: int = 10, artist_limit: int = 10) -> str:
    """Build the ``user-profile-view`` URL for a public profile.

    Args:
        user_id: The Spotify user id (the tail of ``spotify:user:<id>``).
        playlist_limit: Maximum public playlists to include.
        artist_limit: Maximum recently-played artists to include.

    Returns:
        The fully-qualified profile URL.
    """
    return (
        f"{_SPCLIENT}/user-profile-view/v3/profile/{quote(user_id, safe='')}"
        f"?playlist_limit={playlist_limit}&artist_limit={artist_limit}&episode_limit=0"
    )


def auth_headers(token: str) -> dict[str, str]:
    """Return the authorization headers for a user-profile request.

    Args:
        token: A cookie-derived user access token.

    Returns:
        Headers carrying the bearer token and the web-player platform marker.
    """
    return {"Authorization": f"Bearer {token}", "app-platform": "WebPlayer"}
