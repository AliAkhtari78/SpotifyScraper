"""Unit tests for the CLI ``lyrics`` command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar

import pytest
from typer.testing import CliRunner

from spotify_scraper import AuthenticationError, NotFoundError
from spotify_scraper.cli import main as cli_main
from spotify_scraper.cli.main import app
from spotify_scraper.models.lyrics import Lyrics, LyricsLine

runner = CliRunner()


def _lyrics() -> Lyrics:
    return Lyrics(
        lines=(
            LyricsLine(start_ms=19630, text="We're no strangers to love"),
            LyricsLine(start_ms=23400, text="You know the rules and so do I"),
        ),
        sync_type="LINE_SYNCED",
        provider="MusixMatch",
        language="en",
    )


class FakeClient:
    """A drop-in for :class:`SpotifyClient` recording its constructor kwargs."""

    last_kwargs: ClassVar[dict[str, Any]] = {}
    error: ClassVar[Exception | None] = None

    def __init__(self, **kwargs: Any) -> None:
        FakeClient.last_kwargs = kwargs

    def __enter__(self) -> FakeClient:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def get_lyrics(self, value: str) -> Lyrics:
        if FakeClient.error is not None:
            raise FakeClient.error
        return _lyrics()


@pytest.fixture(autouse=True)
def _patch_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_main, "SpotifyClient", FakeClient)
    monkeypatch.delenv("SPOTIFY_SP_DC", raising=False)
    FakeClient.last_kwargs = {}
    FakeClient.error = None


def test_lyrics_with_cookies_option_emits_json(tmp_path: Path) -> None:
    cookies = tmp_path / "cookies.txt"
    cookies.write_text("placeholder", encoding="utf-8")
    result = runner.invoke(app, ["lyrics", TRACK := "x", "--cookies", str(cookies)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["sync_type"] == "LINE_SYNCED"
    assert payload["lines"][0]["text"] == "We're no strangers to love"
    assert FakeClient.last_kwargs["cookies"] == cookies
    assert TRACK == "x"


def test_lyrics_falls_back_to_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPOTIFY_SP_DC", "env_sp_dc_value")
    result = runner.invoke(app, ["lyrics", "x"])
    assert result.exit_code == 0, result.output
    assert FakeClient.last_kwargs["cookies"] == "env_sp_dc_value"


def test_lyrics_without_cookies_or_env_fails() -> None:
    result = runner.invoke(app, ["lyrics", "x"])
    assert result.exit_code != 0
    assert "SPOTIFY_SP_DC" in result.output or "cookies" in result.output


def test_lyrics_pretty_indents(tmp_path: Path) -> None:
    cookies = tmp_path / "c.txt"
    cookies.write_text("x", encoding="utf-8")
    result = runner.invoke(app, ["lyrics", "x", "--cookies", str(cookies), "--pretty"])
    assert result.exit_code == 0
    assert "\n  " in result.stdout


def test_lyrics_auth_error_exits_4(tmp_path: Path) -> None:
    cookies = tmp_path / "c.txt"
    cookies.write_text("x", encoding="utf-8")
    FakeClient.error = AuthenticationError("bad cookie")
    result = runner.invoke(app, ["lyrics", "x", "--cookies", str(cookies)])
    assert result.exit_code == 4
    assert "error:" in result.stderr


def test_lyrics_not_found_exits_3(tmp_path: Path) -> None:
    cookies = tmp_path / "c.txt"
    cookies.write_text("x", encoding="utf-8")
    FakeClient.error = NotFoundError("no lyrics")
    result = runner.invoke(app, ["lyrics", "x", "--cookies", str(cookies)])
    assert result.exit_code == 3
