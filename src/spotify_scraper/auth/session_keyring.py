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
    default_session_path,
    load_session,
    save_session,
    session_info,
)
from spotify_scraper.auth.session import (
    clear_session as _clear_file_session,
)
from spotify_scraper.errors import SessionError

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


class _NeverMatches(Exception):
    """Sentinel exception type that never matches a real keyring failure.

    Returned by :func:`_no_keyring_error` when the installed ``keyring`` exposes
    no ``NoKeyringError``, so ``except _no_keyring_error(keyring)`` is a safe
    no-op rather than accidentally swallowing an unrelated error. Defined once at
    module level rather than per call.
    """


def _no_keyring_error(keyring: Any) -> type[BaseException]:
    """Return ``keyring.errors.NoKeyringError`` or a never-matching sentinel."""
    errors = getattr(keyring, "errors", None)
    candidate = getattr(errors, "NoKeyringError", None)
    if isinstance(candidate, type) and issubclass(candidate, BaseException):
        return candidate
    return _NeverMatches


def _meta_path(path: Path | None) -> Path:
    """Resolve the metadata path for log messages (never ``None``)."""
    return default_session_path() if path is None else path


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
        SessionError: If the keyring is present but rejects the write.
    """
    keyring = _import_keyring()
    try:
        keyring.set_password(_SERVICE, _USERNAME, sp_dc)
    except _no_keyring_error(keyring):
        _LOGGER.warning(
            "No OS keyring available; falling back to the file session store at %s.",
            _meta_path(path),
        )
        return save_session(sp_dc, sp_dc_expires_ms=sp_dc_expires_ms, path=path, now_ms=now_ms)
    except Exception as exc:
        # A real keyring backend error (locked keychain, D-Bus failure, …) is a
        # session failure, surfaced through the project's error hierarchy. The
        # cookie value is never included in the message.
        raise SessionError("The OS keyring rejected the session secret.") from exc
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
        SessionError: If the metadata file is missing, insecure, or malformed,
            or if no ``sp_dc`` secret can be recovered from either the keyring or
            the file (e.g. the keyring entry was deleted out from under us).
    """
    keyring = _import_keyring()
    meta = load_session(path=path)
    try:
        secret = keyring.get_password(_SERVICE, _USERNAME)
    except _no_keyring_error(keyring):
        _LOGGER.warning(
            "No OS keyring available; using the file session store at %s.",
            _meta_path(path),
        )
        secret = None
    except Exception as exc:
        raise SessionError("The OS keyring rejected the session-secret read.") from exc
    if secret:
        return Session(
            sp_dc=secret,
            saved_at_ms=meta.saved_at_ms,
            sp_dc_expires_ms=meta.sp_dc_expires_ms,
            version=meta.version,
        )
    # The no-keyring fallback path stores the real secret in the file, so a
    # non-empty file secret is still usable. An empty one means the secret is
    # gone (keyring deleted, or never written) — refuse rather than hand back an
    # empty-cookie Session that would fail on first use.
    if meta.sp_dc:
        return meta
    raise SessionError("No 'sp_dc' secret found in the OS keyring for this session; log in again.")


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
    non-secret metadata (existence, permissions, expiry) in the JSON file the
    file backend writes. It first runs the file-backed
    :func:`~spotify_scraper.auth.session.session_info` (existence / permission /
    parse / expiry, never raises); if that passes it then confirms the secret is
    actually retrievable, because a valid metadata file with a deleted keyring
    entry is NOT a usable session. To probe, the keyring is lazy-imported; when
    the extra is absent the probe is skipped and the metadata verdict stands.

    Args:
        path: Metadata file path; defaults to the file backend's default.
        now_ms: Injectable clock (Unix ms) for the expiry comparison.

    Returns:
        A cookie-free :class:`SessionInfo`.
    """
    info = session_info(path=path, now_ms=now_ms)
    if not info.valid:
        return info
    try:
        session = load_from_keyring(path=path)
    except ImportError:
        # Can't probe the secret without the extra; trust the metadata verdict.
        return info
    except SessionError as exc:
        return SessionInfo(
            exists=info.exists,
            valid=False,
            saved_at_ms=info.saved_at_ms,
            sp_dc_expires_ms=info.sp_dc_expires_ms,
            reason=str(exc),
        )
    except Exception:
        # This reporter must never raise; if probing the keyring fails in any
        # unexpected way (e.g. a broken backend at import time), fall back to the
        # cookie-free metadata verdict rather than propagating.
        return info
    if not session.sp_dc:
        return SessionInfo(
            exists=info.exists,
            valid=False,
            saved_at_ms=info.saved_at_ms,
            sp_dc_expires_ms=info.sp_dc_expires_ms,
            reason="No 'sp_dc' secret found in the OS keyring; log in again.",
        )
    return info
