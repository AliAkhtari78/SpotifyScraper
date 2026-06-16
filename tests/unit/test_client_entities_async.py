"""respx-driven tests for the asynchronous client's entity methods.

A 1:1 mirror of :mod:`tests.unit.test_client_entities` over the async client.
"""

from __future__ import annotations

import copy
import json
import logging
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest
import respx

from spotify_scraper import AsyncSpotifyClient
from spotify_scraper.http.transport import Response
from spotify_scraper.models.album import Album
from spotify_scraper.models.artist import Artist
from spotify_scraper.models.episode import Episode
from spotify_scraper.models.playlist import Playlist
from spotify_scraper.models.show import Show

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PATHFINDER_RE = re.compile(r"https://api-partner\.spotify\.com/pathfinder/v1/query.*")

IDS: dict[str, str] = {
    "album": "6N9PS4QXF1D0OWPk0Sxtb4",
    "artist": "0gxyHStUsqpMadRV0Di1Qt",
    "playlist": "37i9dQZF1DXcBWIGoYBM5M",
    "episode": "07gKzPFkbvGF0cHoeG7ARS",
    "show": "4rOoJ6Egrf8K2IrywzwOMk",
}


def _embed_next_data(kind: str) -> dict[str, Any]:
    return json.loads((FIXTURES / "embed" / f"{kind}.json").read_text())


def _pathfinder_body(kind: str) -> dict[str, Any]:
    return json.loads((FIXTURES / "pathfinder" / f"{kind}.json").read_text())


def _embed_url(kind: str, entity_id: str) -> str:
    return f"https://open.spotify.com/embed/{kind}/{entity_id}"


def _embed_html(kind: str, *, token: str = "EMBED_TOKEN") -> str:  # noqa: S107
    next_data = copy.deepcopy(_embed_next_data(kind))
    session = next_data["props"]["pageProps"]["state"]["settings"]["session"]
    session["accessToken"] = token
    session["accessTokenExpirationTimestampMs"] = 9_999_999_999_999
    body = json.dumps(next_data)
    return f'<script id="__NEXT_DATA__" type="application/json">{body}</script>'


def _mock(kind: str, *, pathfinder: Any) -> None:
    respx.get(_embed_url(kind, IDS[kind])).mock(
        return_value=httpx.Response(200, text=_embed_html(kind))
    )
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=pathfinder))


# --------------------------------------------------------------------------- #
# Happy paths
# --------------------------------------------------------------------------- #


@respx.mock
async def test_get_album_happy_path() -> None:
    _mock("album", pathfinder=_pathfinder_body("album"))
    async with AsyncSpotifyClient() as client:
        album = await client.get_album(IDS["album"])
    assert isinstance(album, Album)
    assert album.name == "Whenever You Need Somebody"
    assert album.album_type == "album"
    assert album.total_tracks == 10
    assert len(album.tracks) == 10


@respx.mock
async def test_get_artist_happy_path() -> None:
    _mock("artist", pathfinder=_pathfinder_body("artist"))
    async with AsyncSpotifyClient() as client:
        artist = await client.get_artist(IDS["artist"])
    assert isinstance(artist, Artist)
    assert artist.name == "Rick Astley"
    assert artist.monthly_listeners is not None
    assert artist.monthly_listeners > 0


@respx.mock
async def test_get_playlist_happy_path() -> None:
    _mock("playlist", pathfinder=_pathfinder_body("playlist"))
    async with AsyncSpotifyClient() as client:
        playlist = await client.get_playlist(IDS["playlist"], max_tracks=25)
    assert isinstance(playlist, Playlist)
    expected_name = _pathfinder_body("playlist")["data"]["playlistV2"]["name"]
    assert playlist.name == expected_name
    assert playlist.owner is not None
    assert playlist.owner.name == "Spotify"


@respx.mock
async def test_get_episode_happy_path() -> None:
    _mock("episode", pathfinder=_pathfinder_body("episode"))
    async with AsyncSpotifyClient() as client:
        episode = await client.get_episode(IDS["episode"])
    assert isinstance(episode, Episode)
    assert episode.name == "#2512 - Joey Diaz"
    assert episode.duration_ms > 0


