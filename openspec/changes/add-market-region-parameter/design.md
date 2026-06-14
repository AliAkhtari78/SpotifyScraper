# Design: add-market-region-parameter

## The decision the live probe forced

Issue #130 assumes a `market=` that "threads into the existing request builders
and the `market=from_token` path." A decisive anonymous probe (2026-06-14)
disproves the GraphQL-variable mechanism: on `getTrack`, the payload is
byte-identical (hash `4751d64a...`) for `no_market = US = DE = JP =
ZZ(invalid country) = from_token = qqq=X`. The bogus-`qqq` control proves
persisted queries silently discard unknown variables, so `market` "not erroring"
is meaningless — it is dropped. Same on `searchDesktop` and
`queryArtistOverview`. Therefore a `market=` routed as a pathfinder variable
would be a **no-op kwarg**, which the task explicitly forbids.

The probe also identifies the one anonymous lever that *does* change responses:
the **`Accept-Language` HTTP header**. `getTrack` with `Accept-Language: ja-JP`
changed exactly the display names (transliterations) and nothing else — no
availability, playability, or preview change. The pre-existing empty `locale`
GraphQL variable (`pathfinder.py:48,53`) is independently confirmed inert.
Anonymous country is IP-bound (no country in the embed `__NEXT_DATA__`;
`/get_access_token` 403 and `/api/token` 400 anonymously), so true market control
would need a region-pinned proxy — out of scope.

**Design conclusion:** implement the proven-working capability (display-language
localization) under an honest name, `locale=`, threaded as `Accept-Language`;
deliver the requested ISO-3166 alpha-2 validator (`URLError` on bad code) as
`urls.normalize_locale`; and explicitly scope out + document anonymous
market/availability.

## Mechanism: header, not variable

`api/pathfinder.py` is untouched — no `market`/`locale` variable is injected, so
every pathfinder URL stays byte-identical and all URL-shape tests stay green
(this also keeps the hash table the sole concern of that module). Instead the
resolved locale becomes a per-request header:

- A tiny private `_lang_header(locale) -> {"Accept-Language": locale}` (or `{}`
  when `None`) is merged after `pathfinder.auth_headers(token)` in
  `_pathfinder_request`/`_search_request`, and applied to the embed GET in
  `_fetch_next_data` so the tier-2 fallback localizes too.
- `transport.get` already merges `{**self._headers, **(headers or {})}` with the
  caller winning, so a per-request `Accept-Language` cleanly overrides the
  transport default (`headers.py:34` = `Accept-Language: en`).

## Validation home and shape

`normalize_locale` lives in `urls.py` beside `parse` (the established home for
input classifiers that raise `URLError`) and is exported for both clients. It is
regex-only (no `pycountry`; the one-dependency rule forbids it): a bare
`[A-Za-z]{2}` country code is upper-cased; a `[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*`
language-region tag passes through; anything else raises `URLError`. It is
`str -> str`, I/O-free, mypy --strict clean.

## Threading (mirrors existing pagination-option layering)

`locale` resolves once per public call
(`effective = normalize_locale(locale) if locale is not None else self._locale`),
exactly how `max_tracks`/`max_episodes` already layer per-call over a default,
and is forwarded down the SAME private chain the pagination overrides use:

- Entities: getter -> `_get_entity` -> `_fetch_union` -> `_pathfinder_request`;
  plus `_paginate` and `_with_episodes` (which re-enter `_fetch_union`). The
  paginating getters pass one `effective` into both the first fetch and the
  follow-up pages so a single call uses one consistent locale on every page.
- Search: `search` -> `_search_union` -> `_search_request`.
- The `except TokenError: invalidate -> retry-once` blocks already forward
  `overrides`; they forward `locale` the same way on the second attempt.

Validation happens at exactly two boundaries (constructor + each call), both
raising `URLError` before any I/O; the private layer receives only trusted,
already-normalized values.

## Why not parameterize lyrics

`get_lyrics` is the authenticated cookie path; its `market=from_token`
(`lyrics.py:11`) is a real Web-API market token that genuinely filters, but it is
out of #130's anonymous scope and is left untouched to keep this change minimal
and isolated.

## Honesty in the public contract

The spec, docstrings, and README state that anonymous `locale=` localizes
display-name *language* only — not availability or preview URLs — and that the
pathfinder `market` variable is inert. A `@pytest.mark.live` negative-scope test
asserts two locales leave availability/playability unchanged, guarding the
limitation from silent regression. This prevents the feature from being mis-sold
as region/availability control it cannot deliver anonymously.
