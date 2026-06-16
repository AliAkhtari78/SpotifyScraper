# Tasks: add-batch-helpers

## 0. Ground the design (read-only audit — no code yet)

- [x] 0.1 Confirm `_T = TypeVar("_T")` already exists at module level in BOTH
      `_sync/client.py` (line 49) and `_async/client.py` (line 48) — reuse it for
      the `_batch` engines; do not redeclare.
- [x] 0.2 Confirm `test_parity.py` compares `list(signature.parameters)` AND the
      `return_annotation` string for every shared public method (lines 26-32).
      This pins Option A: `max_concurrency` MUST NOT be a method parameter.
- [x] 0.3 Confirm `SpotifyScraperError` is the base of every per-item failure
      (`NotFoundError`, `URLError`, `NetworkError`/`RateLimitedError`,
      `ParsingError`, `TokenError`, `AuthenticationError`, `MediaError`) in
      `errors.py` — it is the single catch boundary.
- [x] 0.4 Confirm `urls.parse` (called inside `_resolve`) raises `URLError`
      BEFORE any I/O, so a malformed input is captured per item like any other
      `SpotifyScraperError`.

## 1. The sans-io result type (frozen, slotted, generic)

- [x] 1.1 Create `src/spotify_scraper/batch.py` with module docstring, `from
      __future__ import annotations`, `from collections.abc import Sequence`,
      `from dataclasses import dataclass`, `from typing import Generic, TypeVar`.
      Declare a local `_T = TypeVar("_T")`.
- [x] 1.2 Add `@dataclass(frozen=True, slots=True) class BatchItem(Generic[_T])`
      with `value: str`, `result: _T | None = None`,
      `error: Exception | None = None`. Type `error` as `Exception` (not
      `SpotifyScraperError`) to stay honest about the field, while the engines
      capture only `SpotifyScraperError`.
- [x] 1.3 Add `@property def ok(self) -> bool: return self.error is None`.
- [x] 1.4 Add `def unwrap(self) -> _T:` — `if self.error is not None: raise
      self.error`; `assert self.result is not None`; `return self.result`.
      Docstring: returns the model on success, re-raises the captured error
      otherwise.
- [x] 1.5 (Optional, only if symmetry is wanted) no `to_dict()` — `BatchItem` is
      a control wrapper, not Spotify data. Document this choice in the docstring.

## 2. Exports

- [x] 2.1 In `src/spotify_scraper/__init__.py` add `from spotify_scraper.batch
      import BatchItem` and insert `"BatchItem"` into `__all__` keeping it
      alphabetized (between `"Artist"`/`"ArtistRef"` group and
      `"AsyncCachingTransport"` — i.e. after `"ArtistRef"`).

## 3. SYNC plural helpers (sequential — already rate-limited)

- [x] 3.1 In `_sync/client.py` add imports: `from collections.abc import
      Sequence` (extend the existing `from collections.abc import Callable,
      Mapping` line) and `from spotify_scraper.batch import BatchItem`.
- [x] 3.2 Add private engine `def _batch(self, values: Sequence[str], fetch:
      Callable[[str], _T]) -> Sequence[BatchItem[_T]]`: call `self._ensure_open()`
      once up front; iterate `values` IN ORDER; per item `try:
      out.append(BatchItem(value, result=fetch(value)))` / `except
      SpotifyScraperError as exc: out.append(BatchItem(value, error=exc))`;
      return the list. Catch ONLY `SpotifyScraperError`.
- [x] 3.3 `def get_tracks(self, values: Sequence[str]) -> Sequence[BatchItem[Track]]:
      return self._batch(values, self.get_track)`.
- [x] 3.4 `get_albums` → `self._batch(values, self.get_album)`;
      `get_artists` → `self._batch(values, self.get_artist)`;
      `get_episodes` → `self._batch(values, self.get_episode)`.
- [x] 3.5 `def get_playlists(self, values: Sequence[str], *, max_tracks: int |
      None = 100) -> Sequence[BatchItem[Playlist]]: return self._batch(values,
      lambda v: self.get_playlist(v, max_tracks=max_tracks))`.
- [x] 3.6 `def get_shows(self, values: Sequence[str], *, max_episodes: int | None
      = 50) -> Sequence[BatchItem[Show]]: return self._batch(values, lambda v:
      self.get_show(v, max_episodes=max_episodes))`.
- [x] 3.7 Add a docstring to each plural getter (Returns: an ordered Sequence of
      `BatchItem`, index-aligned with `values`; per-item `SpotifyScraperError` is
      captured, never raised mid-batch; Raises `SpotifyScraperError` only if the
      client is already closed).

## 4. ASYNC plural helpers (bounded asyncio.gather)

- [x] 4.1 In `_async/client.py` add imports: extend `from collections.abc import
      Callable, Mapping` to also import `Awaitable, Sequence`; add `import asyncio`;
      add `from spotify_scraper.batch import BatchItem`.
- [x] 4.2 Add `"_semaphore"` to `AsyncSpotifyClient.__slots__` (keep sorted).
- [x] 4.3 Add `max_concurrency: int = 5` as a keyword-only param to
      `__init__` (place it among the existing keyword-only args, e.g. after
      `cache`). Validate `max_concurrency >= 1` (raise `ValueError` otherwise,
      mirroring `RateLimit.__post_init__` style). Store
      `self._semaphore = asyncio.Semaphore(max_concurrency)`.
- [x] 4.4 Document `max_concurrency` in the `__init__` docstring: caps how many
      entity pipelines run concurrently in the plural `get_*s` helpers; bounds
      open sockets and bucket-lock contention; the rate limiter still governs
      request rate. Default 5 matches the default `RateLimit.burst`.
