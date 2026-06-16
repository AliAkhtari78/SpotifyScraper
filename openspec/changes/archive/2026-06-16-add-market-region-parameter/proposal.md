# Proposal: add-market-region-parameter

> **Status: targets a v3.x point release.** Addresses issue #130
> (market/region for localized metadata & availability). **A live probe forced an
> honest scope:** Spotify's anonymous pathfinder silently DISCARDS a `market`
> variable, so a `market=` kwarg routed as a GraphQL variable would be a no-op.
> This proposal ships the lever the probe PROVED works — `Accept-Language`
> (display-language localization) — as an optional, validated `locale=`
> parameter, and explicitly scopes out (and documents) anonymous
> availability/region filtering, which is not achievable without the
> authenticated Web API.

## Why

Issue #130 asks for an optional `market=` (ISO-3166 country) at the client and/or
per call, "Spotify varies availability, names, and preview URLs by market." A
decisive live anonymous probe (2026-06-14) shows that, on the anonymous two-tier
ladder this library uses, **only display-name *language* is controllable, and
only via the `Accept-Language` HTTP header** — not availability, not preview
URLs, not via any GraphQL variable:

- The pathfinder `market` variable is **inert**: `getTrack` returns a
  byte-identical payload for `no_market = US = DE = JP = ZZ(invalid) = from_token
  = qqq=X(bogus)` (all HTTP 200). Persisted queries accept and discard unknown
  variables; the bogus-`qqq` control proves "it doesn't error" means nothing.
- `Accept-Language: ja-JP` **does** change the response — but every changed leaf
  is a transliterated display name (Rick Astley -> リック・アストリー); zero
  `playability`/`contentRating`/availability/preview change. Language lever, not
  market lever.
- The existing empty `locale` GraphQL variable (`pathfinder.py:48,53`) is a no-op
  confirmed on `queryArtistOverview`; localization is header-driven.
- Anonymous country is **IP-bound**: no country field is surfaced in the embed
  `__NEXT_DATA__`, and the country-bearing endpoints are blocked anonymously
  (`/get_access_token` -> 403, `/api/token` -> 400). Real `market=`/`from_token`
  availability filtering lives only on the authenticated `api.spotify.com`, which
  the anonymous ladder does not touch.

Shipping a `market=` pathfinder variable would therefore be a silent no-op — the
task explicitly forbids that. We instead ship the proven-working capability under
an honest name and document the limitation.

## What Changes

- **`urls.py`** gains a pure `normalize_locale(value: str) -> str` validator
  (regex-only, zero new deps) that accepts a bare ISO-3166 alpha-2 code
  (upper-cased, e.g. `"de"` -> `"DE"`) or a full language-region tag
  (`"ja-JP"`, `"en-US"`, passed through), and raises **`URLError`** on bad input
  (`""`, `"USA"`, `"u1"`, `"123"`). This is the "market (ISO-3166 alpha-2,
  validated -> URLError on bad code)" validator the task requires; what it sets
  anonymously is the display language, not availability.
- **Both clients** gain an optional, keyword-only `locale: str | None = None`:
  a per-client default in `__init__` (validated once at construction; stored in a
  new `_locale` slot) **and** a per-call override on every getter and `search`
  (per-call wins). Resolution is
  `urls.normalize_locale(locale) if locale is not None else self._locale`,
  mirroring how `max_tracks`/`max_episodes` layer per-call over default.
- **Threading is header-only.** The resolved locale flows down the private
  request chain (`_get_entity`/`_fetch_union`/`_pathfinder_request`/`_paginate`/
  `_with_episodes` for entities; `_search_union`/`_search_request` for search) and
  is applied as a per-request **`Accept-Language`** header merged over the
  transport default (`headers.py:34`, `Accept-Language: en`; caller wins in
  `transport.get`). **No pathfinder variable and no `api/pathfinder.py` change** —
  pathfinder URLs stay byte-identical, all existing URL-shape tests stay green.
- **`get_lyrics` is unchanged** (authenticated path; its hardcoded
  `market=from_token` in `lyrics.py:11` is out of scope).
- **Docs + spec explicitly state the limitation:** anonymous `locale=` localizes
  *display names* (language); it does **not** filter regional *availability* or
  vary *preview URLs* — that requires the authenticated Web API, which this
  library's anonymous ladder does not implement. The pathfinder `market` variable
  is documented as inert so no future contributor models it as a variable.

## Impact

- New: `urls.normalize_locale` + its unit tests; `_locale` slot + `locale=`
  kwargs on both clients (constructor, six getters, `search`); a per-request
  `Accept-Language` header threaded through the private request layer; client
  unit tests (per-call-overrides-per-client, URLError-before-HTTP at both
  boundaries, header carried on the wire) sync + async; a `@pytest.mark.live`
  smoke test asserting a localized display name differs between two locales.
- Unchanged: `api/pathfinder.py` (no variable, hashes untouched), `errors.py`
  (reuses `URLError`), every model and parser, `auth/`, `media/`, lyrics.
- No new runtime dependency. No change to any existing method's behavior when
  `locale` is omitted. `test_parity.py` keeps both facades' signatures identical.
- **Honesty gate:** the spec and README/docs record that anonymous market
  (availability/region) is NOT supported and why (IP-bound token + inert
  variable), so the feature is not mis-sold.
