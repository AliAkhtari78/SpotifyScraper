"""respx-driven tests for the discovery surfaces on both clients.

Related artists, discography, and similar albums are anonymous (bootstrap +
pathfinder, like ``search``). ``get_user`` is cookie-authenticated and hits the
``user-profile-view`` spclient host (like lyrics).
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
from spotify_scraper.errors import AuthenticationError

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
BOOTSTRAP_URL = f"https://open.spotify.com/embed/track/{DEFAULT_BOOTSTRAP_ID}"
PATHFINDER_RE = re.compile(r"https://api-partner\.spotify\.com/pathfinder/v1/query.*")
SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
TOKEN_RE = re.compile(r"https://open\.spotify\.com/api/token.*")
PROFILE_RE = re.compile(r"https://spclient\.wg\.spotify\.com/user-profile-view/v3/profile/.*")

ARTIST_ID = "0gxyHStUsqpMadRV0Di1Qt"
TRACK_ID = "4uLU6hMCjMI75M1A2tKUQC"
SP_DC = "sp_dc_secret_value"


def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / "pathfinder" / name).read_text(encoding="utf-8"))


RELATED = _load("artist_related.json")
DISCOGRAPHY = _load("artist_discography.json")
SIMILAR = _load("similar_albums.json")
EMBED_NEXT_DATA = json.loads((FIXTURES / "embed" / "track.json").read_text(encoding="utf-8"))
USER_PROFILE = json.loads((FIXTURES / "spclient" / "user_profile.json").read_text(encoding="utf-8"))
_EMPTY_DISCO = {"data": {"artistUnion": {"discography": {"all": {"items": [], "totalCount": 58}}}}}


def _bootstrap_html(*, token: str = "ANON_TOKEN") -> str:  # noqa: S107
    next_data = json.loads(json.dumps(EMBED_NEXT_DATA))
    session = next_data["props"]["pageProps"]["state"]["settings"]["session"]
    session["accessToken"] = token
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


# --------------------------------------------------------------------------- #
# Related / similar (anonymous)
# --------------------------------------------------------------------------- #


@respx.mock
def test_get_related_artists() -> None:
    _mock_bootstrap()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=RELATED))
    with SpotifyClient() as client:
        artists = client.get_related_artists(ARTIST_ID)
    assert len(artists) > 0
    assert all(a.name for a in artists)
    assert any(a.images for a in artists)


@respx.mock
def test_get_similar_albums() -> None:
    _mock_bootstrap()
    route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=SIMILAR))
    with SpotifyClient() as client:
        albums = client.get_similar_albums(TRACK_ID, limit=10)
    assert len(albums) > 0
    assert all(a.uri.startswith("spotify:album:") for a in albums)
    assert "operationName=similarAlbumsBasedOnThisTrack" in str(route.calls.last.request.url)


# --------------------------------------------------------------------------- #
# Discography (anonymous, paginated)
# --------------------------------------------------------------------------- #


@respx.mock
def test_get_discography_paginates_until_empty() -> None:
    _mock_bootstrap()
    route = respx.get(PATHFINDER_RE).mock(
        side_effect=[httpx.Response(200, json=DISCOGRAPHY), httpx.Response(200, json=_EMPTY_DISCO)]
    )
    with SpotifyClient() as client:
        releases = client.get_discography(ARTIST_ID)
    assert len(releases) == 5
    assert route.call_count == 2
    assert all(r.uri.startswith("spotify:album:") for r in releases)


@respx.mock
def test_get_discography_respects_max_releases() -> None:
    _mock_bootstrap()
    route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=DISCOGRAPHY))
    with SpotifyClient() as client:
        releases = client.get_discography(ARTIST_ID, max_releases=3)
    assert len(releases) == 3
    # The cap is reached after the first page, so only one request is made.
    assert route.call_count == 1


# --------------------------------------------------------------------------- #
# get_user (authenticated)
# --------------------------------------------------------------------------- #


def test_get_user_without_cookies_raises() -> None:
    with respx.mock(assert_all_mocked=True) as router, SpotifyClient() as client:
        with pytest.raises(AuthenticationError):
            client.get_user("spotify")
        assert len(router.calls) == 0


@respx.mock
def test_get_user_success() -> None:
    _mock_token()
    route = respx.get(PROFILE_RE).mock(return_value=httpx.Response(200, json=USER_PROFILE))
    with SpotifyClient(cookies=SP_DC) as client:
        profile = client.get_user("spotify:user:spotify")
    assert profile.name
    assert profile.followers_count is not None
    assert len(profile.public_playlists) > 0
    assert "user-profile-view/v3/profile/spotify" in str(route.calls.last.request.url)
    assert route.calls.last.request.headers["Authorization"] == "Bearer USER_TOKEN"


@respx.mock
def test_get_user_401_invalidates_and_retries_once() -> None:
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
    profile_route = respx.get(PROFILE_RE).mock(
        side_effect=[httpx.Response(401), httpx.Response(200, json=USER_PROFILE)]
    )
    with SpotifyClient(cookies=SP_DC) as client:
        profile = client.get_user("spotify")
    assert profile.name
    assert profile_route.call_count == 2
    assert token_route.call_count == 2


# --------------------------------------------------------------------------- #
# Async parity
# --------------------------------------------------------------------------- #


@respx.mock
async def test_get_related_artists_async() -> None:
    _mock_bootstrap()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=RELATED))
    async with AsyncSpotifyClient() as client:
        artists = await client.get_related_artists(ARTIST_ID)
    assert len(artists) > 0


@respx.mock
async def test_get_discography_async() -> None:
    _mock_bootstrap()
    respx.get(PATHFINDER_RE).mock(
        side_effect=[httpx.Response(200, json=DISCOGRAPHY), httpx.Response(200, json=_EMPTY_DISCO)]
    )
    async with AsyncSpotifyClient() as client:
        releases = await client.get_discography(ARTIST_ID)
    assert len(releases) == 5


@respx.mock
async def test_get_user_success_async() -> None:
    _mock_token()
    respx.get(PROFILE_RE).mock(return_value=httpx.Response(200, json=USER_PROFILE))
    async with AsyncSpotifyClient(cookies=SP_DC) as client:
        profile = await client.get_user("spotify")
    assert profile.name
    assert len(profile.public_playlists) > 0
