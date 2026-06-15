"""respx-driven tests for the asynchronous client's plural batch helpers.

A 1:1 mirror of :mod:`tests.unit.test_client_batch` over the async client,
plus an async-only bounded-concurrency test that injects a recording stub
transport to prove in-flight entity fetches never exceed ``max_concurrency``
while still running more than one concurrently, and a ``max_concurrency=0``
validation test.
"""

from __future__ import annotations

import asyncio
import copy
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest
import respx

from spotify_scraper import AsyncSpotifyClient
from spotify_scraper.errors import NotFoundError, SpotifyScraperError, URLError
from spotify_scraper.http.transport import Response
from spotify_scraper.models.track import Track

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PATHFINDER_RE = re.compile(r"https://api-partner\.spotify\.com/pathfinder/v1/query.*")

IDS: dict[str, str] = {
    "album": "4aawyAB9vmqN3uQ7FjRGTy",
    "artist": "0gxyHStUsqpMadRV0Di1Qt",
    "playlist": "37i9dQZF1DXcBWIGoYBM5M",
    "episode": "07gKzPFkbvGF0cHoeG7ARS",
    "show": "4rOoJ6Egrf8K2IrywzwOMk",
    "track": "2QjOHCTQ1Jl3zawyYOpxh6",
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


def _variables(query: str) -> str:
    return parse_qs(query)["variables"][0]


# --------------------------------------------------------------------------- #
# Happy path
# --------------------------------------------------------------------------- #


@respx.mock
async def test_get_tracks_happy_path_ordered() -> None:
    ids = [IDS["track"], IDS["album"], IDS["artist"]]
    for entity_id in ids:
        respx.get(_embed_url("track", entity_id)).mock(
            return_value=httpx.Response(200, text=_embed_html("track"))
        )
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=_pathfinder_body("track")))

    async with AsyncSpotifyClient() as client:
        items = await client.get_tracks(ids)

    assert [item.value for item in items] == ids
    assert all(item.ok for item in items)
    assert all(isinstance(item.result, Track) for item in items)
    assert items[0].unwrap().name


# --------------------------------------------------------------------------- #
# Partial failure
# --------------------------------------------------------------------------- #


@respx.mock
async def test_get_tracks_partial_failure_preserves_order() -> None:
    good = IDS["track"]
    dead = IDS["album"]
    respx.get(_embed_url("track", good)).mock(
        return_value=httpx.Response(200, text=_embed_html("track"))
    )
    respx.get(_embed_url("track", dead)).mock(return_value=httpx.Response(404, text="nope"))
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=_pathfinder_body("track")))

    async with AsyncSpotifyClient() as client:
        items = await client.get_tracks([good, dead])

    assert [item.value for item in items] == [good, dead]
    assert items[0].ok
    assert isinstance(items[0].result, Track)
    assert not items[1].ok
    assert isinstance(items[1].error, NotFoundError)
    with pytest.raises(NotFoundError):
        items[1].unwrap()


# --------------------------------------------------------------------------- #
# Malformed input
# --------------------------------------------------------------------------- #


@respx.mock
async def test_get_tracks_malformed_input_captured_as_urlerror() -> None:
    good = IDS["track"]
    bad = "not-a-spotify-id"
    respx.get(_embed_url("track", good)).mock(
        return_value=httpx.Response(200, text=_embed_html("track"))
    )
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=_pathfinder_body("track")))

    async with AsyncSpotifyClient() as client:
        items = await client.get_tracks([bad, good])

    assert [item.value for item in items] == [bad, good]
    assert not items[0].ok
    assert isinstance(items[0].error, URLError)
    assert items[1].ok


# --------------------------------------------------------------------------- #
# Fail-fast on a closed client
# --------------------------------------------------------------------------- #


async def test_get_tracks_closed_client_raises_up_front() -> None:
    client = AsyncSpotifyClient()
    await client.aclose()
    with pytest.raises(SpotifyScraperError):
        await client.get_tracks([IDS["track"]])


# --------------------------------------------------------------------------- #
# Cap forwarding
# --------------------------------------------------------------------------- #


def _playlist_page(count: int) -> dict[str, Any]:
    body = copy.deepcopy(_pathfinder_body("playlist"))
    template = body["data"]["playlistV2"]["content"]["items"][0]
    items: list[dict[str, Any]] = []
    for index in range(count):
        item = copy.deepcopy(template)
        item["uid"] = f"uid{index}"
        item["itemV2"]["data"]["uri"] = f"spotify:track:{index:022d}"
        item["itemV2"]["data"]["name"] = f"Track {index}"
        items.append(item)
    body["data"]["playlistV2"]["content"]["items"] = items
    body["data"]["playlistV2"]["content"]["totalCount"] = 500
    return body


