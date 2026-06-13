"""respx-driven tests for cookie-authenticated lyrics extraction."""

from __future__ import annotations

import re
from typing import Any

import httpx
import pytest
import respx

from spotify_scraper import AsyncSpotifyClient, SpotifyClient
from spotify_scraper.errors import AuthenticationError, NotFoundError

TRACK_ID = "4uLU6hMCjMI75M1A2tKUQC"
SP_DC = "sp_dc_secret_value"
SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
TOKEN_RE = re.compile(r"https://open\.spotify\.com/api/token.*")
LYRICS_RE = re.compile(r"https://spclient\.wg\.spotify\.com/color-lyrics/v2/track/.*")

LYRICS_BODY: dict[str, Any] = {
    "lyrics": {
        "syncType": "LINE_SYNCED",
        "provider": "MusixMatch",
        "language": "en",
        "lines": [
            {"startTimeMs": "19630", "words": "We're no strangers to love"},
            {"startTimeMs": "23400", "words": "You know the rules and so do I"},
        ],
    }
}


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
            client.get_lyrics(TRACK_ID)
        assert len(router.calls) == 0


async def test_async_no_cookies_raises_without_network() -> None:
    async with AsyncSpotifyClient() as client:
        with respx.mock(assert_all_mocked=True) as router:
            with pytest.raises(AuthenticationError):
                await client.get_lyrics(TRACK_ID)
            assert len(router.calls) == 0


# --- success ------------------------------------------------------------------


@respx.mock
def test_get_lyrics_success() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    lyrics_route = respx.get(LYRICS_RE).mock(return_value=httpx.Response(200, json=LYRICS_BODY))

    with SpotifyClient(cookies=SP_DC) as client:
        lyrics = client.get_lyrics(TRACK_ID)

    assert lyrics.sync_type == "LINE_SYNCED"
    assert len(lyrics.lines) == 2
    assert lyrics.lines[0].text == "We're no strangers to love"
    request = lyrics_route.calls.last.request
    assert request.headers["Authorization"] == "Bearer USER_TOKEN"
    assert request.headers["app-platform"] == "WebPlayer"


@respx.mock
async def test_async_get_lyrics_success() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(LYRICS_RE).mock(return_value=httpx.Response(200, json=LYRICS_BODY))

    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        lyrics = await client.get_lyrics(TRACK_ID)

    assert lyrics.sync_type == "LINE_SYNCED"
    assert lyrics.lines[0].start_ms == 19630


def test_get_lyrics_accepts_full_url() -> None:
    with respx.mock:
        _mock_token_handshake()
        respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
        respx.get(LYRICS_RE).mock(return_value=httpx.Response(200, json=LYRICS_BODY))
        with SpotifyClient(cookies=SP_DC) as client:
            lyrics = client.get_lyrics(f"https://open.spotify.com/track/{TRACK_ID}")
    assert len(lyrics.lines) == 2


# --- 404 -> NotFoundError -----------------------------------------------------


@respx.mock
def test_no_lyrics_raises_not_found() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(LYRICS_RE).mock(return_value=httpx.Response(404))

    with SpotifyClient(cookies=SP_DC) as client, pytest.raises(NotFoundError):
        client.get_lyrics(TRACK_ID)


# --- totpVerExpired fallthrough -----------------------------------------------


@respx.mock
def test_totp_ver_expired_falls_through_to_next_version() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(
        side_effect=[
            httpx.Response(200, json={"error": "totpVerExpired"}),
            httpx.Response(200, json=_token_body()),
        ]
    )
    respx.get(LYRICS_RE).mock(return_value=httpx.Response(200, json=LYRICS_BODY))

    with SpotifyClient(cookies=SP_DC) as client:
        lyrics = client.get_lyrics(TRACK_ID)

    assert len(lyrics.lines) == 2


# --- expired cookie -> AuthenticationError ------------------------------------


@respx.mock
def test_anonymous_cookie_raises_authentication_error() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body(anonymous=True)))

    with SpotifyClient(cookies=SP_DC) as client, pytest.raises(AuthenticationError):
        client.get_lyrics(TRACK_ID)


# --- 401 on lyrics -> invalidate + retry once ---------------------------------


@respx.mock
def test_lyrics_401_invalidates_and_retries_once() -> None:
    _mock_token_handshake()
    token_route = respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    lyrics_route = respx.get(LYRICS_RE).mock(
        side_effect=[
            httpx.Response(401),
            httpx.Response(200, json=LYRICS_BODY),
        ]
    )

    with SpotifyClient(cookies=SP_DC) as client:
        lyrics = client.get_lyrics(TRACK_ID)

    assert len(lyrics.lines) == 2
    assert lyrics_route.call_count == 2
    # The token was invalidated and re-exchanged after the 401.
    assert token_route.call_count == 2


def test_use_after_close_raises() -> None:
    client = SpotifyClient(cookies=SP_DC)
    client.close()
    with pytest.raises(Exception, match="closed"):
        client.get_lyrics(TRACK_ID)
