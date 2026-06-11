"""Capture live Spotify responses as scrubbed test fixtures.

Fetches the embed page ``__NEXT_DATA__`` payload and the pathfinder GraphQL
response for one well-known entity of each type, removes every credential-like
value, and writes the results under ``tests/fixtures/``.

Run manually (or from the canary workflow) when Spotify changes payload shapes:

    uv run python scripts/capture_fixtures.py
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

# Stable, well-known public entities.
ENTITIES = {
    "track": "4uLU6hMCjMI75M1A2tKUQC",  # Rick Astley - Never Gonna Give You Up
    "album": "4aawyAB9vmqN3uQ7FjRGTy",  # Pitbull - Global Warming
    "artist": "0gxyHStUsqpMadRV0Di1Qt",  # Rick Astley
    "playlist": "37i9dQZF1DXcBWIGoYBM5M",  # Today's Top Hits (editorial)
    "episode": "07gKzPFkbvGF0cHoeG7ARS",  # a Joe Rogan Experience episode
    "show": "4rOoJ6Egrf8K2IrywzwOMk",  # The Joe Rogan Experience
}

# operationName -> (sha256 hash, variables builder). Mirrors api/pathfinder.py;
# refresh hashes from the web-player bundle when Spotify rotates them.
PATHFINDER_OPS = {
    "track": (
        "getTrack",
        "612585ae06ba435ad26369870deaae23b5c8800a256cd8a57e08eddc25a37294",
        lambda eid: {"uri": f"spotify:track:{eid}"},
    ),
    "album": (
        "getAlbum",
        "b9bfabef66ed756e5e13f68a942deb60bd4125ec1f1be8cc42769dc0259b4b10",
        lambda eid: {"uri": f"spotify:album:{eid}", "locale": "", "offset": 0, "limit": 50},
    ),
    "artist": (
        "queryArtistOverview",
        "ae0e2958a4ab645b35ca19ac04d0495ae12d9c5d7b7286217674801a9aab281a",
        lambda eid: {"uri": f"spotify:artist:{eid}", "locale": "", "includePrerelease": False},
    ),
    "playlist": (
        "fetchPlaylist",
        "a65e12194ed5fc443a1cdebed5fabe33ca5b07b987185d63c72483867ad13cb4",
        lambda eid: {
            "uri": f"spotify:playlist:{eid}",
            "offset": 0,
            "limit": 25,
            "enableWatchFeedEntrypoint": False,
        },
    ),
    "episode": (
        "getEpisodeOrChapter",
        "3416929067571ac4b79db16716be3c6ea5f6265f7975a0ee94b1fc5ee1dc1e9d",
        lambda eid: {"uri": f"spotify:episode:{eid}"},
    ),
    "show": (
        "queryShowMetadataV2",
        "aaad798a17a43c0f443c45d630a83df39d2ca1062a090c2e4fb045d6b00ab360",
        lambda eid: {"uri": f"spotify:show:{eid}"},
    ),
}

SCRUB_KEYS = {
    "accessToken",
    "clientId",
    "correlationId",
    "_sentryTraceData",
    "_sentryBaggage",
}


def _get(url: str, token: str | None = None) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)  # noqa: S310 - https only
    with urllib.request.urlopen(req, timeout=20) as response:  # noqa: S310
        return response.read()  # type: ignore[no-any-return]


def scrub(value: Any) -> Any:
    """Recursively blank credential-like values so fixtures are safe to commit."""
    if isinstance(value, dict):
        return {
            key: "REDACTED" if key in SCRUB_KEYS else scrub(item) for key, item in value.items()
        }
    if isinstance(value, list):
        return [scrub(item) for item in value]
    return value


def extract_next_data(html: str) -> dict[str, Any]:
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json"[^>]*>(.*?)</script>', html, re.S
    )
    if match is None:
        raise RuntimeError("__NEXT_DATA__ script tag not found in embed page")
    return json.loads(match.group(1))  # type: ignore[no-any-return]


def main() -> int:
    (FIXTURES / "embed").mkdir(parents=True, exist_ok=True)
    (FIXTURES / "pathfinder").mkdir(parents=True, exist_ok=True)

    token = ""
    for kind, entity_id in ENTITIES.items():
        html = _get(f"https://open.spotify.com/embed/{kind}/{entity_id}").decode()
        next_data = extract_next_data(html)
        if not token:
            session = next_data["props"]["pageProps"]["state"]["settings"]["session"]
            token = session["accessToken"]
        out = FIXTURES / "embed" / f"{kind}.json"
        out.write_text(json.dumps(scrub(next_data), indent=2, sort_keys=True) + "\n")
        print(f"captured embed/{kind}.json")

    for kind, (operation, sha256, build_variables) in PATHFINDER_OPS.items():
        query = urllib.parse.urlencode(
            {
                "operationName": operation,
                "variables": json.dumps(build_variables(ENTITIES[kind])),
                "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": sha256}}),
            }
        )
        url = f"https://api-partner.spotify.com/pathfinder/v1/query?{query}"
        body = json.loads(_get(url, token))
        if "errors" in body:
            print(f"WARNING pathfinder/{kind}: {body['errors']}", file=sys.stderr)
        out = FIXTURES / "pathfinder" / f"{kind}.json"
        out.write_text(json.dumps(scrub(body), indent=2, sort_keys=True) + "\n")
        print(f"captured pathfinder/{kind}.json")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
