"""Spotify pathfinder GraphQL: the single source of persisted-query hashes.

This module centralizes every pathfinder operation (name, persisted-query
sha256, variables builder) so a rotated hash is a one-line fix. It also builds
the GET request URLs and classifies responses into the library's error model.
All functions here are I/O-free; the sync and async facades reuse them.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
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
    "album": Operation(
        "getAlbum",
        "b9bfabef66ed756e5e13f68a942deb60bd4125ec1f1be8cc42769dc0259b4b10",
        lambda eid: {"uri": f"spotify:album:{eid}", "locale": "", "offset": 0, "limit": 50},
    ),
    "artist": Operation(
        "queryArtistOverview",
        "ae0e2958a4ab645b35ca19ac04d0495ae12d9c5d7b7286217674801a9aab281a",
        lambda eid: {"uri": f"spotify:artist:{eid}", "locale": "", "includePrerelease": False},
    ),
    "playlist": Operation(
        "fetchPlaylist",
        "a65e12194ed5fc443a1cdebed5fabe33ca5b07b987185d63c72483867ad13cb4",
        lambda eid: {
            "uri": f"spotify:playlist:{eid}",
            "offset": 0,
            "limit": 100,
            "enableWatchFeedEntrypoint": False,
        },
    ),
    "episode": Operation(
        "getEpisodeOrChapter",
        "3416929067571ac4b79db16716be3c6ea5f6265f7975a0ee94b1fc5ee1dc1e9d",
        lambda eid: {"uri": f"spotify:episode:{eid}"},
    ),
    "show": Operation(
        "queryShowMetadataV2",
        "aaad798a17a43c0f443c45d630a83df39d2ca1062a090c2e4fb045d6b00ab360",
        lambda eid: {"uri": f"spotify:show:{eid}"},
    ),
    "show_episodes": Operation(
        "queryPodcastEpisodes",
        "06046f9b939d56c8eb7cdbb687da938de1164c006871aec91dc26e4dc7d8eb08",
        lambda eid: {"uri": f"spotify:show:{eid}", "offset": 0, "limit": 50},
    ),
    "canvas": Operation(
        "canvas",
        "575138ab27cd5c1b3e54da54d0a7cc8d85485402de26340c2145f0f6bb5e7a9f",
        lambda eid: {"trackUri": f"spotify:track:{eid}"},
    ),
    "artist_related": Operation(
        "queryArtistRelated",
        "3d031d6cb22a2aa7c8d203d49b49df731f58b1e2799cc38d9876d58771aa66f3",
        lambda eid: {"uri": f"spotify:artist:{eid}"},
    ),
    "artist_discography": Operation(
        "queryArtistDiscographyAll",
        "5e07d323febb57b4a56a42abbf781490e58764aa45feb6e3dc0591564fc56599",
        lambda eid: {"uri": f"spotify:artist:{eid}", "offset": 0, "limit": 50},
    ),
    "similar_albums": Operation(
        "similarAlbumsBasedOnThisTrack",
        "1d1f93a737498adca2c892c73af87fc0b052afe4e1a33c989540c32413dfae17",
        lambda eid: {"uri": f"spotify:track:{eid}", "limit": 10},
    ),
    "artist_concerts": Operation(
        "ArtistConcerts",
        "ef53c43b865496b9890b7167eab1dc614a8949ef9451b3c41184ea888de8bd2b",
        lambda eid: {"artistUri": f"spotify:artist:{eid}", "includeNearby": False},
    ),
}


SEARCH_OPERATION = Operation(
    "searchDesktop",
    "eff59fa0a3d026b88b56fddbcf4bdfa16a186b8175a5c1a358c072e053c2e5b0",
    lambda query: {
        "searchTerm": query,
        "offset": 0,
        "limit": 10,
        "numberOfTopResults": 5,
        "includeAudiobooks": True,
        "includePreReleases": True,
        "includeAlbumPreReleases": False,
        "includeAuthors": False,
        "includeEpisodeContentRatingsV2": False,
    },
)
"""The anonymous aggregate-search operation.

This is the ONLY place the ``searchDesktop`` persisted-query hash may live; a
Spotify rotation is a one-line edit here. The ``build_variables`` argument is the
free-text query (not an entity ID), so it is deliberately kept out of the entity
``OPERATIONS`` table whose builders take an entity ID.
"""


def build_url(
    kind: str,
    entity_id: str,
    *,
    variable_overrides: Mapping[str, Any] | None = None,
) -> str:
    """Build the persisted-query GET URL for an entity.

    Args:
        kind: The operation key (e.g. ``"track"``).
        entity_id: The 22-character entity ID.
        variable_overrides: Optional variables merged over the built ones,
            used for ``offset``/``limit`` pagination.

    Returns:
        The fully URL-encoded pathfinder query URL.

    Raises:
        KeyError: If ``kind`` has no registered operation.
    """
    operation = OPERATIONS[kind]
    variables = operation.build_variables(entity_id)
    if variable_overrides:
        variables.update(variable_overrides)
    params = {
        "operationName": operation.name,
        "variables": json.dumps(variables, separators=(",", ":")),
        "extensions": json.dumps(
            {"persistedQuery": {"version": 1, "sha256Hash": operation.sha256}},
            separators=(",", ":"),
        ),
    }
    return f"{PATHFINDER_URL}?{urlencode(params)}"


def build_search_url(
    query: str,
    *,
    variable_overrides: Mapping[str, Any] | None = None,
) -> str:
    """Build the persisted-query GET URL for an aggregate search.

    Mirrors :func:`build_url` but is driven by a free-text query rather than an
    entity ID, using the dedicated :data:`SEARCH_OPERATION`.

    Args:
        query: The free-text search term.
        variable_overrides: Optional variables merged over the built ones,
            used for ``limit``/``offset`` paging.

    Returns:
        The fully URL-encoded pathfinder search query URL.
    """
    variables = SEARCH_OPERATION.build_variables(query)
    if variable_overrides:
        variables.update(variable_overrides)
    params = {
        "operationName": SEARCH_OPERATION.name,
        "variables": json.dumps(variables, separators=(",", ":")),
        "extensions": json.dumps(
            {"persistedQuery": {"version": 1, "sha256Hash": SEARCH_OPERATION.sha256}},
            separators=(",", ":"),
        ),
    }
    return f"{PATHFINDER_URL}?{urlencode(params)}"


COLORS_OPERATION = Operation(
    "fetchExtractedColors",
    "36e90fcaea00d47c695fce31874efeb2519b97d4cd0ee1abfb4f8dc9348596ea",
    lambda image_uri: {"imageUris": [image_uri]},
)
"""The anonymous cover-art color-extraction operation.

This is the ONLY place the ``fetchExtractedColors`` persisted-query hash may
live; a Spotify rotation is a one-line edit here. It is driven by a list of
``spotify:image:<id>`` uris rather than an entity id, so it is kept out of the
entity ``OPERATIONS`` table whose builders take an entity id.
"""


def build_colors_url(image_uris: Sequence[str]) -> str:
    """Build the persisted-query GET URL for cover-art color extraction.

    Args:
        image_uris: One or more ``spotify:image:<id>`` image uris.

    Returns:
        The fully URL-encoded pathfinder color-extraction query URL.
    """
    variables = {"imageUris": list(image_uris)}
    params = {
        "operationName": COLORS_OPERATION.name,
        "variables": json.dumps(variables, separators=(",", ":")),
        "extensions": json.dumps(
            {"persistedQuery": {"version": 1, "sha256Hash": COLORS_OPERATION.sha256}},
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