- [x] 4.5 Add `async def _batch(self, values: Sequence[str], fetch:
      Callable[[str], Awaitable[_T]]) -> Sequence[BatchItem[_T]]`: call
      `self._ensure_open()`; define an inner `async def one(value: str) ->
      BatchItem[_T]` that does `async with self._semaphore:` then `try: return
      BatchItem(value, result=await fetch(value))` / `except SpotifyScraperError
      as exc: return BatchItem(value, error=exc)`; `return list(await
      asyncio.gather(*(one(v) for v in values)))`. Use default
      `return_exceptions=False` — every task catches its own library error, so
      `gather` never sees one; `CancelledError` (not a `SpotifyScraperError`)
      propagates correctly.
- [x] 4.6 Add the six async plural getters mirroring 3.3-3.6 with `async def` +
      `await self._batch(...)` and BYTE-IDENTICAL signatures to the sync side
      (same param names, order, defaults, return annotation text).
- [x] 4.7 Copy the sync plural docstrings verbatim (the behavioral contract is
      identical; only execution model differs).

## 5. Parity guard

- [x] 5.1 Run `tests/unit/test_parity.py` — the existing
      `test_public_method_sets_match_modulo_lifecycle` now also covers the six new
      methods (must match) and `test_data_methods_share_signatures` asserts
      identical params + return annotation. Confirm GREEN. If it fails on a
      `values` vs `values, max_concurrency` mismatch, `max_concurrency` leaked
      onto a method signature — remove it (Option A).

## 6. Hermetic tests (no live step)

- [x] 6.1 `tests/unit/test_client_batch.py` (sync): reuse the respx + fixture
      harness from `test_client_entities.py` (fixtures under
      `tests/fixtures/embed/` + `tests/fixtures/pathfinder/`, the `IDS` map, the
      `_embed_html`/`_mock` helpers, `PATHFINDER_RE`).
- [x] 6.2 **Happy path:** `get_tracks([id, id])` → two items, both `.ok`, in input
      order, each `.result` is a `Track`.
- [x] 6.3 **Partial failure:** mock one track's embed (or pathfinder) to a 404 so
      the inner getter raises `NotFoundError`; assert that item's `.ok is False`
      and `isinstance(item.error, NotFoundError)`, the other item is `.ok`, ORDER
      is preserved, and `get_tracks` itself did NOT raise. Assert
      `item.unwrap()` re-raises `NotFoundError` for the failed item.
- [x] 6.4 **URLError item:** pass a malformed value (e.g. `"not-a-spotify-id"`)
      alongside a good one; assert the bad item's `.error` is a `URLError`, the
      good item is `.ok`, batch continues.
- [x] 6.5 **Closed client:** `client.close()` then `client.get_tracks([id])`
      raises `SpotifyScraperError` up front (via the engine's `_ensure_open`).
- [x] 6.6 **Cap forwarding:** `get_playlists(values, max_tracks=N)` and
      `get_shows(values, max_episodes=N)` — assert the underlying getter received
      the cap (e.g. via a respx route-count assertion or a parsed-result length
      bound, matching how the singular cap tests already assert).
- [x] 6.7 `tests/unit/test_client_batch_async.py` (async): mirror 6.2-6.6 with
      `await`, `AsyncSpotifyClient`, and the async respx harness from
      `test_client_entities_async.py`.
- [x] 6.8 **Async bounded-concurrency (async-only):** inject a recording
      `AsyncTransport` stub (pattern from `tests/unit/http/test_cache.py`'s
      `_AsyncStubTransport`) that increments an in-flight counter on entry to
      `get`, `await asyncio.sleep(0)`/a small event to overlap, decrements on
      exit, and records the max observed in-flight. Build
      `AsyncSpotifyClient(transport=stub, max_concurrency=2)`, run
      `get_tracks([...8 ids...])`, assert observed max in-flight `<=
      max_concurrency` AND `> 1` (proves the semaphore neither over-runs nor
      serializes). Keep it deterministic with an `asyncio.Event`/barrier, no real
      sleeps.
- [x] 6.9 **max_concurrency validation:** `AsyncSpotifyClient(max_concurrency=0)`
      raises `ValueError`.

## 7. Quality gates

- [x] 7.1 `make type` (mypy --strict) clean — `BatchItem` generic resolves
      (`Sequence[BatchItem[Track]]` etc.); `fetch` callbacks typed
      `Callable[[str], _T]` (sync) / `Callable[[str], Awaitable[_T]]` (async);
      no `Any` leakage.
- [x] 7.2 `make lint` / `make format` clean.
- [x] 7.3 `make test` green (including `test_parity.py`).
- [x] 7.4 `make cov` stays above the 85% floor; `batch.py` and both engines
      well-covered (happy, partial-fail, URLError, closed, bounded-concurrency).
- [x] 7.5 Confirm no new runtime dependency in `pyproject.toml` (stdlib
      `asyncio`, `dataclasses`, `collections.abc`, `typing` only).
- [x] 7.6 (Docs, optional but recommended) add a short "Batch fetching" snippet to
      the docs/usage page showing `BatchItem.ok`/`.unwrap()` and the async
      `max_concurrency` knob.

## 8. Review fixes

- [x] 8.1 (code, prior session) bind the async batch semaphore per event loop so
      a client reused across `asyncio.run()` no longer crashes; cross-loop
      regression test added.
- [x] 8.2 Docs: new `guides/batch.md` (plural helpers, partial-failure `BatchItem`,
      async `max_concurrency`, `BatchItem` autodoc) + nav; README Batch section +
      Features bullet + roadmap (3.5 batch shipped); index roadmap + success
      admonition; CHANGELOG Unreleased.