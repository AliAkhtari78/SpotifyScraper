"""respx-driven tests for the asynchronous AsyncSpotifyClient."""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from spotify_scraper import AsyncSpotifyClient
from spotify_scraper.errors import NotFoundError, SpotifyScraperError
from spotify_scraper.http.transport import Response
from spotify_scraper.models.track import Track

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
TRACK_ID = "4uLU6hMCjMI75M1A2tKUQC"
EMBED_URL = f"https://open.spotify.com/embed/track/{TRACK_ID}"
PATHFINDER_RE = re.compile(r"https://api-partner\.spotify\.com/pathfinder/v1/query.*")

EMBED_NEXT_DATA: dict[str, Any] = json.loads((FIXTURES / "embed" / "track.json").read_text())
PATHFINDER_BODY: dict[str, Any] = json.loads((FIXTURES / "pathfinder" / "track.json").read_text())


def embed_html(*, expires_at_ms: int = 9_999_999_999_999, token: str = "EMBED_TOKEN") -> str:  # noqa: S107
    next_data = json.loads(json.dumps(EMBED_NEXT_DATA))
    session = next_data["props"]["pageProps"]["state"]["settings"]["session"]
    session["accessToken"] = token
    session["accessTokenExpirationTimestampMs"] = expires_at_ms
    body = json.dumps(next_data)
    return f'<script id="__NEXT_DATA__" type="application/json">{body}</script>'


def dead_embed_html() -> str:
    next_data = json.loads(json.dumps(EMBED_NEXT_DATA))
    next_data["props"]["pageProps"] = {"status": 404, "forbiddenReason": "NOT_FOUND"}
    body = json.dumps(next_data)
    return f'<script id="__NEXT_DATA__" type="application/json">{body}</script>'


@respx.mock
async def test_rich_path_merges_tier1_and_embed() -> None:
    respx.get(EMBED_URL).mock(return_value=httpx.Response(200, text=embed_html()))
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=PATHFINDER_BODY))

    async with AsyncSpotifyClient() as client:
        track = await client.get_track(TRACK_ID)

    assert isinstance(track, Track)
    assert track.name == "Never Gonna Give You Up"
    assert track.play_count == 1_137_719_792
    assert track.track_number == 1
    assert track.album is not None
    assert track.album.name == "Whenever You Need Somebody"
    assert track.preview_url is not None
    assert track.preview_url.startswith("https://p.scdn.co/")


@respx.mock
async def test_pathfinder_uses_embed_token() -> None:
    respx.get(EMBED_URL).mock(return_value=httpx.Response(200, text=embed_html(token="TOK_A")))
    route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=PATHFINDER_BODY))

    async with AsyncSpotifyClient() as client:
        await client.get_track(TRACK_ID)

    assert route.calls.last.request.headers["Authorization"] == "Bearer TOK_A"
    assert route.calls.last.request.headers["app-platform"] == "WebPlayer"


@respx.mock
async def test_degraded_path_returns_embed_track_with_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    respx.get(EMBED_URL).mock(return_value=httpx.Response(200, text=embed_html()))
    respx.get(PATHFINDER_RE).mock(
        return_value=httpx.Response(200, json={"errors": [{"message": "PersistedQueryNotFound"}]})
    )

    with caplog.at_level(logging.WARNING, logger="spotify_scraper"):
        async with AsyncSpotifyClient() as client:
            track = await client.get_track(TRACK_ID)

    assert track.name == "Never Gonna Give You Up"
    assert track.play_count is None
    assert track.album is None
    assert track.preview_url is not None
    assert any(record.levelno == logging.WARNING for record in caplog.records)
    assert "degraded" in caplog.text


@respx.mock
async def test_401_invalidates_rebootstraps_and_retries() -> None:
    embed_route = respx.get(EMBED_URL).mock(
        side_effect=[
            httpx.Response(200, text=embed_html(token="STALE_TOKEN")),
            httpx.Response(200, text=embed_html(token="FRESH_TOKEN")),
        ]
    )
    pathfinder_route = respx.get(PATHFINDER_RE).mock(
        side_effect=[
            httpx.Response(401),
            httpx.Response(200, json=PATHFINDER_BODY),
        ]
    )

    async with AsyncSpotifyClient() as client:
        track = await client.get_track(TRACK_ID)

    assert track.play_count == 1_137_719_792
    assert embed_route.call_count == 2
    assert pathfinder_route.call_count == 2
    first, second = (call.request.headers["Authorization"] for call in pathfinder_route.calls)
    assert first == "Bearer STALE_TOKEN"
    assert second == "Bearer FRESH_TOKEN"


@respx.mock
async def test_dead_entity_raises_not_found_without_pathfinder() -> None:
    respx.get(EMBED_URL).mock(return_value=httpx.Response(200, text=dead_embed_html()))
    pathfinder_route = respx.get(PATHFINDER_RE).mock(
        return_value=httpx.Response(200, json=PATHFINDER_BODY)
    )

    async with AsyncSpotifyClient() as client:
        with pytest.raises(NotFoundError):
            await client.get_track(TRACK_ID)

    assert pathfinder_route.call_count == 0


async def test_use_after_close_raises() -> None:
    client = AsyncSpotifyClient()
    await client.aclose()
    with pytest.raises(SpotifyScraperError):
        await client.get_track(TRACK_ID)


async def test_custom_transport_is_used() -> None:
    transport = _RecordingAsyncTransport()
    client = AsyncSpotifyClient(transport=transport)

    track = await client.get_track(TRACK_ID)

    assert track.play_count == 1_137_719_792
    assert transport.urls[0] == EMBED_URL
    assert any("pathfinder" in url for url in transport.urls)


async def test_injected_transport_is_not_closed_by_client() -> None:
    transport = _RecordingAsyncTransport()
    async with AsyncSpotifyClient(transport=transport):
        pass
    assert transport.closed is False


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
    def __init__(self) -> None:
        self.urls: list[str] = []
        self.closed = False

    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response:
        self.urls.append(url)
        if "pathfinder" in url:
            return _FakeResponse(200, body=PATHFINDER_BODY)
        return _FakeResponse(200, text=embed_html())

    async def aclose(self) -> None:
        self.closed = True
