"""A one-time, opt-out "star us" hint for interactive CLI users.

The hint is deliberately unobtrusive: it prints once, ever, to **stderr** only,
and only when stderr is a real terminal — so it never pollutes piped JSON, CI
logs, or `--output` files. Set ``SPOTIFYSCRAPER_NO_HINT=1`` to silence it
entirely. Any filesystem hiccup silently disables it; it never raises.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO_URL = "https://github.com/AliAkhtari78/SpotifyScraper"
_OPT_OUT_ENV = "SPOTIFYSCRAPER_NO_HINT"


def _marker_path() -> Path:
    """Return the once-ever marker file path under the user's cache directory."""
    base = os.environ.get("XDG_CACHE_HOME") or os.environ.get("LOCALAPPDATA")
    root = Path(base) if base else Path.home() / ".cache"
    return root / "spotifyscraper" / "star-hint-shown"


def maybe_star_hint() -> None:
    """Print the star hint once for interactive users; otherwise do nothing.

    No-ops when ``SPOTIFYSCRAPER_NO_HINT`` is set, when stderr is not a TTY, or
    when the hint has already been shown. Never writes to stdout and never raises.
    """
    if os.environ.get(_OPT_OUT_ENV):
        return
    if not sys.stderr.isatty():
        return
    marker = _marker_path()
    try:
        if marker.exists():
            return
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("1", encoding="utf-8")
    except OSError:
        return  # never let a cache-write problem break the CLI
    print(
        f"\n⭐ Enjoying spotifyscraper? A star helps others find it: {_REPO_URL}"
        f"\n   (silence this with {_OPT_OUT_ENV}=1)",
        file=sys.stderr,
    )
