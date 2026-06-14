"""The ``spotifyscraper`` Typer application.

Defines the global callback (``--version`` and shared client options), the six
entity commands, and mounts the ``download`` sub-app. Each entity command
fetches with :class:`SpotifyClient` and emits ``model.to_dict()`` as JSON.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer

import spotify_scraper
from spotify_scraper import RateLimit, SpotifyClient
from spotify_scraper.cli._output import emit, run
from spotify_scraper.cli.download import download_app

app = typer.Typer(
    name="spotifyscraper",
    help="Extract public Spotify data as JSON from the command line.",
    no_args_is_help=True,
    add_completion=False,
)
app.add_typer(download_app, name="download")

# --- Shared option annotations -------------------------------------------------

ValueArg = Annotated[str, typer.Argument(help="Spotify URL, URI, or 22-character ID.")]
PrettyOpt = Annotated[bool, typer.Option("--pretty", help="Indent the JSON output.")]
OutputOpt = Annotated[
    Path | None,
    typer.Option("--output", "-o", help="Write JSON to this file instead of stdout."),
]
ProxyOpt = Annotated[str | None, typer.Option("--proxy", help="Proxy URL for requests.")]
TimeoutOpt = Annotated[float, typer.Option("--timeout", help="Per-request timeout in seconds.")]
RateLimitOpt = Annotated[
    float | None,
    typer.Option("--rate-limit", help="Sustained requests per second."),
]
CookiesOpt = Annotated[
    Path | None,
    typer.Option(
        "--cookies",
        help="Path to a Netscape cookies.txt with an 'sp_dc' line "
        "(falls back to the SPOTIFY_SP_DC environment variable).",
    ),
]


def build_client(proxy: str | None, timeout: float, rate_limit: float | None) -> SpotifyClient:
    """Construct a :class:`SpotifyClient` from the shared CLI options.

    Args:
        proxy: Optional proxy URL.
        timeout: Per-request timeout in seconds.
        rate_limit: Sustained requests per second; ``None`` uses the default.

    Returns:
        A configured client; the caller is responsible for closing it.
    """
    rate = RateLimit(per_second=rate_limit) if rate_limit is not None else None
    return SpotifyClient(proxy=proxy, timeout=timeout, rate_limit=rate)


def _parse_max(value: str) -> int | None:
    """Parse a ``--max-*`` option: ``"all"`` or ``0`` means no limit (``None``)."""
    if value.strip().lower() == "all":
        return None
    try:
        parsed = int(value)
    except ValueError as exc:
        raise typer.BadParameter("must be an integer or 'all'") from exc
    return None if parsed <= 0 else parsed


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(spotify_scraper.__version__)
        raise typer.Exit


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Print the installed version and exit.",
            is_eager=True,
            callback=_version_callback,
        ),
    ] = False,
) -> None:
    """SpotifyScraper command-line interface."""


@app.command()
def track(
    value: ValueArg,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch a track and emit it as JSON."""

    def body() -> None:
        with build_client(proxy, timeout, rate_limit) as client:
            entity = client.get_track(value)
        emit(entity.to_dict(), pretty=pretty, output=output)

    run(body)


@app.command()
def album(
    value: ValueArg,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch an album (with its tracks) and emit it as JSON."""

    def body() -> None:
        with build_client(proxy, timeout, rate_limit) as client:
            entity = client.get_album(value)
        emit(entity.to_dict(), pretty=pretty, output=output)

    run(body)


@app.command()
def artist(
    value: ValueArg,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch an artist and emit it as JSON."""

    def body() -> None:
        with build_client(proxy, timeout, rate_limit) as client:
            entity = client.get_artist(value)
        emit(entity.to_dict(), pretty=pretty, output=output)

    run(body)


@app.command()
def playlist(
    value: ValueArg,
    max_tracks: Annotated[
        str,
        typer.Option("--max-tracks", help="Track cap; an integer or 'all' (0 also means all)."),
    ] = "100",
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch a playlist and emit it as JSON."""

    def body() -> None:
        limit = _parse_max(max_tracks)
        with build_client(proxy, timeout, rate_limit) as client:
            entity = client.get_playlist(value, max_tracks=limit)
        emit(entity.to_dict(), pretty=pretty, output=output)

    run(body)


@app.command()
def episode(
    value: ValueArg,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch a podcast episode and emit it as JSON."""

    def body() -> None:
        with build_client(proxy, timeout, rate_limit) as client:
            entity = client.get_episode(value)
        emit(entity.to_dict(), pretty=pretty, output=output)

    run(body)


@app.command()
def show(
    value: ValueArg,
    max_episodes: Annotated[
        str,
        typer.Option("--max-episodes", help="Episode cap; an integer or 'all' (0 also means all)."),
    ] = "50",
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch a podcast show (with its episodes) and emit it as JSON."""

    def body() -> None:
        limit = _parse_max(max_episodes)
        with build_client(proxy, timeout, rate_limit) as client:
            entity = client.get_show(value, max_episodes=limit)
        emit(entity.to_dict(), pretty=pretty, output=output)

    run(body)


@app.command()
def lyrics(
    value: ValueArg,
    cookies: CookiesOpt = None,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch a track's lyrics (requires an sp_dc cookie) and emit it as JSON."""

    def body() -> None:
        source = _resolve_cookies(cookies)
        rate = RateLimit(per_second=rate_limit) if rate_limit is not None else None
        with SpotifyClient(proxy=proxy, timeout=timeout, rate_limit=rate, cookies=source) as client:
            entity = client.get_lyrics(value)
        emit(entity.to_dict(), pretty=pretty, output=output)

    run(body)


@app.command()
def transcript(
    value: ValueArg,
    cookies: CookiesOpt = None,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch an episode's transcript (requires an sp_dc cookie) and emit JSON."""

    def body() -> None:
        source = _resolve_cookies(cookies)
        rate = RateLimit(per_second=rate_limit) if rate_limit is not None else None
        with SpotifyClient(proxy=proxy, timeout=timeout, rate_limit=rate, cookies=source) as client:
            entity = client.get_transcript(value)
        emit(entity.to_dict(), pretty=pretty, output=output)

    run(body)


def _resolve_cookies(cookies: Path | None) -> str | Path:
    """Resolve the cookie source from ``--cookies`` or ``SPOTIFY_SP_DC``.

    Raises:
        typer.BadParameter: If neither a cookies file nor the env var is set.
    """
    if cookies is not None:
        return cookies
    env = os.environ.get("SPOTIFY_SP_DC")
    if env:
        return env
    raise typer.BadParameter(
        "This feature requires authentication: pass --cookies PATH or set SPOTIFY_SP_DC."
    )
