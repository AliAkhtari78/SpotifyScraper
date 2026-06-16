"""Console entry point for the SpotifyScraper MCP server.

Run with ``spotifyscraper-mcp`` (or ``python -m spotify_scraper.mcp``). Set
``SPOTIFY_SP_DC`` to enable the authenticated tools.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

_EXTRA_HINT = "The MCP server requires the 'mcp' extra: pip install 'spotifyscraper[mcp]'"


def main(argv: Sequence[str] | None = None) -> None:
    """Parse arguments and run the MCP server."""
    parser = argparse.ArgumentParser(
        prog="spotifyscraper-mcp",
        description="Run the SpotifyScraper Model Context Protocol server.",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport to serve on (default: stdio).",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host for HTTP/SSE transports.")
    parser.add_argument("--port", type=int, default=8000, help="Bind port for HTTP/SSE transports.")
    args = parser.parse_args(argv)

    try:
        from spotify_scraper.mcp.server import build_server
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise SystemExit(_EXTRA_HINT) from exc

    server = build_server(host=args.host, port=args.port)
    server.run(transport=args.transport)


if __name__ == "__main__":
    main()
