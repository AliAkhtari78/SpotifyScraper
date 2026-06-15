"""Sans-io, stdlib-only persistent store for a captured ``sp_dc`` cookie.

A successful browser login yields a long-lived ``sp_dc`` cookie. Persisting it
lets a user authenticate once and then run headlessly. This module owns that
on-disk format: a single JSON file in a per-user config directory, written
atomically with owner-only (0600) permissions so the secret is never briefly
world-readable.

Everything here depends on the standard library only — no ``platformdirs``, no
third-party extra — so the store is importable and fully testable without any
optional dependency. The cookie value never reaches :func:`repr`, an exception
message, or a log record.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from spotify_scraper.errors import SessionError

_APP_DIR_NAME = "spotifyscraper"
_SESSION_FILENAME = "session.json"
_SCHEMA_VERSION = 1

#: Hints embedded in :class:`SessionError` messages. None of them ever carries
#: cookie content — a bare filesystem path is the most they reveal.
_MISSING_HINT = "No saved session found; run client.login() (or the 'login' CLI command) first."
_CORRUPT_HINT = "Saved session is unreadable or malformed; log in again to recreate it."
_INSECURE_HINT = (
    "Saved session file is group- or world-readable; refusing to load it. The cookie "
    "may already have leaked — delete the file and log in again."
)


@dataclass(frozen=True, slots=True)
class Session:
    """A persisted browser-login session: the durable ``sp_dc`` plus metadata.

    Only ``sp_dc`` is a secret; ``saved_at_ms`` / ``sp_dc_expires_ms`` /
    ``version`` are plain metadata. The cookie is deliberately excluded from
    :meth:`__repr__` so it cannot leak through logs or tracebacks.
    """

    sp_dc: str
    saved_at_ms: int
    sp_dc_expires_ms: int | None = None
    version: int = _SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dict carrying every field, including the secret.

        This is the on-disk envelope, so it intentionally includes ``sp_dc``
        (the file is the secret store). Never log or print the result.
        """
        return {
            "version": self.version,
            "sp_dc": self.sp_dc,
            "saved_at_ms": self.saved_at_ms,
            "sp_dc_expires_ms": self.sp_dc_expires_ms,
        }

    @classmethod
    def from_dict(cls, data: Any) -> Session:
        """Build a :class:`Session` from a parsed JSON envelope.

        Args:
            data: A mapping as produced by :meth:`to_dict`.

        Returns:
            The validated session.

        Raises:
            SessionError: If the shape is wrong or ``sp_dc`` is missing/empty.
        """
        if not isinstance(data, dict):
            raise SessionError(_CORRUPT_HINT)
        sp_dc = data.get("sp_dc")
        # The secret may be an empty string when the keyring backend keeps the
        # cookie in the OS keyring and only metadata on disk; it must still be a
        # present ``str`` (a missing key or wrong type is corrupt).
        if not isinstance(sp_dc, str):
            raise SessionError(_CORRUPT_HINT)
        saved_at_ms = data.get("saved_at_ms", 0)
        if isinstance(saved_at_ms, bool) or not isinstance(saved_at_ms, int):
            raise SessionError(_CORRUPT_HINT)
        expires = data.get("sp_dc_expires_ms")
        if expires is not None and (isinstance(expires, bool) or not isinstance(expires, int)):
            raise SessionError(_CORRUPT_HINT)
        version = data.get("version", _SCHEMA_VERSION)
        if isinstance(version, bool) or not isinstance(version, int):
            raise SessionError(_CORRUPT_HINT)
        return cls(
            sp_dc=sp_dc,
            saved_at_ms=saved_at_ms,
            sp_dc_expires_ms=expires,
            version=version,
        )

    def __repr__(self) -> str:
        """Return a credential-free representation (no ``sp_dc``)."""
        return (
            f"Session(saved_at_ms={self.saved_at_ms}, "
            f"sp_dc_expires_ms={self.sp_dc_expires_ms}, version={self.version})"
        )


@dataclass(frozen=True, slots=True)
class SessionInfo:
    """A cookie-free snapshot of a saved session, safe to print or log.

    Unlike :class:`Session`, this object never carries the ``sp_dc`` secret: it
    holds only a validity verdict plus non-secret metadata, so it is safe to
    surface to a CLI or a caller asking "is there a usable saved session, and how
    long is it good for?". ``reason`` carries the existing cookie-free hint when
    the session is absent, insecure, corrupt, or expired.

    Attributes:
        exists: Whether a saved session file is present at all.
        valid: Whether the session exists, is securely permissioned (POSIX),
            parses, and has not passed ``sp_dc_expires_ms`` when that is known.
        saved_at_ms: When the session was saved (Unix ms), if known.
        sp_dc_expires_ms: The cookie's expiry (Unix ms), if it was captured.
        reason: A cookie-free explanation when the session is unusable.
    """

    exists: bool
    valid: bool
    saved_at_ms: int | None = None
    sp_dc_expires_ms: int | None = None
    reason: str | None = None


