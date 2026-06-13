"""JSON rendering and error mapping for the CLI.

``emit`` serializes a model's ``to_dict()`` to stdout or a file; ``run`` wraps a
command body so library exceptions become concise ``error: ...`` messages with
the spec's exit codes instead of raw tracebacks.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, TypeVar

import typer

from spotify_scraper.errors import (
    AuthenticationError,
    NotFoundError,
    SpotifyScraperError,
)

_T = TypeVar("_T")

#: Library exception -> process exit code. The first matching base class wins,
#: so list subclasses before their parents.
_EXIT_CODES: tuple[tuple[type[SpotifyScraperError], int], ...] = (
    (NotFoundError, 3),
    (AuthenticationError, 4),
    (SpotifyScraperError, 1),
)


def emit(data: Mapping[str, Any], *, pretty: bool, output: Path | None) -> None:
    """Render ``data`` as JSON to a file or stdout.

    Args:
        data: A JSON-safe mapping (typically ``model.to_dict()``).
        pretty: Indent the JSON with two spaces when ``True``.
        output: Destination file; ``None`` writes to stdout.
    """
    text = json.dumps(data, indent=2 if pretty else None, ensure_ascii=False)
    if output is None:
        typer.echo(text)
    else:
        output.write_text(text + "\n", encoding="utf-8")


def _exit_code(exc: SpotifyScraperError) -> int:
    for exc_type, code in _EXIT_CODES:
        if isinstance(exc, exc_type):
            return code
    return 1


def run(fn: Callable[[], _T]) -> _T:
    """Run a command body, mapping library errors to exit codes.

    Args:
        fn: A zero-argument callable holding the command's work.

    Returns:
        Whatever ``fn`` returns on success.

    Raises:
        typer.Exit: With the spec's exit code (``NotFoundError`` -> 3,
            ``AuthenticationError`` -> 4, other ``SpotifyScraperError`` -> 1)
            after writing ``error: <message>`` to stderr.
    """
    try:
        return fn()
    except SpotifyScraperError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(_exit_code(exc)) from exc
