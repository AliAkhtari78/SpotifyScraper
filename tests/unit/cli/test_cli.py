"""Unit tests for the SpotifyScraper CLI.

The client is replaced with a fake whose ``get_*`` methods return small, real
model instances, so each command is exercised end-to-end through Typer's
:class:`CliRunner` without any network access.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar

import pytest
from typer.testing import CliRunner

import spotify_scraper
from spotify_scraper import (
    Album,
    Artist,
    AuthenticationError,
    Episode,
    NotFoundError,
    Playlist,
    Show,
    SpotifyScraperError,
    Track,
)
from spotify_scraper.cli import download as cli_download
from spotify_scraper.cli import main as cli_main
from spotify_scraper.cli.main import app

runner = CliRunner()


def _track() -> Track:
    return Track(
        id="4uLU6hMCjMI75M1A2tKUQC",
        uri="spotify:track:4uLU6hMCjMI75M1A2tKUQC",
        name="Never Gonna Give You Up",
        duration_ms=213000,
        explicit=False,
        playable=True,
        preview_url="https://preview.example/clip.mp3",
        artists=(),
        images=(),
        release_date=None,
    )


def _album() -> Album:
    return Album(
        id="album123",
        uri="spotify:album:album123",
        name="Whenever You Need Somebody",
        album_type="album",
        images=(),
        release_date=None,
        artists=(),
    )


def _artist() -> Artist:
    return Artist(
        id="artist123",
        uri="spotify:artist:artist123",
        name="Rick Astley",
        images=(),
    )


def _playlist(track_count: int = 3) -> Playlist:
    return Playlist(
        id="playlist123",
        uri="spotify:playlist:playlist123",
        name="My Playlist",
        total_tracks=track_count,
    )


def _episode() -> Episode:
    return Episode(
        id="episode123",
        uri="spotify:episode:episode123",
        name="Episode One",
        duration_ms=600000,
    )


def _show(episode_count: int = 2) -> Show:
    return Show(
        id="show123",
        uri="spotify:show:show123",
        name="My Show",
        total_episodes=episode_count,
    )


class FakeClient:
    """A drop-in for :class:`SpotifyClient` recording the kwargs it received."""

    last_kwargs: ClassVar[dict[str, Any]] = {}

    def __init__(self, **kwargs: Any) -> None:
        FakeClient.last_kwargs = kwargs

    def __enter__(self) -> FakeClient:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def get_track(self, value: str) -> Track:
        return _track()

    def get_album(self, value: str) -> Album:
        return _album()

    def get_artist(self, value: str) -> Artist:
        return _artist()

    def get_playlist(self, value: str, *, max_tracks: int | None = 100) -> Playlist:
        FakeClient.last_kwargs["max_tracks"] = max_tracks
        return _playlist()

    def get_episode(self, value: str) -> Episode:
        return _episode()

    def get_show(self, value: str, *, max_episodes: int | None = 50) -> Show:
        FakeClient.last_kwargs["max_episodes"] = max_episodes
        return _show()

    def download_cover(self, entity: Any, dest: Any = ".", **kwargs: Any) -> Path:
        FakeClient.last_kwargs.update(kwargs)
        return Path(dest) / "cover.jpg"

    def download_preview(self, entity: Any, dest: Any = ".", **kwargs: Any) -> Path:
        FakeClient.last_kwargs.update(kwargs)
        return Path(dest) / "preview.mp3"


@pytest.fixture(autouse=True)
def _patch_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_main, "SpotifyClient", FakeClient)
    monkeypatch.setattr(cli_download, "SpotifyClient", FakeClient)
    FakeClient.last_kwargs = {}


# --- Entity commands emit JSON -------------------------------------------------


@pytest.mark.parametrize(
    ("command", "expected_name", "expected_id"),
    [
        ("track", "Never Gonna Give You Up", "4uLU6hMCjMI75M1A2tKUQC"),
        ("album", "Whenever You Need Somebody", "album123"),
        ("artist", "Rick Astley", "artist123"),
        ("playlist", "My Playlist", "playlist123"),
        ("episode", "Episode One", "episode123"),
        ("show", "My Show", "show123"),
    ],
)
def test_entity_command_emits_json(command: str, expected_name: str, expected_id: str) -> None:
    result = runner.invoke(app, [command, "some-id"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["name"] == expected_name
    assert payload["id"] == expected_id


def test_pretty_indents_output() -> None:
    plain = runner.invoke(app, ["track", "x"])
    pretty = runner.invoke(app, ["track", "x", "--pretty"])
    assert plain.exit_code == 0
    assert pretty.exit_code == 0
    assert "\n  " in pretty.stdout
    assert "\n  " not in plain.stdout
    # Both decode to the same object.
    assert json.loads(plain.stdout) == json.loads(pretty.stdout)


def test_output_writes_file(tmp_path: Path) -> None:
    dest = tmp_path / "track.json"
    result = runner.invoke(app, ["track", "x", "-o", str(dest)])
    assert result.exit_code == 0
    assert result.stdout.strip() == ""
    payload = json.loads(dest.read_text())
    assert payload["id"] == "4uLU6hMCjMI75M1A2tKUQC"


# --- Pagination plumbing -------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [("50", 50), ("all", None), ("0", None)],
)
def test_playlist_max_tracks_plumbing(value: str, expected: int | None) -> None:
    result = runner.invoke(app, ["playlist", "x", "--max-tracks", value])
    assert result.exit_code == 0, result.output
    assert FakeClient.last_kwargs["max_tracks"] == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("25", 25), ("all", None), ("0", None)],
)
def test_show_max_episodes_plumbing(value: str, expected: int | None) -> None:
    result = runner.invoke(app, ["show", "x", "--max-episodes", value])
    assert result.exit_code == 0, result.output
    assert FakeClient.last_kwargs["max_episodes"] == expected


def test_playlist_default_max_tracks() -> None:
    result = runner.invoke(app, ["playlist", "x"])
    assert result.exit_code == 0
    assert FakeClient.last_kwargs["max_tracks"] == 100


def test_invalid_max_tracks_rejected() -> None:
    result = runner.invoke(app, ["playlist", "x", "--max-tracks", "lots"])
    assert result.exit_code != 0


# --- Error mapping -------------------------------------------------------------


@pytest.mark.parametrize(
    ("exc", "code"),
    [
        (NotFoundError("missing"), 3),
        (AuthenticationError("denied"), 4),
        (SpotifyScraperError("boom"), 1),
    ],
)
def test_error_mapping(monkeypatch: pytest.MonkeyPatch, exc: Exception, code: int) -> None:
    def boom(self: Any, value: str) -> Track:
        raise exc

    monkeypatch.setattr(FakeClient, "get_track", boom)
    result = runner.invoke(app, ["track", "x"])
    assert result.exit_code == code
    assert "error:" in result.stderr
    assert result.stdout == ""


def test_error_has_no_traceback(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(self: Any, value: str) -> Track:
        raise NotFoundError("nope")

    monkeypatch.setattr(FakeClient, "get_track", boom)
    result = runner.invoke(app, ["track", "x"])
    assert "Traceback" not in result.output
    assert result.stderr.strip() == "error: nope"


# --- Discoverability -----------------------------------------------------------


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == spotify_scraper.__version__


def test_help_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("track", "album", "artist", "playlist", "show", "episode", "download"):
        assert command in result.stdout


# --- Download commands ---------------------------------------------------------


def test_download_preview_prints_path(tmp_path: Path) -> None:
    result = runner.invoke(app, ["download", "preview", "x", "-o", str(tmp_path)])
    assert result.exit_code == 0, result.output
    printed = Path(result.stdout.strip())
    assert printed == tmp_path / "preview.mp3"
    assert FakeClient.last_kwargs["embed_cover"] is False


def test_download_preview_embed_cover(tmp_path: Path) -> None:
    result = runner.invoke(app, ["download", "preview", "x", "-o", str(tmp_path), "--embed-cover"])
    assert result.exit_code == 0
    assert FakeClient.last_kwargs["embed_cover"] is True


def test_download_cover_prints_path(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["download", "cover", "x", "-o", str(tmp_path), "--size", "smallest"]
    )
    assert result.exit_code == 0, result.output
    printed = Path(result.stdout.strip())
    assert printed == tmp_path / "cover.jpg"
    assert FakeClient.last_kwargs["size"] == "smallest"


def test_download_error_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(self: Any, value: str) -> Track:
        raise NotFoundError("gone")

    monkeypatch.setattr(FakeClient, "get_track", boom)
    result = runner.invoke(app, ["download", "preview", "x"])
    assert result.exit_code == 3
    assert "error: gone" in result.stderr


# --- Client tuning options -----------------------------------------------------


def test_client_tuning_options_plumbed() -> None:
    result = runner.invoke(
        app,
        ["track", "x", "--proxy", "http://p:8080", "--timeout", "5", "--rate-limit", "3"],
    )
    assert result.exit_code == 0
    assert FakeClient.last_kwargs["proxy"] == "http://p:8080"
    assert FakeClient.last_kwargs["timeout"] == 5.0
    assert FakeClient.last_kwargs["rate_limit"] == spotify_scraper.RateLimit(per_second=3.0)


def test_default_rate_limit_is_none() -> None:
    result = runner.invoke(app, ["track", "x"])
    assert result.exit_code == 0
    assert FakeClient.last_kwargs["rate_limit"] is None
