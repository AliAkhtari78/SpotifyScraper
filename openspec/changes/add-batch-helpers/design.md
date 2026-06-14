# Design: add-batch-helpers

## Context

Issue #132. The single-entity getters already route every request through the
per-host `TokenBucket` (`http/ratelimit.py`), so the throttling primitive exists.
What is missing is a batch-granularity surface that (a) does not let one bad ID
kill the run and (b) on async, does not fan out unboundedly. This is pure
ergonomics: no new endpoint, no new dependency, no parser/model/transport change.

## Goals / Non-goals

- **Goal:** plural `get_*s(values)` on both clients with identical signatures,
  ordered per-item results, captured partial failures, and bounded async
  concurrency that composes with the rate limiter.
- **Non-goal:** batching authenticated features (`get_lyrics`, and any future
  transcript) — they are cookie-gated and a different failure/auth story
  (see Open Questions). No retry/backoff changes (the existing `RetryPolicy`
  already governs each request). No streaming/async-iterator API.

## Decision 1 — Partial-failure model: `BatchItem[_T]` (the load-bearing choice)

A batch over real-world IDs WILL contain dead/region-locked entries
(`NotFoundError`) and typos (`URLError`). Raising on the first one is useless for
bulk work. The chosen model is a frozen, slotted, **generic** result wrapper in a
new sans-io module `src/spotify_scraper/batch.py`:

```python
@dataclass(frozen=True, slots=True)
class BatchItem(Generic[_T]):
    value: str                      # the input, echoed back
    result: _T | None = None        # model on success
    error: Exception | None = None  # captured SpotifyScraperError on failure

    @property
    def ok(self) -> bool: ...
    def unwrap(self) -> _T: ...      # model or re-raise
```

**Why this over alternatives:**

- *Raise-on-first-error* — rejected: defeats the purpose of a batch.
- *`return_exceptions=True` raw list of `model | Exception`* — rejected: untyped
  union, loses which input produced which result once values are deduped/reordered
  in user code, and forces `isinstance` checks everywhere. `BatchItem` echoes
  `value` and is typed `Sequence[BatchItem[Track]]`.
- *Separate `(results, errors)` tuple* — rejected: loses input order alignment
  and forces callers to re-correlate.
- *A `BatchResult` collection wrapper with `.ok`/`.errors` helpers* — deferred:
  `Sequence[BatchItem[_T]]` already gives ordering + per-item outcome and is the
  minimal honest type; a convenience collection can be layered later without a
  breaking change (it would wrap the same items).

`unwrap()` gives the "simple list when all succeed" ergonomic the prompt asks for:
`[item.unwrap() for item in client.get_tracks(ids)]` raises on the first failure
if the caller wants all-or-nothing, or they inspect `.ok` for graceful handling.

**Capture boundary = `SpotifyScraperError`.** This is the base of every
library error (`errors.py`): `NotFoundError`, `URLError`, `NetworkError`/
`RateLimitedError`, `ParsingError`, `TokenError`, `AuthenticationError`,
`MediaError`. Catching exactly this base means library failures are captured per
item while real bugs, `KeyboardInterrupt`, and `asyncio.CancelledError` (none of
which subclass `SpotifyScraperError`) propagate and abort the batch — the correct
behavior for cancellation and programming errors. The field is typed `Exception |
None` (honest about what a dataclass field could hold) even though only
`SpotifyScraperError` is ever stored.

`BatchItem` is a control wrapper, not Spotify data, so it carries **no
`to_dict()`** — CLAUDE.md's JSON-safe rule targets entity models.

## Decision 2 — `max_concurrency` is a constructor arg, not a method param (Option A)

`tests/unit/test_parity.py::test_data_methods_share_signatures` compares
`list(signature.parameters)` and the `return_annotation` string for every shared
public method. If `max_concurrency` were a method parameter, it would have to
appear (inertly) on the sync helpers too, or parity breaks.

**Chosen: Option A** — `max_concurrency: int = 5` on `AsyncSpotifyClient.__init__`
only; it builds and stores a single `asyncio.Semaphore`. The sync client has no
such concept (it is sequential). The six plural signatures stay byte-identical
across clients, so parity passes with **no test change**.

