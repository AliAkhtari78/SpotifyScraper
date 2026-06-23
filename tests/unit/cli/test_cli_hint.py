"""Tests for the one-time, opt-out interactive star hint."""

from __future__ import annotations

import io
import sys

import pytest

from spotify_scraper.cli._hint import maybe_star_hint


class _TtyStringIO(io.StringIO):
    """A StringIO that reports itself as a terminal."""

    def isatty(self) -> bool:
        return True


@pytest.fixture
def cache_dir(tmp_path, monkeypatch):
    """Point the hint's marker at a temp cache dir; clear influencing env."""
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.delenv("SPOTIFYSCRAPER_NO_HINT", raising=False)
    return tmp_path


def test_hint_shows_once_when_interactive(cache_dir, monkeypatch):
    err = _TtyStringIO()
    monkeypatch.setattr(sys, "stderr", err)

    maybe_star_hint()
    shown = err.getvalue()
    assert "github.com/AliAkhtari78/SpotifyScraper" in shown
    assert "SPOTIFYSCRAPER_NO_HINT" in shown

    # A second invocation is silent — the marker now exists.
    err2 = _TtyStringIO()
    monkeypatch.setattr(sys, "stderr", err2)
    maybe_star_hint()
    assert err2.getvalue() == ""


def test_hint_silent_when_not_a_tty(cache_dir, monkeypatch):
    err = io.StringIO()  # plain StringIO.isatty() -> False
    monkeypatch.setattr(sys, "stderr", err)
    maybe_star_hint()
    assert err.getvalue() == ""


def test_hint_silent_when_opted_out(cache_dir, monkeypatch):
    monkeypatch.setenv("SPOTIFYSCRAPER_NO_HINT", "1")
    err = _TtyStringIO()
    monkeypatch.setattr(sys, "stderr", err)
    maybe_star_hint()
    assert err.getvalue() == ""


def test_hint_never_raises_on_unwritable_cache(tmp_path, monkeypatch):
    # Point the cache at a path that cannot be created (a file, not a dir).
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    monkeypatch.setenv("XDG_CACHE_HOME", str(blocker))
    monkeypatch.delenv("SPOTIFYSCRAPER_NO_HINT", raising=False)
    err = _TtyStringIO()
    monkeypatch.setattr(sys, "stderr", err)
    maybe_star_hint()  # must not raise
    assert err.getvalue() == ""
