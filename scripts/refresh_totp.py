"""Re-extract Spotify's TOTP secret table from the current web-player bundle.

Run this when lyrics start failing with ``totpVerExpired`` (Spotify rotated the
secret). It prints an updated ``TOTP_SECRETS`` tuple to paste into
``src/spotify_scraper/auth/totp.py``.

    uv run python scripts/refresh_totp.py
"""

from __future__ import annotations

import re
import sys
import urllib.request

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})  # noqa: S310 - https only
    with urllib.request.urlopen(req, timeout=20) as response:  # noqa: S310
        return response.read().decode()


def main() -> int:
    home = _fetch("https://open.spotify.com/")
    match = re.search(
        r"https://open\.spotifycdn\.com/cdn/build/web-player/web-player\.[a-f0-9]+\.js", home
    )
    if match is None:
        print("Could not find the web-player bundle URL.", file=sys.stderr)
        return 1
    bundle = _fetch(match.group(0))

    array = re.search(r"let eU=\[(.*?)\]\.map", bundle)
    if array is None:
        print("Could not find the eU secret array (the bundle layout changed).", file=sys.stderr)
        return 1
    pairs = re.findall(r"""secret:(['"])(.*?)\1,version:(\d+)""", array.group(1))
    if not pairs:
        print("Found the eU array but no secret/version pairs.", file=sys.stderr)
        return 1

    print(f"# Extracted from {match.group(0)}")
    print("TOTP_SECRETS: tuple[tuple[int, str], ...] = (")
    for _quote, secret, version in pairs:
        print(f"    ({version}, {secret!r}),")
    print(")")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
