"""The ``download`` sub-app: ``cover`` and ``preview``.

Both subcommands fetch a track (or episode) by URL/URI/ID, hand the model to the
client's downloader, and print the written path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from spotify_scraper import RateLimit, SpotifyClient
from spotify_scraper.cli._output import run
from spotify_scraper.media import ImageSize

download_app = typer.Typer(
    help="Download cover art or preview audio for a track or episode.",
    no_args_is_help=True,
)

ValueArg = Annotated[str, typer.Argument(help="Spotify URL, URI, or 22-character ID.")]
DirOpt = Annotated[
    Path,
    typer.Option("--output", "-o", help="Destination directory (created if missing)."),
]
NameOpt = Annotated[
    str | None,
    typer.Option("--name", help="Explicit filename; defaults to a sanitized entity name."),
]
ProxyOpt = Annotated[str | None, typer.Option("--proxy", help="Proxy URL for requests.")]
TimeoutOpt = Annotated[float, typer.Option("--timeout", help="Per-request timeout in seconds.")]
RateLimitOpt = Annotated[
    float | None,
    typer.Option("--rate-limit", help="Sustained requests per second."),
]


def _build_client(proxy: str | None, timeout: float, rate_limit: float | None) -> SpotifyClient:
    rate = RateLimit(per_second=rate_limit) if rate_limit is not None else None
    return SpotifyClient(proxy=proxy, timeout=timeout, rate_limit=rate)


@download_app.command()
def cover(
    value: ValueArg,
    output: DirOpt = Path(),
    size: Annotated[
        ImageSize,
        typer.Option("--size", help="Pick the largest or smallest available image."),
    ] = "largest",
    name: NameOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Download a track's cover art to a directory and print the path."""

    def body() -> None:
        with _build_client(proxy, timeout, rate_limit) as client:
            entity = client.get_track(value)
            path = client.download_cover(entity, output, size=size, filename=name)
        typer.echo(str(path))

    run(body)


@download_app.command()
def preview(
    value: ValueArg,
    output: DirOpt = Path(),
    embed_cover: Annotated[
        bool,
        typer.Option("--embed-cover", help="Embed cover art and tags (needs the media extra)."),
    ] = False,
    name: NameOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Download a track's preview MP3 to a directory and print the path."""

    def body() -> None:
        with _build_client(proxy, timeout, rate_limit) as client:
            entity = client.get_track(value)
            path = client.download_preview(entity, output, filename=name, embed_cover=embed_cover)
        typer.echo(str(path))

    run(body)
