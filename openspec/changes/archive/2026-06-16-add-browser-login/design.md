# Design: add-browser-login

## Branch base (binding)

This change MUST build on `add-podcast-transcripts` (current HEAD), where the
`_lyrics_*`→`_cookie_*` rename is already committed: the slot is `_cookie_tokens`,
the builder is `_cookie_provider()`, the cookie module is `auth/cookies.py`
(`load_sp_dc`, `CookieTokenProvider`, `AsyncCookieTokenProvider`). Building on
`master` would collide with that rename.

## Why browser-assisted, not automated credentials

`accounts.spotify.com` is gated behind bot detection, hCaptcha/reCAPTCHA, and
frequent 2FA/OTP. A headless username/password POST is fragile, breaks without
notice, and would force the library to handle and (worse) persist a plaintext
password — violating the project's own security posture. The browser-assisted flow
produces the identical artifact (a valid `sp_dc` cookie) with the user driving a
real, headed browser. The login MUST be user-driven and headed.

## Capture mechanism: poll cookies, do not wait for a URL

Spotify's post-login redirect target varies (premium upsell, region interstitial,
app picker) and 2FA makes timing unpredictable, so `wait_for_url` is brittle.
Playwright has no built-in "wait for cookie". The helper therefore polls
`context.cookies("https://open.spotify.com/")` on a ~1s interval bounded by a
`time.monotonic()` deadline (`asyncio.sleep` in the async twin), returning the
first non-empty `sp_dc` value. `headless=False` is hard-coded (this is the headed
login; any headless knob is ignored). All Playwright errors are caught and
re-raised as `AuthenticationError(_NO_COOKIE_HINT)` — never leaking the cookie or a
stack. The browser/context is always torn down in a `finally`.

### Profile handling (v1 decision)

Use a throwaway `tempfile.mkdtemp()` profile, extract `sp_dc`, then delete it
(`shutil.rmtree`), so there is a single source-of-truth secret store (our 0600 file
or the keyring) rather than a second on-disk secret in a kept Chromium profile. A
kept persistent profile (`launch_persistent_context`) is a possible future opt-in;
flagged in open questions.

## sp_dc vs. token lifetimes

`sp_dc` lives roughly a year; the derived web-player access token is short-lived
(~1h). We persist only the durable secret (`sp_dc`) plus its cookie `expires` (as
`sp_dc_expires_ms`, optional) and let the existing `CookieTokenProvider` re-derive
and cache the short-lived token on demand. The session store deliberately does NOT
cache the access token: the token machinery already lives in `auth/cookies.py` and
re-exchanges within `EXPIRY_SKEW_MS` of expiry. Logging out in Spotify invalidates
`sp_dc` server-side, so docs and the close path tell users to close the window
WITHOUT clicking "Log out".

## Session store (sans-io, stdlib only)

`auth/session.py` depends on nothing beyond stdlib, so it is importable without any
extra and is fully hermetic.

- **Config dir** is hand-rolled (no `platformdirs`): `SPOTIFYSCRAPER_CONFIG_DIR` →
  `XDG_CONFIG_HOME` → `sys.platform` default (`~/.config`, `~/Library/Application
  Support`, `%APPDATA%`). This mirrors the existing `SPOTIFY_SP_DC` env convention.
- **Atomic, leak-free write**: `tempfile.mkstemp(dir=...)` yields a 0600 file from
  the first byte; we `json.dump` into it via `os.fdopen` and `os.replace` onto the
  final path (atomic, same filesystem). No `open()`-then-`chmod` window. The parent
  dir is created `mode=0o700`.