_EXPIRED_HINT = "Saved session's cookie has expired; log in again to refresh it."


def _default_now_ms() -> int:
    return time.time_ns() // 1_000_000


def default_config_dir() -> Path:
    """Resolve the per-user config directory for SpotifyScraper.

    Precedence (all stdlib, no ``platformdirs``):

    1. ``SPOTIFYSCRAPER_CONFIG_DIR`` (used verbatim),
    2. ``XDG_CONFIG_HOME`` + ``/spotifyscraper``,
    3. the platform default: ``~/.config`` (Linux), ``~/Library/Application
       Support`` (macOS), ``%APPDATA%`` (Windows), each + ``/spotifyscraper``.

    Returns:
        The config directory path (not necessarily existing yet).
    """
    override = os.environ.get("SPOTIFYSCRAPER_CONFIG_DIR")
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / _APP_DIR_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / _APP_DIR_NAME
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        return base / _APP_DIR_NAME
    return Path.home() / ".config" / _APP_DIR_NAME


def default_session_path() -> Path:
    """Return the default session file path inside :func:`default_config_dir`."""
    return default_config_dir() / _SESSION_FILENAME


def _resolve_path(path: Path | None) -> Path:
    return default_session_path() if path is None else path


def save_session(
    sp_dc: str,
    *,
    sp_dc_expires_ms: int | None = None,
    path: Path | None = None,
    now_ms: int | None = None,
) -> Path:
    """Persist an ``sp_dc`` cookie to an owner-only JSON file, atomically.

    The parent directory is created ``mode=0o700``. The file is written via
    :func:`tempfile.mkstemp` (0600 from the first byte) and moved into place
    with :func:`os.replace`, so no window exists where the cookie is briefly
    group- or world-readable.

    Args:
        sp_dc: The bare ``sp_dc`` cookie value to store.
        sp_dc_expires_ms: Optional cookie expiry in Unix milliseconds.
        path: Destination file; defaults to :func:`default_session_path`.
        now_ms: Injectable clock (Unix ms) for ``saved_at_ms``.

    Returns:
        The path the session was written to.
    """
    target = _resolve_path(path)
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    session = Session(
        sp_dc=sp_dc,
        saved_at_ms=_default_now_ms() if now_ms is None else now_ms,
        sp_dc_expires_ms=sp_dc_expires_ms,
    )
    payload = json.dumps(session.to_dict(), ensure_ascii=False)
    fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=".session-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(tmp_name, target)
    except BaseException:
        # Best-effort cleanup of the temp file; never mask the original error.
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise
    return target


def load_session(*, path: Path | None = None) -> Session:
    """Load a previously saved :class:`Session`, refusing insecure files.

    On POSIX, a file with any group/world permission bits set is REFUSED (the
    secret may already have leaked); the library never silently relaxes or
    tightens permissions. On Windows the mode-bit check is skipped because
    POSIX mode bits are no-ops there and the per-user AppData ACL is the
    platform guarantee.

    Args:
        path: Source file; defaults to :func:`default_session_path`.

    Returns:
        The loaded session.

    Raises:
        SessionError: If the file is absent, insecurely permissioned (POSIX),
            unreadable, or not a valid session envelope.
    """
    source = _resolve_path(path)
    try:
        stat = source.stat()
    except FileNotFoundError as exc:
        raise SessionError(f"{_MISSING_HINT} (looked at {source})") from exc
    except OSError as exc:
        raise SessionError(f"{_CORRUPT_HINT} ({source})") from exc
    if os.name == "posix" and (stat.st_mode & 0o077):
        raise SessionError(f"{_INSECURE_HINT} ({source})")
    try:
        raw = source.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise SessionError(f"{_CORRUPT_HINT} ({source})") from exc
    return Session.from_dict(data)


def clear_session(*, path: Path | None = None) -> None:
    """Delete a saved session for local revocation; idempotent when absent.

    Args:
        path: Session file to remove; defaults to :func:`default_session_path`.
    """
    target = _resolve_path(path)
    try:
        target.unlink()
    except FileNotFoundError:
        return


