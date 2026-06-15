"""Unit tests for the CLI ``transcript`` command."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar

import pytest
from typer.testing import CliRunner

from spotify_scraper import AuthenticationError, NotFoundError
from spotify_scraper.cli import main as cli_main
from spotify_scraper.cli.main import app
from spotify_scraper.models.transcript import Transcript, TranscriptLine

runner = CliRunner()


def _transcript() -> Transcript:
    return Transcript(
        lines=(
            TranscriptLine(start_ms=0, text="Welcome to the show."),
            TranscriptLine(start_ms=4200, text="Today we talk about transcripts."),
        ),
        language="en",
        provider="Spotify",
        is_auto_generated=True,
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

    def get_transcript(self, value: str) -> Transcript:
        if FakeClient.error is not None:
            raise FakeClient.error
        return _transcript()


@pytest.fixture(autouse=True)
def _patch_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_main, "SpotifyClient", FakeClient)
    monkeypatch.delenv("SPOTIFY_SP_DC", raising=False)
    FakeClient.last_kwargs = {}
    FakeClient.error = None


def test_transcript_with_cookies_option_emits_json(tmp_path: Path) -> None:
    cookies = tmp_path / "cookies.txt"
    cookies.write_text("placeholder", encoding="utf-8")
    result = runner.invoke(app, ["transcript", EP := "x", "--cookies", str(cookies)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["language"] == "en"
    assert payload["lines"][0]["text"] == "Welcome to the show."
    assert FakeClient.last_kwargs["cookies"] == cookies
    assert EP == "x"


def test_transcript_falls_back_to_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SPOTIFY_SP_DC", "env_sp_dc_value")
    result = runner.invoke(app, ["transcript", "x"])
    assert result.exit_code == 0, result.output
    assert FakeClient.last_kwargs["cookies"] == "env_sp_dc_value"


def test_transcript_without_cookies_or_env_fails() -> None:
    result = runner.invoke(app, ["transcript", "x"])
    assert result.exit_code != 0
    assert "SPOTIFY_SP_DC" in result.output or "cookies" in result.output


def test_transcript_pretty_indents(tmp_path: Path) -> None:
    cookies = tmp_path / "c.txt"
    cookies.write_text("x", encoding="utf-8")
    result = runner.invoke(app, ["transcript", "x", "--cookies", str(cookies), "--pretty"])
    assert result.exit_code == 0
    assert "\n  " in result.stdout


def test_transcript_auth_error_exits_4(tmp_path: Path) -> None:
    cookies = tmp_path / "c.txt"
    cookies.write_text("x", encoding="utf-8")
    FakeClient.error = AuthenticationError("bad cookie")
    result = runner.invoke(app, ["transcript", "x", "--cookies", str(cookies)])
    assert result.exit_code == 4
    assert "error:" in result.stderr


def test_transcript_not_found_exits_3(tmp_path: Path) -> None:
    cookies = tmp_path / "c.txt"
    cookies.write_text("x", encoding="utf-8")
    FakeClient.error = NotFoundError("no transcript")
    result = runner.invoke(app, ["transcript", "x", "--cookies", str(cookies)])
    assert result.exit_code == 3
