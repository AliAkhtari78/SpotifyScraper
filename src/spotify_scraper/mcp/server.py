"""The SpotifyScraper :class:`FastMCP` server.

Every public client getter is exposed as a tool returning JSON-safe structured
output (the models' ``to_dict()``); the six entity getters are also addressable
resources (``spotify://track/{id}`` …). Authenticated tools (canvas, credits,
user, lyrics, transcript, account) require the ``SPOTIFY_SP_DC`` cookie and
return a clear error otherwise. A shared :class:`AsyncSpotifyClient` is created
once and closed on shutdown.
"""

from __future__ import annotations

import dataclasses
import json
import os
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any, TypeVar

import httpx
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.exceptions import ToolError

from spotify_scraper import AsyncSpotifyClient
from spotify_scraper.errors import AuthenticationError, SpotifyScraperError
from spotify_scraper.media.images import _pick_cover

_T = TypeVar("_T")

_INSTRUCTIONS = (
    "Extract public Spotify data — tracks, albums, artists, playlists, podcasts, "
    "lyrics, charts, related artists, recommendations, Canvas videos, cover colors, "
    "credits, concerts, and public user profiles — with no official API key. "
    "Authenticated tools (canvas, credits, user, lyrics, transcript, account) need "
    "the server to be started with the SPOTIFY_SP_DC environment variable set."
)

_AUTH_HINT = (
    "This tool needs a Spotify login. Restart spotifyscraper-mcp with the "
    "SPOTIFY_SP_DC environment variable set to your 'sp_dc' cookie value."
)


async def _run(awaitable: Awaitable[_T]) -> _T:
    """Await a client call, mapping library errors to clean MCP tool errors."""
    try:
        return await awaitable
    except AuthenticationError as exc:
        raise ToolError(_AUTH_HINT) from exc
    except SpotifyScraperError as exc:
        raise ToolError(str(exc)) from exc


