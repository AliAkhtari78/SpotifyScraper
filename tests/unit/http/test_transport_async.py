"""respx-driven tests for the asynchronous AsyncHttpxTransport."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from spotify_scraper.errors import NetworkError, NotFoundError, RateLimitedError
from spotify_scraper.http import AsyncHttpxTransport, AsyncTransport, Response, RetryPolicy
from spotify_scraper.http.headers import USER_AGENTS

URL = "https://open.spotify.com/embed/track/4uLU6hMCjMI75M1A2tKUQC"
FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
TRACK_PAYLOAD: dict[str, Any] = json.loads((FIXTURES / "embed" / "track.json").read_text())

NO_BACKOFF = RetryPolicy(max_attempts=4, backoff_base=0.0)


@respx.mock
async def test_success_returns_response() -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, json=TRACK_PAYLOAD))
    transport = AsyncHttpxTransport(retry=NO_BACKOFF)

    response = await transport.get(URL)

    assert response.status_code == 200
    assert response.json() == TRACK_PAYLOAD
    await transport.aclose()


@respx.mock
async def test_503_then_200_retries_transparently() -> None:
    route = respx.get(URL).mock(
        side_effect=[httpx.Response(503), httpx.Response(200, json=TRACK_PAYLOAD)]
    )
    transport = AsyncHttpxTransport(retry=NO_BACKOFF)

    response = await transport.get(URL)

    assert response.status_code == 200
    assert route.call_count == 2


@respx.mock
async def test_5xx_exhausted_raises_network_error() -> None:
    route = respx.get(URL).mock(return_value=httpx.Response(503))
    transport = AsyncHttpxTransport(retry=RetryPolicy(max_attempts=2, backoff_base=0.0))

    with pytest.raises(NetworkError) as excinfo:
        await transport.get(URL)

    assert excinfo.value.request_url == URL
    assert route.call_count == 2


@respx.mock
async def test_429_hard_raise_carries_retry_after() -> None:
    route = respx.get(URL).mock(return_value=httpx.Response(429, headers={"Retry-After": "47231"}))
    transport = AsyncHttpxTransport(retry=NO_BACKOFF)

    with pytest.raises(RateLimitedError) as excinfo:
        await transport.get(URL)

    assert excinfo.value.retry_after == 47231
    assert excinfo.value.request_url == URL
    assert route.call_count == 1


@respx.mock
async def test_404_raises_not_found() -> None:
    respx.get(URL).mock(return_value=httpx.Response(404))
    transport = AsyncHttpxTransport(retry=NO_BACKOFF)

    with pytest.raises(NotFoundError):
        await transport.get(URL)


@respx.mock
async def test_connect_error_maps_to_network_error_with_cause() -> None:
    respx.get(URL).mock(side_effect=httpx.ConnectError("dns failure"))
    transport = AsyncHttpxTransport(retry=RetryPolicy(max_attempts=2, backoff_base=0.0))

    with pytest.raises(NetworkError) as excinfo:
        await transport.get(URL)

    assert excinfo.value.request_url == URL
    assert isinstance(excinfo.value.__cause__, httpx.ConnectError)


@respx.mock
async def test_ua_pool_variety_across_instances() -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, json=TRACK_PAYLOAD))
    for _ in range(24):
        transport = AsyncHttpxTransport(retry=NO_BACKOFF)
        await transport.get(URL)
        await transport.aclose()
    seen = {call.request.headers["User-Agent"] for call in respx.calls}

    assert seen <= set(USER_AGENTS)
    assert len(seen) > 1


@respx.mock
async def test_caller_headers_merge_over_defaults() -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, json=TRACK_PAYLOAD))
    transport = AsyncHttpxTransport(retry=NO_BACKOFF)

    await transport.get(URL, headers={"Authorization": "Bearer xyz", "Accept-Language": "de"})

    sent = respx.calls.last.request.headers
    assert sent["Authorization"] == "Bearer xyz"
    assert sent["Accept-Language"] == "de"
    assert sent["User-Agent"] in USER_AGENTS


def test_async_httpx_transport_satisfies_protocol() -> None:
    transport = AsyncHttpxTransport()
    assert isinstance(transport, AsyncTransport)


def test_custom_object_satisfies_protocol() -> None:
    class FakeAsyncTransport:
        async def get(self, url: str, *, headers: dict[str, str] | None = None) -> Response:
            return httpx.Response(200, request=httpx.Request("GET", url))

        async def aclose(self) -> None:
            return None

    assert isinstance(FakeAsyncTransport(), AsyncTransport)
    assert not isinstance(object(), AsyncTransport)
