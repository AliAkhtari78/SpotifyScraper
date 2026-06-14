"""respx-driven tests for sync and async ``search`` on both clients.

Search skips entity embed pages entirely; the only embed fetched is the
anonymous-token bootstrap (``DEFAULT_BOOTSTRAP_ID``), which seeds the bearer
token search shares with the entity getters.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from spotify_scraper import AsyncSpotifyClient, SpotifyClient
from spotify_scraper.auth.anonymous import DEFAULT_BOOTSTRAP_ID
from spotify_scraper.errors import SpotifyScraperError, URLError

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
BOOTSTRAP_URL = f"https://open.spotify.com/embed/track/{DEFAULT_BOOTSTRAP_ID}"
PATHFINDER_RE = re.compile(r"https://api-partner\.spotify\.com/pathfinder/v1/query.*")

SEARCH_BODY: dict[str, Any] = json.loads(
    (FIXTURES / "pathfinder" / "search.json").read_text(encoding="utf-8")
)
EMBED_NEXT_DATA: dict[str, Any] = json.loads(
    (FIXTURES / "embed" / "track.json").read_text(encoding="utf-8")
)


def _bootstrap_html(*, token: str = "ANON_TOKEN") -> str:  # noqa: S107
    next_data = json.loads(json.dumps(EMBED_NEXT_DATA))
    session = next_data["props"]["pageProps"]["state"]["settings"]["session"]
    session["accessToken"] = token
    session["accessTokenExpirationTimestampMs"] = 9_999_999_999_999
    body = json.dumps(next_data)
    return f'<script id="__NEXT_DATA__" type="application/json">{body}</script>'


def _mock_bootstrap(*, token: str = "ANON_TOKEN") -> None:  # noqa: S107
    respx.get(BOOTSTRAP_URL).mock(
        return_value=httpx.Response(200, text=_bootstrap_html(token=token))
    )


# --------------------------------------------------------------------------- #
# Sync
# --------------------------------------------------------------------------- #


@respx.mock
def test_search_populates_all_sections() -> None:
    _mock_bootstrap()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=SEARCH_BODY))
    with SpotifyClient() as client:
        results = client.search("daft punk")
    assert results.query == "daft punk"
    assert results.tracks[0].name == "One More Time"
    assert results.artists[0].name == "Daft Punk"
    assert results.albums[0].name == "Random Access Memories"
    assert len(results.playlists) == 3
    assert len(results.shows) == 3
    assert len(results.episodes) == 3
    assert results.total == 1000


@respx.mock
def test_search_sends_bearer_and_platform_headers() -> None:
    _mock_bootstrap(token="ANON_TOKEN")
    route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=SEARCH_BODY))
    with SpotifyClient() as client:
        client.search("daft punk")
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer ANON_TOKEN"
    assert request.headers["app-platform"] == "WebPlayer"
    assert "operationName=searchDesktop" in str(request.url)


@respx.mock
def test_search_types_filter_restricts_sections() -> None:
    _mock_bootstrap()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=SEARCH_BODY))
    with SpotifyClient() as client:
        results = client.search("daft punk", types=("artist",))
    assert len(results.artists) == 3
    assert results.tracks == ()
    assert results.albums == ()
    assert results.playlists == ()
    assert results.shows == ()
    assert results.episodes == ()


@respx.mock
def test_search_limit_override_in_variables() -> None:
    _mock_bootstrap()
    route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=SEARCH_BODY))
    with SpotifyClient() as client:
        client.search("daft punk", limit=7)
    variables = dict(httpx.QueryParams(route.calls.last.request.url.query))
    assert json.loads(variables["variables"])["limit"] == 7


@respx.mock
def test_search_401_invalidates_and_retries_once() -> None:
    respx.get(BOOTSTRAP_URL).mock(
        side_effect=[
            httpx.Response(200, text=_bootstrap_html(token="STALE")),
            httpx.Response(200, text=_bootstrap_html(token="FRESH")),
        ]
    )
    pathfinder_route = respx.get(PATHFINDER_RE).mock(
        side_effect=[httpx.Response(401), httpx.Response(200, json=SEARCH_BODY)]
    )
    with SpotifyClient() as client:
        results = client.search("daft punk")
    assert len(results.tracks) == 3
    assert pathfinder_route.call_count == 2
    first, second = (call.request.headers["Authorization"] for call in pathfinder_route.calls)
    assert first == "Bearer STALE"
    assert second == "Bearer FRESH"


@respx.mock
def test_search_empty_results_is_not_an_error() -> None:
    _mock_bootstrap()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json={"data": {"searchV2": {}}}))
    with SpotifyClient() as client:
        results = client.search("zzzzz no hits")
    assert results.tracks == ()
    assert results.total is None


def test_search_unknown_type_raises_url_error_without_request() -> None:
    pathfinder_route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json={}))
    with SpotifyClient() as client, pytest.raises(URLError, match="bogus"):
        client.search("daft punk", types=("bogus",))
    assert pathfinder_route.call_count == 0


def test_search_use_after_close_raises() -> None:
    client = SpotifyClient()
    client.close()
    with pytest.raises(SpotifyScraperError):
        client.search("daft punk")


# --------------------------------------------------------------------------- #
# Async
# --------------------------------------------------------------------------- #


@respx.mock
async def test_search_populates_all_sections_async() -> None:
    _mock_bootstrap()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=SEARCH_BODY))
    async with AsyncSpotifyClient() as client:
        results = await client.search("daft punk")
    assert results.tracks[0].name == "One More Time"
    assert results.artists[0].name == "Daft Punk"
    assert results.total == 1000


@respx.mock
async def test_search_types_filter_restricts_sections_async() -> None:
    _mock_bootstrap()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=SEARCH_BODY))
    async with AsyncSpotifyClient() as client:
        results = await client.search("daft punk", types=("track",))
    assert len(results.tracks) == 3
    assert results.artists == ()


@respx.mock
async def test_search_401_invalidates_and_retries_once_async() -> None:
    respx.get(BOOTSTRAP_URL).mock(
        side_effect=[
            httpx.Response(200, text=_bootstrap_html(token="STALE")),
            httpx.Response(200, text=_bootstrap_html(token="FRESH")),
        ]
    )
    pathfinder_route = respx.get(PATHFINDER_RE).mock(
        side_effect=[httpx.Response(401), httpx.Response(200, json=SEARCH_BODY)]
    )
    async with AsyncSpotifyClient() as client:
        results = await client.search("daft punk")
    assert len(results.tracks) == 3
    assert pathfinder_route.call_count == 2


async def test_search_unknown_type_raises_url_error_async() -> None:
    async with AsyncSpotifyClient() as client:
        with pytest.raises(URLError):
            await client.search("daft punk", types=("bogus",))


async def test_search_use_after_close_raises_async() -> None:
    client = AsyncSpotifyClient()
    await client.aclose()
    with pytest.raises(SpotifyScraperError):
        await client.search("daft punk")
