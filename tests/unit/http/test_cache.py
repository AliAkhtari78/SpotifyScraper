"""Fully hermetic tests for the response cache (no network, no live step).

A stub inner transport records calls and returns canned responses; a real
``FileCache`` writes to ``tmp_path``. Together they exercise the whole feature
offline: hit/miss, the never-cache rules, no-cache-on-error, TTL expiry, the
locale-sensitive key, ``Authorization`` exclusion, corrupt-file silent miss,
``clear()`` invalidation, close propagation, and the client ``cache=`` flag.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

import httpx
import pytest

from spotify_scraper import SpotifyClient
from spotify_scraper._async.client import AsyncSpotifyClient
from spotify_scraper.errors import NotFoundError
from spotify_scraper.http.cache import (
    AsyncCachingTransport,
    CacheConfig,
    CachedResponse,
    CacheEntry,
    CachingTransport,
    DiskCache,
    FileCache,
)
from spotify_scraper.http.transport import AsyncTransport, Response, Transport

PATHFINDER_URL = "https://api-partner.spotify.com/pathfinder/v1/query?operationName=x"
EMBED_URL = "https://open.spotify.com/embed/track/4uLU6hMCjMI75M1A2tKUQC"
TOKEN_URL = "https://open.spotify.com/api/token?reason=transport"  # noqa: S105 — a URL, not a secret
SERVER_TIME_URL = "https://open.spotify.com/api/server-time"
LYRICS_URL = "https://spclient.wg.spotify.com/color-lyrics/v2/track/abc"

PAYLOAD: dict[str, Any] = {"data": {"trackUnion": {"name": "Hermetic"}}}


def _response(
    status: int = 200,
    *,
    body: bytes | None = None,
    headers: Mapping[str, str] | None = None,
) -> Response:
    """A canned ``Response``-satisfying value object for the stub to return.

    Typed as ``Response``: a frozen ``CachedResponse`` satisfies the protocol at
    runtime, but its read-only ``status_code`` trips mypy's settable-variable
    check, so the value is bridged here exactly as the wrapper does internally.
    """
    content = body if body is not None else json.dumps(PAYLOAD).encode("utf-8")
    resp = CachedResponse(status, content, dict(headers or {"content-type": "application/json"}))
    return cast(Response, resp)


class _StubTransport:
    """A ``Transport``/``AsyncTransport`` stub recording calls + canned replies."""

    def __init__(self, *, reply: Response | None = None, raises: Exception | None = None) -> None:
        self._reply = reply if reply is not None else _response()
        self._raises = raises
        self.calls: list[tuple[str, Mapping[str, str] | None]] = []
        self.closed = 0

    def _serve(self, url: str, headers: Mapping[str, str] | None) -> Response:
        self.calls.append((url, dict(headers) if headers is not None else None))
        if self._raises is not None:
            raise self._raises
        return self._reply

    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> Response:
        return self._serve(url, headers)

    def close(self) -> None:
        self.closed += 1


class _AsyncStubTransport(_StubTransport):
    async def get(  # type: ignore[override]
        self, url: str, *, headers: Mapping[str, str] | None = None
    ) -> Response:
        return self._serve(url, headers)

    async def aclose(self) -> None:
        self.closed += 1


def _config(tmp_path: Path, **overrides: Any) -> CacheConfig:
    return CacheConfig(store=FileCache(tmp_path), **overrides)


# --- protocol satisfaction -------------------------------------------------


def test_wrappers_and_store_satisfy_runtime_protocols(tmp_path: Path) -> None:
    config = _config(tmp_path)
    assert isinstance(CachingTransport(_StubTransport(), config), Transport)
    assert isinstance(AsyncCachingTransport(_AsyncStubTransport(), config), AsyncTransport)
    assert isinstance(FileCache(tmp_path), DiskCache)


def test_cached_response_has_response_shape() -> None:
    # ``Response`` is not @runtime_checkable, so assert the structure directly:
    # status_code + the headers/text/content/json() members the protocol needs.
    resp = _response()
    assert resp.status_code == 200
    assert isinstance(resp.headers, Mapping)
    assert isinstance(resp.text, str)
    assert isinstance(resp.content, bytes)
    assert callable(resp.json)
    typed: Response = resp  # mypy: structurally satisfies the protocol
    assert typed.json() == PAYLOAD


# --- hit path (sync) -------------------------------------------------------


def test_first_get_records_second_served_from_disk(tmp_path: Path) -> None:
    stub = _StubTransport(reply=_response(headers={"x-cache-test": "1"}))
    cache = CachingTransport(stub, _config(tmp_path))

    first = cache.get(PATHFINDER_URL)
    second = cache.get(PATHFINDER_URL)

    assert len(stub.calls) == 1  # inner transport NOT called the second time
    assert second.status_code == first.status_code == 200
    assert second.content == first.content
    assert second.headers["x-cache-test"] == "1"
    assert second.json() == PAYLOAD


def test_embed_url_is_cached(tmp_path: Path) -> None:
    stub = _StubTransport()
    cache = CachingTransport(stub, _config(tmp_path))

    cache.get(EMBED_URL)
    cache.get(EMBED_URL)

    assert len(stub.calls) == 1


# --- never-cache rules -----------------------------------------------------


@pytest.mark.parametrize("url", [TOKEN_URL, SERVER_TIME_URL, LYRICS_URL])
def test_never_cached_urls_pass_through_and_write_nothing(tmp_path: Path, url: str) -> None:
    stub = _StubTransport()
    cache = CachingTransport(stub, _config(tmp_path))

    cache.get(url)
    cache.get(url)

    assert len(stub.calls) == 2  # every call hits the inner transport
    assert list(tmp_path.iterdir()) == []  # nothing written to the store


# --- no-cache-on-error -----------------------------------------------------


def test_not_found_propagates_and_writes_nothing(tmp_path: Path) -> None:
    stub = _StubTransport(raises=NotFoundError("missing"))
    cache = CachingTransport(stub, _config(tmp_path))

    with pytest.raises(NotFoundError):
        cache.get(PATHFINDER_URL)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("status", [401, 403])
def test_pass_through_non_200_not_stored(tmp_path: Path, status: int) -> None:
    stub = _StubTransport(reply=_response(status))
    cache = CachingTransport(stub, _config(tmp_path))

    returned = cache.get(PATHFINDER_URL)
    cache.get(PATHFINDER_URL)

    assert returned.status_code == status
    assert len(stub.calls) == 2  # not served from cache the second time
    assert list(tmp_path.iterdir()) == []


def test_error_then_success_is_cached(tmp_path: Path) -> None:
    store = FileCache(tmp_path)
    config = CacheConfig(store=store)
    failing = CachingTransport(_StubTransport(raises=NotFoundError("x")), config)
    with pytest.raises(NotFoundError):
        failing.get(PATHFINDER_URL)

    stub = _StubTransport()
    cache = CachingTransport(stub, config)
    cache.get(PATHFINDER_URL)
    cache.get(PATHFINDER_URL)

    assert len(stub.calls) == 1


# --- TTL -------------------------------------------------------------------


def test_expired_entry_refetches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stub = _StubTransport()
    config = _config(tmp_path, ttl_seconds=10.0)
    cache = CachingTransport(stub, config)

    monkeypatch.setattr("spotify_scraper.http.cache.time.time", lambda: 1_000.0)
    cache.get(PATHFINDER_URL)

    monkeypatch.setattr("spotify_scraper.http.cache.time.time", lambda: 1_011.0)
    cache.get(PATHFINDER_URL)

    assert len(stub.calls) == 2  # expired, re-fetched


def test_fresh_entry_within_ttl_hits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stub = _StubTransport()
    cache = CachingTransport(stub, _config(tmp_path, ttl_seconds=100.0))

    monkeypatch.setattr("spotify_scraper.http.cache.time.time", lambda: 1_000.0)
    cache.get(PATHFINDER_URL)

    monkeypatch.setattr("spotify_scraper.http.cache.time.time", lambda: 1_050.0)
    cache.get(PATHFINDER_URL)

    assert len(stub.calls) == 1


# --- key derivation --------------------------------------------------------


def test_accept_language_varies_the_key(tmp_path: Path) -> None:
    de_body = json.dumps({"lang": "de"}).encode()
    ja_body = json.dumps({"lang": "ja"}).encode()
    stub = _StubTransport()
    cache = CachingTransport(stub, _config(tmp_path))

    stub._reply = _response(body=de_body)
    cache.get(PATHFINDER_URL, headers={"Accept-Language": "de"})
    stub._reply = _response(body=ja_body)
    cache.get(PATHFINDER_URL, headers={"Accept-Language": "ja"})

    # Two distinct entries, each served its own body on repeat.
    assert len(stub.calls) == 2
    de_hit = cache.get(PATHFINDER_URL, headers={"Accept-Language": "de"})
    ja_hit = cache.get(PATHFINDER_URL, headers={"Accept-Language": "ja"})
    assert len(stub.calls) == 2  # both served from cache
    assert de_hit.content == de_body
    assert ja_hit.content == ja_body


def test_accept_language_header_name_is_case_insensitive(tmp_path: Path) -> None:
    stub = _StubTransport()
    cache = CachingTransport(stub, _config(tmp_path))

    cache.get(PATHFINDER_URL, headers={"Accept-Language": "de"})
    cache.get(PATHFINDER_URL, headers={"accept-language": "de"})

    assert len(stub.calls) == 1  # same key despite header-name casing


def test_authorization_excluded_from_key(tmp_path: Path) -> None:
    stub = _StubTransport()
    cache = CachingTransport(stub, _config(tmp_path))

    cache.get(PATHFINDER_URL, headers={"Authorization": "Bearer one"})
    cache.get(PATHFINDER_URL, headers={"Authorization": "Bearer two"})

    assert len(stub.calls) == 1  # rotated token still hits the same entry


# --- failure / invalidation ------------------------------------------------


def test_corrupt_file_is_silent_miss(tmp_path: Path) -> None:
    stub = _StubTransport()
    store = FileCache(tmp_path)
    cache = CachingTransport(stub, CacheConfig(store=store))

    cache.get(PATHFINDER_URL)
    [entry_file] = list(tmp_path.iterdir())
    entry_file.write_bytes(b"this is not json {{{")

    served = cache.get(PATHFINDER_URL)  # no exception

    assert served.status_code == 200
    assert len(stub.calls) == 2  # corrupt entry triggered a re-fetch


def test_get_missing_key_is_none(tmp_path: Path) -> None:
    assert FileCache(tmp_path).get("does-not-exist") is None


def test_write_failure_degrades_to_uncached(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _boom(_src: str, _dst: Any) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("spotify_scraper.http.cache.os.replace", _boom)
    stub = _StubTransport()
    cache = CachingTransport(stub, _config(tmp_path))

    served = cache.get(PATHFINDER_URL)  # write fails silently
    cache.get(PATHFINDER_URL)

    assert served.status_code == 200  # request still succeeds
    assert len(stub.calls) == 2  # nothing cached, so re-fetched
    # The temp file must have been cleaned up: only the (absent) entry remains.
    assert list(tmp_path.glob(".tmp-*")) == []


def test_clear_invalidates(tmp_path: Path) -> None:
    stub = _StubTransport()
    store = FileCache(tmp_path)
    cache = CachingTransport(stub, CacheConfig(store=store))

    cache.get(PATHFINDER_URL)
    store.clear()
    cache.get(PATHFINDER_URL)

    assert len(stub.calls) == 2  # re-fetched after clear


def test_clear_tolerates_subdir(tmp_path: Path) -> None:
    store = FileCache(tmp_path)
    (tmp_path / "subdir").mkdir()  # clear() must skip non-files without error
    store.set("k", CacheEntry(200, b"x", {}, 1.0))
    store.clear()
    assert store.get("k") is None


def test_custom_in_memory_store_works(tmp_path: Path) -> None:
    class _DictStore:
        def __init__(self) -> None:
            self.data: dict[str, CacheEntry] = {}

        def get(self, key: str) -> CacheEntry | None:
            return self.data.get(key)

        def set(self, key: str, entry: CacheEntry) -> None:
            self.data[key] = entry

        def clear(self) -> None:
            self.data.clear()

        def close(self) -> None:
            pass

    store = _DictStore()
    assert isinstance(store, DiskCache)
    stub = _StubTransport()
    cache = CachingTransport(stub, CacheConfig(store=store))

    cache.get(PATHFINDER_URL)
    cache.get(PATHFINDER_URL)

    assert len(stub.calls) == 1
    assert len(store.data) == 1


# --- CachedResponse contract -----------------------------------------------


def test_cached_response_json_raises_on_bad_body() -> None:
    bad = CachedResponse(200, b"not json", {})
    with pytest.raises(ValueError):
        bad.json()


def test_cached_response_text_decodes_with_replacement() -> None:
    resp = CachedResponse(200, b"\xff\xfe caf\xc3\xa9", {})
    assert "café" in resp.text  # invalid bytes replaced, valid utf-8 decoded


# --- close propagation -----------------------------------------------------


def test_close_propagates_to_inner(tmp_path: Path) -> None:
    stub = _StubTransport()
    cache = CachingTransport(stub, _config(tmp_path))
    cache.close()
    assert stub.closed == 1


def test_close_inner_runs_even_if_store_close_raises(tmp_path: Path) -> None:
    class _BadStore(FileCache):
        def close(self) -> None:
            raise OSError("store boom")

    stub = _StubTransport()
    cache = CachingTransport(stub, CacheConfig(store=_BadStore(tmp_path)))
    with pytest.raises(OSError):
        cache.close()
    assert stub.closed == 1  # inner still torn down


# --- client cache= flag ----------------------------------------------------


def test_client_cache_flag_builds_caching_transport(tmp_path: Path) -> None:
    client = SpotifyClient(cache=_config(tmp_path))
    try:
        assert isinstance(client._transport, CachingTransport)
    finally:
        client.close()


def test_client_cache_ignored_when_transport_given(tmp_path: Path) -> None:
    stub = _StubTransport()
    client = SpotifyClient(transport=stub, cache=_config(tmp_path))
    try:
        assert client._transport is stub
    finally:
        client.close()


def test_client_without_cache_uses_plain_transport() -> None:
    client = SpotifyClient()
    try:
        assert not isinstance(client._transport, CachingTransport)
    finally:
        client.close()


def test_async_client_cache_flag_builds_caching_transport(tmp_path: Path) -> None:
    client = AsyncSpotifyClient(cache=_config(tmp_path))
    assert isinstance(client._transport, AsyncCachingTransport)


def test_async_client_cache_ignored_when_transport_given(tmp_path: Path) -> None:
    stub = _AsyncStubTransport()
    client = AsyncSpotifyClient(transport=stub, cache=_config(tmp_path))
    assert client._transport is stub


# --- async variants --------------------------------------------------------


async def test_async_first_get_records_second_from_disk(tmp_path: Path) -> None:
    stub = _AsyncStubTransport()
    cache = AsyncCachingTransport(stub, _config(tmp_path))

    first = await cache.get(PATHFINDER_URL)
    second = await cache.get(PATHFINDER_URL)

    assert len(stub.calls) == 1
    assert second.content == first.content
    assert second.json() == PAYLOAD


@pytest.mark.parametrize("url", [TOKEN_URL, SERVER_TIME_URL, LYRICS_URL])
async def test_async_never_cached_pass_through(tmp_path: Path, url: str) -> None:
    stub = _AsyncStubTransport()
    cache = AsyncCachingTransport(stub, _config(tmp_path))

    await cache.get(url)
    await cache.get(url)

    assert len(stub.calls) == 2
    assert list(tmp_path.iterdir()) == []


async def test_async_not_found_propagates_and_writes_nothing(tmp_path: Path) -> None:
    stub = _AsyncStubTransport(raises=NotFoundError("missing"))
    cache = AsyncCachingTransport(stub, _config(tmp_path))

    with pytest.raises(NotFoundError):
        await cache.get(PATHFINDER_URL)

    assert list(tmp_path.iterdir()) == []


async def test_async_403_not_stored(tmp_path: Path) -> None:
    stub = _AsyncStubTransport(reply=_response(403))
    cache = AsyncCachingTransport(stub, _config(tmp_path))

    await cache.get(PATHFINDER_URL)
    await cache.get(PATHFINDER_URL)

    assert len(stub.calls) == 2
    assert list(tmp_path.iterdir()) == []


async def test_async_close_propagates_to_inner(tmp_path: Path) -> None:
    stub = _AsyncStubTransport()
    cache = AsyncCachingTransport(stub, _config(tmp_path))
    await cache.aclose()
    assert stub.closed == 1


# --- round-trip of an httpx.Response through the store ---------------------


def test_real_httpx_response_round_trips(tmp_path: Path) -> None:
    real = httpx.Response(200, json=PAYLOAD, headers={"x-source": "httpx"})
    stub = _StubTransport(reply=real)
    cache = CachingTransport(stub, _config(tmp_path))

    cache.get(PATHFINDER_URL)
    served = cache.get(PATHFINDER_URL)

    assert len(stub.calls) == 1
    assert served.json() == PAYLOAD
    assert served.headers["x-source"] == "httpx"
