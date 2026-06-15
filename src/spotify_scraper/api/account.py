"""URL and header construction for Spotify's product-state endpoint.

The product-state host (``spclient.wg.spotify.com``) is the same authenticated
web-player host as color-lyrics and transcripts, and is reached with the same
cookie-derived web-player token. These helpers are I/O-free; the sync and async
facades reuse them. The endpoint host and path live ONLY here, mirroring how the
lyrics/transcript hosts and pathfinder hashes are confined to one module, so a
Spotify change is a single-file edit.
"""

from __future__ import annotations

_PRODUCT_STATE_URL = "https://spclient.wg.spotify.com/melody/v1/product_state"


def product_state_url() -> str:
    """Return the product-state request URL.

    The body is a flat per-account object, so this takes no entity argument.

    Returns:
        The fully-qualified product-state request URL.
    """
    return _PRODUCT_STATE_URL


def auth_headers(token: str) -> dict[str, str]:
    """Return the authorization headers for a product-state request.

    Args:
        token: A cookie-derived web-player bearer token.

    Returns:
        Headers carrying the bearer token and the web-player platform marker.
    """
    return {"Authorization": f"Bearer {token}", "app-platform": "WebPlayer"}