def build_server(
    *,
    sp_dc: str | None = None,
    name: str = "spotifyscraper",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> FastMCP:
    """Build the SpotifyScraper MCP server.

    Args:
        sp_dc: The Spotify ``sp_dc`` cookie for authenticated tools; falls back to
            the ``SPOTIFY_SP_DC`` environment variable.
        name: The server name advertised to clients.
        host: Bind host for the HTTP/SSE transports.
        port: Bind port for the HTTP/SSE transports.

    Returns:
        A configured :class:`FastMCP` instance.
    """
    cookies = sp_dc if sp_dc is not None else (os.environ.get("SPOTIFY_SP_DC") or None)
    client = AsyncSpotifyClient(cookies=cookies)

    @asynccontextmanager
    async def lifespan(_server: FastMCP) -> Any:
        try:
            yield {}
        finally:
            await client.aclose()

    mcp: FastMCP = FastMCP(
        name, instructions=_INSTRUCTIONS, lifespan=lifespan, host=host, port=port
    )

    # --- entity getters (anonymous) ---------------------------------------- #

    @mcp.tool()
    async def get_track(value: str) -> dict[str, Any]:
        """Fetch a track by URL, URI, or 22-character ID."""
        return (await _run(client.get_track(value))).to_dict()

    @mcp.tool()
    async def get_album(value: str) -> dict[str, Any]:
        """Fetch an album (with its tracks) by URL, URI, or ID."""
        return (await _run(client.get_album(value))).to_dict()

    @mcp.tool()
    async def get_artist(value: str) -> dict[str, Any]:
        """Fetch an artist by URL, URI, or ID."""
        return (await _run(client.get_artist(value))).to_dict()

    @mcp.tool()
    async def get_playlist(value: str, max_tracks: int = 100) -> dict[str, Any]:
        """Fetch a playlist by URL, URI, or ID (up to ``max_tracks`` tracks)."""
        return (await _run(client.get_playlist(value, max_tracks=max_tracks))).to_dict()

    @mcp.tool()
    async def get_episode(value: str) -> dict[str, Any]:
        """Fetch a podcast episode by URL, URI, or ID."""
        return (await _run(client.get_episode(value))).to_dict()

    @mcp.tool()
    async def get_show(value: str, max_episodes: int = 50) -> dict[str, Any]:
        """Fetch a podcast show (with episodes) by URL, URI, or ID."""
        return (await _run(client.get_show(value, max_episodes=max_episodes))).to_dict()

    # --- discovery (anonymous) --------------------------------------------- #

    @mcp.tool()
    async def search(query: str, types: list[str] | None = None, limit: int = 20) -> dict[str, Any]:
        """Search across tracks, albums, artists, playlists, shows, and episodes."""
        if types is None:
            results = await _run(client.search(query, limit=limit))
        else:
            results = await _run(client.search(query, types=tuple(types), limit=limit))
        return results.to_dict()

    @mcp.tool()
    async def list_charts() -> dict[str, Any]:
        """List the built-in editorial charts (key, name, backing playlist id)."""
        return {"charts": [dataclasses.asdict(chart) for chart in client.list_charts()]}

    @mcp.tool()
    async def get_chart(key: str, max_tracks: int = 100) -> dict[str, Any]:
        """Fetch an editorial chart (e.g. 'top-50-global') as a playlist."""
        return (await _run(client.get_chart(key, max_tracks=max_tracks))).to_dict()

    @mcp.tool()
    async def get_related_artists(value: str) -> dict[str, Any]:
        """Fetch artists related to an artist ('fans also like')."""
        artists = await _run(client.get_related_artists(value))
        return {"artists": [a.to_dict() for a in artists]}

    @mcp.tool()
    async def get_discography(value: str, max_releases: int | None = None) -> dict[str, Any]:
        """Fetch an artist's full discography (albums, singles, compilations)."""
        releases = await _run(client.get_discography(value, max_releases=max_releases))
        return {"releases": [r.to_dict() for r in releases]}

    @mcp.tool()
    async def get_similar_albums(value: str, limit: int = 10) -> dict[str, Any]:
        """Recommend albums similar to a track."""
        albums = await _run(client.get_similar_albums(value, limit=limit))
        return {"albums": [a.to_dict() for a in albums]}

    @mcp.tool()
    async def get_colors(value: str) -> dict[str, Any]:
        """Extract a cover image's theming colors (image URL/uri, or any entity URL/URI/ID)."""
        return (await _run(client.get_colors(value))).to_dict()

    @mcp.tool()
    async def get_artist_events(value: str) -> dict[str, Any]:
        """Fetch an artist's upcoming concerts/events."""
        concerts = await _run(client.get_artist_events(value))
        return {"concerts": [c.to_dict() for c in concerts]}

    # --- authenticated tools ----------------------------------------------- #

    @mcp.tool()
    async def get_canvas(value: str) -> dict[str, Any]:
        """Fetch a track's Canvas looping video (needs SPOTIFY_SP_DC)."""
        canvas = await _run(client.get_canvas(value))
        return {"canvas": canvas.to_dict() if canvas is not None else None}

    @mcp.tool()
    async def get_credits(value: str) -> dict[str, Any]:
        """Fetch a track's credits — performers, writers, producers (needs SPOTIFY_SP_DC)."""
        return (await _run(client.get_credits(value))).to_dict()

    @mcp.tool()
    async def get_user(user_id: str) -> dict[str, Any]:
        """Fetch a public user profile (needs SPOTIFY_SP_DC)."""
        return (await _run(client.get_user(user_id))).to_dict()

    @mcp.tool()
    async def get_lyrics(value: str) -> dict[str, Any]:
        """Fetch a track's lyrics (needs SPOTIFY_SP_DC)."""
        return (await _run(client.get_lyrics(value))).to_dict()

    @mcp.tool()
    async def get_transcript(value: str) -> dict[str, Any]:
        """Fetch a podcast episode's transcript (needs SPOTIFY_SP_DC)."""
        return (await _run(client.get_transcript(value))).to_dict()

    @mcp.tool()
    async def get_account() -> dict[str, Any]:
        """Fetch the logged-in account's product state (needs SPOTIFY_SP_DC)."""
        return (await _run(client.get_account())).to_dict()

    # --- visual tool: cover art as an inline image ------------------------- #

    _cover_getters: dict[str, Callable[[str], Awaitable[Any]]] = {
        "track": client.get_track,
        "album": client.get_album,
        "artist": client.get_artist,
        "playlist": client.get_playlist,
        "episode": client.get_episode,
        "show": client.get_show,
    }

    @mcp.tool()
    async def get_cover_image(value: str, kind: str = "track") -> Image:
        """Return an entity's cover art as an inline image.

        ``kind`` is one of track/album/artist/playlist/episode/show.
        """
        getter = _cover_getters.get(kind)
        if getter is None:
            raise ToolError(f"Unknown kind {kind!r}; use one of: {', '.join(_cover_getters)}.")
        entity = await _run(getter(value))
        try:
            image = _pick_cover(entity, "largest")
        except SpotifyScraperError as exc:
            raise ToolError(str(exc)) from exc
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as http:
            data = (await http.get(image.url)).content
        return Image(data=data, format="jpeg")

    # --- resources: addressable entities ----------------------------------- #

    @mcp.resource("spotify://track/{track_id}")
    async def track_resource(track_id: str) -> str:
        """A track as JSON."""
        return json.dumps((await _run(client.get_track(track_id))).to_dict())

    @mcp.resource("spotify://album/{album_id}")
    async def album_resource(album_id: str) -> str:
        """An album as JSON."""
        return json.dumps((await _run(client.get_album(album_id))).to_dict())

    @mcp.resource("spotify://artist/{artist_id}")
    async def artist_resource(artist_id: str) -> str:
        """An artist as JSON."""
        return json.dumps((await _run(client.get_artist(artist_id))).to_dict())

    @mcp.resource("spotify://playlist/{playlist_id}")
    async def playlist_resource(playlist_id: str) -> str:
        """A playlist as JSON."""
        return json.dumps((await _run(client.get_playlist(playlist_id))).to_dict())

    @mcp.resource("spotify://episode/{episode_id}")
    async def episode_resource(episode_id: str) -> str:
        """A podcast episode as JSON."""
        return json.dumps((await _run(client.get_episode(episode_id))).to_dict())

    @mcp.resource("spotify://show/{show_id}")
    async def show_resource(show_id: str) -> str:
        """A podcast show as JSON."""
        return json.dumps((await _run(client.get_show(show_id))).to_dict())

    # --- prompts ----------------------------------------------------------- #

    @mcp.prompt()
    def describe_album(album: str) -> str:
        """Prompt: describe an album's vibe."""
        return (
            f"Use get_album to fetch the Spotify album '{album}', then describe its "
            "overall vibe, themes, and a few standout tracks in two short paragraphs."
        )

    @mcp.prompt()
    def playlist_blurb(playlist: str) -> str:
        """Prompt: write a short blurb for a playlist."""
        return (
            f"Use get_playlist to fetch the Spotify playlist '{playlist}', then write a "
            "punchy two-sentence blurb capturing its mood and who it's for."
        )

    @mcp.prompt()
    def summarize_episode(episode: str) -> str:
        """Prompt: summarize a podcast episode from its transcript."""
        return (
            f"Use get_transcript to fetch the transcript of the Spotify podcast episode "
            f"'{episode}', then summarize the main topics and any notable takeaways."
        )

    return mcp