def session_info(*, path: Path | None = None, now_ms: int | None = None) -> SessionInfo:
    """Report a saved session's status WITHOUT exposing the cookie.

    This never raises for the common missing / corrupt / insecure / expired
    cases: it catches the :class:`SessionError` that :func:`load_session` would
    raise and turns it into ``exists`` / ``valid`` flags plus the existing
    cookie-free hint as ``reason``. Validity is a purely local check — file
    exists, securely permissioned (POSIX), parseable, and not past
    ``sp_dc_expires_ms`` when that expiry is known — so it cannot detect a
    Spotify-side revocation.

    Args:
        path: Source file; defaults to :func:`default_session_path`.
        now_ms: Injectable clock (Unix ms) for the expiry comparison.

    Returns:
        A cookie-free :class:`SessionInfo`.
    """
    source = _resolve_path(path)
    exists = source.exists()
    try:
        session = load_session(path=path)
    except SessionError as exc:
        # The hint is cookie-free by construction (see _MISSING_HINT etc.); the
        # bare path is the most it reveals.
        return SessionInfo(exists=exists, valid=False, reason=str(exc))
    now = _default_now_ms() if now_ms is None else now_ms
    if session.sp_dc_expires_ms is not None and now >= session.sp_dc_expires_ms:
        return SessionInfo(
            exists=True,
            valid=False,
            saved_at_ms=session.saved_at_ms,
            sp_dc_expires_ms=session.sp_dc_expires_ms,
            reason=_EXPIRED_HINT,
        )
    return SessionInfo(
        exists=True,
        valid=True,
        saved_at_ms=session.saved_at_ms,
        sp_dc_expires_ms=session.sp_dc_expires_ms,
    )


def has_saved_session(*, path: Path | None = None, now_ms: int | None = None) -> bool:
    """Return ``True`` when a valid saved session exists (cookie-free check)."""
    return session_info(path=path, now_ms=now_ms).valid


class SessionStore:
    """Backend indirection selecting where the ``sp_dc`` secret is kept.

    The default ``"file"`` backend uses the module-level functions above. The
    ``"keyring"`` backend (see :mod:`spotify_scraper.auth.session_keyring`)
    stores only the secret in the OS keyring while keeping metadata in the JSON
    file. Backend choice is always EXPLICIT — never inferred from what happens
    to be pip-installed.
    """

    __slots__ = ("_backend",)

    def __init__(self, backend: str = "file") -> None:
        """Initialize the store.

        Args:
            backend: Either ``"file"`` (default) or ``"keyring"``.

        Raises:
            ValueError: If ``backend`` is not a recognized name.
        """
        if backend not in ("file", "keyring"):
            raise ValueError(f"Unknown session store backend: {backend!r}")
        self._backend = backend

    def save(
        self,
        sp_dc: str,
        *,
        sp_dc_expires_ms: int | None = None,
        path: Path | None = None,
        now_ms: int | None = None,
    ) -> Path:
        """Persist ``sp_dc`` via the selected backend; return the metadata path."""
        if self._backend == "keyring":
            from spotify_scraper.auth import session_keyring

            return session_keyring.save_to_keyring(
                sp_dc, sp_dc_expires_ms=sp_dc_expires_ms, path=path, now_ms=now_ms
            )
        return save_session(sp_dc, sp_dc_expires_ms=sp_dc_expires_ms, path=path, now_ms=now_ms)

    def load(self, *, path: Path | None = None) -> Session:
        """Load a session via the selected backend."""
        if self._backend == "keyring":
            from spotify_scraper.auth import session_keyring

            return session_keyring.load_from_keyring(path=path)
        return load_session(path=path)

    def clear(self, *, path: Path | None = None) -> None:
        """Clear a session via the selected backend (idempotent)."""
        if self._backend == "keyring":
            from spotify_scraper.auth import session_keyring

            session_keyring.clear_keyring(path=path)
            return
        clear_session(path=path)

    def info(self, *, path: Path | None = None, now_ms: int | None = None) -> SessionInfo:
        """Report the saved session's status via the selected backend.

        The result is cookie-free and never raises for missing / corrupt /
        insecure / expired sessions.
        """
        if self._backend == "keyring":
            from spotify_scraper.auth import session_keyring

            return session_keyring.keyring_info(path=path, now_ms=now_ms)
        return session_info(path=path, now_ms=now_ms)

    def has_session(self, *, path: Path | None = None, now_ms: int | None = None) -> bool:
        """Return ``True`` when a valid saved session exists for this backend."""
        return self.info(path=path, now_ms=now_ms).valid

    def __repr__(self) -> str:
        """Return a credential-free representation."""
        return f"SessionStore(backend={self._backend!r})"
