"""respx-driven tests for credits (auth) and artist events (anonymous)."""

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
from spotify_scraper.errors import AuthenticationError

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
BOOTSTRAP_URL = f"https://open.spotify.com/embed/track/{DEFAULT_BOOTSTRAP_ID}"
PATHFINDER_RE = re.compile(r"https://api-partner\.spotify\.com/pathfinder/v1/query.*")
SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
TOKEN_RE = re.compile(r"https://open\.spotify\.com/api/token.*")
CREDITS_RE = re.compile(r"https://spclient\.wg\.spotify\.com/track-credits-view/.*")

ARTIST_ID = "0gxyHStUsqpMadRV0Di1Qt"
TRACK_ID = "4LfCY65LvojKjWEnU7fNN4"
SP_DC = "sp_dc_secret_value"

CONCERTS: dict[str, Any] = json.loads(
    (FIXTURES / "pathfinder" / "concerts.json").read_text(encoding="utf-8")
)
CREDITS: dict[str, Any] = json.loads(
    (FIXTURES / "spclient" / "track_credits.json").read_text(encoding="utf-8")
)
EMBED_NEXT_DATA = json.loads((FIXTURES / "embed" / "track.json").read_text(encoding="utf-8"))


def _bootstrap_html() -> str:
    next_data = json.loads(json.dumps(EMBED_NEXT_DATA))
    session = next_data["props"]["pageProps"]["state"]["settings"]["session"]
    session["accessToken"] = "ANON_TOKEN"
    session["accessTokenExpirationTimestampMs"] = 9_999_999_999_999
    return f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(next_data)}</script>'


def _mock_bootstrap() -> None:
    respx.get(BOOTSTRAP_URL).mock(return_value=httpx.Response(200, text=_bootstrap_html()))


def _mock_token() -> None:
    respx.get(SERVER_TIME_URL).mock(
        return_value=httpx.Response(200, json={"serverTime": 1_700_000_000})
    )
    respx.get(TOKEN_RE).mock(
        return_value=httpx.Response(
            200,
            json={
                "accessToken": "USER_TOKEN",
                "accessTokenExpirationTimestampMs": 9_999_999_999_999,
                "isAnonymous": False,
            },
        )
    )


# --- artist events (anonymous) ------------------------------------------------


@respx.mock
def test_get_artist_events() -> None:
    _mock_bootstrap()
    route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=CONCERTS))
    with SpotifyClient() as client:
        concerts = client.get_artist_events(ARTIST_ID)
    assert len(concerts) > 0
    assert all(c.title and c.uri.startswith("spotify:concert:") for c in concerts)
    assert "operationName=ArtistConcerts" in str(route.calls.last.request.url)


@respx.mock
async def test_get_artist_events_async() -> None:
    _mock_bootstrap()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=CONCERTS))
    async with AsyncSpotifyClient() as client:
        concerts = await client.get_artist_events(ARTIST_ID)
    assert len(concerts) > 0


# --- credits (authenticated) --------------------------------------------------


def test_get_credits_without_cookies_raises() -> None:
    with respx.mock(assert_all_mocked=True) as router, SpotifyClient() as client:
        with pytest.raises(AuthenticationError):
            client.get_credits(TRACK_ID)
        assert len(router.calls) == 0


@respx.mock
def test_get_credits_success() -> None:
    _mock_token()
    route = respx.get(CREDITS_RE).mock(return_value=httpx.Response(200, json=CREDITS))
    with SpotifyClient(cookies=SP_DC) as client:
        credits = client.get_credits(TRACK_ID)
    assert credits.track_uri.startswith("spotify:track:")
    assert len(credits.roles) > 0
    assert all(role.title for role in credits.roles)
    assert any(role.artists for role in credits.roles)
    assert route.calls.last.request.headers["Authorization"] == "Bearer USER_TOKEN"
    assert f"experimental/{TRACK_ID}/credits" in str(route.calls.last.request.url)


@respx.mock
def test_get_credits_401_invalidates_and_retries_once() -> None:
    _mock_token()
    token_route = respx.get(TOKEN_RE).mock(
        return_value=httpx.Response(
            200,
            json={
                "accessToken": "USER_TOKEN",
                "accessTokenExpirationTimestampMs": 9_999_999_999_999,
                "isAnonymous": False,
            },
        )
    )
    credits_route = respx.get(CREDITS_RE).mock(
        side_effect=[httpx.Response(401), httpx.Response(200, json=CREDITS)]
    )
    with SpotifyClient(cookies=SP_DC) as client:
        credits = client.get_credits(TRACK_ID)
    assert len(credits.roles) > 0
    assert credits_route.call_count == 2
    assert token_route.call_count == 2


@respx.mock
async def test_get_credits_success_async() -> None:
    _mock_token()
    respx.get(CREDITS_RE).mock(return_value=httpx.Response(200, json=CREDITS))
    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        credits = await client.get_credits(TRACK_ID)
    assert len(credits.roles) > 0