*Option B* (per-call `*, max_concurrency: int = 8` on both, a no-op on sync) was
rejected: it adds a dead parameter to the entire sync API surface just to satisfy
the signature comparison. Construction-time configuration matches the existing
pattern (`rate_limit`, `retry`, `host_rate_limits` are all constructor-set).

Default `5` deliberately equals the default `RateLimit.burst=5`, so concurrency
never structurally exceeds burst capacity; the bucket remains the rate limiter and
the semaphore the fan-out limiter, and the two compose without one masking the
other. `max_concurrency >= 1` is validated in `__init__` (mirroring
`RateLimit.__post_init__`).

## Decision 3 — Sync sequential, async semaphore-bounded `gather`

**Sync** (`_sync/client.py`):

```python
def _batch(self, values, fetch):
    self._ensure_open()                       # fail fast if closed
    out = []
    for value in values:
        try:    out.append(BatchItem(value, result=fetch(value)))
        except SpotifyScraperError as exc:
                out.append(BatchItem(value, error=exc))
    return out
```

No threads, no semaphore: each `fetch(value)` (a single-entity getter) routes
every underlying request through the same per-host `TokenBucket`, so a sequential
loop is already rate-limited. Each inner getter also re-checks `_ensure_open` via
`_resolve`, so a mid-batch `close()` is still safe; the up-front check just fails
fast on an already-closed client.

**Async** (`_async/client.py`):

```python
async def _batch(self, values, fetch):
    self._ensure_open()
    async def one(value):
        async with self._semaphore:           # bounded fan-out
            try:    return BatchItem(value, result=await fetch(value))
            except SpotifyScraperError as exc:
                    return BatchItem(value, error=exc)
    return list(await asyncio.gather(*(one(v) for v in values)))
```

- `asyncio.Semaphore(max_concurrency)` caps concurrent entity pipelines →
  bounds open sockets and bucket-lock contention. The `AsyncTokenBucket` still
  enforces request *rate* underneath. Semaphore = concurrency, bucket = rate;
  they compose.
- `gather` with default `return_exceptions=False`: every task catches its own
  `SpotifyScraperError`, so `gather` never sees a library exception. A non-library
  escape (a bug) cancels siblings and re-raises — correct. `CancelledError` is not
  a `SpotifyScraperError`, so it is never swallowed.
- `gather` returns positionally → results are index-aligned with `values`,
  matching the sync contract for free.
- A single shared per-client semaphore bounds concurrency **across overlapping
  batch calls** too, which is what you want for one IP. (Per-call isolation was
  considered and rejected as surprising — a second concurrent batch could double
  the real fan-out.)

`_semaphore` is added to the async client's `__slots__`.

The plural getters are six thin wrappers each delegating to `_batch` with the
matching single-entity getter (or a `lambda` forwarding the `max_tracks`/
`max_episodes` cap).

## Types / mypy --strict

- `BatchItem(Generic[_T])`; helpers return `Sequence[BatchItem[Track]]` etc.
- `fetch` is `Callable[[str], _T]` (sync) / `Callable[[str], Awaitable[_T]]`
  (async). Reuse the module-level `_T = TypeVar("_T")` already present in both
  clients; declare a local `_T` in `batch.py`.
- New imports: `Sequence` (both), `Awaitable` + `import asyncio` (async),
  `from spotify_scraper.batch import BatchItem` (both), `BatchItem` export in the
  package `__init__`.

## Testing strategy (hermetic)

- Reuse the respx + fixture harness from `test_client_entities*.py` for happy
  path, partial failure (one ID → 404 → captured `NotFoundError`, order
  preserved, no raise), `URLError` item, closed-client fail-fast, and cap
  forwarding.
- Async-only bounded-concurrency test uses a **recording stub `AsyncTransport`**
  (the `_AsyncStubTransport` pattern from `tests/unit/http/test_cache.py`):
  increment an in-flight counter on `get` entry, coordinate overlap with an
  `asyncio.Event`/barrier (no real sleeps → deterministic), record max in-flight,
  assert `1 < max <= max_concurrency`.
- `test_parity.py` runs unchanged and must stay green (Option A guarantees it).

## Risks

- **Memory:** all `BatchItem`s are held until the batch completes (no streaming).
  Acceptable for the convenience use case; an async-iterator variant is a future,
  non-breaking addition.
- **Shared semaphore semantics:** overlapping batches share one budget. Documented
  as intentional (one IP, one fan-out budget).