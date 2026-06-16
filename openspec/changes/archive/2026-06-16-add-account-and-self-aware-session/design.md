# Design: add-account-and-self-aware-session

## Endpoint (CONFIRMED live, 2026-06-15, real Premium account)

`GET https://spclient.wg.spotify.com/melody/v1/product_state` with headers
`Authorization: Bearer <cookie-derived web-player token>` and
`app-platform: WebPlayer` — the SAME host and token as color-lyrics and
transcripts. Returns `200 application/json`. The body is a **flat** object with
hyphenated keys:

```json
{"product": "premium", "catalogue": "premium", "country": "CA",
 "on-demand": "...", "ads": "...", "is-standalone-audiobooks": "...",
 "preferred-locale": "...", "selected-language": "...",
 "multiuserplan-current-size": "...", "multiuserplan-member-type": "..."}
```

`api.spotify.com/v1/me` is BLOCKED for this token (429) — `product_state` is the
source. Host/path live ONLY in `api/account.py` (the lyrics/transcript/pathfinder
isolation discipline). Because the body is flat there is **no envelope-decode
step** — `get_account` is simpler than transcripts.

## Why `get_account` is the simplest member of the get_* family

The lyrics/transcript flow is a 4-layer sandwich: endpoint module → pure parser →
frozen model → thin client facade. `get_account` mirrors it with three
simplifications: (1) no `_resolve`/entity ID (`product_state_url()` takes no
argument); (2) no `decode_envelope` (flat body); (3) no per-entity
`NotFoundError` (there is no entity that can be absent — only auth can fail). The
client control flow is otherwise identical to `get_lyrics`: shared
`self._cookie_provider()`, `token()`, try `_fetch_account(token)`, on
`AuthenticationError` `provider.invalidate()` and retry once.

## Account model

`Account(ModelBase)`, frozen + slotted, fields `product`, `catalogue`,
`country`, `on_demand`, `preferred_locale`, `selected_language`, all `str|None`/
`bool|None` defaulting `None` (CLAUDE.md's tier-1-only `| None` rule maps to
"fields Spotify may omit are `| None`"; the flat body makes every field
independently optional). `is_premium` is a **derived `@property`**
(`product == "premium"`), which on a `slots=True` frozen dataclass does not
collide with a field and is excluded from `dataclasses.fields()` — so
`to_dict()` (and `from_dict` round-trip) stay a pure wire mirror with no
redundant serialized boolean. The alternative (a real `is_premium` field set by
the parser) was rejected to keep one source of truth.

## Parser

`parse_account(payload)` is the one place the hyphen→snake mapping lives
(`on-demand`→`on_demand`, `preferred-locale`→`preferred_locale`,
`selected-language`→`selected_language`). It reuses `_optional_str` for string
fields and a new `_account_bool` for `on-demand`. `_account_bool` is tolerant
because product_state historically sends booleans as strings: `True`/`"1"`/
`"true"`→`True`, `False`/`"0"`/`"false"`→`False` (case-insensitive), anything
else→`None`. The plain `_optional_bool` would mis-read `"1"` as `None`, hence the
dedicated helper. No `ParsingError` shape gate — a flat/partial/empty body yields
an `Account` of `| None`s; only a non-JSON HTTP body raises (in `_fetch_account`).

## SessionInfo and self-aware session

`SessionInfo` is a frozen, slotted, **cookie-free** value object (`exists`,
`valid`, `saved_at_ms`, `sp_dc_expires_ms`, `reason`). It is NOT a `ModelBase`:
it lives in `auth/` (not `models/`), carries a validity verdict rather than wire
data, and matches how `Session` itself is a plain frozen dataclass there.
`session_info()` catches `SessionError` from `load_session` and converts it into
`exists`/`valid` flags plus the existing cookie-free hint as `reason`, so callers
branch on flags instead of catching exceptions. Validity is purely local: file
exists + securely permissioned (POSIX) + parseable + not past
`sp_dc_expires_ms` (when known). `SessionStore.info()`/`has_session()` delegate
to the file or keyring backend; `keyring_info()` mirrors `load_from_keyring`,
degrading to file-backed metadata when the OS keyring is absent.

`login(reuse=True)` checks `backend.has_session(...)` first; on a hit it loads the
session, sets `self._cookies`, resets `self._cookie_tokens = None`, and returns —
the lazy `from spotify_scraper.browser import capture_sp_dc[_async]` moves INSIDE
the non-reuse branch, so reusing a session never needs Playwright. Default `True`
is the requested auto-skip; it is safe because `has_session()` is `True` only for
a secure, parseable, unexpired session. Validity is a *local* check, so a
Spotify-side revocation still skips the browser and surfaces on the first
authenticated call as `AuthenticationError` (the existing 401 contract) — this is
documented, not a bug.

## Cookie-expiry capture (the days-remaining gap)

Today `capture_sp_dc` returns only the cookie string; `_extract_sp_dc`
(`browser/login.py`) discards the Playwright cookie's `expires` field, so
`login()` always calls `save_session(..., sp_dc_expires_ms=None)` and every saved
session has an unknown expiry. `SessionInfo.sp_dc_expires_ms` is therefore `None`
for current sessions, and "days remaining" cannot be computed. The store already
accepts `sp_dc_expires_ms`, so making days-remaining real is a small, **optional**
add: surface the cookie `expires` (epoch seconds → ms) from `_extract_sp_dc` and
thread it into the `login()` save call. The session helpers are written to work
either way — they simply omit days-remaining when expiry is unknown. Carried as
an open question so the maintainer decides whether to touch the browser module in
this change.

## Deferred: auto-adopt country as default locale/market

The optional smart touch (use `account.country` as a default market/locale when
none is set) is deferred. There is no market/locale machinery on the clients
today, and a separate in-flight branch (`add-market-region-parameter`) owns that
surface. Adding an implicit default here would risk a merge collision and a
surprising silent behavior change. Recommendation: revisit as a follow-up once
the market parameter lands, and even then keep it explicit/opt-in.

## Open questions (carry to live verification)

- Exact product-state key set and casing, and the wire type of `on-demand`
  (string `"1"` vs JSON `true`) — gates `_account_bool` only; the parser is
  tolerant.
- Whether to surface cookie expiry from the capture path so days-remaining is
  real, or ship session-awareness with expiry-unknown for now.
- Whether `SessionInfo` and the client `session_info()` classmethod are public
  API (export from top-level `__init__`) or internal-only (reachable via
  `client.session_info()`).
- Whether to add the CLI `session`/`status` command and `--reuse/--no-reuse` in
  this change or a follow-up.