"""respx-driven tests for sync and async ``get_colors`` on both clients.

Color extraction is anonymous and tier-1-only: the only embed fetched is the
anonymous-token bootstrap, exactly like ``search``.
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
from spotify_scraper.errors import SpotifyScraperError, URLError
from spotify_scraper.models.common import Image
from spotify_scraper.models.track import Track

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
BOOTSTRAP_URL = f"https://open.spotify.com/embed/track/{DEFAULT_BOOTSTRAP_ID}"
PATHFINDER_RE = re.compile(r"https://api-partner\.spotify\.com/pathfinder/v1/query.*")

COLORS_BODY: dict[str, Any] = json.loads(
    (FIXTURES / "pathfinder" / "colors.json").read_text(encoding="utf-8")
)
EMBED_NEXT_DATA: dict[str, Any] = json.loads(
    (FIXTURES / "embed" / "track.json").read_text(encoding="utf-8")
)


def _bootstrap_html(*, token: str = "ANON_TOKEN") -> str:  # noqa: S107
    next_data = json.loads(json.dumps(EMBED_NEXT_DATA))
    session = next_data["props"]["pageProps"]["state"]["settings"]["session"]
    session["accessToken"] = token
    session["accessTokenExpirationTimestampMs"] = 9_999_999_999_999
    body = json.dumps(next_data)
    return f'<script id="__NEXT_DATA__" type="application/json">{body}</script>'


def _mock_bootstrap(*, token: str = "ANON_TOKEN") -> None:  # noqa: S107
    respx.get(BOOTSTRAP_URL).mock(
        return_value=httpx.Response(200, text=_bootstrap_html(token=token))
    )


def _image_track() -> Track:
    return Track(
        id="x",
        uri="spotify:track:x",
        name="n",
        duration_ms=0,
        explicit=False,
        playable=True,
        preview_url=None,
        artists=(),
        images=(Image(url="https://i.scdn.co/image/IMG123", width=640, height=640),),
        release_date=None,
    )


# --------------------------------------------------------------------------- #
# Sync
# --------------------------------------------------------------------------- #


@respx.mock
def test_get_colors_returns_hex_triplet() -> None:
    _mock_bootstrap()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=COLORS_BODY))
    with SpotifyClient() as client:
        colors = client.get_colors("spotify:image:ab67616d0000b273fe8a8d62b127592ff546d9c8")
    assert colors.raw.startswith("#") and len(colors.raw) == 7
    assert colors.dark.startswith("#") and colors.light.startswith("#")
    assert isinstance(colors.is_fallback, bool)


@respx.mock
def test_get_colors_resolves_image_uri_from_url() -> None:
    _mock_bootstrap()
    route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=COLORS_BODY))
    with SpotifyClient() as client:
        client.get_colors("https://i.scdn.co/image/ABCDEF")
    variables = json.loads(dict(httpx.QueryParams(route.calls.last.request.url.query))["variables"])
    assert variables["imageUris"] == ["spotify:image:ABCDEF"]
    assert "operationName=fetchExtractedColors" in str(route.calls.last.request.url)


@respx.mock
def test_get_colors_resolves_image_uri_from_entity() -> None:
    _mock_bootstrap()
    route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=COLORS_BODY))
    with SpotifyClient() as client:
        client.get_colors(_image_track())
    variables = json.loads(dict(httpx.QueryParams(route.calls.last.request.url.query))["variables"])
    assert variables["imageUris"] == ["spotify:image:IMG123"]


def test_get_colors_entity_without_images_raises() -> None:
    track = Track(
        id="x",
        uri="spotify:track:x",
        name="n",
        duration_ms=0,
        explicit=False,
        playable=True,
        preview_url=None,
        artists=(),
        images=(),
        release_date=None,
    )
    with SpotifyClient() as client, pytest.raises(URLError):
        client.get_colors(track)


@respx.mock
def test_get_colors_401_invalidates_and_retries_once() -> None:
    respx.get(BOOTSTRAP_URL).mock(
        side_effect=[
            httpx.Response(200, text=_bootstrap_html(token="STALE")),
            httpx.Response(200, text=_bootstrap_html(token="FRESH")),
        ]
    )
    route = respx.get(PATHFINDER_RE).mock(
        side_effect=[httpx.Response(401), httpx.Response(200, json=COLORS_BODY)]
    )
    with SpotifyClient() as client:
        colors = client.get_colors("spotify:image:abc")
    assert colors.raw.startswith("#")
    assert route.call_count == 2


def test_get_colors_use_after_close_raises() -> None:
    client = SpotifyClient()
    client.close()
    with pytest.raises(SpotifyScraperError):
        client.get_colors("spotify:image:abc")


# --------------------------------------------------------------------------- #
# Async
# --------------------------------------------------------------------------- #


@respx.mock
async def test_get_colors_async() -> None:
    _mock_bootstrap()
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=COLORS_BODY))
    async with AsyncSpotifyClient() as client:
        colors = await client.get_colors("spotify:image:abc")
    assert colors.raw.startswith("#") and len(colors.raw) == 7


async def test_get_colors_async_use_after_close_raises() -> None:
    client = AsyncSpotifyClient()
    await client.aclose()
    with pytest.raises(SpotifyScraperError):
        await client.get_colors("spotify:image:abc")