def _show_episodes_page(offset: int, limit: int, total: int) -> dict[str, Any]:
    body = copy.deepcopy(_pathfinder_body("show_episodes"))
    node = body["data"]["podcastUnionV2"]["episodesV2"]
    template = node["items"][0]
    items: list[dict[str, Any]] = []
    for index in range(offset, min(offset + limit, total)):
        item = copy.deepcopy(template)
        item["entity"]["data"]["uri"] = f"spotify:episode:{index:022d}"
        item["entity"]["data"]["name"] = f"Episode {index}"
        items.append(item)
    node["items"] = items
    node["totalCount"] = total
    return body


def _show_router(metadata: dict[str, Any], *, total: int) -> Any:
    def handler(request: httpx.Request) -> httpx.Response:
        query = request.url.query.decode()
        operation = parse_qs(query)["operationName"][0]
        if operation == "queryShowMetadataV2":
            return httpx.Response(200, json=metadata)
        variables = json.loads(_variables(query))
        return httpx.Response(
            200, json=_show_episodes_page(variables["offset"], variables["limit"], total)
        )

    return handler


@respx.mock
async def test_get_show_happy_path() -> None:
    respx.get(_embed_url("show", IDS["show"])).mock(
        return_value=httpx.Response(200, text=_embed_html("show"))
    )
    respx.get(PATHFINDER_RE).mock(side_effect=_show_router(_pathfinder_body("show"), total=2707))
    async with AsyncSpotifyClient() as client:
        show = await client.get_show(IDS["show"], max_episodes=120)
    assert isinstance(show, Show)
    assert show.name == "The Joe Rogan Experience"
    assert show.publisher is not None
    assert show.publisher != ""
    assert show.total_episodes == 2707
    assert len(show.episodes) == 120


@respx.mock
async def test_pathfinder_uses_embed_token() -> None:
    respx.get(_embed_url("episode", IDS["episode"])).mock(
        return_value=httpx.Response(200, text=_embed_html("episode", token="TOK_A"))
    )
    route = respx.get(PATHFINDER_RE).mock(
        return_value=httpx.Response(200, json=_pathfinder_body("episode"))
    )
    async with AsyncSpotifyClient() as client:
        await client.get_episode(IDS["episode"])
    assert route.calls.last.request.headers["Authorization"] == "Bearer TOK_A"


# --------------------------------------------------------------------------- #
# Degradation
# --------------------------------------------------------------------------- #


@respx.mock
async def test_episode_degrades_to_embed_on_gql_error(caplog: pytest.LogCaptureFixture) -> None:
    respx.get(_embed_url("episode", IDS["episode"])).mock(
        return_value=httpx.Response(200, text=_embed_html("episode"))
    )
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(400, text="bad request"))

    with caplog.at_level(logging.WARNING, logger="spotify_scraper"):
        async with AsyncSpotifyClient() as client:
            episode = await client.get_episode(IDS["episode"])

    assert isinstance(episode, Episode)
    assert episode.name == "#2512 - Joey Diaz"
    assert episode.share_url is None
    assert any(record.levelno == logging.WARNING for record in caplog.records)
    assert "degraded" in caplog.text


# --------------------------------------------------------------------------- #
# Pagination
# --------------------------------------------------------------------------- #


def _playlist_page(uids: range) -> dict[str, Any]:
    """Build a one-page playlistV2 body with synthetic Track items."""
    body = copy.deepcopy(_pathfinder_body("playlist"))
    template = body["data"]["playlistV2"]["content"]["items"][0]
    items: list[dict[str, Any]] = []
    for index in uids:
        item = copy.deepcopy(template)
        item["uid"] = f"uid{index}"
        item["itemV2"]["data"]["uri"] = f"spotify:track:{index:022d}"
        item["itemV2"]["data"]["name"] = f"Track {index}"
        items.append(item)
    body["data"]["playlistV2"]["content"]["items"] = items
    body["data"]["playlistV2"]["content"]["totalCount"] = 50
    return body


@respx.mock
async def test_playlist_pagination_collects_all_pages() -> None:
    first = _playlist_page(range(0, 25))
    second = _playlist_page(range(25, 50))
    respx.get(_embed_url("playlist", IDS["playlist"])).mock(
        return_value=httpx.Response(200, text=_embed_html("playlist"))
    )
    pathfinder_route = respx.get(PATHFINDER_RE).mock(
        side_effect=[
            httpx.Response(200, json=first),
            httpx.Response(200, json=second),
        ]
    )

    async with AsyncSpotifyClient() as client:
        playlist = await client.get_playlist(IDS["playlist"], max_tracks=None)

    assert len(playlist.tracks) == 50
    assert pathfinder_route.call_count == 2
    offsets = [
        json.loads(_variables(call.request.url.query.decode()))["offset"]
        for call in pathfinder_route.calls
    ]
    assert offsets == [0, 25]


