"""Hermetic client login / saved-session wiring tests (sync + async).

The real browser capture is monkeypatched to return a fake ``sp_dc`` so these
run with ZERO network and ZERO browser. They prove ``login`` wires the cookie
and resets the cached cookie-token provider, that save/from_saved_session round-
trips, that a missing session raises ``SessionError``, and that ``logout`` clears
the file.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any, NamedTuple

import pytest
import respx

from spotify_scraper import AsyncSpotifyClient, SpotifyClient
from spotify_scraper.auth.session import load_session, save_session
from spotify_scraper.errors import SessionError

FAKE_SP_DC = "fake_sp_dc_from_browser_capture"
FAKE_EXPIRES_MS = 1_900_000_000_000


class _FakeCapture(NamedTuple):
    """Mirror of ``browser.CapturedLogin`` without importing the Playwright module."""

    sp_dc: str
    sp_dc_expires_ms: int | None


@pytest.fixture
def fake_browser(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Inject a fake ``spotify_scraper.browser`` exposing the capture helpers.

    A module is injected so ``login``'s method-level ``from spotify_scraper.browser
    import ...`` resolves to fakes that do no I/O.
    """
    calls: dict[str, Any] = {"sync": [], "async": []}
    module = types.ModuleType("spotify_scraper.browser")

    def capture_sp_dc(*, timeout: float = 300.0, proxy: str | None = None) -> _FakeCapture:
        calls["sync"].append({"timeout": timeout, "proxy": proxy})
        return _FakeCapture(FAKE_SP_DC, FAKE_EXPIRES_MS)

    async def capture_sp_dc_async(
        *, timeout: float = 300.0, proxy: str | None = None
    ) -> _FakeCapture:
        calls["async"].append({"timeout": timeout, "proxy": proxy})
        return _FakeCapture(FAKE_SP_DC, FAKE_EXPIRES_MS)

    module.capture_sp_dc = capture_sp_dc  # type: ignore[attr-defined]
    module.capture_sp_dc_async = capture_sp_dc_async  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "spotify_scraper.browser", module)
    return calls


@pytest.fixture
def fake_keyring(monkeypatch: pytest.MonkeyPatch) -> dict[tuple[str, str], str]:
    """Inject a minimal in-memory ``keyring`` module so store='keyring' works."""
    module = types.ModuleType("keyring")

    class _Errors:
        class NoKeyringError(Exception):
            """Mimics keyring.errors.NoKeyringError."""

    store: dict[tuple[str, str], str] = {}
    module.errors = _Errors  # type: ignore[attr-defined]
    module.set_password = lambda s, u, p: store.__setitem__((s, u), p)  # type: ignore[attr-defined]
    module.get_password = lambda s, u: store.get((s, u))  # type: ignore[attr-defined]
    module.delete_password = lambda s, u: store.pop((s, u), None)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "keyring", module)
    return store


# --- login wiring (zero network) ----------------------------------------------


def test_login_wires_cookie_and_resets_provider_without_network(
    fake_browser: dict[str, Any],
) -> None:
    with respx.mock(assert_all_mocked=True) as router, SpotifyClient() as client:
        # Pretend a provider was already cached; login must reset it.
        client._cookie_tokens = object()  # type: ignore[assignment]
        client.login(save=False, timeout=5.0, proxy="http://p:1")
        assert client._cookies == FAKE_SP_DC
        assert client._cookie_tokens is None
        assert len(router.calls) == 0
    assert fake_browser["sync"] == [{"timeout": 5.0, "proxy": "http://p:1"}]


async def test_async_login_wires_cookie_without_network(
    fake_browser: dict[str, Any],
) -> None:
    async with AsyncSpotifyClient() as client:
        with respx.mock(assert_all_mocked=True) as router:
            client._cookie_tokens = object()  # type: ignore[assignment]
            await client.login(save=False, timeout=9.0)
            assert client._cookies == FAKE_SP_DC
            assert client._cookie_tokens is None
            assert len(router.calls) == 0
    assert fake_browser["async"] == [{"timeout": 9.0, "proxy": None}]


