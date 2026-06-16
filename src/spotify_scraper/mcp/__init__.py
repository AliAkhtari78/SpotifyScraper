"""SpotifyScraper MCP server (optional ``mcp`` extra).

Exposes the library as a Model Context Protocol server so Claude and other LLM
hosts can call it as a tool. The heavy ``mcp`` SDK import is deferred to
:func:`build_server` so importing this package never fails without the extra.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

__all__ = ["build_server"]

_EXTRA_HINT = (
    "The SpotifyScraper MCP server requires the 'mcp' extra: pip install 'spotifyscraper[mcp]'"
)


def build_server(**kwargs: Any) -> FastMCP:
    """Build the SpotifyScraper :class:`FastMCP` server.

    Args:
        **kwargs: Forwarded to the underlying builder (``sp_dc``, ``name``,
            ``host``, ``port``).

    Returns:
        A configured ``FastMCP`` instance ready to ``run``.

    Raises:
        ImportError: If the ``mcp`` extra is not installed.
    """
    try:
        from spotify_scraper.mcp.server import build_server as _build
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise ImportError(_EXTRA_HINT) from exc
    return _build(**kwargs)
