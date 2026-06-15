"""respx-driven tests for the ``locale`` (``Accept-Language``) parameter.

Covers both clients: the per-client default and per-call override both set the
``Accept-Language`` header on the pathfinder (and embed) requests; per-call wins
over per-client; an invalid locale raises ``URLError`` with ZERO network calls at
both construction and call time; an omitted locale sends no override; and the
header is applied to ``search`` too.
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
from spotify_scraper.errors import URLError

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
TRACK_ID = "4uLU6hMCjMI75M1A2tKUQC"
EMBED_URL = f"https://open.spotify.com/embed/track/{TRACK_ID}"
BOOTSTRAP_URL = f"https://open.spotify.com/embed/track/{DEFAULT_BOOTSTRAP_ID}"
PATHFINDER_RE = re.compile(r"https://api-partner\.spotify\.com/pathfinder/v1/query.*")

EMBED_NEXT_DATA: dict[str, Any] = json.loads(
    (FIXTURES / "embed" / "track.json").read_text(encoding="utf-8")
)
PATHFINDER_BODY: dict[str, Any] = json.loads(
    (FIXTURES / "pathfinder" / "track.json").read_text(encoding="utf-8")
)
SEARCH_BODY: dict[str, Any] = json.loads(
    (FIXTURES / "pathfinder" / "search.json").read_text(encoding="utf-8")
)


def _embed_html(*, token: str = "EMBED_TOKEN") -> str:  # noqa: S107
    next_data = json.loads(json.dumps(EMBED_NEXT_DATA))
    session = next_data["props"]["pageProps"]["state"]["settings"]["session"]
    session["accessToken"] = token
    session["accessTokenExpirationTimestampMs"] = 9_999_999_999_999
    body = json.dumps(next_data)
    return f'<script id="__NEXT_DATA__" type="application/json">{body}</script>'


def _mock_track() -> respx.Route:
    respx.get(EMBED_URL).mock(return_value=httpx.Response(200, text=_embed_html()))
    return respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=PATHFINDER_BODY))


def _mock_search() -> respx.Route:
    respx.get(BOOTSTRAP_URL).mock(return_value=httpx.Response(200, text=_embed_html()))
    return respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=SEARCH_BODY))


# --------------------------------------------------------------------------- #
# Sync
# --------------------------------------------------------------------------- #


@respx.mock
def test_per_client_locale_sets_accept_language() -> None:
    embed = respx.get(EMBED_URL).mock(return_value=httpx.Response(200, text=_embed_html()))
    pathfinder = respx.get(PATHFINDER_RE).mock(
        return_value=httpx.Response(200, json=PATHFINDER_BODY)
    )
    with SpotifyClient(locale="ja-JP") as client:
        client.get_track(TRACK_ID)
    assert pathfinder.calls.last.request.headers["Accept-Language"] == "ja-JP"
    assert embed.calls.last.request.headers["Accept-Language"] == "ja-JP"


@respx.mock
def test_per_call_locale_overrides_per_client() -> None:
    pathfinder = _mock_track()
    with SpotifyClient(locale="de-DE") as client:
        client.get_track(TRACK_ID, locale="ja-JP")
    assert pathfinder.calls.last.request.headers["Accept-Language"] == "ja-JP"


@respx.mock
def test_bare_language_subtag_is_lower_cased_on_the_wire() -> None:
    pathfinder = _mock_track()
    with SpotifyClient() as client:
        client.get_track(TRACK_ID, locale="DE")
    assert pathfinder.calls.last.request.headers["Accept-Language"] == "de"


@respx.mock
def test_omitted_locale_sends_default_en_only() -> None:
    pathfinder = _mock_track()
    with SpotifyClient() as client:
        client.get_track(TRACK_ID)
    assert pathfinder.calls.last.request.headers["Accept-Language"] == "en"


@respx.mock
def test_invalid_per_call_locale_raises_before_any_request() -> None:
    pathfinder = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json={}))
    embed = respx.get(EMBED_URL).mock(return_value=httpx.Response(200, text=_embed_html()))
    with SpotifyClient() as client, pytest.raises(URLError, match="deutsch"):
        client.get_track(TRACK_ID, locale="deutsch")
    assert pathfinder.call_count == 0
    assert embed.call_count == 0


def test_invalid_construction_locale_raises_without_network() -> None:
    with pytest.raises(URLError, match="u1"):
        SpotifyClient(locale="u1")


@respx.mock
def test_search_carries_resolved_locale() -> None:
    pathfinder = _mock_search()
    with SpotifyClient(locale="de") as client:
        client.search("daft punk", locale="ja-JP")
    assert pathfinder.calls.last.request.headers["Accept-Language"] == "ja-JP"


@respx.mock
def test_search_invalid_locale_raises_before_request() -> None:
    pathfinder = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json={}))
    with SpotifyClient() as client, pytest.raises(URLError):
        client.search("daft punk", locale="123")
    assert pathfinder.call_count == 0


# --------------------------------------------------------------------------- #
# Async
# --------------------------------------------------------------------------- #


@respx.mock
async def test_per_client_locale_sets_accept_language_async() -> None:
    embed = respx.get(EMBED_URL).mock(return_value=httpx.Response(200, text=_embed_html()))
    pathfinder = respx.get(PATHFINDER_RE).mock(
        return_value=httpx.Response(200, json=PATHFINDER_BODY)
    )
    async with AsyncSpotifyClient(locale="ja-JP") as client:
        await client.get_track(TRACK_ID)
    assert pathfinder.calls.last.request.headers["Accept-Language"] == "ja-JP"
    assert embed.calls.last.request.headers["Accept-Language"] == "ja-JP"


@respx.mock
async def test_per_call_locale_overrides_per_client_async() -> None:
    pathfinder = _mock_track()
    async with AsyncSpotifyClient(locale="de-DE") as client:
        await client.get_track(TRACK_ID, locale="ja-JP")
    assert pathfinder.calls.last.request.headers["Accept-Language"] == "ja-JP"


@respx.mock
async def test_omitted_locale_sends_default_en_only_async() -> None:
    pathfinder = _mock_track()
    async with AsyncSpotifyClient() as client:
        await client.get_track(TRACK_ID)
    assert pathfinder.calls.last.request.headers["Accept-Language"] == "en"


@respx.mock
async def test_invalid_per_call_locale_raises_before_any_request_async() -> None:
    pathfinder = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json={}))
    embed = respx.get(EMBED_URL).mock(return_value=httpx.Response(200, text=_embed_html()))
    async with AsyncSpotifyClient() as client:
        with pytest.raises(URLError, match="deutsch"):
            await client.get_track(TRACK_ID, locale="deutsch")
    assert pathfinder.call_count == 0
    assert embed.call_count == 0


def test_invalid_construction_locale_raises_without_network_async() -> None:
    with pytest.raises(URLError):
        AsyncSpotifyClient(locale="u1")


@respx.mock
async def test_search_carries_resolved_locale_async() -> None:
    pathfinder = _mock_search()
    async with AsyncSpotifyClient(locale="de") as client:
        await client.search("daft punk", locale="ja-JP")
    assert pathfinder.calls.last.request.headers["Accept-Language"] == "ja-JP"


@respx.mock
async def test_bare_language_subtag_is_lower_cased_on_the_wire_async() -> None:
    pathfinder = _mock_track()
    async with AsyncSpotifyClient() as client:
        await client.get_track(TRACK_ID, locale="DE")
    assert pathfinder.calls.last.request.headers["Accept-Language"] == "de"


@respx.mock
async def test_search_invalid_locale_raises_before_request_async() -> None:
    pathfinder = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json={}))
    async with AsyncSpotifyClient() as client:
        with pytest.raises(URLError):
            await client.search("daft punk", locale="123")
    assert pathfinder.call_count == 0