# --- save + from_saved_session round-trip -------------------------------------


def test_login_save_then_from_saved_session(fake_browser: dict[str, Any], tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    with SpotifyClient() as client:
        client.login(save=True, session_path=path)
    assert path.exists()
    # The captured cookie expiry is threaded through and persisted.
    assert load_session(path=path).sp_dc_expires_ms == FAKE_EXPIRES_MS

    restored = SpotifyClient.from_saved_session(session_path=path, timeout=42.0)
    try:
        assert restored._cookies == FAKE_SP_DC
        # **kwargs are forwarded to the constructor.
        assert isinstance(restored, SpotifyClient)
    finally:
        restored.close()


async def test_async_login_save_then_from_saved_session(
    fake_browser: dict[str, Any], tmp_path: Path
) -> None:
    path = tmp_path / "session.json"
    async with AsyncSpotifyClient() as client:
        await client.login(save=True, session_path=path)
    assert path.exists()

    restored = AsyncSpotifyClient.from_saved_session(session_path=path)
    try:
        assert restored._cookies == FAKE_SP_DC
        assert isinstance(restored, AsyncSpotifyClient)
    finally:
        await restored.aclose()


def test_login_keyring_round_trip(
    fake_browser: dict[str, Any], fake_keyring: dict[tuple[str, str], str], tmp_path: Path
) -> None:
    path = tmp_path / "session.json"
    with SpotifyClient() as client:
        client.login(save=True, store="keyring", session_path=path)
    # The secret is in the keyring; the file holds metadata only.
    assert fake_keyring[("spotifyscraper", "sp_dc")] == FAKE_SP_DC
    assert FAKE_SP_DC not in path.read_text(encoding="utf-8")

    restored = SpotifyClient.from_saved_session(store="keyring", session_path=path)
    try:
        assert restored._cookies == FAKE_SP_DC
    finally:
        restored.close()


def test_from_saved_session_forwards_kwargs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "session.json"
    save_session(FAKE_SP_DC, path=path)

    captured: dict[str, Any] = {}
    real_init = SpotifyClient.__init__

    def _spy(self: SpotifyClient, **kwargs: Any) -> None:
        captured.update(kwargs)
        real_init(self, **kwargs)

    # Verify the saved cookie and every extra kwarg reach the constructor.
    monkeypatch.setattr(SpotifyClient, "__init__", _spy)
    client = SpotifyClient.from_saved_session(session_path=path, user_agent="UA", timeout=42.0)
    try:
        assert captured["cookies"] == FAKE_SP_DC
        assert captured["user_agent"] == "UA"
        assert captured["timeout"] == 42.0
    finally:
        client.close()


# --- missing session ----------------------------------------------------------


def test_from_saved_session_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(SessionError):
        SpotifyClient.from_saved_session(session_path=tmp_path / "absent.json")


async def test_async_from_saved_session_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(SessionError):
        AsyncSpotifyClient.from_saved_session(session_path=tmp_path / "absent.json")


# --- logout -------------------------------------------------------------------


def test_logout_removes_file(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(FAKE_SP_DC, path=path)
    assert path.exists()
    SpotifyClient.logout(session_path=path)
    assert not path.exists()
    # Idempotent.
    SpotifyClient.logout(session_path=path)


async def test_async_logout_removes_file(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(FAKE_SP_DC, path=path)
    AsyncSpotifyClient.logout(session_path=path)
    assert not path.exists()


# --- login after close --------------------------------------------------------


def test_login_after_close_raises(fake_browser: dict[str, Any]) -> None:
    client = SpotifyClient()
    client.close()
    with pytest.raises(Exception, match="closed"):
        client.login(save=False)


async def test_async_login_after_close_raises(fake_browser: dict[str, Any]) -> None:
    client = AsyncSpotifyClient()
    await client.aclose()
    with pytest.raises(Exception, match="closed"):
        await client.login(save=False)
