# Proposal: add-batch-helpers

> **Status: targets v3.x.** Closes issue #132. Adds six **plural convenience
> helpers** (`get_tracks`, `get_albums`, `get_artists`, `get_playlists`,
> `get_episodes`, `get_shows`) to **both** client facades so callers can fetch
> many IDs in one call without hand-rolling throttling. **Pure ergonomics** — no
> new endpoint, no new runtime dependency, no parser/model/transport change. The
> existing per-host `TokenBucket` already throttles every request, so SYNC is a
> simple ordered loop; ASYNC is `asyncio.gather` bounded by a constructor-set
> `asyncio.Semaphore` so it never opens too many sockets or outruns the rate
> limiter. Partial failures are captured per item in a new pure, frozen/slotted,
> generic `BatchItem[_T]` result — a 404 on one ID never kills the batch.
> Fully hermetic to test (respx + a recording stub transport); no live step.

## Why

Users routinely have a list of IDs/URLs (a column in a CSV, a set of artist URIs,
a playlist's worth of track links) and want all of them. Today they must write
their own loop and — to avoid bans — their own throttling and their own
try/except per item. That is exactly the boilerplate the library should own: the
single-entity getters already pass every underlying request through the
per-host `TokenBucket` (`ratelimit.py`), so the throttling primitive exists; it
just is not exposed at batch granularity.

Two things make a naive `[client.get_track(v) for v in values]` (sync) or
`asyncio.gather(*(client.get_track(v) ...))` (async) wrong:

1. **One bad ID kills the batch.** A single `NotFoundError` (dead/region-locked
   ID) or `URLError` (typo) aborts the whole loop / fails the whole `gather`.
   A batch over mixed real-world IDs *must* return per-item outcomes.
2. **Unbounded async fan-out.** `get_album`/`get_show`/`get_playlist` each issue
   an embed fetch plus 1..N pathfinder pages. Firing all N entities into one
   `gather` schedules a huge number of in-flight coroutines all contending on the
   bucket lock and all holding `httpx.AsyncClient` connections — unbounded socket
   and memory pressure. The `AsyncTokenBucket` caps the *rate*; nothing caps the
   *fan-out width*.

So: add plural helpers that (a) capture `SpotifyScraperError` per item into an
ordered, typed result and (b) bound async concurrency with a semaphore that
composes cleanly with the rate limiter (semaphore = concurrency limiter, bucket =
rate limiter).

## What Changes

- **`src/spotify_scraper/batch.py`** (new, **sans-io**, zero I/O, stdlib only):
  a `BatchItem[_T]` frozen slotted generic dataclass — the load-bearing
  partial-failure type. Fields `value: str` (the input, echoed back), `result: _T
  | None`, `error: Exception | None`; properties `.ok` and `.unwrap()`
  (returns the model or re-raises the captured error). This is a *control
  wrapper*, not Spotify data, so it needs no `to_dict()` (CLAUDE.md's JSON-safe
  rule applies to entity models).
- **`_sync/client.py`** — a private `_batch(values, fetch)` engine (ordered
  sequential loop; one up-front `_ensure_open()`; capture only
  `SpotifyScraperError` per item) plus six thin plural getters delegating to it.
  No threads, no semaphore: the per-host `TokenBucket` in the transport already
  throttles each underlying call, so sequential **is** rate-limited.
- **`_async/client.py`** — a `max_concurrency: int = 5` constructor kwarg
  (**async client only**), a `_semaphore` slot holding an
  `asyncio.Semaphore(max_concurrency)`, an `async def _batch(values, fetch)`
  engine running `asyncio.gather` over per-item coroutines each gated by that
  semaphore (order preserved by `gather`; capture only `SpotifyScraperError`
  inside each task so `CancelledError`/bugs propagate), plus the six plural
  getters. `_semaphore` is added to `__slots__`.
- **Critical parity decision (Option A): `max_concurrency` is a constructor arg
  on the async client, NOT a method parameter.** `test_parity.py` compares
  `list(signature.parameters)` and the `return_annotation` string for every
  shared public method. Keeping `max_concurrency` off the method signatures means
  the six plural helpers have **byte-identical** signatures across sync/async, so
  parity passes trivially. Default `5` matches `RateLimit.burst=5` so concurrency
  never structurally outruns burst capacity.
- **Plural signatures (identical on both clients, only `async`/`await` differs):**
  - `get_tracks(self, values: Sequence[str]) -> Sequence[BatchItem[Track]]`
  - `get_albums(self, values: Sequence[str]) -> Sequence[BatchItem[Album]]`
  - `get_artists(self, values: Sequence[str]) -> Sequence[BatchItem[Artist]]`
  - `get_episodes(self, values: Sequence[str]) -> Sequence[BatchItem[Episode]]`
  - `get_playlists(self, values: Sequence[str], *, max_tracks: int | None = 100) -> Sequence[BatchItem[Playlist]]`
  - `get_shows(self, values: Sequence[str], *, max_episodes: int | None = 50) -> Sequence[BatchItem[Show]]`
  The `max_tracks`/`max_episodes` caps forward to the underlying singular getter.
- **Exports:** `BatchItem` added to `src/spotify_scraper/__init__.py` imports and
  `__all__` (kept alphabetized). The six instance methods are auto-public.
- **Hermetic tests** mirroring the respx/fixture harness in
  `tests/unit/test_client_entities*.py`: happy path (ordered `ok` items), partial
  failure (one ID 404 → that item's `.error` is `NotFoundError`, batch does not
  raise, order preserved), `URLError` item (malformed input captured, batch
  continues), closed-client raises up front, cap forwarding, and — async only —
  a recording stub transport asserting in-flight `get` calls never exceed
  `max_concurrency` while still proving `>1` runs concurrently.

## Impact

- **New:** `src/spotify_scraper/batch.py`,
  `tests/unit/test_client_batch.py`, `tests/unit/test_client_batch_async.py`.
- **Edited:** `src/spotify_scraper/_sync/client.py` (imports + `_batch` + 6
  getters), `src/spotify_scraper/_async/client.py` (imports + `max_concurrency`
  ctor arg + `_semaphore` slot + `_batch` + 6 getters),
  `src/spotify_scraper/__init__.py` (export `BatchItem`).
- **No changes** to `transport.py`, `ratelimit.py`, `retry.py`, `pathfinder.py`,
  `urls.py`, `errors.py`, `auth/*`, `api/*`, `media/*`, or any model. The helpers
  only orchestrate existing I/O methods.
- **Default behavior unchanged:** existing single-entity getters are untouched.
  `test_parity.py` passes unchanged (Option A keeps signatures identical). One new
  runtime dependency: **none** (`asyncio`, `dataclasses`, `collections.abc` are
  stdlib).