"""In-memory MCP client tests for the SpotifyScraper MCP server.

Drives the real ``FastMCP`` server through an in-process client session, with
the underlying Spotify HTTP calls mocked by respx.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import httpx
import pytest
import respx

pytest.importorskip("mcp")

from mcp.shared.memory import (
    create_connected_server_and_client_session as connect,
)

from spotify_scraper.mcp import build_server

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
EMBED_TRACK_RE = re.compile(r"https://open\.spotify\.com/embed/track/.*")
PATHFINDER_RE = re.compile(r"https://api-partner\.spotify\.com/pathfinder/v1/query.*")
IMAGE_RE = re.compile(r"https://i\.scdn\.co/.*")

EMBED_NEXT_DATA: dict[str, Any] = json.loads(
    (FIXTURES / "embed" / "track.json").read_text(encoding="utf-8")
)
TRACK_PF: dict[str, Any] = json.loads(
    (FIXTURES / "pathfinder" / "track.json").read_text(encoding="utf-8")
)
COLORS_PF: dict[str, Any] = json.loads(
    (FIXTURES / "pathfinder" / "colors.json").read_text(encoding="utf-8")
)
TRACK_ID = "4uLU6hMCjMI75M1A2tKUQC"


def _embed_html() -> str:
    return (
        f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(EMBED_NEXT_DATA)}</script>'
    )


def _mock_track() -> None:
    respx.get(EMBED_TRACK_RE).mock(return_value=httpx.Response(200, text=_embed_html()))
    respx.get(PATHFINDER_RE).mock(return_value=httpx.Response(200, json=TRACK_PF))


def _pathfinder_dispatch(request: httpx.Request) -> httpx.Response:
    """Return the track or colors payload by the request's ``operationName``."""
    op = httpx.QueryParams(request.url.query).get("operationName")
    if op == "fetchExtractedColors":
        return httpx.Response(200, json=COLORS_PF)
    return httpx.Response(200, json=TRACK_PF)


# --------------------------------------------------------------------------- #
# Capability listing
# --------------------------------------------------------------------------- #


async def test_lists_tools_resources_prompts() -> None:
    server = build_server()
    async with connect(server) as session:
        tools = {t.name for t in (await session.list_tools()).tools}
        templates = {
            str(t.uriTemplate) for t in (await session.list_resource_templates()).resourceTemplates
        }
        prompts = {p.name for p in (await session.list_prompts()).prompts}

    # A representative span of the tool surface, including the batch + visuals tools.
    for name in (
        "get_track",
        "search",
        "get_related_artists",
        "get_canvas",
        "get_cover_image",
        "get_tracks",
        "get_albums",
        "get_track_visuals",
    ):
        assert name in tools
    assert "spotify://track/{track_id}" in templates
    assert "describe_album" in prompts


# --------------------------------------------------------------------------- #
# Tool calls
# --------------------------------------------------------------------------- #


@respx.mock
async def test_call_get_track_returns_structured_output() -> None:
    _mock_track()
    server = build_server()
    async with connect(server) as session:
        result = await session.call_tool("get_track", {"value": TRACK_ID})
    assert result.isError is False
    payload = result.structuredContent or json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload.get("uri", "").startswith("spotify:track:")
    assert payload.get("name")


async def test_list_charts_tool_needs_no_network() -> None:
    server = build_server()
    async with respx.mock(assert_all_mocked=True), connect(server) as session:
        result = await session.call_tool("list_charts", {})
    payload = result.structuredContent or json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert any(c["key"] == "top-50-global" for c in payload["charts"])


async def test_auth_tool_without_cookie_errors_cleanly() -> None:
    server = build_server(sp_dc=None)
    async with respx.mock(assert_all_mocked=True) as router, connect(server) as session:
        result = await session.call_tool("get_credits", {"value": TRACK_ID})
    assert result.isError is True
    text = result.content[0].text  # type: ignore[union-attr]
    assert "SPOTIFY_SP_DC" in text
    # No network was touched — the auth gate fires before any request.
    assert len(router.calls) == 0


@respx.mock
async def test_cover_image_tool_returns_image_content() -> None:
    _mock_track()
    respx.get(IMAGE_RE).mock(return_value=httpx.Response(200, content=b"JPEGDATA"))
    server = build_server()
    async with connect(server) as session:
        result = await session.call_tool("get_cover_image", {"value": TRACK_ID, "kind": "track"})
    assert result.isError is False
    block = result.content[0]
    assert block.type == "image"
    assert block.mimeType.startswith("image/")  # type: ignore[union-attr]


@respx.mock
async def test_track_resource_read() -> None:
    _mock_track()
    server = build_server()
    async with connect(server) as session:
        result = await session.read_resource(f"spotify://track/{TRACK_ID}")  # type: ignore[arg-type]
    payload = json.loads(result.contents[0].text)  # type: ignore[union-attr]
    assert payload["uri"].startswith("spotify:track:")


async def test_prompt_render() -> None:
    server = build_server()
    async with connect(server) as session:
        result = await session.get_prompt("describe_album", {"album": "Random Access Memories"})
    text = result.messages[0].content.text  # type: ignore[union-attr]
    assert "get_album" in text
    assert "Random Access Memories" in text


# --------------------------------------------------------------------------- #
# Batch tools + visual composite
# --------------------------------------------------------------------------- #


@respx.mock
async def test_get_tracks_batch_returns_ordered_items() -> None:
    _mock_track()
    server = build_server()
    async with connect(server) as session:
        result = await session.call_tool("get_tracks", {"values": [TRACK_ID, TRACK_ID]})
    assert result.isError is False
    payload = result.structuredContent or json.loads(result.content[0].text)  # type: ignore[union-attr]
    items = payload["items"]
    assert len(items) == 2
    assert all(item["ok"] for item in items)
    assert items[0]["value"] == TRACK_ID
    assert items[0]["error"] is None
    assert items[0]["result"]["uri"].startswith("spotify:track:")


@respx.mock
async def test_get_tracks_batch_captures_per_item_failure() -> None:
    _mock_track()
    server = build_server()
    async with connect(server) as session:
        result = await session.call_tool("get_tracks", {"values": [TRACK_ID, "@@not-a-track@@"]})
    assert result.isError is False  # the batch as a whole never errors
    payload = result.structuredContent or json.loads(result.content[0].text)  # type: ignore[union-attr]
    good, bad = payload["items"]
    assert good["ok"] is True and good["result"] is not None
    assert bad["ok"] is False
    assert bad["result"] is None
    assert bad["error"]  # a non-empty captured message


@respx.mock
async def test_get_track_visuals_combines_track_colors_canvas() -> None:
    respx.get(EMBED_TRACK_RE).mock(return_value=httpx.Response(200, text=_embed_html()))
    respx.get(PATHFINDER_RE).mock(side_effect=_pathfinder_dispatch)
    server = build_server(sp_dc=None)  # no cookie → canvas is best-effort null
    async with connect(server) as session:
        result = await session.call_tool("get_track_visuals", {"value": TRACK_ID})
    assert result.isError is False
    payload = result.structuredContent or json.loads(result.content[0].text)  # type: ignore[union-attr]
    assert payload["track"]["uri"].startswith("spotify:track:")
    assert payload["colors"]["raw"].startswith("#")
    assert payload["canvas"] is None
