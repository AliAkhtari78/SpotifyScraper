"""respx-driven tests for cookie-authenticated Canvas extraction."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from spotify_scraper import AsyncSpotifyClient, SpotifyClient
from spotify_scraper.errors import AuthenticationError

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
TRACK_ID = "4LfCY65LvojKjWEnU7fNN4"
SP_DC = "sp_dc_secret_value"
SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
TOKEN_RE = re.compile(r"https://open\.spotify\.com/api/token.*")
PATHFINDER_RE = re.compile(r"https://api-partner\.spotify\.com/pathfinder/v1/query.*")

CANVAS_BODY: dict[str, Any] = json.loads(
    (FIXTURES / "pathfinder" / "canvas.json").read_text(encoding="utf-8")
)
CANVAS_ABSENT: dict[str, Any] = json.loads(
    (FIXTURES / "pathfinder" / "canvas_absent.json").read_text(encoding="utf-8")
)
CANVAS_URL: str = CANVAS_BODY["data"]["trackUnion"]["canvas"]["url"]


def _token_body(*, anonymous: bool = False) -> dict[str, Any]:
    return {
        "accessToken": "USER_TOKEN",
        "accessTokenExpirationTimestampMs": 9_999_999_999_999,
        "isAnonymous": anonymous,
    }


def _mock_token() -> None:
    respx.get(SERVER_TIME_URL).mock(
        return_value=httpx.Response(200, json={"serverTime": 1_700_000_000})
    )
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))


# --------------------------------------------------------------------------- #
# Sync
# --------------------------------------------------------------------------- #


def test_no_cookies_raises_without_network() -> None:
    with respx.mock(assert_all_mocked=True) as router, SpotifyClient() as client:
        with pytest.raises(AuthenticationError):
            client.get_canvas(TRACK_ID)
        assert len(router.calls) == 0


@respx.mock
def test_get_canvas_present() -> None:
    _mock_token()
    route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=CANVAS_BODY))
    with SpotifyClient(cookies=SP_DC) as client:
        canvas = client.get_canvas(TRACK_ID)
    assert canvas is not None
    assert canvas.url == CANVAS_URL
    assert canvas.uri.startswith("spotify:canvas:")
    assert canvas.id and canvas.canvas_type
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer USER_TOKEN"
    assert request.headers["app-platform"] == "WebPlayer"
    assert "operationName=canvas" in str(request.url)


@respx.mock
def test_get_canvas_absent_returns_none() -> None:
    _mock_token()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=CANVAS_ABSENT))
    with SpotifyClient(cookies=SP_DC) as client:
        canvas = client.get_canvas("4uLU6hMCjMI75M1A2tKUQC")
    assert canvas is None


@respx.mock
def test_canvas_401_invalidates_and_retries_once() -> None:
    _mock_token()
    token_route = respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    canvas_route = respx.get(PATHFINDER_RE).mock(
        side_effect=[httpx.Response(401), httpx.Response(200, json=CANVAS_BODY)]
    )
    with SpotifyClient(cookies=SP_DC) as client:
        canvas = client.get_canvas(TRACK_ID)
    assert canvas is not None
    assert canvas_route.call_count == 2
    assert token_route.call_count == 2


@respx.mock
def test_download_canvas_writes_file(tmp_path: Path) -> None:
    _mock_token()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=CANVAS_BODY))
    respx.get(CANVAS_URL).mock(return_value=httpx.Response(200, content=b"MP4DATA"))
    with SpotifyClient(cookies=SP_DC) as client:
        path = client.download_canvas(TRACK_ID, tmp_path)
    assert path.exists()
    assert path.read_bytes() == b"MP4DATA"
    assert path.suffix == ".mp4"


# --------------------------------------------------------------------------- #
# Async
# --------------------------------------------------------------------------- #


@respx.mock
async def test_get_canvas_present_async() -> None:
    _mock_token()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=CANVAS_BODY))
    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        canvas = await client.get_canvas(TRACK_ID)
    assert canvas is not None
    assert canvas.url == CANVAS_URL


@respx.mock
async def test_get_canvas_absent_returns_none_async() -> None:
    _mock_token()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=CANVAS_ABSENT))
    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        canvas = await client.get_canvas("4uLU6hMCjMI75M1A2tKUQC")
    assert canvas is None


async def test_no_cookies_raises_without_network_async() -> None:
    async with AsyncSpotifyClient() as client:
        with respx.mock(assert_all_mocked=True) as router:
            with pytest.raises(AuthenticationError):
                await client.get_canvas(TRACK_ID)
            assert len(router.calls) == 0


@respx.mock
async def test_download_canvas_writes_file_async(tmp_path: Path) -> None:
    _mock_token()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=CANVAS_BODY))
    respx.get(CANVAS_URL).mock(return_value=httpx.Response(200, content=b"MP4DATA"))
    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        path = await client.download_canvas(TRACK_ID, tmp_path)
    assert path.exists()
    assert path.read_bytes() == b"MP4DATA"
