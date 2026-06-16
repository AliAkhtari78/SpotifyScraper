# Proposal: add-browser-login

> **Status: targets v3.4.** Builds directly on `add-podcast-transcripts` (HEAD),
> reusing the shipped cookie machinery **unchanged**: the `_cookie_tokens` slot,
> the `_cookie_provider()` builder, `CookieTokenProvider` /
> `AsyncCookieTokenProvider`, and `load_sp_dc`. This change adds a way to
> *acquire* and *persist* the `sp_dc` cookie those pieces already consume.
> **MUST branch off `add-podcast-transcripts`** (or land after it merges) — building
> on `master` would collide with the already-committed `_lyrics_*`→`_cookie_*` rename.

## Why

Today, the only authenticated features (`get_lyrics`, `get_transcript`) require the
caller to obtain an `sp_dc` cookie by hand — open a browser, log in, open dev tools,
copy the cookie, and pass it to `SpotifyClient(cookies=...)` on every run. Issue
#128 asks for first-class authenticated-session management so this is a one-time
guided step.

Fully automated username/password login is deliberately **off the table**:
`accounts.spotify.com` is gated behind bot detection, hCaptcha/reCAPTCHA, and
frequent 2FA/OTP, so a headless credential POST is fragile and would force the
library to handle a plaintext password — a direct violation of the project's
security posture. The browser-assisted flow yields the identical artifact (a valid
`sp_dc` cookie) without ever touching credentials. We therefore add:

1. A **sans-io session store** (`auth/session.py`, stdlib-only) that persists the
   captured `sp_dc` plus metadata to a per-user config dir as an owner-only (0600)
   JSON file, reloads and validates it, clears it for revocation, and offers an
   **optional OS-keyring backend** behind a new `keyring` extra.
2. A **browser-assisted login helper** (`browser/login.py`, in the existing
   `browser` extra, lazy Playwright import) that opens a **headed** Chromium, lets
   the user sign in to `open.spotify.com` manually, and captures the `sp_dc` cookie.
3. Two client entry points wiring them together: `SpotifyClient.login(...)` (opens
   the browser once, wires the cookie in, persists it) and
   `SpotifyClient.from_saved_session(...)` (reuse the persisted cookie with no
   browser, fully headless-server friendly).

The cookie value never appears in `repr`, error messages, logs, or fixtures, and is
persisted owner-only. No password is ever collected or stored.

## What Changes

- **New sans-io `auth/session.py`** (stdlib only — no new runtime dependency):
  frozen, slotted `Session(sp_dc, saved_at_ms, sp_dc_expires_ms=None, version=1)`
  with a cookie-free `__repr__` and JSON-safe `to_dict()`/`from_dict()`;
  `default_config_dir()`/`default_session_path()` (hand-rolled XDG/macOS/Windows
  resolution honoring `SPOTIFYSCRAPER_CONFIG_DIR` then `XDG_CONFIG_HOME`);
  `save_session()` (atomic `mkstemp`+`os.replace`, 0600 from first byte),
  `load_session()` (validates, **refuses group/world-readable files on POSIX**),
  `clear_session()` (idempotent delete for revocation). A pluggable
  `SessionStore` indirection selects the **file** backend (default) or an
  **optional keyring** backend.
- **New `auth/session_keyring.py`** (lazy `import keyring`, behind the new
  `keyring` extra): stores **only** the `sp_dc` value in the OS secret store
  (macOS Keychain / Windows Credential Locker / Freedesktop Secret Service),
  keeping non-secret metadata in the 0600 JSON file; helpful `ImportError` when
  the extra is missing; graceful fallback to the file backend on headless Linux
  `NoKeyringError`.
- **New `browser/login.py`** (in the `browser` extra): `capture_sp_dc(...)` and
  `capture_sp_dc_async(...)` open a **headed** Chromium (`headless=False` always),
  navigate to the login page, **poll `context.cookies("https://open.spotify.com/")`
  until `sp_dc` appears or a generous timeout elapses**, and return the value;
  `AuthenticationError` on no-capture/timeout. Never logs the value; catches
  Playwright errors and re-raises as `AuthenticationError` without leaking a stack
  or the cookie.
- **`browser/__init__.py`**: re-export `capture_sp_dc`/`capture_sp_dc_async` inside
  the existing `try/except ImportError` guard; extend `__all__`.
- **Client entry points on both clients** (sync + async):
  - `login(*, save=True, store="file", timeout=300.0, proxy=None, session_path=None)`
    — lazy `from spotify_scraper.browser import capture_sp_dc[_async]`, capture,
    set `self._cookies`, reset `self._cookie_tokens = None`, and (when `save`)
    `save_session(...)`. The async client awaits `capture_sp_dc_async`.
  - `from_saved_session(*, store="file", session_path=None, **kwargs)` classmethod
    — `load_session(...)` then `cls(cookies=session.sp_dc, **kwargs)`. Pure stdlib;
    no extra needed to *reload*. `**kwargs` forwards `rate_limit`/`retry`/`proxy`/
    `timeout`/`transport`/etc.
  - `logout(*, store="file", session_path=None)` classmethod — `clear_session(...)`
    for one-call local revocation (deletes the file and the keyring entry if used).
- **New typed error**: `SessionError(SpotifyScraperError)` for store-layer faults
  (missing/corrupt/insecure/expired session file). The client entry points surface
  these as `SessionError`; lyrics/transcript token failures keep raising
  `AuthenticationError` unchanged.
- **Optional CLI surface** (`cli` extra): a `login` command that runs
  `capture_sp_dc()` + `save_session()` and prints **only** the saved path; a
  `logout` command that calls `clear_session()`. Clear message when the `browser`
  extra is missing.
- **`pyproject.toml`**: add a `keyring = ["keyring>=24"]` extra, fold it into `all`;
  add `src/spotify_scraper/browser/login.py` to the coverage `omit` list (real
  browser, like `playwright.py`). No new *required* runtime dependency.
- **Hermetic tests** for the session store, the keyring backend (monkeypatched fake
  keyring), and the client wiring (injected fake cookie source + temp dir); a single
  `@pytest.mark.browser` manual smoke test for the real Playwright login; an
  extension of the existing ImportError test to cover the two new browser symbols.

## Impact

- **New**: `auth/session.py`, `auth/session_keyring.py`, `browser/login.py`,
  `SessionError`, `login`/`from_saved_session`/`logout` on both clients, a `login`/
  `logout` CLI command, a `keyring` extra, exports.
- **Reused unchanged**: `auth/cookies.py` (`load_sp_dc`, `CookieTokenProvider`,
  `AsyncCookieTokenProvider`), the `_cookie_tokens` slot + `_cookie_provider()`
  builder, `browser/playwright.py`, the `browser`-extra lazy-import guard.
- **One live verification item gates only the headed-login UX**: the real
  Playwright capture (does `sp_dc` reliably appear on `.spotify.com` after a manual
  login, within the timeout, across regions/2FA?) can only be confirmed by the
  maintainer actually logging in. Everything else — file format, permissions,
  config-dir resolution, validation/refusal, keyring backend, and client wiring —
  is fully hermetic and proven now.
- **No new required dependency**: config-dir resolution is hand-rolled stdlib; the
  session store is sans-io stdlib; Playwright stays behind `browser`; keyring is a
  new *optional* extra. `mypy --strict` and the one-runtime-dependency rule hold.