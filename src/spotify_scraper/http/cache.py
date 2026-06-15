"""Opt-in, off-by-default persistent HTTP response cache at the transport seam.

The cache is a thin wrapper transport that structurally satisfies the existing
:class:`~spotify_scraper.http.transport.Transport` /
:class:`~spotify_scraper.http.transport.AsyncTransport` protocols, so it is a
drop-in for the ``transport=`` constructor override and composes with rate
limiting, retries, and locale handling without re-implementing any of them.

Only safe GETs to the token-free pathfinder host
(``api-partner.spotify.com/pathfinder/*``) are cacheable by default. The embed
pages (``open.spotify.com/embed/*``) are deliberately NOT cached: their
``__NEXT_DATA__`` carries the short-lived anonymous access token, so caching
them would both persist a credential to disk and re-serve an expired token once
it rotated (breaking tier-1 extraction for the whole TTL). The token endpoints
(``open.spotify.com/api/*``) and the cookie-authenticated lyrics/transcript host
(``spclient.wg.spotify.com``) are likewise never cached. Only ``status_code ==
200`` responses are stored; inner-transport errors propagate uncaught and are
never cached.

The default :class:`FileCache` is stdlib-only (no new runtime dependency) and
plugs in behind the :class:`DiskCache` protocol, so callers can substitute any
backend (an in-memory dict for tests, Redis in their own code).
"""

from __future__ import annotations

import base64
import binascii
import contextlib
import hashlib
import json
import logging
import os
import tempfile
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast, runtime_checkable

import httpx

from spotify_scraper.http.transport import AsyncTransport, Response, Transport

_LOGGER = logging.getLogger("spotify_scraper")

# Only the token-free pathfinder host is cached by default. Embed pages on
# open.spotify.com carry the anonymous access token in their __NEXT_DATA__, so
# caching them would persist a credential and re-serve a stale token once it
# rotates; they are excluded deliberately. Do NOT add token-bearing hosts here.
_DEFAULT_CACHEABLE_HOSTS: frozenset[str] = frozenset({"api-partner.spotify.com"})
_DEFAULT_DENIED_PATH_PREFIXES: frozenset[str] = frozenset({"/api/"})
_DEFAULT_TTL_SECONDS = 86_400.0


@dataclass(frozen=True, slots=True)
class CachedResponse:
    """A frozen response value object reconstructed from a cache entry.

    A live ``httpx.Response`` holds a closed stream and cannot be re-served from
    disk, so a cache hit is reconstructed as this value object, which satisfies
    the :class:`~spotify_scraper.http.transport.Response` protocol.
    """

    status_code: int
    content: bytes
    headers: Mapping[str, str]

    @property
    def text(self) -> str:
        """Decoded response body."""
        return self.content.decode("utf-8", errors="replace")

    def json(self) -> Any:
        """Parse the body as JSON.

        Raises:
            ValueError: If the body is not valid JSON, matching the clients'
                ``_safe_json`` contract.
        """
        return json.loads(self.content)


@dataclass(frozen=True, slots=True)
class CacheEntry:
    """The stored unit: a successful response plus its write timestamp."""

    status_code: int
    content: bytes
    headers: Mapping[str, str]
    stored_at: float


@dataclass(frozen=True, slots=True)
class CacheConfig:
    """Configuration for the caching transport wrappers.

    Attributes:
        store: The pluggable :class:`DiskCache` backend.
        ttl_seconds: Entry lifetime; an entry older than this is a miss.
        cacheable_hosts: Hosts whose GETs may be cached. Defaults to the
            token-free pathfinder host only; never add a token-bearing host
            (e.g. ``open.spotify.com``, whose embed pages carry the anonymous
            access token), or the cache will persist and re-serve a credential.
        denied_path_prefixes: Path prefixes that are never cached even on an
            otherwise-cacheable host (e.g. ``/api/`` token endpoints).
    """

    store: DiskCache
    ttl_seconds: float = _DEFAULT_TTL_SECONDS
    cacheable_hosts: frozenset[str] = _DEFAULT_CACHEABLE_HOSTS
    denied_path_prefixes: frozenset[str] = _DEFAULT_DENIED_PATH_PREFIXES


@runtime_checkable
class DiskCache(Protocol):
    """A pluggable key/value store for cache entries.

    Implementations may be backed by anything (a stdlib file store, an
    in-memory dict, Redis). Read failures should degrade to ``None`` (a miss)
    rather than raising.
    """

    def get(self, key: str) -> CacheEntry | None:
        """Return the stored entry for ``key``, or ``None`` on miss/failure."""
        ...

    def set(self, key: str, entry: CacheEntry) -> None:
        """Store ``entry`` under ``key``."""
        ...

    def clear(self) -> None:
        """Remove every stored entry (invalidation)."""
        ...

    def close(self) -> None:
        """Release any underlying resources."""
        ...


