"""The ``spotifyscraper`` Typer application.

Defines the global callback (``--version`` and shared client options), the six
entity commands, and mounts the ``download`` sub-app. Each entity command
fetches with :class:`SpotifyClient` and emits ``model.to_dict()`` as JSON.
"""

from __future__ import annotations

import dataclasses
import os
import time
from pathlib import Path
from typing import Annotated

import typer

import spotify_scraper
from spotify_scraper import RateLimit, SpotifyClient
from spotify_scraper.auth.session import SessionStore, default_session_path
from spotify_scraper.cli._output import emit, run
from spotify_scraper.cli.download import download_app
from spotify_scraper.errors import SpotifyScraperError

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


def _now_ms() -> int:
    return time.time_ns() // 1_000_000


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


@app.command()
def charts(
    key: Annotated[
        str | None,
        typer.Argument(help="Chart key to fetch (omit to list the available charts)."),
    ] = None,
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
    """List editorial charts, or fetch one (e.g. 'top-50-global') as a playlist."""

    def body() -> None:
        with build_client(proxy, timeout, rate_limit) as client:
            if key is None:
                listing = [dataclasses.asdict(chart) for chart in client.list_charts()]
                emit({"charts": listing}, pretty=pretty, output=output)
                return
            entity = client.get_chart(key, max_tracks=_parse_max(max_tracks))
            emit(entity.to_dict(), pretty=pretty, output=output)

    run(body)


@app.command()
def colors(
    value: Annotated[
        str, typer.Argument(help="Spotify image URL, 'spotify:image:' uri, or image id.")
    ],
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Extract a cover image's theming colors and emit them as JSON."""

    def body() -> None:
        with build_client(proxy, timeout, rate_limit) as client:
            entity = client.get_colors(value)
        emit(entity.to_dict(), pretty=pretty, output=output)

    run(body)


@app.command()
def canvas(
    value: ValueArg,
    cookies: CookiesOpt = None,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch a track's Canvas video (requires an sp_dc cookie) and emit JSON.

    Emits an empty object when the track has no Canvas.
    """

    def body() -> None:
        source = _resolve_cookies(cookies)
        rate = RateLimit(per_second=rate_limit) if rate_limit is not None else None
        with SpotifyClient(proxy=proxy, timeout=timeout, rate_limit=rate, cookies=source) as client:
            entity = client.get_canvas(value)
        emit(entity.to_dict() if entity is not None else {}, pretty=pretty, output=output)

    run(body)


@app.command()
def related(
    value: ValueArg,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch an artist's related artists and emit them as JSON."""

    def body() -> None:
        with build_client(proxy, timeout, rate_limit) as client:
            artists = client.get_related_artists(value)
        emit({"artists": [a.to_dict() for a in artists]}, pretty=pretty, output=output)

    run(body)


@app.command()
def discography(
    value: ValueArg,
    max_releases: Annotated[
        str,
        typer.Option("--max-releases", help="Release cap; an integer or 'all' (0 also means all)."),
    ] = "all",
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch an artist's full discography and emit it as JSON."""

    def body() -> None:
        with build_client(proxy, timeout, rate_limit) as client:
            releases = client.get_discography(value, max_releases=_parse_max(max_releases))
        emit({"releases": [r.to_dict() for r in releases]}, pretty=pretty, output=output)

    run(body)


@app.command()
def similar(
    value: ValueArg,
    limit: Annotated[int, typer.Option("--limit", help="Maximum recommended albums.")] = 10,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Recommend albums similar to a track and emit them as JSON."""

    def body() -> None:
        with build_client(proxy, timeout, rate_limit) as client:
            albums = client.get_similar_albums(value, limit=limit)
        emit({"albums": [a.to_dict() for a in albums]}, pretty=pretty, output=output)

    run(body)


@app.command()
def user(
    user_id: Annotated[
        str, typer.Argument(help="Spotify user id, 'spotify:user:' uri, or profile URL.")
    ],
    cookies: CookiesOpt = None,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch a public user profile (requires an sp_dc cookie) and emit JSON."""

    def body() -> None:
        source = _resolve_cookies(cookies)
        rate = RateLimit(per_second=rate_limit) if rate_limit is not None else None
        with SpotifyClient(proxy=proxy, timeout=timeout, rate_limit=rate, cookies=source) as client:
            profile = client.get_user(user_id)
        emit(profile.to_dict(), pretty=pretty, output=output)

    run(body)


@app.command()
def events(
    value: ValueArg,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch an artist's upcoming concerts/events and emit them as JSON."""

    def body() -> None:
        with build_client(proxy, timeout, rate_limit) as client:
            concerts = client.get_artist_events(value)
        emit({"concerts": [c.to_dict() for c in concerts]}, pretty=pretty, output=output)

    run(body)


@app.command()
def credits(
    value: ValueArg,
    cookies: CookiesOpt = None,
    pretty: PrettyOpt = False,
    output: OutputOpt = None,
    proxy: ProxyOpt = None,
    timeout: TimeoutOpt = 10.0,
    rate_limit: RateLimitOpt = None,
) -> None:
    """Fetch a track's credits (requires an sp_dc cookie) and emit JSON."""

    def body() -> None:
        source = _resolve_cookies(cookies)
        rate = RateLimit(per_second=rate_limit) if rate_limit is not None else None
        with SpotifyClient(proxy=proxy, timeout=timeout, rate_limit=rate, cookies=source) as client:
            entity = client.get_credits(value)
        emit(entity.to_dict(), pretty=pretty, output=output)

    run(body)


StoreOpt = Annotated[
    str,
    typer.Option("--store", help="Where to keep the cookie: 'file' (default) or 'keyring'."),
]


@app.command()
def login(
    store: StoreOpt = "file",
    reuse: Annotated[
        bool,
        typer.Option(
            "--reuse/--no-reuse",
            help="Reuse a valid saved session and skip the browser when present.",
        ),
    ] = True,
    timeout: Annotated[
        float, typer.Option("--timeout", help="Seconds to wait for the manual login.")
    ] = 300.0,
    proxy: ProxyOpt = None,
) -> None:
    """Sign in and save the session, reusing a valid one when present.

    With ``--reuse`` (the default), a valid saved session skips the browser
    entirely. Only the session path is printed; the cookie is never displayed.
    """

    def body() -> None:
        backend = SessionStore(store)
        if reuse and backend.has_session():
            typer.echo(f"Reused existing session at {default_session_path()}")
            return
        try:
            from spotify_scraper.browser import capture_sp_dc
        except ImportError as exc:
            raise SpotifyScraperError(
                "Browser login requires the 'browser' extra: "
                "pip install spotifyscraper[browser] && playwright install chromium"
            ) from exc
        captured = capture_sp_dc(timeout=timeout, proxy=proxy)
        path = backend.save(captured.sp_dc, sp_dc_expires_ms=captured.sp_dc_expires_ms)
        typer.echo(f"Saved session to {path}")

    run(body)


@app.command()
def logout(store: StoreOpt = "file") -> None:
    """Clear the saved session (idempotent); prints only the cleared path."""

    def body() -> None:
        SessionStore(store).clear()
        typer.echo(f"Cleared session at {default_session_path()}")

    run(body)


@app.command()
def session(store: StoreOpt = "file") -> None:
    """Print the saved session's status; never displays the cookie.

    Reports existence, validity, when it was saved, and (when the cookie's
    expiry is known) how many days remain.
    """

    def body() -> None:
        info = SessionStore(store).info()
        typer.echo(f"exists: {info.exists}")
        typer.echo(f"valid: {info.valid}")
        typer.echo(f"saved_at_ms: {info.saved_at_ms}")
        typer.echo(f"sp_dc_expires_ms: {info.sp_dc_expires_ms}")
        if info.sp_dc_expires_ms is not None:
            days = (info.sp_dc_expires_ms - _now_ms()) / 86_400_000
            typer.echo(f"days_remaining: {days:.1f}")
        if info.reason:
            typer.echo(f"reason: {info.reason}")

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
