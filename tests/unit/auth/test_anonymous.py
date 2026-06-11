"""Tests for the anonymous token providers."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.auth.anonymous import (
    EXPIRY_SKEW_MS,
    AnonymousTokenProvider,
    AsyncAnonymousTokenProvider,
    is_stale,
)
from spotify_scraper.errors import NetworkError, TokenError

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "embed"

NOW_MS = 1_700_000_000_000
EXPIRES_MS = NOW_MS + 3_600_000


def build_embed_html(expires_at_ms: int) -> str:
    next_data = json.loads((FIXTURES / "track.json").read_text())
    session = next_data["props"]["pageProps"]["state"]["settings"]["session"]
    session["accessToken"] = "BOOTSTRAP_TOKEN"
    session["accessTokenExpirationTimestampMs"] = expires_at_ms
    body = json.dumps(next_data)
    return f'<script id="__NEXT_DATA__" type="application/json">{body}</script>'


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.status_code = 200
        self._text = text

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
        return json.loads(self._text)


class FakeTransport:
    def __init__(self, html: str) -> None:
        self._html = html
        self.calls = 0

    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> FakeResponse:
        self.calls += 1
        return FakeResponse(self._html)

    def close(self) -> None:
        return None


class FakeAsyncTransport:
    def __init__(self, html: str) -> None:
        self._html = html
        self.calls = 0

    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> FakeResponse:
        self.calls += 1
        return FakeResponse(self._html)

    async def aclose(self) -> None:
        return None


class FailingTransport:
    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> FakeResponse:
        raise NetworkError("boom", request_url=url)

    def close(self) -> None:
        return None


class TokenlessTransport:
    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> FakeResponse:
        return FakeResponse("<html><body>no next data</body></html>")

    def close(self) -> None:
        return None


class AsyncTokenlessTransport:
    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> FakeResponse:
        return FakeResponse("<html><body>no next data</body></html>")

    async def aclose(self) -> None:
        return None


def test_is_stale_boundaries() -> None:
    assert is_stale(EXPIRES_MS, EXPIRES_MS) is True
    assert is_stale(EXPIRES_MS, EXPIRES_MS - EXPIRY_SKEW_MS) is True
    assert is_stale(EXPIRES_MS, EXPIRES_MS - EXPIRY_SKEW_MS - 1) is False


def test_cache_hit_one_fetch_for_two_calls() -> None:
    transport = FakeTransport(build_embed_html(EXPIRES_MS))
    provider = AnonymousTokenProvider(transport, now_ms=lambda: NOW_MS)
    first = provider.token()
    second = provider.token()
    assert first == second == "BOOTSTRAP_TOKEN"
    assert transport.calls == 1


def test_expiry_skew_triggers_refresh() -> None:
    transport = FakeTransport(build_embed_html(EXPIRES_MS))
    clock = [NOW_MS]
    provider = AnonymousTokenProvider(transport, now_ms=lambda: clock[0])
    provider.token()
    assert transport.calls == 1
    clock[0] = EXPIRES_MS - EXPIRY_SKEW_MS
    provider.token()
    assert transport.calls == 2


def test_invalidate_forces_refetch() -> None:
    transport = FakeTransport(build_embed_html(EXPIRES_MS))
    provider = AnonymousTokenProvider(transport, now_ms=lambda: NOW_MS)
    provider.token()
    provider.invalidate()
    provider.token()
    assert transport.calls == 2


def test_token_error_on_network_failure() -> None:
    provider = AnonymousTokenProvider(FailingTransport(), now_ms=lambda: NOW_MS)
    with pytest.raises(TokenError) as excinfo:
        provider.token()
    assert isinstance(excinfo.value.__cause__, NetworkError)


def test_token_error_on_tokenless_payload_has_no_token_text() -> None:
    provider = AnonymousTokenProvider(TokenlessTransport(), now_ms=lambda: NOW_MS)
    with pytest.raises(TokenError) as excinfo:
        provider.token()
    assert "BOOTSTRAP_TOKEN" not in str(excinfo.value)
    assert "REDACTED" not in str(excinfo.value)


def test_repr_has_no_token() -> None:
    transport = FakeTransport(build_embed_html(EXPIRES_MS))
    provider = AnonymousTokenProvider(transport, now_ms=lambda: NOW_MS)
    provider.token()
    assert "BOOTSTRAP_TOKEN" not in repr(provider)
    assert "REDACTED" not in repr(provider)
    assert "cached=True" in repr(provider)


async def test_async_cache_hit_one_fetch_for_two_calls() -> None:
    transport = FakeAsyncTransport(build_embed_html(EXPIRES_MS))
    provider = AsyncAnonymousTokenProvider(transport, now_ms=lambda: NOW_MS)
    first = await provider.token()
    second = await provider.token()
    assert first == second == "BOOTSTRAP_TOKEN"
    assert transport.calls == 1


async def test_async_expiry_skew_triggers_refresh() -> None:
    transport = FakeAsyncTransport(build_embed_html(EXPIRES_MS))
    clock = [NOW_MS]
    provider = AsyncAnonymousTokenProvider(transport, now_ms=lambda: clock[0])
    await provider.token()
    clock[0] = EXPIRES_MS - EXPIRY_SKEW_MS
    await provider.token()
    assert transport.calls == 2


async def test_async_invalidate_forces_refetch() -> None:
    transport = FakeAsyncTransport(build_embed_html(EXPIRES_MS))
    provider = AsyncAnonymousTokenProvider(transport, now_ms=lambda: NOW_MS)
    await provider.token()
    provider.invalidate()
    await provider.token()
    assert transport.calls == 2


async def test_async_token_error_on_tokenless_payload() -> None:
    provider = AsyncAnonymousTokenProvider(AsyncTokenlessTransport(), now_ms=lambda: NOW_MS)
    with pytest.raises(TokenError) as excinfo:
        await provider.token()
    assert "BOOTSTRAP_TOKEN" not in str(excinfo.value)
