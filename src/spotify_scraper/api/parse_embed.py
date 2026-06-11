"""Pure parsing of Spotify embed-page ``__NEXT_DATA__`` payloads.

Embed pages carry a ``__NEXT_DATA__`` script that holds both the entity data
(used as the tier-2 extraction source) and a short-lived anonymous session
token (used to bootstrap tier-1 requests). These helpers are I/O-free so the
sync and async facades can share them.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from spotify_scraper.errors import NotFoundError, ParsingError

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)

_UPDATE_HINT = "Spotify may have changed its embed page format; check for a library update."


@dataclass(frozen=True, slots=True)
class EmbedSession:
    """Anonymous session block extracted from an embed page.

    Attributes:
        access_token: Bearer token for tier-1 pathfinder requests.
        expires_at_ms: Token expiry as a Unix timestamp in milliseconds.
        is_anonymous: Whether the session is an anonymous (credential-free) one.
    """

    access_token: str
    expires_at_ms: int
    is_anonymous: bool


def extract_next_data(html: str) -> dict[str, Any]:
    """Extract the ``__NEXT_DATA__`` JSON object from embed-page HTML.

    Args:
        html: Raw HTML of a Spotify embed page.

    Returns:
        The decoded ``__NEXT_DATA__`` object.

    Raises:
        ParsingError: If the script tag is absent or its body is not a JSON
            object.
    """
    match = _NEXT_DATA_RE.search(html)
    if match is None:
        raise ParsingError(f"No __NEXT_DATA__ script in embed page. {_UPDATE_HINT}")
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ParsingError(f"Malformed __NEXT_DATA__ JSON. {_UPDATE_HINT}") from exc
    if not isinstance(data, dict):
        raise ParsingError(f"__NEXT_DATA__ is not a JSON object. {_UPDATE_HINT}")
    return data


def get_entity(next_data: Mapping[str, Any]) -> dict[str, Any]:
    """Return the embedded entity object from a ``__NEXT_DATA__`` payload.

    Args:
        next_data: A decoded ``__NEXT_DATA__`` object.

    Returns:
        The ``props.pageProps.state.data.entity`` object.

    Raises:
        NotFoundError: If the page reports a missing or unavailable entity
            (``status`` / ``forbiddenReason`` markers in place of entity data).
        ParsingError: If the payload shape is otherwise unexpected.
    """
    page_props = _page_props(next_data)
    if "status" in page_props or "forbiddenReason" in page_props:
        raise NotFoundError("Spotify embed page reports the entity is unavailable.")
    state = _require_mapping(page_props, "state", "props.pageProps.state")
    data = _require_mapping(state, "data", "props.pageProps.state.data")
    entity = data.get("entity")
    if not isinstance(entity, dict):
        raise ParsingError(
            f"Embed payload missing 'props.pageProps.state.data.entity'. {_UPDATE_HINT}"
        )
    return entity


def get_session(next_data: Mapping[str, Any]) -> EmbedSession:
    """Return the anonymous session block from a ``__NEXT_DATA__`` payload.

    Args:
        next_data: A decoded ``__NEXT_DATA__`` object.

    Returns:
        The parsed :class:`EmbedSession`.

    Raises:
        ParsingError: If the session block or any of its fields is missing or
            of the wrong type.
    """
    page_props = _page_props(next_data)
    state = _require_mapping(page_props, "state", "props.pageProps.state")
    settings = _require_mapping(state, "settings", "props.pageProps.state.settings")
    session = _require_mapping(settings, "session", "props.pageProps.state.settings.session")
    token = session.get("accessToken")
    expires = session.get("accessTokenExpirationTimestampMs")
    if not isinstance(token, str) or not token:
        raise ParsingError(f"Embed session missing accessToken. {_UPDATE_HINT}")
    if not isinstance(expires, int):
        raise ParsingError(
            f"Embed session missing accessTokenExpirationTimestampMs. {_UPDATE_HINT}"
        )
    return EmbedSession(
        access_token=token,
        expires_at_ms=expires,
        is_anonymous=bool(session.get("isAnonymous", False)),
    )


def _page_props(next_data: Mapping[str, Any]) -> Mapping[str, Any]:
    props = _require_mapping(next_data, "props", "props")
    return _require_mapping(props, "pageProps", "props.pageProps")


def _require_mapping(container: Mapping[str, Any], key: str, path: str) -> Mapping[str, Any]:
    value = container.get(key)
    if not isinstance(value, Mapping):
        raise ParsingError(f"Embed payload missing {path!r}. {_UPDATE_HINT}")
    return value
