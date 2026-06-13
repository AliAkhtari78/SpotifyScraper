"""Tests for cookie ingestion and the cookie token providers."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.auth.cookies import (
    SERVER_TIME_URL,
    AsyncCookieTokenProvider,
    CookieTokenProvider,
    load_sp_dc,
)
from spotify_scraper.errors import AuthenticationError

NOW_MS = 1_700_000_000_000
SERVER_TIME_S = 1_700_000_000
TOKEN = "USER_TOKEN_VALUE"  # noqa: S105
SP_DC = "sp_dc_secret_value"

NETSCAPE_FILE = (
    "# Netscape HTTP Cookie File\n"
    ".spotify.com\tTRUE\t/\tTRUE\t0\tsome_other\tnope\n"
    "#HttpOnly_.spotify.com\tTRUE\t/\tTRUE\t1999999999\tsp_dc\t" + SP_DC + "\n"
)


def _token_body(*, token: str = TOKEN, anonymous: bool = False) -> dict[str, Any]:
    return {
        "accessToken": token,
        "accessTokenExpirationTimestampMs": NOW_MS + 3_600_000,
        "isAnonymous": anonymous,
    }


class FakeResponse:
    def __init__(self, body: Any, status_code: int = 200) -> None:
        self.status_code = status_code
        self._body = body

    @property
    def headers(self) -> Mapping[str, str]:
        return {}

    @property
    def text(self) -> str:
        return ""

    @property
    def content(self) -> bytes:
        return b""

    def json(self) -> Any:
        return self._body


class ScriptedTransport:
    """Returns the server-time body, then a queue of token bodies in order."""

    def __init__(self, token_bodies: list[Any]) -> None:
        self._token_bodies = list(token_bodies)
        self.calls: list[str] = []
        self.cookie_headers: list[str | None] = []

    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> FakeResponse:
        self.calls.append(url)
        self.cookie_headers.append((headers or {}).get("Cookie"))
        if url == SERVER_TIME_URL:
            return FakeResponse({"serverTime": SERVER_TIME_S})
        return FakeResponse(self._token_bodies.pop(0))

    def close(self) -> None:
        return None


class AsyncScriptedTransport:
    def __init__(self, token_bodies: list[Any]) -> None:
        self._token_bodies = list(token_bodies)
        self.calls: list[str] = []

    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> FakeResponse:
        self.calls.append(url)
        if url == SERVER_TIME_URL:
            return FakeResponse({"serverTime": SERVER_TIME_S})
        return FakeResponse(self._token_bodies.pop(0))

    async def aclose(self) -> None:
        return None


# --- load_sp_dc ---------------------------------------------------------------


def test_load_from_raw_string() -> None:
    assert load_sp_dc(SP_DC) == SP_DC


def test_load_from_mapping() -> None:
    assert load_sp_dc({"sp_dc": SP_DC, "other": "x"}) == SP_DC


def test_load_from_mapping_missing_raises() -> None:
    with pytest.raises(AuthenticationError) as excinfo:
        load_sp_dc({"other": "x"})
    assert "sp_dc" in str(excinfo.value)


def test_load_from_netscape_file(tmp_path: Path) -> None:
    cookies = tmp_path / "cookies.txt"
    cookies.write_text(NETSCAPE_FILE, encoding="utf-8")
    assert load_sp_dc(cookies) == SP_DC


def test_load_from_path_string(tmp_path: Path) -> None:
    cookies = tmp_path / "cookies.txt"
    cookies.write_text(NETSCAPE_FILE, encoding="utf-8")
    assert load_sp_dc(str(cookies)) == SP_DC


def test_load_from_file_without_sp_dc_raises(tmp_path: Path) -> None:
    cookies = tmp_path / "cookies.txt"
    cookies.write_text(".spotify.com\tTRUE\t/\tTRUE\t0\tother\tval\n", encoding="utf-8")
    with pytest.raises(AuthenticationError):
        load_sp_dc(cookies)


def test_load_empty_string_raises() -> None:
    with pytest.raises(AuthenticationError):
        load_sp_dc("   ")


# --- token exchange -----------------------------------------------------------


def test_exchange_success_sends_cookie_header() -> None:
    transport = ScriptedTransport([_token_body()])
    provider = CookieTokenProvider(transport, SP_DC, now_ms=lambda: NOW_MS)
    assert provider.token() == TOKEN
    assert transport.calls[0] == SERVER_TIME_URL
    assert all(header == f"sp_dc={SP_DC}" for header in transport.cookie_headers)


def test_token_is_cached() -> None:
    transport = ScriptedTransport([_token_body()])
    provider = CookieTokenProvider(transport, SP_DC, now_ms=lambda: NOW_MS)
    provider.token()
    provider.token()
    assert transport.calls.count(SERVER_TIME_URL) == 1


def test_invalidate_forces_re_exchange() -> None:
    transport = ScriptedTransport([_token_body(), _token_body()])
    provider = CookieTokenProvider(transport, SP_DC, now_ms=lambda: NOW_MS)
    provider.token()
    provider.invalidate()
    provider.token()
    assert transport.calls.count(SERVER_TIME_URL) == 2


def test_totp_ver_expired_falls_through_to_next_version() -> None:
    # First (newest) version is retired; second succeeds.
    transport = ScriptedTransport([{"error": "totpVerExpired"}, _token_body()])
    provider = CookieTokenProvider(transport, SP_DC, now_ms=lambda: NOW_MS)
    assert provider.token() == TOKEN


def test_all_versions_expired_raises_rotate_hint() -> None:
    transport = ScriptedTransport([{"error": "totpVerExpired"}] * 3)
    provider = CookieTokenProvider(transport, SP_DC, now_ms=lambda: NOW_MS)
    with pytest.raises(AuthenticationError) as excinfo:
        provider.token()
    assert "rotated" in str(excinfo.value)


def test_anonymous_cookie_raises_authentication_error() -> None:
    transport = ScriptedTransport([_token_body(anonymous=True)])
    provider = CookieTokenProvider(transport, SP_DC, now_ms=lambda: NOW_MS)
    with pytest.raises(AuthenticationError) as excinfo:
        provider.token()
    assert "sp_dc" in str(excinfo.value)


def test_error_text_has_no_credentials() -> None:
    transport = ScriptedTransport([_token_body(anonymous=True)])
    provider = CookieTokenProvider(transport, SP_DC, now_ms=lambda: NOW_MS)
    with pytest.raises(AuthenticationError) as excinfo:
        provider.token()
    message = str(excinfo.value)
    assert SP_DC not in message
    assert TOKEN not in message


def test_repr_has_no_credentials() -> None:
    transport = ScriptedTransport([_token_body()])
    provider = CookieTokenProvider(transport, SP_DC, now_ms=lambda: NOW_MS)
    provider.token()
    text = repr(provider)
    assert SP_DC not in text
    assert TOKEN not in text
    assert "cached=True" in text


# --- async mirror -------------------------------------------------------------


async def test_async_exchange_success() -> None:
    transport = AsyncScriptedTransport([_token_body()])
    provider = AsyncCookieTokenProvider(transport, SP_DC, now_ms=lambda: NOW_MS)
    assert await provider.token() == TOKEN


async def test_async_totp_ver_expired_falls_through() -> None:
    transport = AsyncScriptedTransport([{"error": "totpVerExpired"}, _token_body()])
    provider = AsyncCookieTokenProvider(transport, SP_DC, now_ms=lambda: NOW_MS)
    assert await provider.token() == TOKEN


async def test_async_anonymous_raises() -> None:
    transport = AsyncScriptedTransport([_token_body(anonymous=True)])
    provider = AsyncCookieTokenProvider(transport, SP_DC, now_ms=lambda: NOW_MS)
    with pytest.raises(AuthenticationError):
        await provider.token()
