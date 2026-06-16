# batch-helpers Specification

## Purpose

Plural get_*s helpers returning per-item, partial-failure-safe results with managed concurrency.

## Requirements
### Requirement: Plural convenience helpers on both clients

Both `SpotifyClient` and `AsyncSpotifyClient` SHALL provide six plural helpers —
`get_tracks`, `get_albums`, `get_artists`, `get_playlists`, `get_episodes`,
`get_shows` — that accept a `Sequence[str]` of URLs/URIs/IDs and apply the
client's configured rate limiting (and, on async, bounded concurrency) across all
inputs. The helpers SHALL add **no new endpoint and no new runtime dependency**;
they SHALL only orchestrate the existing single-entity getters.

#### Scenario: Many tracks in one call

- **WHEN** `client.get_tracks([id1, id2, id3])` is called with three valid IDs
- **THEN** three results are returned, each carrying the fetched `Track`, with no
  caller-written loop or throttling

#### Scenario: Pagination caps forward

- **WHEN** `get_playlists(values, max_tracks=25)` or
  `get_shows(values, max_episodes=10)` is called
- **THEN** each underlying `get_playlist`/`get_show` receives that cap

### Requirement: Sync/async signature parity

The six plural helpers SHALL have **byte-identical** public signatures across the
sync and async clients — identical parameter names, order, defaults, and
return-annotation text — differing only by `async def`/`await`. The
async-only concurrency control SHALL therefore be a **constructor argument**, not
a method parameter, so the parity test (`tests/unit/test_parity.py`) passes
without modification.

#### Scenario: Parity test stays green

- **WHEN** `test_data_methods_share_signatures` inspects the six plural helpers
- **THEN** `list(signature.parameters)` and the return annotation match between
  `SpotifyClient` and `AsyncSpotifyClient` for every one

#### Scenario: Concurrency is set at construction, not per call

- **WHEN** a caller wants to bound async concurrency
- **THEN** they pass `AsyncSpotifyClient(max_concurrency=N)`; no plural method
  accepts a `max_concurrency` argument on either client

### Requirement: Typed, ordered, per-item partial-failure result

Each plural helper SHALL return an ordered `Sequence[BatchItem[_T]]`,
index-aligned with the input sequence. `BatchItem` SHALL be a frozen, slotted,
generic dataclass carrying the echoed input `value`, a `result` (the model on
success) XOR an `error` (the captured exception on failure), an `ok` property,
and an `unwrap()` method that returns the model or re-raises the captured error.
A per-item failure SHALL NOT abort the batch.

#### Scenario: A 404 on one ID does not kill the batch

- **WHEN** one ID in `get_tracks([good, dead])` does not exist
- **THEN** the helper returns both items in input order; the dead item's `ok` is
  `False` and its `error` is a `NotFoundError`; the good item's `ok` is `True`;
  the call itself does not raise

#### Scenario: Invalid input is captured, not raised

- **WHEN** a malformed value (failing `urls.parse`) is included
- **THEN** its item carries a `URLError` in `error`, `ok` is `False`, and the
  remaining valid inputs are still fetched

#### Scenario: Ordered and index-aligned

- **WHEN** any plural helper returns
- **THEN** result `i` corresponds to input `i` for every index, on both clients

#### Scenario: unwrap re-raises the captured error

- **WHEN** `item.unwrap()` is called on a failed item
- **THEN** it re-raises the captured exception; on a successful item it returns
  the model

### Requirement: Capture boundary is the library error base

The plural helpers SHALL capture **only** `SpotifyScraperError` (and subclasses)
per item. Any non-library exception — including programming bugs,
`KeyboardInterrupt`, and `asyncio.CancelledError` — SHALL propagate and abort the
batch, so cancellation and real bugs are never silently swallowed.

#### Scenario: CancelledError propagates

- **WHEN** an in-flight async batch task is cancelled
- **THEN** the cancellation is not captured as a `BatchItem.error`; it propagates

#### Scenario: Closed client fails fast

- **WHEN** a plural helper is called on a closed client
- **THEN** it raises `SpotifyScraperError` up front, before fetching any item

### Requirement: Sync is sequential; async is bounded-concurrent

The sync helpers SHALL fetch sequentially on one thread; the per-host
`TokenBucket` already throttles each underlying request, so no additional
throttling is added. The async helpers SHALL run `asyncio.gather` over per-item
coroutines, each gated by a single per-client `asyncio.Semaphore(max_concurrency)`
(default a small safe value, e.g. 5), so the number of concurrent entity
pipelines — and thus open sockets and bucket-lock contention — is bounded while
the rate limiter still governs request rate.

#### Scenario: Async never exceeds max_concurrency

- **WHEN** `get_tracks` runs over many IDs on a client built with
  `max_concurrency=N`
- **THEN** the number of simultaneously in-flight entity fetches never exceeds
  `N`, while more than one runs concurrently (the semaphore bounds but does not
  serialize)

#### Scenario: Sync needs no extra throttling

- **WHEN** a sync plural helper runs over many IDs
- **THEN** each underlying request passes through the same per-host token bucket,
  so the batch is already rate-limited without threads or a semaphore

#### Scenario: max_concurrency is validated

- **WHEN** `AsyncSpotifyClient(max_concurrency=0)` is constructed
- **THEN** a `ValueError` is raised

