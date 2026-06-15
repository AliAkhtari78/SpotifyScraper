"""respx-driven tests for cookie-authenticated account product-state."""

from __future__ import annotations

import re
from typing import Any

import httpx
import pytest
import respx

from spotify_scraper import AsyncSpotifyClient, SpotifyClient
from spotify_scraper.errors import AuthenticationError

SP_DC = "sp_dc_secret_value"
SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
TOKEN_RE = re.compile(r"https://open\.spotify\.com/api/token.*")
PRODUCT_STATE_RE = re.compile(r"https://spclient\.wg\.spotify\.com/melody/v1/product_state.*")

# Inline, scrubbed body — no real tokens or PII. Stringy booleans mirror live.
PREMIUM_BODY: dict[str, Any] = {
    "product": "premium",
    "catalogue": "premium",
    "country": "CA",
    "on-demand": "1",
    "preferred-locale": "en",
    "selected-language": "en",
}
FREE_BODY: dict[str, Any] = {"product": "free", "country": "US", "on-demand": "0"}


def _token_body(*, anonymous: bool = False) -> dict[str, Any]:
    return {
        "accessToken": "USER_TOKEN",
        "accessTokenExpirationTimestampMs": 9_999_999_999_999,
        "isAnonymous": anonymous,
    }


def _mock_token_handshake() -> None:
    respx.get(SERVER_TIME_URL).mock(
        return_value=httpx.Response(200, json={"serverTime": 1_700_000_000})
    )


# --- no cookies -> AuthenticationError without network ------------------------


def test_no_cookies_raises_without_network() -> None:
    with respx.mock(assert_all_mocked=True) as router, SpotifyClient() as client:
        with pytest.raises(AuthenticationError):
            client.get_account()
        assert len(router.calls) == 0


async def test_async_no_cookies_raises_without_network() -> None:
    async with AsyncSpotifyClient() as client:
        with respx.mock(assert_all_mocked=True) as router:
            with pytest.raises(AuthenticationError):
                await client.get_account()
            assert len(router.calls) == 0


# --- success ------------------------------------------------------------------


@respx.mock
def test_get_account_success_premium() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    route = respx.get(PRODUCT_STATE_RE).mock(return_value=httpx.Response(200, json=PREMIUM_BODY))

    with SpotifyClient(cookies=SP_DC) as client:
        account = client.get_account()
        assert client.is_premium() is True

    assert account.product == "premium"
    assert account.country == "CA"
    assert account.on_demand is True
    assert account.is_premium is True
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer USER_TOKEN"
    assert request.headers["app-platform"] == "WebPlayer"


@respx.mock
def test_get_account_free_is_not_premium() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(PRODUCT_STATE_RE).mock(return_value=httpx.Response(200, json=FREE_BODY))

    with SpotifyClient(cookies=SP_DC) as client:
        account = client.get_account()

    assert account.is_premium is False
    assert account.on_demand is False


@respx.mock
async def test_async_get_account_success_premium() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    route = respx.get(PRODUCT_STATE_RE).mock(return_value=httpx.Response(200, json=PREMIUM_BODY))

    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        account = await client.get_account()
        assert await client.is_premium() is True

    assert account.is_premium is True
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer USER_TOKEN"
    assert request.headers["app-platform"] == "WebPlayer"


# --- empty body -> all None, not premium --------------------------------------


@respx.mock
def test_empty_body_yields_account_with_none_fields() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(PRODUCT_STATE_RE).mock(return_value=httpx.Response(200, json={}))

    with SpotifyClient(cookies=SP_DC) as client:
        account = client.get_account()

    assert account.product is None
    assert account.is_premium is False


# --- anonymous cookie -> AuthenticationError ----------------------------------


@respx.mock
def test_anonymous_cookie_raises_authentication_error() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body(anonymous=True)))

    with SpotifyClient(cookies=SP_DC) as client, pytest.raises(AuthenticationError):
        client.get_account()


# --- 401 -> invalidate + retry once -------------------------------------------


@respx.mock
def test_account_401_invalidates_and_retries_once() -> None:
    _mock_token_handshake()
    token_route = respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    account_route = respx.get(PRODUCT_STATE_RE).mock(
        side_effect=[
            httpx.Response(401),
            httpx.Response(200, json=PREMIUM_BODY),
        ]
    )

    with SpotifyClient(cookies=SP_DC) as client:
        account = client.get_account()

    assert account.is_premium is True
    assert account_route.call_count == 2
    # The token was invalidated and re-exchanged after the 401.
    assert token_route.call_count == 2


@respx.mock
def test_account_second_401_surfaces_as_auth_error() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(PRODUCT_STATE_RE).mock(return_value=httpx.Response(401))

    with SpotifyClient(cookies=SP_DC) as client, pytest.raises(AuthenticationError):
        client.get_account()


@respx.mock
async def test_async_account_401_invalidates_and_retries_once() -> None:
    _mock_token_handshake()
    token_route = respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    account_route = respx.get(PRODUCT_STATE_RE).mock(
        side_effect=[
            httpx.Response(401),
            httpx.Response(200, json=PREMIUM_BODY),
        ]
    )

    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        account = await client.get_account()

    assert account.is_premium is True
    assert account_route.call_count == 2
    assert token_route.call_count == 2


@respx.mock
async def test_async_empty_body_yields_account_with_none_fields() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(PRODUCT_STATE_RE).mock(return_value=httpx.Response(200, json={}))

    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        account = await client.get_account()

    assert account.product is None
    assert account.is_premium is False


@respx.mock
async def test_async_account_second_401_surfaces_as_auth_error() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(PRODUCT_STATE_RE).mock(return_value=httpx.Response(401))

    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        with pytest.raises(AuthenticationError):
            await client.get_account()


# --- non-JSON body -> ParsingError --------------------------------------------


@respx.mock
def test_non_json_body_raises_parsing_error() -> None:
    from spotify_scraper.errors import ParsingError

    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(PRODUCT_STATE_RE).mock(return_value=httpx.Response(200, text="<html>nope"))

    with SpotifyClient(cookies=SP_DC) as client, pytest.raises(ParsingError):
        client.get_account()


@respx.mock
async def test_async_non_json_body_raises_parsing_error() -> None:
    from spotify_scraper.errors import ParsingError

    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(PRODUCT_STATE_RE).mock(return_value=httpx.Response(200, text="<html>nope"))

    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        with pytest.raises(ParsingError):
            await client.get_account()


# --- use after close ----------------------------------------------------------


def test_use_after_close_raises() -> None:
    client = SpotifyClient(cookies=SP_DC)
    client.close()
    with pytest.raises(Exception, match="closed"):
        client.get_account()


async def test_async_use_after_close_raises() -> None:
    client = AsyncSpotifyClient(cookies=SP_DC)
    await client.aclose()
    with pytest.raises(Exception, match="closed"):
        await client.get_account()
