"""respx-driven tests for the synchronous client's plural batch helpers.

Reuses the embed/pathfinder fixture harness from
:mod:`tests.unit.test_client_entities`. Covers the happy path, partial
failure (one 404 captured, order preserved, no raise), malformed input
captured as a :class:`URLError`, fail-fast on a closed client,
:meth:`BatchItem.unwrap`, and cap forwarding for playlists/shows.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest
import respx

from spotify_scraper import SpotifyClient
from spotify_scraper.errors import NotFoundError, SpotifyScraperError, URLError
from spotify_scraper.models.track import Track

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PATHFINDER_RE = re.compile(r"https://api-partner\.spotify\.com/pathfinder/v1/query.*")

IDS: dict[str, str] = {
    "album": "6N9PS4QXF1D0OWPk0Sxtb4",
    "artist": "0gxyHStUsqpMadRV0Di1Qt",
    "playlist": "37i9dQZF1DXcBWIGoYBM5M",
    "episode": "07gKzPFkbvGF0cHoeG7ARS",
    "show": "4rOoJ6Egrf8K2IrywzwOMk",
    "track": "2QjOHCTQ1Jl3zawyYOpxh6",
}


def _embed_next_data(kind: str) -> dict[str, Any]:
    return json.loads((FIXTURES / "embed" / f"{kind}.json").read_text())


def _pathfinder_body(kind: str) -> dict[str, Any]:
    return json.loads((FIXTURES / "pathfinder" / f"{kind}.json").read_text())


def _embed_url(kind: str, entity_id: str) -> str:
    return f"https://open.spotify.com/embed/{kind}/{entity_id}"


def _embed_html(kind: str, *, token: str = "EMBED_TOKEN") -> str:  # noqa: S107
    next_data = copy.deepcopy(_embed_next_data(kind))
    session = next_data["props"]["pageProps"]["state"]["settings"]["session"]
    session["accessToken"] = token
    session["accessTokenExpirationTimestampMs"] = 9_999_999_999_999
    body = json.dumps(next_data)
    return f'<script id="__NEXT_DATA__" type="application/json">{body}</script>'


def _variables(query: str) -> str:
    return parse_qs(query)["variables"][0]


# --------------------------------------------------------------------------- #
# Happy path
# --------------------------------------------------------------------------- #


@respx.mock
def test_get_tracks_happy_path_ordered() -> None:
    ids = [IDS["track"], IDS["album"], IDS["artist"]]  # any valid track IDs
    for entity_id in ids:
        respx.get(_embed_url("track", entity_id)).mock(
            return_value=httpx.Response(200, text=_embed_html("track"))
        )
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=_pathfinder_body("track")))

    with SpotifyClient() as client:
        items = client.get_tracks(ids)

    assert [item.value for item in items] == ids
    assert all(item.ok for item in items)
    assert all(isinstance(item.result, Track) for item in items)
    assert items[0].unwrap().name


# --------------------------------------------------------------------------- #
# Partial failure
# --------------------------------------------------------------------------- #


@respx.mock
def test_get_tracks_partial_failure_preserves_order() -> None:
    good = IDS["track"]
    dead = IDS["album"]  # a syntactically valid but "missing" ID
    respx.get(_embed_url("track", good)).mock(
        return_value=httpx.Response(200, text=_embed_html("track"))
    )
    respx.get(_embed_url("track", dead)).mock(return_value=httpx.Response(404, text="nope"))
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=_pathfinder_body("track")))

    with SpotifyClient() as client:
        items = client.get_tracks([good, dead])

    assert [item.value for item in items] == [good, dead]
    assert items[0].ok
    assert isinstance(items[0].result, Track)
    assert not items[1].ok
    assert isinstance(items[1].error, NotFoundError)
    with pytest.raises(NotFoundError):
        items[1].unwrap()


# --------------------------------------------------------------------------- #
# Malformed input
# --------------------------------------------------------------------------- #


@respx.mock
def test_get_tracks_malformed_input_captured_as_urlerror() -> None:
    good = IDS["track"]
    bad = "not-a-spotify-id"
    respx.get(_embed_url("track", good)).mock(
        return_value=httpx.Response(200, text=_embed_html("track"))
    )
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=_pathfinder_body("track")))

    with SpotifyClient() as client:
        items = client.get_tracks([bad, good])

    assert [item.value for item in items] == [bad, good]
    assert not items[0].ok
    assert isinstance(items[0].error, URLError)
    assert items[1].ok


# --------------------------------------------------------------------------- #
# Fail-fast on a closed client
# --------------------------------------------------------------------------- #


def test_get_tracks_closed_client_raises_up_front() -> None:
    client = SpotifyClient()
    client.close()
    with pytest.raises(SpotifyScraperError):
        client.get_tracks([IDS["track"]])


# --------------------------------------------------------------------------- #
# Cap forwarding
# --------------------------------------------------------------------------- #


def _playlist_page(count: int) -> dict[str, Any]:
    body = copy.deepcopy(_pathfinder_body("playlist"))
    template = body["data"]["playlistV2"]["content"]["items"][0]
    items: list[dict[str, Any]] = []
    for index in range(count):
        item = copy.deepcopy(template)
        item["uid"] = f"uid{index}"
        item["itemV2"]["data"]["uri"] = f"spotify:track:{index:022d}"
        item["itemV2"]["data"]["name"] = f"Track {index}"
        items.append(item)
    body["data"]["playlistV2"]["content"]["items"] = items
    body["data"]["playlistV2"]["content"]["totalCount"] = 500
    return body


@respx.mock
def test_get_playlists_forwards_max_tracks() -> None:
    respx.get(_embed_url("playlist", IDS["playlist"])).mock(
        return_value=httpx.Response(200, text=_embed_html("playlist"))
    )
    route = respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=_playlist_page(50)))

    with SpotifyClient() as client:
        items = client.get_playlists([IDS["playlist"]], max_tracks=10)

    assert items[0].ok
    # The cap reaches the underlying get_playlist: only 10 of the 50 available
    # tracks are kept, and pagination stops (a single pathfinder request).
    assert len(items[0].unwrap().tracks) == 10
    assert route.call_count == 1


def _show_router(metadata: dict[str, Any], *, total: int) -> Any:
    def _show_episodes_page(offset: int, limit: int) -> dict[str, Any]:
        body = copy.deepcopy(_pathfinder_body("show_episodes"))
        node = body["data"]["podcastUnionV2"]["episodesV2"]
        template = node["items"][0]
        items: list[dict[str, Any]] = []
        for index in range(offset, min(offset + limit, total)):
            item = copy.deepcopy(template)
            item["entity"]["data"]["uri"] = f"spotify:episode:{index:022d}"
            item["entity"]["data"]["name"] = f"Episode {index}"
            items.append(item)
        node["items"] = items
        node["totalCount"] = total
        return body

    def handler(request: httpx.Request) -> httpx.Response:
        query = request.url.query.decode()
        operation = parse_qs(query)["operationName"][0]
        if operation == "queryShowMetadataV2":
            return httpx.Response(200, json=metadata)
        variables = json.loads(_variables(query))
        return httpx.Response(
            200, json=_show_episodes_page(variables["offset"], variables["limit"])
        )

    return handler


@respx.mock
def test_get_shows_forwards_max_episodes() -> None:
    respx.get(_embed_url("show", IDS["show"])).mock(
        return_value=httpx.Response(200, text=_embed_html("show"))
    )
    respx.get(PATHFINDER_RE).mock(side_effect=_show_router(_pathfinder_body("show"), total=2707))

    with SpotifyClient() as client:
        items = client.get_shows([IDS["show"]], max_episodes=10)

    assert items[0].ok
    assert len(items[0].unwrap().episodes) == 10
