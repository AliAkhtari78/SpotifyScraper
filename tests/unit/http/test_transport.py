"""respx-driven tests for the synchronous HttpxTransport."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

from spotify_scraper.errors import NetworkError, NotFoundError, RateLimitedError
from spotify_scraper.http import HttpxTransport, Response, RetryPolicy, Transport
from spotify_scraper.http.headers import USER_AGENTS

URL = "https://open.spotify.com/embed/track/4uLU6hMCjMI75M1A2tKUQC"
FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
TRACK_PAYLOAD: dict[str, Any] = json.loads((FIXTURES / "embed" / "track.json").read_text())

NO_BACKOFF = RetryPolicy(max_attempts=4, backoff_base=0.0)


@pytest.fixture
def transport() -> HttpxTransport:
    return HttpxTransport(retry=NO_BACKOFF)


@respx.mock
def test_success_returns_response(transport: HttpxTransport) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, json=TRACK_PAYLOAD))

    response = transport.get(URL)

    assert response.status_code == 200
    assert response.json() == TRACK_PAYLOAD
    transport.close()


@respx.mock
def test_503_then_200_retries_transparently(transport: HttpxTransport) -> None:
    route = respx.get(URL).mock(
        side_effect=[httpx.Response(503), httpx.Response(200, json=TRACK_PAYLOAD)]
    )

    response = transport.get(URL)

    assert response.status_code == 200
    assert route.call_count == 2


@respx.mock
def test_5xx_exhausted_raises_network_error() -> None:
    route = respx.get(URL).mock(return_value=httpx.Response(503))
    transport = HttpxTransport(retry=RetryPolicy(max_attempts=2, backoff_base=0.0))

    with pytest.raises(NetworkError) as excinfo:
        transport.get(URL)

    assert excinfo.value.request_url == URL
    assert route.call_count == 2


@respx.mock
def test_403_then_200_retries_transparently(transport: HttpxTransport) -> None:
    route = respx.get(URL).mock(
        side_effect=[httpx.Response(403), httpx.Response(200, json=TRACK_PAYLOAD)]
    )

    response = transport.get(URL)

    assert response.status_code == 200
    assert route.call_count == 2


@respx.mock
def test_403_exhausted_raises_network_error() -> None:
    route = respx.get(URL).mock(return_value=httpx.Response(403))
    transport = HttpxTransport(retry=RetryPolicy(max_attempts=2, backoff_base=0.0))

    with pytest.raises(NetworkError) as excinfo:
        transport.get(URL)

    assert excinfo.value.request_url == URL
    assert route.call_count == 2


@respx.mock
def test_429_hard_raise_carries_retry_after(transport: HttpxTransport) -> None:
    route = respx.get(URL).mock(return_value=httpx.Response(429, headers={"Retry-After": "47231"}))

    with pytest.raises(RateLimitedError) as excinfo:
        transport.get(URL)

    assert excinfo.value.retry_after == 47231
    assert excinfo.value.request_url == URL
    assert route.call_count == 1


@respx.mock
def test_429_with_small_retry_after_is_retried(transport: HttpxTransport) -> None:
    route = respx.get(URL).mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json=TRACK_PAYLOAD),
        ]
    )

    response = transport.get(URL)

    assert response.status_code == 200
    assert route.call_count == 2


@respx.mock
def test_404_raises_not_found(transport: HttpxTransport) -> None:
    respx.get(URL).mock(return_value=httpx.Response(404))

    with pytest.raises(NotFoundError):
        transport.get(URL)


@respx.mock
def test_connect_error_maps_to_network_error_with_cause() -> None:
    respx.get(URL).mock(side_effect=httpx.ConnectError("dns failure"))
    transport = HttpxTransport(retry=RetryPolicy(max_attempts=2, backoff_base=0.0))

    with pytest.raises(NetworkError) as excinfo:
        transport.get(URL)

    assert excinfo.value.request_url == URL
    assert isinstance(excinfo.value.__cause__, httpx.ConnectError)


@respx.mock
def test_ua_pool_variety_across_instances() -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, json=TRACK_PAYLOAD))
    seen: set[str] = set()
    for _ in range(24):
        transport = HttpxTransport(retry=NO_BACKOFF)
        transport.get(URL)
        transport.close()
    seen = {call.request.headers["User-Agent"] for call in respx.calls}

    assert seen <= set(USER_AGENTS)
    assert len(seen) > 1


@respx.mock
def test_ua_stable_within_instance(transport: HttpxTransport) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, json=TRACK_PAYLOAD))

    transport.get(URL)
    transport.get(URL)

    first, second = (call.request.headers["User-Agent"] for call in respx.calls)
    assert first == second


@respx.mock
def test_explicit_user_agent_wins() -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, json=TRACK_PAYLOAD))
    transport = HttpxTransport(retry=NO_BACKOFF, user_agent="custom-agent/1.0")

    transport.get(URL)

    assert respx.calls.last.request.headers["User-Agent"] == "custom-agent/1.0"


@respx.mock
def test_caller_headers_merge_over_defaults(transport: HttpxTransport) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, json=TRACK_PAYLOAD))

    transport.get(URL, headers={"Authorization": "Bearer xyz", "Accept-Language": "de"})

    sent = respx.calls.last.request.headers
    assert sent["Authorization"] == "Bearer xyz"
    assert sent["Accept-Language"] == "de"
    assert sent["User-Agent"] in USER_AGENTS
    assert "text/html" in sent["Accept"]


def test_httpx_transport_satisfies_protocol() -> None:
    transport = HttpxTransport()
    assert isinstance(transport, Transport)
    transport.close()


def test_custom_object_satisfies_protocol() -> None:
    class FakeTransport:
        def get(self, url: str, *, headers: dict[str, str] | None = None) -> Response:
            return httpx.Response(200, request=httpx.Request("GET", url))

        def close(self) -> None:
            return None

    assert isinstance(FakeTransport(), Transport)
    assert not isinstance(object(), Transport)
