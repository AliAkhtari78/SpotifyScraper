"""Hermetic tests for cookie-free saved-session introspection + login reuse.

``session_info`` / ``has_saved_session`` report a saved session's status without
ever exposing the cookie, and ``login(reuse=True)`` auto-skips the browser when a
valid saved session exists. All cases use ``tmp_path`` and an injected clock; no
network and no browser.
"""

from __future__ import annotations

import os
import sys
import types
from pathlib import Path
from typing import Any

import pytest
import respx

from spotify_scraper import AsyncSpotifyClient, SpotifyClient
from spotify_scraper.auth.session import (
    SessionInfo,
    SessionStore,
    has_saved_session,
    save_session,
    session_info,
)

SECRET = "sp_dc_super_secret_cookie_value"  # noqa: S105

_POSIX_ONLY = pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits only")


# --- session_info status ------------------------------------------------------


def test_missing_session_is_absent_and_invalid(tmp_path: Path) -> None:
    info = session_info(path=tmp_path / "nope.json")
    assert info.exists is False
    assert info.valid is False
    assert SECRET not in (info.reason or "")
    assert has_saved_session(path=tmp_path / "nope.json") is False


def test_freshly_saved_no_expiry_is_valid(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, path=path, now_ms=1000)
    info = session_info(path=path)
    assert info.exists is True
    assert info.valid is True
    assert info.saved_at_ms == 1000
    assert info.sp_dc_expires_ms is None
    assert info.reason is None
    assert has_saved_session(path=path) is True


def test_future_expiry_is_valid(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, sp_dc_expires_ms=5000, path=path, now_ms=1000)
    info = session_info(path=path, now_ms=1000)
    assert info.valid is True
    assert info.sp_dc_expires_ms == 5000


def test_past_expiry_is_invalid_with_reason(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, sp_dc_expires_ms=2000, path=path, now_ms=1000)
    info = session_info(path=path, now_ms=9999)
    assert info.exists is True
    assert info.valid is False
    assert info.reason is not None
    assert "expired" in info.reason.lower()
    assert SECRET not in info.reason
    assert has_saved_session(path=path, now_ms=9999) is False


@_POSIX_ONLY
def test_insecure_permissions_make_invalid(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, path=path)
    path.chmod(0o644)
    info = session_info(path=path)
    assert info.exists is True
    assert info.valid is False
    assert info.reason is not None
    assert SECRET not in info.reason


def test_corrupt_json_makes_invalid(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    path.write_text("{not json", encoding="utf-8")
    if os.name == "posix":
        path.chmod(0o600)
    info = session_info(path=path)
    assert info.exists is True
    assert info.valid is False
    assert info.reason is not None
    assert SECRET not in info.reason


# --- secret hygiene -----------------------------------------------------------


def test_session_info_repr_carries_no_cookie() -> None:
    info = SessionInfo(
        exists=True, valid=False, saved_at_ms=1, sp_dc_expires_ms=2, reason="expired"
    )
    rendered = repr(info)
    assert SECRET not in rendered
    assert "exists=True" in rendered


def test_session_store_info_delegates(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, path=path, now_ms=1000)
    store = SessionStore("file")
    assert store.has_session(path=path) is True
    info = store.info(path=path)
    assert info.valid is True
    assert SECRET not in repr(info)


# --- login(reuse=...) auto-skip -----------------------------------------------


@pytest.fixture
def fake_browser(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Inject a fake ``spotify_scraper.browser`` recording capture calls."""
    calls: dict[str, Any] = {"sync": [], "async": []}
    module = types.ModuleType("spotify_scraper.browser")

    def capture_sp_dc(*, timeout: float = 300.0, proxy: str | None = None) -> str:
        calls["sync"].append({"timeout": timeout, "proxy": proxy})
        return "freshly_captured_cookie"

    async def capture_sp_dc_async(*, timeout: float = 300.0, proxy: str | None = None) -> str:
        calls["async"].append({"timeout": timeout, "proxy": proxy})
        return "freshly_captured_cookie"

    module.capture_sp_dc = capture_sp_dc  # type: ignore[attr-defined]
    module.capture_sp_dc_async = capture_sp_dc_async  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "spotify_scraper.browser", module)
    return calls


def test_login_reuse_skips_browser_when_valid(fake_browser: dict[str, Any], tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, path=path)
    with respx.mock(assert_all_mocked=True) as router, SpotifyClient() as client:
        client._cookie_tokens = object()  # type: ignore[assignment]
        client.login(reuse=True, session_path=path)
        assert client._cookies == SECRET
        assert client._cookie_tokens is None
        assert len(router.calls) == 0
    # The browser capture was never invoked.
    assert fake_browser["sync"] == []


def test_login_reuse_captures_when_no_session(fake_browser: dict[str, Any], tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    with SpotifyClient() as client:
        client.login(reuse=True, save=False, session_path=path)
        assert client._cookies == "freshly_captured_cookie"
    assert len(fake_browser["sync"]) == 1


def test_login_no_reuse_captures_even_with_valid_session(
    fake_browser: dict[str, Any], tmp_path: Path
) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, path=path)
    with SpotifyClient() as client:
        client.login(reuse=False, save=False, session_path=path)
        assert client._cookies == "freshly_captured_cookie"
    assert len(fake_browser["sync"]) == 1


def test_login_reuse_skips_expired_session(fake_browser: dict[str, Any], tmp_path: Path) -> None:
    # An expired saved session is NOT valid, so reuse falls through to capture.
    path = tmp_path / "session.json"
    save_session(SECRET, sp_dc_expires_ms=1, path=path, now_ms=0)
    with SpotifyClient() as client:
        client.login(reuse=True, save=False, session_path=path)
        assert client._cookies == "freshly_captured_cookie"
    assert len(fake_browser["sync"]) == 1


async def test_async_login_reuse_skips_browser_when_valid(
    fake_browser: dict[str, Any], tmp_path: Path
) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, path=path)
    async with AsyncSpotifyClient() as client:
        with respx.mock(assert_all_mocked=True) as router:
            client._cookie_tokens = object()  # type: ignore[assignment]
            await client.login(reuse=True, session_path=path)
            assert client._cookies == SECRET
            assert client._cookie_tokens is None
            assert len(router.calls) == 0
    assert fake_browser["async"] == []


async def test_async_login_reuse_captures_when_no_session(
    fake_browser: dict[str, Any], tmp_path: Path
) -> None:
    path = tmp_path / "session.json"
    async with AsyncSpotifyClient() as client:
        await client.login(reuse=True, save=False, session_path=path)
        assert client._cookies == "freshly_captured_cookie"
    assert len(fake_browser["async"]) == 1


# --- client session_info() classmethod ----------------------------------------


def test_client_session_info_classmethod(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, path=path, now_ms=1000)
    info = SpotifyClient.session_info(session_path=path)
    assert info.valid is True
    assert SECRET not in repr(info)

    missing = AsyncSpotifyClient.session_info(session_path=tmp_path / "absent.json")
    assert missing.exists is False
    assert missing.valid is False
