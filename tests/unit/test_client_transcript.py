"""respx-driven tests for cookie-authenticated transcript extraction."""

from __future__ import annotations

import re
from typing import Any

import httpx
import pytest
import respx

from spotify_scraper import AsyncSpotifyClient, SpotifyClient
from spotify_scraper.errors import AuthenticationError, NotFoundError, ParsingError

EPISODE_ID = "07gKzPFkbvGF0cHoeG7ARS"
SP_DC = "sp_dc_secret_value"
SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
TOKEN_RE = re.compile(r"https://open\.spotify\.com/api/token.*")
TRANSCRIPT_RE = re.compile(
    r"https://spclient\.wg\.spotify\.com/transcript-read-along/v2/episode/.*"
)

# Inline, scrubbed body — no real tokens. Mirrors the live transcript-read-along
# shape: a speaker `title` label, then spoken `text.sentence` cues.
TRANSCRIPT_BODY: dict[str, Any] = {
    "language": "en",
    "timeSyncedStatus": "SYLLABLE_SYNCED",
    "section": [
        {"startMs": 0, "title": {"title": "Speaker 1"}},
        {"startMs": 0, "text": {"sentence": {"startMs": 0, "text": "Welcome to the show."}}},
        {
            "startMs": 4200,
            "text": {"sentence": {"startMs": 4200, "text": "Today we talk about transcripts."}},
        },
    ],
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
            client.get_transcript(EPISODE_ID)
        assert len(router.calls) == 0


async def test_async_no_cookies_raises_without_network() -> None:
    async with AsyncSpotifyClient() as client:
        with respx.mock(assert_all_mocked=True) as router:
            with pytest.raises(AuthenticationError):
                await client.get_transcript(EPISODE_ID)
            assert len(router.calls) == 0


# --- success ------------------------------------------------------------------


@respx.mock
def test_get_transcript_success() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    route = respx.get(TRANSCRIPT_RE).mock(return_value=httpx.Response(200, json=TRANSCRIPT_BODY))

    with SpotifyClient(cookies=SP_DC) as client:
        transcript = client.get_transcript(EPISODE_ID)

    assert len(transcript.lines) == 2
    assert transcript.lines[0].text == "Welcome to the show."
    assert transcript.lines[0].start_ms == 0
    assert transcript.language == "en"
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer USER_TOKEN"
    assert request.headers["app-platform"] == "WebPlayer"


@respx.mock
async def test_async_get_transcript_success() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(TRANSCRIPT_RE).mock(return_value=httpx.Response(200, json=TRANSCRIPT_BODY))

    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        transcript = await client.get_transcript(EPISODE_ID)

    assert len(transcript.lines) == 2
    assert transcript.lines[1].start_ms == 4200


def test_get_transcript_accepts_full_url() -> None:
    with respx.mock:
        _mock_token_handshake()
        respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
        respx.get(TRANSCRIPT_RE).mock(return_value=httpx.Response(200, json=TRANSCRIPT_BODY))
        with SpotifyClient(cookies=SP_DC) as client:
            transcript = client.get_transcript(f"https://open.spotify.com/episode/{EPISODE_ID}")
    assert len(transcript.lines) == 2


# --- 404 -> NotFoundError -----------------------------------------------------


@respx.mock
def test_no_transcript_raises_not_found() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(TRANSCRIPT_RE).mock(return_value=httpx.Response(404))

    with (
        SpotifyClient(cookies=SP_DC) as client,
        pytest.raises(NotFoundError, match="No transcript for episode"),
    ):
        client.get_transcript(EPISODE_ID)


# --- 200 with no spoken text (speaker labels only) -> NotFoundError -----------


@respx.mock
def test_label_only_200_raises_not_found() -> None:
    # A 200 whose cue container holds only speaker-label cues (no text) means the
    # episode has no transcript content; the contract reports that as NotFoundError.
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    label_only = {"language": "en", "section": [{"startMs": 0, "title": {"title": "Speaker 1"}}]}
    respx.get(TRANSCRIPT_RE).mock(return_value=httpx.Response(200, json=label_only))

    with (
        SpotifyClient(cookies=SP_DC) as client,
        pytest.raises(NotFoundError, match="No transcript for episode"),
    ):
        client.get_transcript(EPISODE_ID)


@respx.mock
async def test_async_label_only_200_raises_not_found() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    label_only = {"language": "en", "section": [{"startMs": 0, "title": {"title": "Speaker 1"}}]}
    respx.get(TRANSCRIPT_RE).mock(return_value=httpx.Response(200, json=label_only))

    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        with pytest.raises(NotFoundError, match="No transcript for episode"):
            await client.get_transcript(EPISODE_ID)


# --- malformed 200 -> ParsingError --------------------------------------------


@respx.mock
def test_non_json_200_raises_parsing_error() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(TRANSCRIPT_RE).mock(return_value=httpx.Response(200, text="<html>not json</html>"))

    with SpotifyClient(cookies=SP_DC) as client, pytest.raises(ParsingError):
        client.get_transcript(EPISODE_ID)


@respx.mock
def test_no_cue_container_200_raises_parsing_error() -> None:
    # A JSON 200 that carries no recognized cue container is an unexpected shape
    # (Spotify changed its format), which is ParsingError, not "no transcript".
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(TRANSCRIPT_RE).mock(return_value=httpx.Response(200, json={"language": "en"}))

    with SpotifyClient(cookies=SP_DC) as client, pytest.raises(ParsingError):
        client.get_transcript(EPISODE_ID)


# --- expired cookie -> AuthenticationError ------------------------------------


@respx.mock
def test_anonymous_cookie_raises_authentication_error() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body(anonymous=True)))

    with SpotifyClient(cookies=SP_DC) as client, pytest.raises(AuthenticationError):
        client.get_transcript(EPISODE_ID)


# --- 401 on transcript -> invalidate + retry once -----------------------------


@respx.mock
def test_transcript_401_invalidates_and_retries_once() -> None:
    _mock_token_handshake()
    token_route = respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    transcript_route = respx.get(TRANSCRIPT_RE).mock(
        side_effect=[
            httpx.Response(401),
            httpx.Response(200, json=TRANSCRIPT_BODY),
        ]
    )

    with SpotifyClient(cookies=SP_DC) as client:
        transcript = client.get_transcript(EPISODE_ID)

    assert len(transcript.lines) == 2
    assert transcript_route.call_count == 2
    # The token was invalidated and re-exchanged after the 401.
    assert token_route.call_count == 2


@respx.mock
def test_transcript_second_401_surfaces_as_auth_error() -> None:
    _mock_token_handshake()
    respx.get(TOKEN_RE).mock(return_value=httpx.Response(200, json=_token_body()))
    respx.get(TRANSCRIPT_RE).mock(return_value=httpx.Response(401))

    with SpotifyClient(cookies=SP_DC) as client, pytest.raises(AuthenticationError):
        client.get_transcript(EPISODE_ID)


def test_use_after_close_raises() -> None:
    client = SpotifyClient(cookies=SP_DC)
    client.close()
    with pytest.raises(Exception, match="closed"):
        client.get_transcript(EPISODE_ID)
