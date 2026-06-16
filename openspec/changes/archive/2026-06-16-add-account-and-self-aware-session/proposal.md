# Proposal: add-account-and-self-aware-session

> **Status: targets v3.5.** Stacks directly on `add-browser-login` (HEAD of the
> v3 stack) and reuses its shipped pieces **unchanged**: the `SessionStore`
> file/keyring backends, `Session`/`load_session`/`save_session`/`clear_session`,
> `default_session_path`/`_resolve_path`/`_default_now_ms`, and the cookie
> plumbing from `add-cookie-auth-lyrics`/`add-podcast-transcripts` (the
> `_cookie_tokens` slot, the `_cookie_provider()` builder, `CookieTokenProvider`/
> `AsyncCookieTokenProvider`, `load_sp_dc`). **MUST branch off `add-browser-login`**
> (or land after it merges) — `session_info`/`has_saved_session` and
> `login(reuse=...)` build on the session store that change introduces.

## Why

The library can already authenticate with an `sp_dc` cookie (lyrics, transcripts)
and acquire/persist that cookie via browser login. Two gaps remain that the
maintainer hits on every authenticated run:

1. **The client cannot answer "who am I?"** There is no way to learn the
   logged-in account's product tier (Premium vs Free), country, catalogue, or
   locale. Callers need this to branch (e.g. skip Premium-only features, pick a
   market) and to confirm a cookie actually authenticated a *real* account.
   Spotify's web player reads this from
   `GET https://spclient.wg.spotify.com/melody/v1/product_state` — the **same
   authenticated host and cookie-derived token** as color-lyrics and
   transcripts, confirmed live (2026-06-15) against a real Premium account.
   (`api.spotify.com/v1/me` is **blocked** for this token — 429 — so
   `product_state` is the source.)

2. **The session is not self-aware.** `login()` always opens a headed browser,
   even when a perfectly good saved session already exists, and there is no
   cookie-free way to ask "is there a usable saved session, and how long is it
   good for?" Headless-server and CI flows want a `login(reuse=True)` that
   auto-skips the browser when a valid saved session is present, plus a
   `session_info()`/`has_saved_session` introspection helper that **never
   exposes the cookie**.

Both are small, reuse the hardened machinery with no new auth code and no new
dependency, and mirror the established `get_*` 4-layer pattern (endpoint module
→ pure parser → frozen model → thin client facade) exactly.

## What Changes

### Feature 1 — `get_account()` / `is_premium()`

- **New sans-io `api/account.py`**: `product_state_url()` (no path params — flat
  body) and `auth_headers(token)`, with the endpoint host/path as a
  module-private constant living in **exactly one place** (the lyrics/transcript/
  pathfinder isolation discipline).
- **New `models/account.py`**: frozen, slotted `Account(ModelBase)` mirroring the
  flat product-state body with snake_case fields, every field `| None`
  (Spotify may omit any), and a derived `is_premium` **property** (`product ==
  "premium"`) that is excluded from `to_dict()` so the dict stays a faithful
  wire mirror.
- **New `parse_account(payload)` in `api/parse_entities.py`**: pure, I/O-free,
  the one place the hyphen→snake key mapping (`on-demand`, `preferred-locale`,
  `selected-language`) lives; flat body so every field is independently optional
  (no `ParsingError` shape gate). A tolerant `_account_bool` helper coerces
  product_state's stringy booleans (`"1"`/`"true"`/`True`).
- **New `get_account()` + `is_premium()` + `_fetch_account()` on both clients**
  (sync + async): routed through the **shared** `_cookie_provider()`, with the
  same no-cookie→`AuthenticationError`-without-network and 401→invalidate+retry-
  once classification lyrics/transcripts use. No `_resolve`, no entity ID, no
  envelope decode (the body is flat), no per-entity `NotFoundError`.
- **`Account` exported** from `spotify_scraper.models` and the top-level package.

### Feature 2 — Self-aware session (`session_info` / `has_saved_session` / `login(reuse=True)`)