@respx.mock
async def test_playlist_pagination_stops_at_max_tracks() -> None:
    respx.get(_embed_url("playlist", IDS["playlist"])).mock(
        return_value=httpx.Response(200, text=_embed_html("playlist"))
    )
    route = respx.get(PATHFINDER_RE).mock(
        return_value=httpx.Response(200, json=_playlist_page(range(0, 25)))
    )

    async with AsyncSpotifyClient() as client:
        playlist = await client.get_playlist(IDS["playlist"], max_tracks=25)

    assert len(playlist.tracks) == 25
    assert route.call_count == 1


@respx.mock
async def test_playlist_pagination_tail_failure_returns_collected(
    caplog: pytest.LogCaptureFixture,
) -> None:
    respx.get(_embed_url("playlist", IDS["playlist"])).mock(
        return_value=httpx.Response(200, text=_embed_html("playlist"))
    )
    respx.get(PATHFINDER_RE).mock(
        side_effect=[
            httpx.Response(200, json=_playlist_page(range(0, 25))),
            httpx.Response(200, json={"errors": [{"message": "PersistedQueryNotFound"}]}),
        ]
    )

    with caplog.at_level(logging.WARNING, logger="spotify_scraper"):
        async with AsyncSpotifyClient() as client:
            playlist = await client.get_playlist(IDS["playlist"], max_tracks=None)

    assert len(playlist.tracks) == 25
    assert "stopped early" in caplog.text


@respx.mock
async def test_album_single_page_does_not_overpaginate() -> None:
    respx.get(_embed_url("album", IDS["album"])).mock(
        return_value=httpx.Response(200, text=_embed_html("album"))
    )
    route = respx.get(PATHFINDER_RE).mock(
        return_value=httpx.Response(200, json=_pathfinder_body("album"))
    )

    async with AsyncSpotifyClient() as client:
        album = await client.get_album(IDS["album"])

    assert len(album.tracks) == 10
    assert route.call_count == 1


# --------------------------------------------------------------------------- #
# Local-file skip, end to end
# --------------------------------------------------------------------------- #


@respx.mock
async def test_playlist_skips_local_file_items() -> None:
    body = copy.deepcopy(_pathfinder_body("playlist"))
    items = body["data"]["playlistV2"]["content"]["items"]
    local = copy.deepcopy(items[0])
    local["itemV2"]["data"]["__typename"] = "NotPlayable"
    local["itemV2"]["data"].pop("uri", None)
    body["data"]["playlistV2"]["content"]["items"] = [local, *items]
    body["data"]["playlistV2"]["content"]["totalCount"] = len(items) + 1

    respx.get(_embed_url("playlist", IDS["playlist"])).mock(
        return_value=httpx.Response(200, text=_embed_html("playlist"))
    )
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=body))

    async with AsyncSpotifyClient() as client:
        playlist = await client.get_playlist(IDS["playlist"], max_tracks=25)

    assert all(track.track.uri.startswith("spotify:track:") for track in playlist.tracks)


def _variables(query: str) -> str:
    return parse_qs(query)["variables"][0]


# --------------------------------------------------------------------------- #
# Custom transport (no network), proves wiring for one entity
# --------------------------------------------------------------------------- #


class _FakeResponse:
    def __init__(self, status_code: int, *, text: str = "", body: Any = None) -> None:
        self.status_code = status_code
        self._text = text
        self._body = body

    @property
    def headers(self) -> Mapping[str, str]:
        return {}

    @property
    def text(self) -> str:
        return self._text

    @property
    def content(self) -> bytes:
        return self._text.encode()

    def json(self) -> Any:
        return self._body


class _RecordingAsyncTransport:
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self.urls: list[str] = []
        self.closed = False

    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response:
        self.urls.append(url)
        if "pathfinder" in url:
            return _FakeResponse(200, body=_pathfinder_body(self.kind))
        return _FakeResponse(200, text=_embed_html(self.kind))

    async def aclose(self) -> None:
        self.closed = True


async def test_custom_transport_drives_get_show() -> None:
    transport = _RecordingAsyncTransport("show")
    client = AsyncSpotifyClient(transport=transport)
    show = await client.get_show(IDS["show"])
    assert show.name == "The Joe Rogan Experience"
    assert transport.urls[0] == _embed_url("show", IDS["show"])
    assert any("pathfinder" in url for url in transport.urls)
