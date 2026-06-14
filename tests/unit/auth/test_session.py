"""Hermetic tests for the stdlib-only persistent session store."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from spotify_scraper.auth.session import (
    Session,
    SessionStore,
    clear_session,
    default_config_dir,
    default_session_path,
    load_session,
    save_session,
)
from spotify_scraper.errors import SessionError

SECRET = "sp_dc_super_secret_cookie_value"  # noqa: S105

_POSIX_ONLY = pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits only")


# --- round-trip ---------------------------------------------------------------


def test_save_then_load_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    saved = save_session(SECRET, sp_dc_expires_ms=999, path=path, now_ms=1000)
    assert saved == path
    session = load_session(path=path)
    assert session.sp_dc == SECRET
    assert session.saved_at_ms == 1000
    assert session.sp_dc_expires_ms == 999
    assert session.version == 1


def test_save_creates_parent_directory(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "deeper" / "session.json"
    save_session(SECRET, path=path)
    assert path.exists()


# --- permissions --------------------------------------------------------------


@_POSIX_ONLY
def test_saved_file_is_owner_only(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, path=path)
    mode = stat.S_IMODE(path.stat().st_mode)
    assert mode == 0o600


@_POSIX_ONLY
def test_load_refuses_group_or_world_readable(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, path=path)
    path.chmod(0o644)
    with pytest.raises(SessionError) as excinfo:
        load_session(path=path)
    # Refused, not repaired: the loose bits are still set.
    assert stat.S_IMODE(path.stat().st_mode) == 0o644
    assert SECRET not in str(excinfo.value)


# --- refuse-on-load -----------------------------------------------------------


def test_load_missing_raises_session_error(tmp_path: Path) -> None:
    with pytest.raises(SessionError) as excinfo:
        load_session(path=tmp_path / "nope.json")
    assert "login" in str(excinfo.value).lower()
    assert SECRET not in str(excinfo.value)


def test_load_malformed_json_raises_session_error(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    path.write_text("{not json", encoding="utf-8")
    if os.name == "posix":
        path.chmod(0o600)
    with pytest.raises(SessionError):
        load_session(path=path)


def test_load_missing_sp_dc_raises_session_error(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    path.write_text(json.dumps({"saved_at_ms": 1, "version": 1}), encoding="utf-8")
    if os.name == "posix":
        path.chmod(0o600)
    with pytest.raises(SessionError):
        load_session(path=path)


def test_from_dict_rejects_non_mapping() -> None:
    with pytest.raises(SessionError):
        Session.from_dict(["not", "a", "dict"])


def test_from_dict_rejects_wrong_types() -> None:
    with pytest.raises(SessionError):
        Session.from_dict({"sp_dc": SECRET, "saved_at_ms": "nope"})
    with pytest.raises(SessionError):
        Session.from_dict({"sp_dc": SECRET, "saved_at_ms": 1, "sp_dc_expires_ms": "x"})
    with pytest.raises(SessionError):
        Session.from_dict({"sp_dc": SECRET, "saved_at_ms": 1, "version": "x"})


# --- secret hygiene -----------------------------------------------------------


def test_repr_excludes_cookie() -> None:
    session = Session(sp_dc=SECRET, saved_at_ms=1, sp_dc_expires_ms=2)
    rendered = repr(session)
    assert SECRET not in rendered
    assert "saved_at_ms=1" in rendered
    assert "sp_dc_expires_ms=2" in rendered


def test_to_dict_is_the_secret_envelope() -> None:
    # to_dict is the on-disk envelope, so it intentionally carries the secret.
    data = Session(sp_dc=SECRET, saved_at_ms=1).to_dict()
    assert data["sp_dc"] == SECRET
    assert set(data) == {"version", "sp_dc", "saved_at_ms", "sp_dc_expires_ms"}


def test_every_error_message_excludes_cookie(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    # missing
    with pytest.raises(SessionError) as missing:
        load_session(path=path)
    # corrupt
    path.write_text("garbage", encoding="utf-8")
    if os.name == "posix":
        path.chmod(0o600)
    with pytest.raises(SessionError) as corrupt:
        load_session(path=path)
    for exc in (missing, corrupt):
        assert SECRET not in str(exc.value)


# --- revocation ---------------------------------------------------------------


def test_clear_session_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    save_session(SECRET, path=path)
    assert path.exists()
    clear_session(path=path)
    assert not path.exists()
    # Second call must not raise.
    clear_session(path=path)


# --- config dir resolution ----------------------------------------------------


def test_config_dir_honors_spotifyscraper_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SPOTIFYSCRAPER_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    assert default_config_dir() == tmp_path / "cfg"
    assert default_session_path() == tmp_path / "cfg" / "session.json"


def test_config_dir_falls_back_to_xdg(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("SPOTIFYSCRAPER_CONFIG_DIR", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    assert default_config_dir() == tmp_path / "xdg" / "spotifyscraper"


def test_config_dir_platform_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("SPOTIFYSCRAPER_CONFIG_DIR", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr("spotify_scraper.auth.session.sys.platform", "linux")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    assert default_config_dir() == tmp_path / ".config" / "spotifyscraper"


def test_config_dir_macos_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("SPOTIFYSCRAPER_CONFIG_DIR", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr("spotify_scraper.auth.session.sys.platform", "darwin")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    assert default_config_dir() == tmp_path / "Library" / "Application Support" / "spotifyscraper"


def test_config_dir_windows_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("SPOTIFYSCRAPER_CONFIG_DIR", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr("spotify_scraper.auth.session.sys.platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path / "AppData" / "Roaming"))
    assert default_config_dir() == tmp_path / "AppData" / "Roaming" / "spotifyscraper"


# --- SessionStore indirection -------------------------------------------------


def test_session_store_file_backend_round_trips(tmp_path: Path) -> None:
    store = SessionStore("file")
    path = tmp_path / "session.json"
    store.save(SECRET, path=path)
    assert store.load(path=path).sp_dc == SECRET
    store.clear(path=path)
    assert not path.exists()


def test_session_store_rejects_unknown_backend() -> None:
    with pytest.raises(ValueError, match="backend"):
        SessionStore("nope")


def test_session_store_repr_is_credential_free() -> None:
    assert repr(SessionStore("file")) == "SessionStore(backend='file')"
