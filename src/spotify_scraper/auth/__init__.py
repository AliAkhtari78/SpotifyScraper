"""Token providers: anonymous bootstrap and cookie-authenticated exchange."""

from __future__ import annotations

from spotify_scraper.auth.anonymous import (
    AnonymousTokenProvider,
    AsyncAnonymousTokenProvider,
)
from spotify_scraper.auth.cookies import (
    AsyncCookieTokenProvider,
    CookieTokenProvider,
    load_sp_dc,
)
from spotify_scraper.auth.session import (
    Session,
    SessionStore,
    clear_session,
    default_config_dir,
    default_session_path,
    load_session,
    save_session,
)

__all__ = [
    "AnonymousTokenProvider",
    "AsyncAnonymousTokenProvider",
    "AsyncCookieTokenProvider",
    "CookieTokenProvider",
    "Session",
    "SessionStore",
    "clear_session",
    "default_config_dir",
    "default_session_path",
    "load_session",
    "load_sp_dc",
    "save_session",
]
