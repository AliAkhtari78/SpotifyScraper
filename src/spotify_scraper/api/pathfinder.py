"""Spotify pathfinder GraphQL: the single source of persisted-query hashes.

This module centralizes every pathfinder operation (name, persisted-query
sha256, variables builder) so a rotated hash is a one-line fix. It also builds
the GET request URLs and classifies responses into the library's error model.
All functions here are I/O-free; the sync and async facades reuse them.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from spotify_scraper.errors import NotFoundError, ParsingError, TokenError

PATHFINDER_URL = "https://api-partner.spotify.com/pathfinder/v1/query"

_UPDATE_HINT = "Spotify may have changed its API; check for a library update."


@dataclass(frozen=True, slots=True)
class Operation:
    """A pathfinder GraphQL operation backed by a persisted query.

    Attributes:
        name: The GraphQL ``operationName``.
        sha256: The persisted-query sha256 hash Spotify expects.
        build_variables: Maps an entity ID to the operation's variables.
    """

    name: str
    sha256: str
    build_variables: Callable[[str], dict[str, Any]]


OPERATIONS: dict[str, Operation] = {
    "track": Operation(
        "getTrack",
        "612585ae06ba435ad26369870deaae23b5c8800a256cd8a57e08eddc25a37294",
        lambda eid: {"uri": f"spotify:track:{eid}"},
    ),
}


def build_url(kind: str, entity_id: str) -> str:
    """Build the persisted-query GET URL for an entity.

    Args:
        kind: The operation key (e.g. ``"track"``).
        entity_id: The 22-character entity ID.

    Returns:
        The fully URL-encoded pathfinder query URL.

    Raises:
        KeyError: If ``kind`` has no registered operation.
    """
    operation = OPERATIONS[kind]
    params = {
        "operationName": operation.name,
        "variables": json.dumps(operation.build_variables(entity_id), separators=(",", ":")),
        "extensions": json.dumps(
            {"persistedQuery": {"version": 1, "sha256Hash": operation.sha256}},
            separators=(",", ":"),
        ),
    }
    return f"{PATHFINDER_URL}?{urlencode(params)}"


def auth_headers(token: str) -> dict[str, str]:
    """Return the authorization headers for a pathfinder request.

    Args:
        token: An anonymous bearer access token.

    Returns:
        Headers carrying the bearer token and the web-player platform marker.
    """
    return {"Authorization": f"Bearer {token}", "app-platform": "WebPlayer"}


def classify_response(status: int, body: Mapping[str, Any] | None) -> dict[str, Any]:
    """Classify a pathfinder response into parsed data or a library error.

    Args:
        status: The HTTP status code of the response.
        body: The decoded JSON body, or ``None`` when it could not be parsed.

    Returns:
        The ``body["data"]`` object on success.

    Raises:
        TokenError: On HTTP 401, signalling the bearer token must be refreshed.
        ParsingError: When the body reports ``PersistedQueryNotFound`` (a
            rotated hash) or is otherwise unusable.
        NotFoundError: When the response is well-formed but the requested
            entity union is missing or null.
    """
    if status == 401:
        raise TokenError("Pathfinder rejected the anonymous token (HTTP 401).")
    if body is None:
        raise ParsingError(f"Pathfinder returned no JSON body (HTTP {status}). {_UPDATE_HINT}")
    errors = body.get("errors")
    if isinstance(errors, list) and _has_persisted_query_error(errors):
        raise ParsingError(
            f"Spotify changed their persisted-query API (PersistedQueryNotFound). {_UPDATE_HINT}"
        )
    data = body.get("data")
    if not isinstance(data, Mapping):
        raise ParsingError(f"Pathfinder response missing 'data'. {_UPDATE_HINT}")
    if _has_null_union(data):
        raise NotFoundError("Spotify pathfinder returned a null entity union.")
    return dict(data)


def _has_persisted_query_error(errors: list[Any]) -> bool:
    for error in errors:
        if isinstance(error, Mapping) and error.get("message") == "PersistedQueryNotFound":
            return True
    return False


def _has_null_union(data: Mapping[str, Any]) -> bool:
    if not data:
        return True
    return all(value is None for value in data.values())
