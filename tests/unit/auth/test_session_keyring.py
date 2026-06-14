"""Hermetic tests for the optional keyring session backend.

A fake ``keyring`` module is injected via ``sys.modules`` so the OS keyring is
never touched. These prove only ``sp_dc`` reaches the keyring, the metadata
lands in the JSON file, the helpful ImportError fires when the extra is absent,
and ``NoKeyringError`` falls back to the file backend.
"""

from __future__ import annotations

import builtins
import json
import os
import sys
import types
from pathlib import Path
from typing import Any

import pytest

from spotify_scraper.auth import session_keyring
from spotify_scraper.auth.session import SessionStore
from spotify_scraper.errors import SessionError

SECRET = "sp_dc_keyring_secret"  # noqa: S105


class _FakeKeyringErrors:
    class NoKeyringError(Exception):
        """Mimics keyring.errors.NoKeyringError."""


def _make_fake_keyring(*, raise_no_keyring: bool = False) -> types.ModuleType:
    module = types.ModuleType("keyring")
    store: dict[tuple[str, str], str] = {}
    module.errors = _FakeKeyringErrors  # type: ignore[attr-defined]
    module._store = store  # type: ignore[attr-defined]

    def set_password(service: str, username: str, password: str) -> None:
        if raise_no_keyring:
            raise _FakeKeyringErrors.NoKeyringError
        store[(service, username)] = password

    def get_password(service: str, username: str) -> str | None:
        if raise_no_keyring:
            raise _FakeKeyringErrors.NoKeyringError
        return store.get((service, username))

    def delete_password(service: str, username: str) -> None:
        store.pop((service, username), None)

    module.set_password = set_password  # type: ignore[attr-defined]
    module.get_password = get_password  # type: ignore[attr-defined]
    module.delete_password = delete_password  # type: ignore[attr-defined]
    return module


@pytest.fixture
def fake_keyring(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    module = _make_fake_keyring()
    monkeypatch.setitem(sys.modules, "keyring", module)
    return module


def _secured(path: Path) -> Path:
    if os.name == "posix" and path.exists():
        path.chmod(0o600)
    return path


# --- only the secret goes to the keyring --------------------------------------


def test_only_sp_dc_in_keyring_metadata_in_file(
    fake_keyring: types.ModuleType, tmp_path: Path
) -> None:
    path = tmp_path / "session.json"
    session_keyring.save_to_keyring(SECRET, sp_dc_expires_ms=42, path=path, now_ms=7)

    # Secret in the keyring.
    assert fake_keyring._store[("spotifyscraper", "sp_dc")] == SECRET  # type: ignore[attr-defined]

    # Metadata in the file, but NOT the secret.
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk["sp_dc"] == ""
    assert on_disk["saved_at_ms"] == 7
    assert on_disk["sp_dc_expires_ms"] == 42
    assert SECRET not in path.read_text(encoding="utf-8")


def test_load_from_keyring_merges_secret(fake_keyring: types.ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    session_keyring.save_to_keyring(SECRET, path=path, now_ms=11)
    session = session_keyring.load_from_keyring(path=path)
    assert session.sp_dc == SECRET
    assert session.saved_at_ms == 11


def test_clear_keyring_removes_secret_and_file(
    fake_keyring: types.ModuleType, tmp_path: Path
) -> None:
    path = tmp_path / "session.json"
    session_keyring.save_to_keyring(SECRET, path=path)
    session_keyring.clear_keyring(path=path)
    assert ("spotifyscraper", "sp_dc") not in fake_keyring._store  # type: ignore[attr-defined]
    assert not path.exists()
    # Idempotent.
    session_keyring.clear_keyring(path=path)


def test_load_from_keyring_missing_metadata_raises(
    fake_keyring: types.ModuleType, tmp_path: Path
) -> None:
    with pytest.raises(SessionError):
        session_keyring.load_from_keyring(path=tmp_path / "absent.json")


# --- missing extra ------------------------------------------------------------


def test_missing_keyring_extra_raises_helpful_import_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delitem(sys.modules, "keyring", raising=False)
    real_import = builtins.__import__

    def _block(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "keyring" or name.startswith("keyring."):
            raise ImportError("No module named 'keyring'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _block)

    with pytest.raises(ImportError) as excinfo:
        session_keyring.save_to_keyring(SECRET, path=tmp_path / "s.json")
    assert "spotifyscraper[keyring]" in str(excinfo.value)


# --- NoKeyringError falls back to the file backend ----------------------------


def test_no_keyring_available_falls_back_to_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    module = _make_fake_keyring(raise_no_keyring=True)
    monkeypatch.setitem(sys.modules, "keyring", module)
    path = tmp_path / "session.json"

    with caplog.at_level("WARNING"):
        saved = session_keyring.save_to_keyring(SECRET, path=path, now_ms=3)

    # The file backend stored the secret because no keyring was available.
    assert saved == path
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk["sp_dc"] == SECRET
    assert any("file session store" in r.message for r in caplog.records)
    # The cookie value never appears in the log.
    assert all(SECRET not in r.getMessage() for r in caplog.records)

    _secured(path)
    session = session_keyring.load_from_keyring(path=path)
    assert session.sp_dc == SECRET


# --- SessionStore keyring dispatch --------------------------------------------


def test_session_store_keyring_backend_round_trips(
    fake_keyring: types.ModuleType, tmp_path: Path
) -> None:
    store = SessionStore("keyring")
    path = tmp_path / "session.json"
    store.save(SECRET, path=path)
    assert fake_keyring._store[("spotifyscraper", "sp_dc")] == SECRET  # type: ignore[attr-defined]
    assert store.load(path=path).sp_dc == SECRET
    store.clear(path=path)
    assert ("spotifyscraper", "sp_dc") not in fake_keyring._store  # type: ignore[attr-defined]
    assert not path.exists()
