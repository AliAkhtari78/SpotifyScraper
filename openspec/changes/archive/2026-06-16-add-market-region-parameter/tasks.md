# Tasks: add-market-region-parameter

## 0. Live verification (BLOCKS the mechanism choice) — DONE

- [x] 0.1 Anonymous bearer probe (same bootstrap as get_track) confirms the
      pathfinder `market` variable is INERT: getTrack payload byte-identical for
      no_market = US = DE = JP = ZZ(invalid) = from_token = qqq=X(bogus control),
      all HTTP 200. searchDesktop/queryArtistOverview show the same (only random
      requestIds/CDN-host noise differs). => no GraphQL `market` variable.
- [x] 0.2 `Accept-Language: ja-JP` on getTrack changes ONLY display names
      (Rick Astley -> リック・アストリー); no playability/contentRating/availability/
      preview change. => Accept-Language is the language lever; not a market lever.
- [x] 0.3 Empty `locale` GraphQL variable is a no-op (queryArtistOverview
      locale in {"",en,ja,ja_JP,de} all "Rick Astley"; only the header changes it).
- [x] 0.4 No country surfaced in embed __NEXT_DATA__; /get_access_token=403,
      /api/token=400 anonymously => country is IP-bound, not settable. Conclusion:
      ship Accept-Language-backed `locale=`; scope out anonymous market/availability.

## 1. Validator (urls.py, raises URLError)

- [x] 1.1 In `src/spotify_scraper/urls.py` add `normalize_locale(value: str) -> str`:
      strip; accept a bare ISO-3166 alpha-2 (`[A-Za-z]{2}`) -> return upper-cased,
      OR a language-region tag (`[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*`) -> return as-is;
      else raise `URLError("Invalid locale {value!r}: expected an ISO-3166 alpha-2
      code (e.g. 'US') or a language tag (e.g. 'ja-JP').")`. Regex-only, no new dep.
- [x] 1.2 Add a module `_LOCALE_RE`/`_MARKET_RE` constant; keep the function
      I/O-free and `str -> str` (mypy --strict clean). Export-friendly (no `_`).

## 2. Per-client default (constructors)

- [x] 2.1 Add `"_locale"` to `__slots__` in both `_sync/client.py` and
      `_async/client.py`.
- [x] 2.2 Add keyword-only `locale: str | None = None` to both `__init__`
      signatures + docstrings. Store
      `self._locale = urls.normalize_locale(locale) if locale is not None else None`
      (raises URLError at construction for a bad default — fail fast).

## 3. Per-call override (getters + search)

- [x] 3.1 Add keyword-only `locale: str | None = None` to `get_track`,
      `get_album`, `get_artist`, `get_playlist`, `get_episode`, `get_show`,
      `search` on BOTH clients (identical signatures — test_parity.py enforces).
      Document in each docstring that it localizes display-name LANGUAGE only.
- [x] 3.2 In each method resolve once, before any I/O:
      `effective = urls.normalize_locale(locale) if locale is not None else self._locale`
      (per-call wins; invalid per-call code raises URLError before any request).

## 4. Thread the resolved locale to a per-request Accept-Language header

- [x] 4.1 Add `locale: str | None = None` param to the entity chain:
      `_get_entity`, `_fetch_union`, `_pathfinder_request`, `_paginate`,
      `_with_episodes` (both clients). Forward `effective` from each getter; the
      paginating getters (album/playlist/show) pass the SAME `effective` to both
      `_get_entity` and the follow-up `_paginate`/`_with_episodes` so every page
      uses one locale.
- [x] 4.2 Add `locale` param to the search chain: `_search_union`,
      `_search_request` (both clients); forward `effective` from `search`.
- [x] 4.3 In `_pathfinder_request` and `_search_request`, build the request
      headers as `{**pathfinder.auth_headers(token), **_lang_header(locale)}`
      where `_lang_header(locale)` returns `{"Accept-Language": locale}` when
      `locale` is not None else `{}`. (Caller-wins merge in `transport.get`
      overrides the default `Accept-Language: en`.) Also apply the same header to
      `_fetch_next_data` (the embed GET) so the tier-2 fallback localizes too.
- [x] 4.4 The TokenError retry blocks in `_fetch_union`/`_search_union` already
      forward `overrides`; forward `locale` identically on the second attempt.
- [x] 4.5 Do NOT touch `api/pathfinder.py` (no variable). Confirm
      `build_url`/`build_search_url` outputs are byte-identical to before.

## 5. Tests (hermetic by default)

- [x] 5.1 `tests/unit/test_urls.py`: `normalize_locale` happy paths
      (`"de"`->`"DE"`, `"GB"`->`"GB"`, `"ja-JP"`->`"ja-JP"`, `"en-US"`->`"en-US"`)
      and URLError on `""`, `"USA"`, `"u1"`, `"123"`, `"x_y"`.
- [x] 5.2 `tests/unit/test_client_locale.py` (respx, sync+async): with a fake
      transport capturing headers, assert the pathfinder (and embed) request
      carries `Accept-Language: <resolved>`; assert per-call overrides per-client;
      assert a bad `locale` raises URLError with NO HTTP issued at BOTH
      construction and call time; assert that omitting `locale` sends no
      per-request Accept-Language override (default `en` only); assert `search`
      carries the header too; parity.
- [x] 5.3 `tests/unit/test_parity.py` already enforces signature parity — confirm
      both facades gained identical `locale` kwargs (constructor + all 7 methods).
- [x] 5.4 `make type` (mypy --strict), `make lint`, `make test`, `make cov`
      (>=85%) all green.

## 6. Docs + honest scope

- [x] 6.1 In the `locale` spec (Requirement scenarios) and docstrings, state
      plainly: anonymous `locale=` localizes display-name LANGUAGE; it does NOT
      filter regional availability or vary preview URLs. The pathfinder `market`
      variable is inert (IP-bound token). True market/availability requires the
      authenticated Web API (out of scope).
- [x] 6.2 README/docs: short note + example
      `SpotifyClient(locale="ja-JP")` / `get_track(url, locale="de-DE")`.

## 7. Live verification (excluded from default run)

- [x] 7.1 `@pytest.mark.live` (`tests/live/`): `get_track(<known track>,
      locale="ja")` vs the default — assert at least one artist/display name
      differs (the proven-working effect) and the localized name is non-ASCII.
      Assert it runs with NO cookie.
- [x] 7.2 `@pytest.mark.live` negative-scope guard: assert that two locales return
      the SAME `playability`/availability-shaped fields (documents that locale is
      language-only, not market) — keeps the limitation honest under `make live`.

## 8. Review fixes (locale-vs-market decision: language-only / honest)

- [x] 8.1 `normalize_locale` reframed as a BCP-47 **language** tag: accepts bare
      language subtags (2-3 letters, lower-cased) and language-region tags; drops
      the "ISO-3166 alpha-2 country code"/upper-case/`US` framing. Now accepts
      bare 3-letter language codes (e.g. `por`); error message says "language tag".
- [x] 8.2 Client `__init__` docstrings reframed to "BCP-47 language tag" (no
      "ISO-3166 country code"); README "Localized display names" reframed.
- [x] 8.3 Tests: bare subtag lower-cased on the wire (sync + async); bare 3-letter
      language accepted; multi-page pagination carries `Accept-Language` on page 2;
      `search` invalid-locale async parity; updated accept/reject vectors.
- [x] 8.4 Docs: new `guides/localization.md` (language-only, not market) + nav;
      index roadmap (3.4 localization shipped) + success admonition; CHANGELOG;
      spec reframed to language-only (lower-case normalization).