class FileCache:
    """Stdlib-only on-disk :class:`DiskCache` (one JSON file per key).

    Entries are written atomically (a temporary file in the same directory plus
    ``os.replace``) so a crash cannot leave a torn entry. The body is base64
    encoded inside a JSON envelope; ``pickle`` is never used. A corrupt or
    unreadable file is treated as a silent miss.
    """

    def __init__(self, dir: Path | None = None) -> None:
        """Initialize the file store.

        Args:
            dir: Base directory for entry files; defaults to
                ``~/.cache/spotify_scraper``. Created if absent.
        """
        self._dir = dir if dir is not None else Path.home() / ".cache" / "spotify_scraper"
        self._dir.mkdir(parents=True, exist_ok=True)
        # Owner-only: cached metadata bodies and the sha256 entry filenames are
        # not world-business. chmod (a no-op on Windows) hardens a pre-existing dir.
        with contextlib.suppress(OSError):
            self._dir.chmod(0o700)

    def _path(self, key: str) -> Path:
        return self._dir / key

    def get(self, key: str) -> CacheEntry | None:
        """Read the entry for ``key``; any failure is a silent miss."""
        path = self._path(key)
        try:
            raw = path.read_bytes()
        except OSError:
            return None
        try:
            doc = json.loads(raw)
            return CacheEntry(
                status_code=int(doc["status_code"]),
                content=base64.b64decode(doc["content"]),
                headers=dict(doc["headers"]),
                stored_at=float(doc["stored_at"]),
            )
        except (ValueError, KeyError, TypeError, binascii.Error):
            _LOGGER.warning("Ignoring corrupt cache entry at %s", path)
            return None

    def set(self, key: str, entry: CacheEntry) -> None:
        """Atomically write ``entry`` under ``key``; write failures degrade."""
        doc = {
            "status_code": entry.status_code,
            "headers": dict(entry.headers),
            "stored_at": entry.stored_at,
            "content": base64.b64encode(entry.content).decode("ascii"),
        }
        payload = json.dumps(doc).encode("utf-8")
        try:
            fd, tmp_name = tempfile.mkstemp(dir=self._dir, prefix=".tmp-")
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(payload)
                os.replace(tmp_name, self._path(key))
            except OSError:
                with contextlib.suppress(OSError):
                    os.unlink(tmp_name)
                raise
        except OSError:
            _LOGGER.warning("Failed to write cache entry %s", key)

    def clear(self) -> None:
        """Remove every entry file under the base directory."""
        for path in self._dir.iterdir():
            if path.is_file():
                with contextlib.suppress(OSError):
                    path.unlink()

    def close(self) -> None:
        """No-op: entries are flushed on ``set``."""


def _is_cacheable(url: str, config: CacheConfig) -> bool:
    """Return whether a GET to ``url`` may be cached.

    Cache iff the host is in ``cacheable_hosts`` and the path matches none of
    the ``denied_path_prefixes``. This single predicate enforces every
    never-cache rule (token endpoints by the ``/api/`` prefix, the lyrics host
    by host-absence).
    """
    parsed = httpx.URL(url)
    return parsed.host in config.cacheable_hosts and not any(
        parsed.path.startswith(prefix) for prefix in config.denied_path_prefixes
    )


def _key(url: str, headers: Mapping[str, str] | None) -> str:
    """Derive the sha256 cache key from the full URL and locale header.

    ``Accept-Language`` varies the public response, so it is part of the key.
    ``Authorization`` is excluded: the anonymous bearer token rotates without
    changing the public response, and authenticated hosts are already denied at
    :func:`_is_cacheable`.
    """
    accept_language = ""
    if headers:
        for name, value in headers.items():
            if name.lower() == "accept-language":
                accept_language = value
                break
    digest = hashlib.sha256()
    digest.update(url.encode("utf-8"))
    digest.update(b"\n")
    digest.update(accept_language.encode("utf-8"))
    return digest.hexdigest()


def _entry_from(response: Response) -> CacheEntry:
    return CacheEntry(
        status_code=response.status_code,
        content=response.content,
        headers=dict(response.headers),
        stored_at=time.time(),
    )


def _fresh_hit(entry: CacheEntry | None, config: CacheConfig) -> Response | None:
    if entry is None:
        return None
    if time.time() - entry.stored_at >= config.ttl_seconds:
        return None
    # A frozen ``CachedResponse`` satisfies the ``Response`` protocol at runtime
    # (``isinstance`` passes); the cast bridges mypy's settable-variable check on
    # ``status_code`` without re-opening the protocol or unfreezing the model.
    return cast(Response, CachedResponse(entry.status_code, entry.content, entry.headers))


class CachingTransport:
    """A :class:`Transport` wrapper that serves cacheable GETs from a store."""

    def __init__(self, inner: Transport, config: CacheConfig) -> None:
        """Wrap ``inner`` with the cache described by ``config``."""
        self._inner = inner
        self._config = config

    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response:
        """Fetch ``url``, serving a fresh cache hit when possible.

        On a cacheable GET a fresh stored entry is returned with no network
        call; otherwise the inner transport is called and a ``200`` response is
        stored. Non-cacheable URLs pass straight through with no store access.
        """
        if not _is_cacheable(url, self._config):
            return self._inner.get(url, headers=headers)
        key = _key(url, headers)
        hit = _fresh_hit(self._config.store.get(key), self._config)
        if hit is not None:
            return hit
        response = self._inner.get(url, headers=headers)
        if response.status_code == 200:
            self._config.store.set(key, _entry_from(response))
        return response

    def close(self) -> None:
        """Close the store and the inner transport."""
        try:
            self._config.store.close()
        finally:
            self._inner.close()


class AsyncCachingTransport:
    """An :class:`AsyncTransport` wrapper that serves cacheable GETs from a store."""

    def __init__(self, inner: AsyncTransport, config: CacheConfig) -> None:
        """Wrap ``inner`` with the cache described by ``config``."""
        self._inner = inner
        self._config = config

    async def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response:
        """Fetch ``url``, serving a fresh cache hit when possible.

        The store stays synchronous (blocking file I/O, like the media and
        cookie stores); only the inner network fetch is awaited.
        """
        if not _is_cacheable(url, self._config):
            return await self._inner.get(url, headers=headers)
        key = _key(url, headers)
        hit = _fresh_hit(self._config.store.get(key), self._config)
        if hit is not None:
            return hit
        response = await self._inner.get(url, headers=headers)
        if response.status_code == 200:
            self._config.store.set(key, _entry_from(response))
        return response

    async def aclose(self) -> None:
        """Close the store and the inner transport."""
        try:
            self._config.store.close()
        finally:
            await self._inner.aclose()