- **Refuse-on-load, never repair**: on POSIX, `st_mode & 0o077 != 0` → `SessionError`
  (the secret may already have leaked; surface it, do not silently chmod). On Windows
  the check is skipped (`os.chmod`/mode bits are no-ops; AppData is per-user ACL'd).
- **`Session`** is a frozen, slotted dataclass with a cookie-free `__repr__`,
  JSON-safe `to_dict()`, and a validating `from_dict()` (matching the project's model
  conventions). Fields: `sp_dc`, `saved_at_ms`, `sp_dc_expires_ms: int | None`,
  `version`.
- A small `SessionStore` indirection (Protocol or `store=` string dispatch) selects
  the file backend by default; the keyring backend plugs in without touching callers.

## Keyring backend (optional extra)

`auth/session_keyring.py` lazy-imports `keyring` and stores ONLY `sp_dc` in the OS
secret store (`set/get/delete_password("spotifyscraper", "sp_dc", ...)`), keeping
metadata in the 0600 JSON file. This dodges the Windows Credential Locker ~1280-char
limit (a JSON envelope plus a cached token could exceed it). `NoKeyringError` on
headless Linux falls back to the file backend with a `logging.warning`, never a
crash. Backend choice is always explicit (`store="file"|"keyring"`) — never switched
implicitly by what is pip-installed.

## Errors

Add `SessionError(SpotifyScraperError)` for store-layer faults (missing, corrupt,
insecure, expired). The client entry points (`from_saved_session`/`logout`) surface
these as `SessionError`. The existing `get_lyrics`/`get_transcript` token path keeps
raising `AuthenticationError` unchanged — the two stay distinct. (The blueprint
allowed `AuthenticationError` to suffice; a dedicated `SessionError` is chosen so
"bad saved file" is distinguishable from "Spotify rejected the cookie", matching the
research's `SessionExpiredError` intent without a separate expiry class for v1.)

## Client wiring

`login(*, save=True, store="file", timeout=300.0, proxy=None, session_path=None)`:
`_ensure_open()`; method-level lazy `from spotify_scraper.browser import
capture_sp_dc`; capture; `self._cookies = sp_dc`; `self._cookie_tokens = None`
(force re-exchange next authenticated call); `save_session(...)` when `save`. The
async client awaits `capture_sp_dc_async`. No new slot is needed — both
`self._cookies` and `self._cookie_tokens` already exist.

**Proxy note (codebase fact):** neither client stores `proxy` as a slot — it is
consumed by `HttpxTransport` at construction and not retained. The blueprint's
`self._proxy_or_none()` is therefore not viable. `login` takes an explicit `proxy=`
parameter instead, which is cleaner and avoids adding a slot. Callers who built the
client with a proxy pass it through here if they want the login browser to use it.

`from_saved_session(*, store="file", session_path=None, **kwargs)` is a classmethod:
`load_session(...)` then `cls(cookies=session.sp_dc, **kwargs)`. Pure stdlib — no
extra needed to reload, so a user who logged in once runs hermetically afterward.
`**kwargs` forwards `rate_limit`/`retry`/`proxy`/`timeout`/`transport`/etc.
`logout(*, store, session_path)` is a classmethod calling `clear_session(...)`.
On the async client, `from_saved_session`/`logout` stay sync (they only read/delete
a file; no event loop needed) and return `AsyncSpotifyClient`.

## CLI (optional)

A `login` command runs `capture_sp_dc()` + `save_session()` and prints ONLY the
saved path; a `logout` command calls `clear_session()`. A `--store file|keyring`
option selects the backend. Missing `browser` extra surfaces the existing helpful
message.

## Test strategy (hermetic vs. live)

Everything except the real Playwright login is hermetic: the store (temp dir, fake
clock, permission/refusal assertions, cookie-never-in-output assertions), the
keyring backend (monkeypatched fake `keyring`), and the client wiring (monkeypatched
`capture_sp_dc[_async]` returning a fake value, zero network). The real headed login
gets one `@pytest.mark.browser` smoke test asserting timeout → `AuthenticationError`
(a real Spotify login cannot be scripted in CI). `browser/login.py` is added to the
coverage `omit` list alongside `playwright.py`.

## Open questions (carry to live verification)

- Exact post-login landing URL(s) and whether `sp_dc` always lands on
  `.spotify.com` within the default 300s across regions / 2FA.
- Whether a kept persistent profile is worth offering later (vs. the v1 throwaway).
- Whether to persist/act on `sp_dc_expires_ms` (proactive `SessionExpiredError`) in
  v1 or defer to the token exchange's existing rejection path.