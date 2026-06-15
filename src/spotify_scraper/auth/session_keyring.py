"""Optional OS-keyring backend for the ``sp_dc`` session secret.

This backend stores ONLY the ``sp_dc`` cookie in the operating-system keyring
(macOS Keychain, Windows Credential Locker, Linux Secret Service). Non-secret
metadata (``saved_at_ms``, expiry, schema version) stays in the same 0600 JSON
file the file backend writes, so the keyring entry stays well under the Windows
Credential Locker's ~1280-character limit.

The backend is selected EXPLICITLY (``store="keyring"``) — never inferred from
what is pip-installed — and lazy-imports :mod:`keyring` so importing this module
never requires the extra. On a host with no usable keyring (e.g. headless Linux
without Secret Service) it falls back to the file backend with a warning rather
than crashing. The cookie value is never logged.
"""

from __future__ import annotations

import contextlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from spotify_scraper.auth.session import (
    Session,
    SessionInfo,
    load_session,
    save_session,
    session_info,
)
from spotify_scraper.auth.session import (
    clear_session as _clear_file_session,
)

if TYPE_CHECKING:
    from types import ModuleType

_LOGGER = logging.getLogger("spotify_scraper")

_SERVICE = "spotifyscraper"
_USERNAME = "sp_dc"

_IMPORT_HINT = (
    "The keyring backend requires the 'keyring' extra: pip install spotifyscraper[keyring]"
)


def _import_keyring() -> ModuleType:
    try:
        import keyring
    except ImportError as exc:  # pragma: no cover - exercised via monkeypatched import
        raise ImportError(_IMPORT_HINT) from exc
    return keyring


def _no_keyring_error(keyring: Any) -> type[BaseException]:
    """Return ``keyring.errors.NoKeyringError`` or a never-matching sentinel."""
    errors = getattr(keyring, "errors", None)
    candidate = getattr(errors, "NoKeyringError", None)
    if isinstance(candidate, type) and issubclass(candidate, BaseException):
        return candidate

    class _Never(Exception):
        """Sentinel that never matches when keyring exposes no NoKeyringError."""

    return _Never


def save_to_keyring(
    sp_dc: str,
    *,
    sp_dc_expires_ms: int | None = None,
    path: Path | None = None,
    now_ms: int | None = None,
) -> Path:
    """Store ``sp_dc`` in the OS keyring and the metadata in the JSON file.

    The JSON file is written with an empty ``sp_dc`` so the secret lives only in
    the keyring. If no keyring is available, this falls back to the file backend
    (which stores the secret in the 0600 file) and logs a warning.

    Args:
        sp_dc: The bare ``sp_dc`` cookie value.
        sp_dc_expires_ms: Optional cookie expiry in Unix milliseconds.
        path: Metadata file path; defaults to the file backend's default.
        now_ms: Injectable clock (Unix ms) for ``saved_at_ms``.

    Returns:
        The metadata file path.

    Raises:
        ImportError: If the ``keyring`` extra is not installed.
    """
    keyring = _import_keyring()
    try:
        keyring.set_password(_SERVICE, _USERNAME, sp_dc)
    except _no_keyring_error(keyring):
        _LOGGER.warning(
            "No OS keyring available; falling back to the file session store at %s.",
            path,
        )
        return save_session(sp_dc, sp_dc_expires_ms=sp_dc_expires_ms, path=path, now_ms=now_ms)
    return save_session("", sp_dc_expires_ms=sp_dc_expires_ms, path=path, now_ms=now_ms)


def load_from_keyring(*, path: Path | None = None) -> Session:
    """Load a session, taking ``sp_dc`` from the keyring and metadata from file.

    When no keyring is available, this falls back to the file backend.

    Args:
        path: Metadata file path; defaults to the file backend's default.

    Returns:
        The loaded :class:`Session` with the secret merged in.

    Raises:
        ImportError: If the ``keyring`` extra is not installed.
        SessionError: If the metadata file is missing, insecure, or malformed.
    """
    keyring = _import_keyring()
    meta = load_session(path=path)
    try:
        secret = keyring.get_password(_SERVICE, _USERNAME)
    except _no_keyring_error(keyring):
        _LOGGER.warning(
            "No OS keyring available; using the file session store at %s.",
            path,
        )
        return meta
    if secret:
        return Session(
            sp_dc=secret,
            saved_at_ms=meta.saved_at_ms,
            sp_dc_expires_ms=meta.sp_dc_expires_ms,
            version=meta.version,
        )
    return meta


def clear_keyring(*, path: Path | None = None) -> None:
    """Delete the keyring secret and the metadata file; idempotent.

    Args:
        path: Metadata file path; defaults to the file backend's default.

    Raises:
        ImportError: If the ``keyring`` extra is not installed.
    """
    keyring = _import_keyring()
    # Deleting an absent secret (or with no keyring available) must stay
    # idempotent, so any backend error here is swallowed deliberately.
    with contextlib.suppress(Exception):
        keyring.delete_password(_SERVICE, _USERNAME)
    _clear_file_session(path=path)


def keyring_info(*, path: Path | None = None, now_ms: int | None = None) -> SessionInfo:
    """Report the keyring-backed session's status WITHOUT exposing the cookie.

    The keyring backend keeps only the secret in the OS keyring and all
    non-secret metadata (existence, permissions, expiry) in the same JSON file
    the file backend writes, so validity is governed entirely by that metadata
    file. This therefore delegates to the file-backed
    :func:`~spotify_scraper.auth.session.session_info`, which already performs
    the local existence / permission / parse / expiry checks and never raises.
    The keyring is not imported here, so introspection needs no extra.

    Args:
        path: Metadata file path; defaults to the file backend's default.
        now_ms: Injectable clock (Unix ms) for the expiry comparison.

    Returns:
        A cookie-free :class:`SessionInfo`.
    """
    return session_info(path=path, now_ms=now_ms)