@respx.mock
async def test_get_playlists_forwards_max_tracks() -> None:
    respx.get(_embed_url("playlist", IDS["playlist"])).mock(
        return_value=httpx.Response(200, text=_embed_html("playlist"))
    )
    route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=_playlist_page(50)))

    async with AsyncSpotifyClient() as client:
        items = await client.get_playlists([IDS["playlist"]], max_tracks=10)

    assert items[0].ok
    assert len(items[0].unwrap().tracks) == 10
    assert route.call_count == 1


def _show_router(metadata: dict[str, Any], *, total: int) -> Any:
    def _show_episodes_page(offset: int, limit: int) -> dict[str, Any]:
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

    def handler(request: httpx.Request) -> httpx.Response:
        query = request.url.query.decode()
        operation = parse_qs(query)["operationName"][0]
        if operation == "queryShowMetadataV2":
            return httpx.Response(200, json=metadata)
        variables = json.loads(_variables(query))
        return httpx.Response(
            200, json=_show_episodes_page(variables["offset"], variables["limit"])
        )

    return handler


@respx.mock
async def test_get_shows_forwards_max_episodes() -> None:
    respx.get(_embed_url("show", IDS["show"])).mock(
        return_value=httpx.Response(200, text=_embed_html("show"))
    )
    respx.get(PATHFINDER_RE).mock(side_effect=_show_router(_pathfinder_body("show"), total=2707))

    async with AsyncSpotifyClient() as client:
        items = await client.get_shows([IDS["show"]], max_episodes=10)

    assert items[0].ok
    assert len(items[0].unwrap().episodes) == 10


# --------------------------------------------------------------------------- #
# Bounded concurrency (async only)
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


class _ConcurrencyProbeTransport:
    """Records the peak number of concurrent entity pipelines.

    Each entity pipeline starts with an embed ``get``; that call increments an
    in-flight counter, waits on a barrier until ``max_concurrency`` pipelines
    have arrived (deterministic overlap, no sleeps), records the peak, then
    releases. Subsequent pathfinder ``get`` calls return immediately.
    """

    def __init__(self, *, expected_batch: int, gate_at: int) -> None:
        self._gate_at = gate_at
        self._lock = asyncio.Lock()
        self._in_flight = 0
        self.peak_in_flight = 0
        # Released once gate_at coroutines are simultaneously in flight, or
        # once every pipeline has started (so the last, smaller wave proceeds).
        self._release = asyncio.Event()
        self._started = 0
        self._expected = expected_batch

    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response:
        if "pathfinder" in url:
            return _FakeResponse(200, body=_pathfinder_body("track"))
        # Embed request: this is the entry point of one entity pipeline.
        async with self._lock:
            self._in_flight += 1
            self._started += 1
            self.peak_in_flight = max(self.peak_in_flight, self._in_flight)
            if self._in_flight >= self._gate_at or self._started >= self._expected:
                self._release.set()
        await self._release.wait()
        async with self._lock:
            self._in_flight -= 1
            if self._in_flight == 0:
                self._release.clear()
        return _FakeResponse(200, text=_embed_html("track"))

    async def aclose(self) -> None:
        return None


async def test_get_tracks_bounded_by_max_concurrency() -> None:
    ids = [f"{i:022d}" for i in range(8)]
    transport = _ConcurrencyProbeTransport(expected_batch=len(ids), gate_at=2)
    client = AsyncSpotifyClient(transport=transport, max_concurrency=2)
    items = await client.get_tracks(ids)

    assert [item.value for item in items] == ids
    assert all(item.ok for item in items)
    # The semaphore bounds fan-out but does not serialize it.
    assert transport.peak_in_flight <= 2
    assert transport.peak_in_flight > 1


async def test_max_concurrency_zero_rejected() -> None:
    with pytest.raises(ValueError, match="max_concurrency"):
        AsyncSpotifyClient(max_concurrency=0)


class _LoopAgnosticTransport:
    """A minimal stub with no asyncio state, so it is reusable across loops."""

    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response:
        if "pathfinder" in url:
            return _FakeResponse(200, body=_pathfinder_body("track"))
        return _FakeResponse(200, text=_embed_html("track"))

    async def aclose(self) -> None:
        return None


def test_async_client_reused_across_event_loops() -> None:
    # Regression: the per-client concurrency semaphore must be created per running
    # loop, not bound at construction. max_concurrency=1 forces the semaphore to
    # suspend a waiter (which is what binds it to a loop), so reusing the client
    # from a second asyncio.run() would raise "bound to a different event loop".
    ids = [f"{i:022d}" for i in range(3)]
    client = AsyncSpotifyClient(transport=_LoopAgnosticTransport(), max_concurrency=1)

    first = asyncio.run(client.get_tracks(ids))
    second = asyncio.run(client.get_tracks(ids))  # a fresh event loop

    assert all(item.ok for item in first)
    assert all(item.ok for item in second)
    assert [item.value for item in second] == ids