- **New `SessionInfo` value object + `session_info()`/`has_saved_session()` in
  `auth/session.py`** (stdlib-only): a frozen, slotted, **cookie-free** snapshot
  (`exists`, `valid`, `saved_at_ms`, `sp_dc_expires_ms`, `reason`) safe to print/
  log. `session_info` never raises for the common missing/corrupt/insecure/
  expired cases — it reports them as flags by catching `SessionError` from
  `load_session` and surfacing the existing cookie-free hint as `reason`. Validity
  = exists + securely permissioned + parseable + not past `sp_dc_expires_ms`
  (when known). `SessionStore.info()`/`has_session()` delegate to the file or
  keyring backend; `auth/session_keyring.py` gains a parallel `keyring_info()`.
- **`login(reuse=True default)` auto-skip on both clients**: when `reuse` is set
  and a valid saved session exists, load it and wire the cookie in **without
  opening the browser** (the lazy Playwright import moves inside the non-reuse
  branch, strengthening the "import never needs Playwright" guarantee). Default
  `True` is the requested behavior; it is safe because `has_session()` only
  returns `True` for a secure, parseable, unexpired session.
- **Optional `session_info()` classmethod on both clients** so callers introspect
  without reaching into `auth.session`. `SessionInfo` exported only if surfaced
  publicly.
- **Optional CLI `session`/`status` command** printing the `SessionInfo` fields
  (exists/valid/expiry) — **never the cookie** — and a `--reuse/--no-reuse` flag
  wired into the `login` command.

### Cookie-expiry capture (gates meaningful "days remaining")

Today `capture_sp_dc` returns only the cookie string; the Playwright cookie's
`expires` field is discarded, so every saved session has `sp_dc_expires_ms=None`
and `SessionInfo` can report existence/validity but **not** days remaining. This
change **optionally** surfaces the cookie expiry from the capture path (an
`_extract_sp_dc` tweak + threading it into the `save_session(..., sp_dc_expires_ms=)`
call already supported by the store) so days-remaining becomes real. Carried as
an open question — see below; the session helpers work either way and simply
omit days-remaining when expiry is unknown.

### Deferred (NOT in this change)

The optional "auto-adopt account country as a default locale/market" smart touch
is **deferred**. There is no market/locale machinery on the clients today, and a
separate in-flight branch (`add-market-region-parameter`) owns that surface;
adding it here risks a collision and a surprising implicit-default behavior.
Noted in design.md and open questions for a follow-up once the market parameter
lands.

## Impact

- **New**: `api/account.py`, `models/account.py`, `parse_account` +
  `_account_bool`, `get_account`/`is_premium`/`_fetch_account` on both clients,
  `SessionInfo` + `session_info`/`has_saved_session` + `SessionStore.info`/
  `has_session` + `keyring_info`, `login(reuse=...)`, an optional client
  `session_info` classmethod and CLI `session`/`status` command, exports.
- **Reused unchanged**: `auth/cookies.py` (`load_sp_dc`, `CookieTokenProvider`,
  `AsyncCookieTokenProvider`), the `_cookie_tokens` slot + `_cookie_provider()`
  builder, `models/base.py`, `errors.py`, `SessionStore`/`load_session`/
  `save_session`/`clear_session`, `browser/playwright.py`.
- **Behavior change**: `login()` no longer always opens a browser — with the new
  default `reuse=True` it skips the browser when a valid saved session exists.
  This is the explicitly requested auto-skip. Existing `login(save=...)` tests
  stay green because they run with no pre-saved session (capture still fires).
- **One live verification item gates only `parse_account` field coverage**: the
  exact set/casing of product-state keys and the wire type of `on-demand`
  (string `"1"` vs JSON `true`) is confirmed from a maintainer capture; the
  parser is written tolerant so only `parse_account`/`_account_bool` change if a
  key differs. The live `tests/live/test_account.py` is gated on `SPOTIFY_SP_DC`
  and skipped without it.
- **No new dependency**: account path uses only `httpx` via the existing
  transport; session helpers are stdlib-only. `mypy --strict` and the
  one-runtime-dependency rule hold.