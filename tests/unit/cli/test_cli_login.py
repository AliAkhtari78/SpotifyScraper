"""Hermetic tests for the CLI ``login`` / ``logout`` commands.

The browser capture is faked via an injected ``spotify_scraper.browser`` module
and the config dir is redirected to ``tmp_path``. These prove the printed output
carries the saved/cleared path and NEVER the cookie, plus exit codes and the
missing-browser-extra message.
"""

from __future__ import annotations

import builtins
import sys
import types
from pathlib import Path
from typing import Any, NamedTuple

import pytest
from typer.testing import CliRunner

from spotify_scraper.cli.main import app

runner = CliRunner()

FAKE_SP_DC = "fake_cli_sp_dc_secret_value"
FAKE_EXPIRES_MS = 1_900_000_000_000


class _FakeCapture(NamedTuple):
    """Mirror of ``browser.CapturedLogin`` without importing the Playwright module."""

    sp_dc: str
    sp_dc_expires_ms: int | None


@pytest.fixture(autouse=True)
def _config_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.setenv("SPOTIFYSCRAPER_CONFIG_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def fake_browser(monkeypatch: pytest.MonkeyPatch) -> None:
    module = types.ModuleType("spotify_scraper.browser")

    def capture_sp_dc(*, timeout: float = 300.0, proxy: str | None = None) -> _FakeCapture:
        return _FakeCapture(FAKE_SP_DC, FAKE_EXPIRES_MS)

    module.capture_sp_dc = capture_sp_dc  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "spotify_scraper.browser", module)


def test_login_prints_path_never_cookie(fake_browser: None, _config_dir: Path) -> None:
    result = runner.invoke(app, ["login"])
    assert result.exit_code == 0, result.output
    saved = _config_dir / "session.json"
    assert str(saved) in result.output
    assert FAKE_SP_DC not in result.output
    assert saved.exists()


def test_logout_prints_cleared_path(_config_dir: Path) -> None:
    # Pre-create a session, then clear it.
    from spotify_scraper.auth.session import save_session

    save_session(FAKE_SP_DC, path=_config_dir / "session.json")
    result = runner.invoke(app, ["logout"])
    assert result.exit_code == 0, result.output
    assert str(_config_dir / "session.json") in result.output
    assert FAKE_SP_DC not in result.output
    assert not (_config_dir / "session.json").exists()


def test_logout_is_idempotent_when_absent(_config_dir: Path) -> None:
    result = runner.invoke(app, ["logout"])
    assert result.exit_code == 0, result.output


def test_login_missing_browser_extra_message(
    monkeypatch: pytest.MonkeyPatch, _config_dir: Path
) -> None:
    monkeypatch.delitem(sys.modules, "spotify_scraper.browser", raising=False)
    real_import = builtins.__import__

    def _block(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "playwright" or name.startswith("playwright."):
            raise ImportError("No module named 'playwright'")
        return real_import(name, *args, **kwargs)

    for mod in list(sys.modules):
        if mod == "spotify_scraper.browser" or mod.startswith("playwright"):
            monkeypatch.delitem(sys.modules, mod, raising=False)
    monkeypatch.setattr(builtins, "__import__", _block)

    result = runner.invoke(app, ["login"])
    assert result.exit_code == 1
    assert "spotifyscraper[browser]" in result.output
    assert FAKE_SP_DC not in result.output
